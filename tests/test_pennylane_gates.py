"""The Qiskit translation of PennyLane's excitation gates must equal PennyLane's own matrices."""

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

qml = pytest.importorskip("pennylane", reason="PennyLane not installed: uv sync --extra pennylane")

from vqe_native.pennylane_gates import append_double_excitation, append_single_excitation  # noqa: E402


def _reverse_qubit_order(matrix: np.ndarray, num_qubits: int) -> np.ndarray:
    """PennyLane matrices are big-endian (wire 0 = most significant); Qiskit is little-endian."""
    tensor = matrix.reshape([2] * (2 * num_qubits))
    order = list(range(num_qubits))[::-1]
    return tensor.transpose(order + [num_qubits + k for k in order]).reshape(matrix.shape)


@pytest.mark.parametrize("theta", [0.0, 0.3, -1.2, 2.5])
def test_single_excitation_matches_pennylane(theta):
    circuit = QuantumCircuit(2)
    append_single_excitation(circuit, theta, 0, 1)
    expected = _reverse_qubit_order(qml.matrix(qml.SingleExcitation(theta, wires=[0, 1])), 2)
    assert np.allclose(Operator(circuit).data, expected)


@pytest.mark.parametrize("theta", [0.0, 0.3, -1.2, 2.5])
def test_double_excitation_matches_pennylane(theta):
    circuit = QuantumCircuit(4)
    append_double_excitation(circuit, theta, (0, 1), (2, 3))
    expected = _reverse_qubit_order(qml.matrix(qml.DoubleExcitation(theta, wires=[0, 1, 2, 3])), 4)
    assert np.allclose(Operator(circuit).data, expected)
