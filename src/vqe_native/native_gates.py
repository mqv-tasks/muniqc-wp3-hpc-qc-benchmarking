"""Compile circuits to the neutral-atom hardware format requested by the experimental team.

Hardware rules (from the experimentalists):

1. CZ gates can run in parallel on pairs of qubits.
2. Single-qubit gates are decomposed as [local Z_1, global sqrt(X), local Z_2, global sqrt(X),
   local Z_3]. The global sqrt(X) acts on *all* qubits at once; the three local Z rotations can
   have a different phase on each qubit.

The compiled circuit is therefore a sequence of *moments*, separated by barriers:

- a **CZ layer**: CZ gates on disjoint qubit pairs, executed in parallel;
- a **single-qubit block**: ``rz`` per qubit, ``gsx``, ``rz`` per qubit, ``gsx``, ``rz`` per qubit,
  where ``gsx`` is one global sqrt(X) pulse on every qubit;
- a **Z layer**: only ``rz`` (virtual phases, no pulse). Used only at the end of ``ansatz.qasm``,
  which has no measurement and must reproduce the state exactly.

How the compiler keeps this cheap:

- Qiskit's transpiler (optimization level 3) first minimizes the CZ count. CZs are then placed
  in the earliest layer where both qubits are free (ASAP), so CZs on disjoint pairs share a layer.
- All single-qubit gates of a qubit between two of its CZs are merged into one 2x2 unitary.
  Purely diagonal (Z-only) pieces commute with CZ, so they are pushed forward into that qubit's
  next single-qubit gate instead of costing a block of their own.
- Each merged gate may sit in any single-qubit block between its two CZs. Choosing the blocks is
  an interval-stabbing problem; the greedy "earliest right endpoint" choice is optimal, so the
  number of blocks (each costs 2 global pulses) is minimal for the given CZ layering.
- A qubit with nothing to do in a block still receives the global pulses; its Z phases are set
  so the block acts as identity on it (Rz(pi) sqrt(X) Rz(pi) sqrt(X) = identity up to phase).
- Z rotations right before the final measurement do not change the outcome and are dropped. Z
  rotations acting on the initial |0> state are only a phase and are dropped too.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from qiskit.circuit import Gate, QuantumCircuit
from qiskit.circuit.library import RZGate, SXGate
from qiskit.compiler import transpile
from qiskit.quantum_info import Operator, Statevector, state_fidelity
from qiskit.synthesis import OneQubitEulerDecomposer

GLOBAL_SX_NAME = "gsx"
HARDWARE_OPS = frozenset({"rz", GLOBAL_SX_NAME, "cz", "barrier", "measure"})
_TRANSPILE_BASIS = ["rz", "sx", "cz"]
_ATOL = 1e-10

_SX = Operator(SXGate()).data
_U3_DECOMPOSER = OneQubitEulerDecomposer("U3")


def global_sx(num_qubits: int) -> Gate:
    """One global sqrt(X) pulse: sqrt(X) on every qubit at the same time."""
    definition = QuantumCircuit(num_qubits, name=GLOBAL_SX_NAME)
    for qubit in range(num_qubits):
        definition.sx(qubit)
    gate = Gate(GLOBAL_SX_NAME, num_qubits, [], label="global sqrt(X)")
    gate.definition = definition
    return gate


def _rz(angle: float) -> np.ndarray:
    return np.diag([np.exp(-0.5j * angle), np.exp(0.5j * angle)])


def _wrap(angle: float) -> float:
    """Map an angle to (-pi, pi]."""
    wrapped = (angle + np.pi) % (2 * np.pi) - np.pi
    return np.pi if np.isclose(wrapped, -np.pi) else float(wrapped)


def _is_diagonal(unitary: np.ndarray) -> bool:
    return abs(unitary[0, 1]) < _ATOL and abs(unitary[1, 0]) < _ATOL


def _equal_up_to_phase(a: np.ndarray, b: np.ndarray) -> bool:
    return abs(abs(np.trace(a.conj().T @ b)) - 2) < 1e-9


def zsxzsxz_angles(unitary: np.ndarray) -> tuple[float, float, float]:
    """Angles (z1, z2, z3) with unitary = Rz(z3) . SX . Rz(z2) . SX . Rz(z1), up to global phase.

    Time order is z1 first. Uses U3(theta, phi, lam) = Rz(phi + pi) SX Rz(theta + pi) SX Rz(lam),
    which holds for every single-qubit unitary, so the result is always checked, not assumed.
    """
    theta, phi, lam = _U3_DECOMPOSER.angles(unitary)
    z1, z2, z3 = _wrap(lam), _wrap(theta + np.pi), _wrap(phi + np.pi)
    rebuilt = _rz(z3) @ _SX @ _rz(z2) @ _SX @ _rz(z1)
    if not _equal_up_to_phase(rebuilt, unitary):
        raise ValueError("Z-sqrt(X)-Z-sqrt(X)-Z decomposition failed")
    return z1, z2, z3


@dataclass
class _Segment:
    """Single-qubit work on one qubit between two of its CZ layers.

    It may be placed in any single-qubit block k with first_block <= k <= last_block, where
    block k sits between CZ layer k and CZ layer k+1 (block 0 is before the first CZ layer).
    """

    qubit: int
    first_block: int
    last_block: int
    unitary: np.ndarray


def compile_to_hardware(circuit: QuantumCircuit, *, measure: bool) -> QuantumCircuit:
    """Compile a measurement-free circuit to the hardware moment format described above.

    With ``measure=True``, every qubit ``i`` is measured into ``meas[i]`` at the end, and Z
    rotations right before measurement are dropped (they cannot change the outcome).
    """
    if any(instr.operation.name == "measure" for instr in circuit.data):
        raise ValueError("Pass the circuit without measurements; use measure=True instead")
    num_qubits = circuit.num_qubits
    # Expand SWAP/permutation gates first: otherwise the transpiler's ElidePermutations pass
    # removes them and only *records* the resulting qubit relabelling in its layout, which would
    # silently change which physical qubit carries which logical qubit.
    circuit = circuit.decompose(gates_to_decompose=["swap", "permutation"])
    transpiled = transpile(circuit, basis_gates=_TRANSPILE_BASIS, optimization_level=3, seed_transpiler=0)
    if transpiled.layout is not None and (
        transpiled.layout.initial_index_layout() != list(range(num_qubits))
        or transpiled.layout.final_index_layout() != list(range(num_qubits))
    ):
        raise ValueError("Transpiler permuted the qubits; refusing to emit a relabelled circuit")

    # --- 1. ASAP CZ layering, collecting each qubit's single-qubit work between its CZs. ---
    cz_layers: list[list[tuple[int, int]]] = []
    last_layer = [0] * num_qubits  # CZ layer index (1-based) of the qubit's latest CZ; 0 = none
    pending = [np.eye(2, dtype=complex) for _ in range(num_qubits)]
    raw_segments: list[list[tuple[int, int, np.ndarray]]] = [[] for _ in range(num_qubits)]

    for instruction in transpiled.data:
        name = instruction.operation.name
        qubits = [transpiled.find_bit(q).index for q in instruction.qubits]
        if name == "cz":
            layer = max(last_layer[q] for q in qubits) + 1
            if layer > len(cz_layers):
                cz_layers.append([])
            cz_layers[layer - 1].append((qubits[0], qubits[1]))
            for q in qubits:
                raw_segments[q].append((last_layer[q], layer - 1, pending[q]))
                pending[q] = np.eye(2, dtype=complex)
                last_layer[q] = layer
        elif name in ("rz", "sx"):
            (q,) = qubits
            pending[q] = Operator(instruction.operation).data @ pending[q]
        elif name == "barrier":
            continue
        else:
            raise ValueError(f"Unexpected operation after transpilation: {name}")

    num_layers = len(cz_layers)
    for q in range(num_qubits):
        raw_segments[q].append((last_layer[q], num_layers, pending[q]))

    # --- 2. Push diagonal (Z-only) pieces forward through CZs (they commute with CZ). ---
    segments: list[_Segment] = []
    trailing_z = [0.0] * num_qubits
    for q in range(num_qubits):
        carried = np.eye(2, dtype=complex)
        for index, (first, last, unitary) in enumerate(raw_segments[q]):
            combined = unitary @ carried
            if _is_diagonal(combined):
                # On the initial |0> state a diagonal gate is only a phase: drop it.
                carried = np.eye(2, dtype=complex) if index == 0 else combined
                continue
            segments.append(_Segment(q, first, last, combined))
            carried = np.eye(2, dtype=complex)
        if not _is_diagonal(carried):  # pragma: no cover - guarded by construction
            raise AssertionError("carried part must be diagonal")
        trailing_z[q] = _wrap(float(np.angle(carried[1, 1]) - np.angle(carried[0, 0])))

    # --- 3. Choose single-qubit blocks: greedy interval stabbing (minimal number of blocks). ---
    chosen_blocks: list[int] = []
    for segment in sorted(segments, key=lambda s: s.last_block):
        if not any(segment.first_block <= block <= segment.last_block for block in chosen_blocks):
            chosen_blocks.append(segment.last_block)
    block_contents: dict[int, dict[int, np.ndarray]] = {block: {} for block in chosen_blocks}
    for segment in segments:
        block = min(b for b in chosen_blocks if segment.first_block <= b <= segment.last_block)
        block_contents[block][segment.qubit] = segment.unitary

    # --- 4. Emit moments. ---
    out = QuantumCircuit(num_qubits, name=circuit.name)
    pulse = global_sx(num_qubits)
    identity_angles = zsxzsxz_angles(np.eye(2))

    def emit_rz_layer(angles: list[float]) -> None:
        for q, angle in enumerate(angles):
            if abs(angle) > _ATOL:
                out.append(RZGate(angle), [q])

    for block in range(num_layers + 1):
        if block in block_contents:
            angles = [
                zsxzsxz_angles(block_contents[block][q]) if q in block_contents[block] else identity_angles
                for q in range(num_qubits)
            ]
            if block == 0:  # Z_1 acts on |0>: only a phase
                angles = [(0.0, z2, z3) for (_, z2, z3) in angles]
            emit_rz_layer([a[0] for a in angles])
            out.append(pulse, range(num_qubits))
            emit_rz_layer([a[1] for a in angles])
            out.append(pulse, range(num_qubits))
            emit_rz_layer([a[2] for a in angles])
            out.barrier()
        if block < num_layers:
            for a, b in cz_layers[block]:
                out.cz(a, b)
            out.barrier()

    if measure:
        if out.data and out.data[-1].operation.name == "barrier":
            del out.data[-1]
        out.measure_all()
    else:
        if any(abs(angle) > _ATOL for angle in trailing_z):
            emit_rz_layer(trailing_z)
        if out.data and out.data[-1].operation.name == "barrier":
            del out.data[-1]
    return out


@dataclass(frozen=True)
class HardwareCost:
    cz_gates: int
    cz_layers: int
    single_qubit_blocks: int
    global_sx_pulses: int


def validate_hardware_format(circuit: QuantumCircuit) -> HardwareCost:
    """Check that a circuit follows the moment format exactly; return its cost.

    Raises ``ValueError`` describing the first violation found.
    """
    num_qubits = circuit.num_qubits
    used = {instr.operation.name for instr in circuit.data}
    if not used <= HARDWARE_OPS:
        raise ValueError(f"Non-hardware operations: {sorted(used - HARDWARE_OPS)}")

    moments: list[list] = [[]]
    for instruction in circuit.data:
        if instruction.operation.name == "barrier":
            moments.append([])
        else:
            moments[-1].append(instruction)
    moments = [m for m in moments if m]

    cz_gates = cz_layers = blocks = 0
    seen_measure = False
    for position, moment in enumerate(moments):
        names = [instr.operation.name for instr in moment]
        qubit_lists = [[circuit.find_bit(q).index for q in instr.qubits] for instr in moment]
        if seen_measure:
            raise ValueError("Operations after measurement")

        if set(names) == {"cz"}:
            touched = [q for qubits in qubit_lists for q in qubits]
            if len(touched) != len(set(touched)):
                raise ValueError(f"CZ layer {position} uses a qubit twice: {qubit_lists}")
            cz_gates += len(moment)
            cz_layers += 1
        elif set(names) == {"measure"}:
            seen_measure = True
        elif GLOBAL_SX_NAME in names:
            # Expect: rz* gsx rz* gsx rz*, each rz slot touching each qubit at most once.
            slots: list[list[int]] = [[]]
            for name, qubits in zip(names, qubit_lists):
                if name == GLOBAL_SX_NAME:
                    if sorted(qubits) != list(range(num_qubits)):
                        raise ValueError(f"gsx in moment {position} is not global: {qubits}")
                    slots.append([])
                elif name == "rz":
                    slots[-1].append(qubits[0])
                else:
                    raise ValueError(f"'{name}' inside single-qubit block {position}")
            if len(slots) != 3:
                raise ValueError(f"Block {position} has {len(slots) - 1} global sqrt(X), expected 2")
            for slot in slots:
                if len(slot) != len(set(slot)):
                    raise ValueError(f"Block {position} applies two Z rotations to a qubit in one slot")
            blocks += 1
        elif set(names) == {"rz"}:
            touched = [qubits[0] for qubits in qubit_lists]
            if len(touched) != len(set(touched)):
                raise ValueError(f"Z layer {position} rotates a qubit twice")
        else:
            raise ValueError(f"Moment {position} mixes operations: {names}")

    return HardwareCost(
        cz_gates=cz_gates, cz_layers=cz_layers, single_qubit_blocks=blocks, global_sx_pulses=2 * blocks
    )


def assert_statevector_equivalent(original: QuantumCircuit, compiled: QuantumCircuit) -> None:
    """Verify compilation preserved the prepared state from |0...0> (up to global phase).

    Only valid for circuits with no measurements. Uses a direct state-fidelity threshold rather
    than ``Statevector.equiv``, which estimates the global phase from a single amplitude and is
    numerically unstable when two amplitudes are close in magnitude.
    """
    fidelity = state_fidelity(Statevector(original), Statevector(compiled))
    if fidelity < 1 - 1e-9:
        raise ValueError(f"Compiled circuit is not equivalent to the original circuit (fidelity={fidelity})")


def assert_same_measurement_distribution(original: QuantumCircuit, compiled: QuantumCircuit) -> None:
    """Verify two circuits give the same computational-basis outcome probabilities.

    Used for measurement circuits, where Z rotations before measurement are legitimately dropped.
    """
    p_original = Statevector(original.remove_final_measurements(inplace=False)).probabilities()
    p_compiled = Statevector(compiled.remove_final_measurements(inplace=False)).probabilities()
    distance = 0.5 * float(np.abs(p_original - p_compiled).sum())
    if distance > 1e-9:
        raise ValueError(f"Measurement distributions differ (total variation distance {distance:.2e})")
