"""The circuits must follow the experimentalists' hardware rules exactly:

1. CZ gates run in parallel on disjoint pairs of qubits (CZ layers).
2. Single-qubit gates are [local Z_1, global sqrt(X), local Z_2, global sqrt(X), local Z_3],
   where the global sqrt(X) acts on all qubits.

``validate_hardware_format`` enforces both; these tests run it on the pipeline circuits, on the
committed QASM files, and on random circuits, and check it rejects circuits that break a rule.
"""

import hashlib
from pathlib import Path

import numpy as np
import pytest
from qiskit import QuantumCircuit, qasm3
from qiskit.circuit.random import random_circuit
from qiskit.quantum_info import Operator, Statevector, random_unitary, state_fidelity

from vqe_native.native_gates import (
    _SX,
    _rz,
    assert_same_measurement_distribution,
    assert_statevector_equivalent,
    compile_to_hardware,
    global_sx,
    validate_hardware_format,
    zsxzsxz_angles,
)

OUTPUTS = Path(__file__).resolve().parent.parent / "outputs"
V1 = OUTPUTS / "v1_sent_to_experiment"

# Regression ceilings on CZ layers (the dominant hardware cost) for the pair ansatz.
PAIR_MAX_CZ_LAYERS = {"h2": 2, "lih": 12}


def test_pipeline_circuits_follow_hardware_format(case, result, groups):
    molecule, ansatz = case
    for circuit in [result.native_ansatz_circuit] + [g.circuit for g in groups]:
        cost = validate_hardware_format(circuit)
        if ansatz == "pair":
            assert cost.cz_layers <= PAIR_MAX_CZ_LAYERS[molecule]


GENERATED_QASM = sorted(p for p in OUTPUTS.glob("*/*/*.qasm") if V1 not in p.parents)


@pytest.mark.parametrize("path", GENERATED_QASM, ids=lambda p: str(p.relative_to(OUTPUTS)))
def test_committed_qasm_files_follow_hardware_format(path):
    validate_hardware_format(qasm3.load(path))


# --- The first delivery is kept frozen, and the uccsd-qiskit ansatz must still reproduce it. ---


def test_v1_files_are_unchanged():
    for line in (V1 / "SHA256SUMS").read_text().splitlines():
        expected, name = line.split(maxsplit=1)
        assert hashlib.sha256((V1 / name).read_bytes()).hexdigest() == expected, name


@pytest.mark.parametrize("molecule", ["h2", "lih"])
def test_uccsd_qiskit_reproduces_the_v1_state(molecule):
    from conftest import cached_pipeline

    v1_state = Statevector(qasm3.load(V1 / molecule / "ansatz.qasm"))
    new_state = Statevector(cached_pipeline(molecule, "uccsd-qiskit").vqe_result.bound_circuit)
    assert state_fidelity(v1_state, new_state) > 1 - 1e-9


def test_zsxzsxz_decomposition_of_random_unitaries():
    for seed in range(50):
        unitary = random_unitary(2, seed=seed).data
        z1, z2, z3 = zsxzsxz_angles(unitary)
        rebuilt = _rz(z3) @ _SX @ _rz(z2) @ _SX @ _rz(z1)
        assert abs(abs(np.trace(unitary.conj().T @ rebuilt)) - 2) < 1e-9


def _random_unitary_circuit(num_qubits: int, seed: int) -> QuantumCircuit:
    return random_circuit(num_qubits, depth=6, max_operands=2, seed=seed)


@pytest.mark.parametrize("seed", range(10))
def test_compiler_preserves_state_on_random_circuits(seed):
    circuit = _random_unitary_circuit(5, seed)
    compiled = compile_to_hardware(circuit, measure=False)
    validate_hardware_format(compiled)
    assert_statevector_equivalent(circuit, compiled)


@pytest.mark.parametrize("seed", range(10))
def test_compiler_preserves_measurement_distribution_on_random_circuits(seed):
    circuit = _random_unitary_circuit(5, seed)
    compiled = compile_to_hardware(circuit, measure=True)
    validate_hardware_format(compiled)
    assert_same_measurement_distribution(circuit, compiled)


def test_global_sx_is_sqrt_x_on_every_qubit():
    expected = Operator(QuantumCircuit(3).compose(_all_sx(3)))
    assert Operator(global_sx(3)).equiv(expected)


def _all_sx(n: int) -> QuantumCircuit:
    circuit = QuantumCircuit(n)
    for q in range(n):
        circuit.sx(q)
    return circuit


# --- The validator must reject circuits that break the rules. ---


def test_validator_rejects_per_qubit_sx():
    circuit = QuantumCircuit(2)
    circuit.sx(0)
    with pytest.raises(ValueError, match="Non-hardware"):
        validate_hardware_format(circuit)


def test_validator_rejects_non_global_pulse():
    circuit = QuantumCircuit(3)
    circuit.append(global_sx(2), [0, 1])
    circuit.append(global_sx(2), [0, 1])
    with pytest.raises(ValueError, match="not global"):
        validate_hardware_format(circuit)


def test_validator_rejects_block_with_one_pulse():
    circuit = QuantumCircuit(2)
    circuit.rz(0.3, 0)
    circuit.append(global_sx(2), [0, 1])
    with pytest.raises(ValueError, match="expected 2"):
        validate_hardware_format(circuit)


def test_validator_rejects_cz_layer_reusing_a_qubit():
    circuit = QuantumCircuit(3)
    circuit.cz(0, 1)
    circuit.cz(1, 2)
    with pytest.raises(ValueError, match="uses a qubit twice"):
        validate_hardware_format(circuit)


def test_validator_rejects_mixed_moment():
    circuit = QuantumCircuit(2)
    circuit.cz(0, 1)
    circuit.rz(0.1, 0)
    with pytest.raises(ValueError, match="mixes"):
        validate_hardware_format(circuit)
