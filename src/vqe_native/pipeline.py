"""End-to-end pipeline: molecule -> qubit Hamiltonian -> ansatz -> converged VQE circuit.

The ansatz is chosen by name from ``vqe_native.ansatz.ANSATZE``
("uccsd-qiskit", "uccsd-pennylane" or "pair").
"""

from __future__ import annotations

from dataclasses import dataclass

from qiskit.circuit import QuantumCircuit

from vqe_native.ansatz import ANSATZE, AnsatzSpec
from vqe_native.hamiltonian import QubitHamiltonian, build_qubit_hamiltonian
from vqe_native.molecules import MoleculeSpec, build_problem
from vqe_native.native_gates import assert_statevector_equivalent, compile_to_hardware
from vqe_native.vqe_runner import VQERunResult, run_vqe


@dataclass(frozen=True)
class PipelineResult:
    ansatz: AnsatzSpec
    hamiltonian: QubitHamiltonian
    vqe_result: VQERunResult
    native_ansatz_circuit: QuantumCircuit


def run_pipeline(spec: MoleculeSpec, ansatz_name: str) -> PipelineResult:
    if ansatz_name not in ANSATZE:
        raise ValueError(f"Unknown ansatz {ansatz_name!r}; choose from {sorted(ANSATZE)}")
    ansatz_spec = ANSATZE[ansatz_name]

    problem = build_problem(spec)
    hamiltonian = build_qubit_hamiltonian(problem)
    ansatz = ansatz_spec.build(hamiltonian)
    vqe_result = run_vqe(
        hamiltonian, ansatz, tight_convergence=ansatz_spec.tight_convergence, prune=ansatz_spec.prune
    )

    native_ansatz_circuit = compile_to_hardware(vqe_result.bound_circuit, measure=False)
    assert_statevector_equivalent(vqe_result.bound_circuit, native_ansatz_circuit)

    return PipelineResult(
        ansatz=ansatz_spec,
        hamiltonian=hamiltonian,
        vqe_result=vqe_result,
        native_ansatz_circuit=native_ansatz_circuit,
    )
