"""PennyLane's fermionic excitation gates, translated gate by gate into Qiskit circuits.

PennyLane's single- and double-excitation gates come with published decompositions
(``qml.SingleExcitation``: 2 CNOTs, Arrazola et al., Quantum 6, 742 (2022), arXiv:2104.05695;
``qml.DoubleExcitation``: 14 CNOTs, Anselmetti et al., New J. Phys. 23, 113010 (2021)). They are much shorter than
qiskit-nature's generic construction, which exponentiates each Pauli string of the excitation
operator with its own CNOT ladder (one double excitation -> 8 Pauli strings).

We take PennyLane's decomposition (so the gates are traceably PennyLane's), and append the resulting
elementary gates to a Qiskit circuit, keeping the rotation angles as Qiskit ``Parameter``
expressions. Everything downstream (VQE, hardware compilation, QASM 3 export) stays in Qiskit.

Note: PennyLane's excitation gates are Givens rotations on the chosen qubits and leave out the
Jordan-Wigner parity (Z) strings of the fermionic operators. They form a valid, general,
particle-number-conserving UCCSD-type ansatz, but each excitation is not exactly the operator
applied by qiskit-nature's UCCSD (and the angle convention differs), so circuits and converged
angles differ.

PennyLane is an optional dependency: ``uv sync --extra pennylane``.
"""

from __future__ import annotations

from qiskit.circuit import QuantumCircuit


def _require_pennylane():
    try:
        import pennylane as qml
    except ImportError as error:  # pragma: no cover - depends on the environment
        raise ImportError(
            "The 'uccsd-pennylane' ansatz needs PennyLane. Install it with: uv sync --extra pennylane"
        ) from error
    return qml


# PennyLane operation name -> function appending the Qiskit equivalent.
_TRANSLATION = {
    "Hadamard": lambda qc, params, qubits: qc.h(*qubits),
    "CNOT": lambda qc, params, qubits: qc.cx(*qubits),
    "CZ": lambda qc, params, qubits: qc.cz(*qubits),
    "PauliX": lambda qc, params, qubits: qc.x(*qubits),
    "RX": lambda qc, params, qubits: qc.rx(params[0], *qubits),
    "RY": lambda qc, params, qubits: qc.ry(params[0], *qubits),
    "RZ": lambda qc, params, qubits: qc.rz(params[0], *qubits),
    "S": lambda qc, params, qubits: qc.s(*qubits),
    "T": lambda qc, params, qubits: qc.t(*qubits),
}


def _append(circuit: QuantumCircuit, operation, wire_to_qubit: dict) -> None:
    qubits = [wire_to_qubit[w] for w in operation.wires]
    if operation.name in _TRANSLATION:
        _TRANSLATION[operation.name](circuit, operation.parameters, qubits)
        return
    if not operation.has_decomposition:
        raise ValueError(f"No Qiskit translation for PennyLane operation {operation.name!r}")
    for sub_operation in operation.decomposition():
        _append(circuit, sub_operation, wire_to_qubit)


def append_single_excitation(circuit: QuantumCircuit, theta, occupied: int, virtual: int) -> None:
    """PennyLane ``SingleExcitation(theta)``: rotates |1_occ 0_virt> <-> |0_occ 1_virt>."""
    qml = _require_pennylane()
    _append(circuit, qml.SingleExcitation(theta, wires=[0, 1]), {0: occupied, 1: virtual})


def append_double_excitation(circuit: QuantumCircuit, theta, occupied: tuple[int, int], virtual: tuple[int, int]) -> None:
    """PennyLane ``DoubleExcitation(theta)``: rotates both electrons from ``occupied`` to ``virtual``."""
    qml = _require_pennylane()
    wires = {0: occupied[0], 1: occupied[1], 2: virtual[0], 3: virtual[1]}
    _append(circuit, qml.DoubleExcitation(theta, wires=[0, 1, 2, 3]), wires)
