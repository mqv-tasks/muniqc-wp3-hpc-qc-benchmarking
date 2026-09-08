"""Compile circuits to the neutral-atom native gate set.

Native operations: CZ (entangling) + local Pauli rotations, physically
realized as SQRT(X)-PHI-SQRT(X). This corresponds to Qiskit's standard
``{rz, sx, cz}`` basis: ``sx`` is the fixed SQRT(X) pulse and ``rz`` is the
free virtual phase ("PHI") rotation.
"""

from __future__ import annotations

from qiskit.circuit import QuantumCircuit
from qiskit.compiler import transpile
from qiskit.quantum_info import Statevector, state_fidelity

NATIVE_BASIS_GATES = ["rz", "sx", "cz"]
ALLOWED_OPS = frozenset(NATIVE_BASIS_GATES) | {"barrier", "measure"}


def compile_to_native(circuit: QuantumCircuit) -> QuantumCircuit:
    """Transpile to {rz, sx, cz}, assuming all-to-all connectivity.

    Neutral-atom arrays are reconfigurable (atoms can be rearranged between
    entangling operations), so no ``coupling_map`` is imposed here. Mapping
    onto a specific hardware layout/connectivity is the hardware co-design
    step flagged by the collaborators as future work, not part of this first
    compiled version.
    """
    compiled = transpile(circuit, basis_gates=NATIVE_BASIS_GATES, optimization_level=3)
    used_ops = set(compiled.count_ops())
    if not used_ops <= ALLOWED_OPS:
        raise ValueError(f"Compiled circuit uses non-native operations: {used_ops - ALLOWED_OPS}")
    return compiled


def assert_statevector_equivalent(original: QuantumCircuit, compiled: QuantumCircuit) -> None:
    """Verify compilation preserved the circuit's action (up to global phase).

    Only valid for circuits with no measurements/classical registers. Uses a
    direct state-fidelity threshold rather than ``Statevector.equiv``: that
    method estimates the global phase from a single (largest-magnitude)
    amplitude, which becomes numerically unstable exactly when two amplitudes
    are close in magnitude, and can spuriously return False even when the
    true fidelity is 1 to within machine precision.
    """
    fidelity = state_fidelity(Statevector(original), Statevector(compiled))
    if fidelity < 1 - 1e-9:
        raise ValueError(f"Compiled circuit is not equivalent to the original circuit (fidelity={fidelity})")
