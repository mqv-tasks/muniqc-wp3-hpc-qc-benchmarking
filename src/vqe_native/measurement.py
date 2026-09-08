"""Group Hamiltonian terms into qubit-wise commuting sets and build measurement circuits.

Qubit-wise commuting grouping (as opposed to general commuting grouping) means
every term in a group can be measured simultaneously using only a single layer
of *local* basis-change gates (H for X, S-dagger then H for Y, nothing for Z
or I) before a standard computational-basis measurement. That matters here
because the native gate set has no free two-qubit rotation to spend on a more
general diagonalizing circuit -- only CZ.
"""

from __future__ import annotations

from dataclasses import dataclass

from qiskit.circuit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp

from vqe_native.native_gates import compile_to_native

# Per-qubit basis label, in the order the qubits appear in the Pauli string
# (index 0 == qubit 0), not the usual reversed string-label convention.
_PAULI_LABELS = {(False, False): "I", (True, False): "X", (False, True): "Z", (True, True): "Y"}


@dataclass(frozen=True)
class MeasurementGroup:
    index: int
    # One basis label per qubit ("I", "X", "Y", or "Z"), qubit-0-first order.
    qubit_bases: list[str]
    paulis: SparsePauliOp  # the qubit-wise commuting terms measured by this circuit
    circuit: QuantumCircuit  # ansatz + basis rotation + measurement, compiled to native gates


def _qubit_bases_for_group(group: SparsePauliOp) -> list[str]:
    """Determine, per qubit, the single Pauli (I/X/Y/Z) shared by every term in the group."""
    num_qubits = group.num_qubits
    bases = ["I"] * num_qubits
    for pauli in group.paulis:
        for qubit in range(num_qubits):
            label = _PAULI_LABELS[(bool(pauli.x[qubit]), bool(pauli.z[qubit]))]
            if label == "I":
                continue
            if bases[qubit] not in ("I", label):
                raise ValueError(
                    f"Group is not qubit-wise commuting at qubit {qubit}: "
                    f"saw both {bases[qubit]!r} and {label!r}"
                )
            bases[qubit] = label
    return bases


def _add_measurement_basis_rotation(circuit: QuantumCircuit, qubit_bases: list[str]) -> None:
    for qubit, basis in enumerate(qubit_bases):
        if basis == "X":
            circuit.h(qubit)
        elif basis == "Y":
            circuit.sdg(qubit)
            circuit.h(qubit)
        # "Z" and "I" both measure directly in the computational basis.


def build_measurement_groups(
    bound_ansatz: QuantumCircuit, hamiltonian_operator: SparsePauliOp
) -> list[MeasurementGroup]:
    """Build one native-gate measurement circuit per qubit-wise commuting group."""
    groups = hamiltonian_operator.group_commuting(qubit_wise=True)

    measurement_groups = []
    for index, group in enumerate(groups):
        qubit_bases = _qubit_bases_for_group(group)

        circuit = bound_ansatz.copy()
        _add_measurement_basis_rotation(circuit, qubit_bases)
        circuit.measure_all()

        compiled = compile_to_native(circuit)

        measurement_groups.append(
            MeasurementGroup(
                index=index,
                qubit_bases=qubit_bases,
                paulis=group,
                circuit=compiled,
            )
        )
    return measurement_groups
