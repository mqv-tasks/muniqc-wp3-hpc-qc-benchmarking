"""Closed-loop proof that the exported, native-gate-compiled measurement circuits
actually reconstruct the right energy.

This uses exact statevector probabilities rather than sampled shots (no shot
noise to average away), so any mismatch here would mean the measurement/basis
-rotation/grouping logic itself is wrong -- not a statistics artifact.
"""

from qiskit.quantum_info import Statevector

EXACT_DIAGONALIZATION_TOLERANCE_HA = 1e-6


def _bit_at(bitstring: str, qubit: int) -> int:
    return int(bitstring[len(bitstring) - 1 - qubit])


def _term_expectation(probabilities: dict, non_identity_qubits: list[int]) -> float:
    if not non_identity_qubits:
        return 1.0  # an all-identity term always has expectation value 1
    expectation = 0.0
    for bitstring, probability in probabilities.items():
        parity = 1
        for qubit in non_identity_qubits:
            if _bit_at(bitstring, qubit):
                parity *= -1
        expectation += probability * parity
    return expectation


def _reconstruct_energy(measurement_groups, energy_offset: float) -> float:
    total = energy_offset
    for group in measurement_groups:
        circuit_without_measurement = group.circuit.remove_final_measurements(inplace=False)
        probabilities = Statevector(circuit_without_measurement).probabilities_dict()
        for pauli, coeff in zip(group.paulis.paulis, group.paulis.coeffs):
            non_identity_qubits = [q for q in range(pauli.num_qubits) if pauli.x[q] or pauli.z[q]]
            total += coeff.real * _term_expectation(probabilities, non_identity_qubits)
    return total


def test_measurement_circuits_reconstruct_vqe_energy(result, groups):
    reconstructed = _reconstruct_energy(groups, result.hamiltonian.energy_offset)
    assert abs(reconstructed - result.vqe_result.vqe_total_energy) < EXACT_DIAGONALIZATION_TOLERANCE_HA
