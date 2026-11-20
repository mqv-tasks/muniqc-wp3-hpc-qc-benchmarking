"""End-to-end pipeline: molecule -> qubit Hamiltonian -> pair ansatz -> converged VQE circuit."""

from __future__ import annotations

from dataclasses import dataclass

from qiskit.circuit import QuantumCircuit

from vqe_native.ansatz import build_pair_ansatz
from vqe_native.hamiltonian import QubitHamiltonian, build_qubit_hamiltonian
from vqe_native.molecules import MoleculeSpec, build_problem
from vqe_native.native_gates import assert_statevector_equivalent, compile_to_hardware
from vqe_native.vqe_runner import VQERunResult, run_vqe


@dataclass(frozen=True)
class PipelineResult:
    hamiltonian: QubitHamiltonian
    vqe_result: VQERunResult
    native_ansatz_circuit: QuantumCircuit


def run_pipeline(spec: MoleculeSpec) -> PipelineResult:
    problem = build_problem(spec)
    hamiltonian = build_qubit_hamiltonian(problem)
    ansatz = build_pair_ansatz(hamiltonian)
    vqe_result = run_vqe(hamiltonian, ansatz)

    native_ansatz_circuit = compile_to_hardware(vqe_result.bound_circuit, measure=False)
    assert_statevector_equivalent(vqe_result.bound_circuit, native_ansatz_circuit)

    return PipelineResult(
        hamiltonian=hamiltonian,
        vqe_result=vqe_result,
        native_ansatz_circuit=native_ansatz_circuit,
    )
