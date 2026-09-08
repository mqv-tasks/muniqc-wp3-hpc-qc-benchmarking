"""Run VQE to convergence and bind the optimal parameters into the ansatz.

This module produces the *final* circuit only. The experimentalists receive a
fixed, already-optimized circuit with numeric parameters bound in — they do
not run a VQE optimization loop themselves. Iterating VQE against real
hardware is an explicit second-phase item, out of scope here.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from qiskit.circuit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit_algorithms import NumPyMinimumEigensolver, VQE
from qiskit_algorithms.optimizers import SLSQP

from vqe_native.hamiltonian import QubitHamiltonian


@dataclass(frozen=True)
class VQERunResult:
    bound_circuit: QuantumCircuit
    optimal_parameters: np.ndarray
    vqe_total_energy: float
    exact_total_energy: float


def run_vqe(hamiltonian: QubitHamiltonian, ansatz: QuantumCircuit) -> VQERunResult:
    """Run VQE with an exact statevector estimator (no shot noise, no hardware noise).

    This is the classical pre-optimization step: it finds the parameters, not
    something the experimentalists need to repeat. ``NumPyMinimumEigensolver``
    is run on the same qubit operator as an in-Qiskit sanity check that VQE
    actually converged to the ground state (a separate, independent PySCF
    cross-check lives in ``classical_reference.py``).
    """
    estimator = StatevectorEstimator()
    vqe = VQE(
        estimator,
        ansatz,
        SLSQP(),
        initial_point=np.zeros(ansatz.num_parameters),
    )
    vqe_result = vqe.compute_minimum_eigenvalue(hamiltonian.operator)

    exact_result = NumPyMinimumEigensolver().compute_minimum_eigenvalue(hamiltonian.operator)

    bound_circuit = ansatz.assign_parameters(vqe_result.optimal_point)

    return VQERunResult(
        bound_circuit=bound_circuit,
        optimal_parameters=vqe_result.optimal_point,
        vqe_total_energy=vqe_result.eigenvalue.real + hamiltonian.energy_offset,
        exact_total_energy=exact_result.eigenvalue.real + hamiltonian.energy_offset,
    )
