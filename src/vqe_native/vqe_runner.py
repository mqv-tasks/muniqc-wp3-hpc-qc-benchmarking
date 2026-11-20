"""Run VQE to convergence and bind the optimal parameters into the ansatz.

This module produces the *final* circuit only. The experimentalists receive a fixed,
already-optimized circuit with numeric parameters bound in; they do not run a VQE optimization
loop themselves. Iterating VQE against real hardware is an explicit second-phase item.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from qiskit.circuit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit_algorithms import NumPyMinimumEigensolver, VQE
from qiskit_algorithms.optimizers import SLSQP

from vqe_native.ansatz import drop_zero_rotations
from vqe_native.hamiltonian import QubitHamiltonian

# Parameters that converge below this magnitude (radians) are removed and VQE is re-run on the
# smaller circuit. Every removed rotation saves CZ layers on hardware.
PRUNE_ANGLE_TOLERANCE = 1e-3
# Removing them must not raise the converged energy by more than this.
PRUNE_ENERGY_TOLERANCE_HA = 1e-8


@dataclass(frozen=True)
class VQERunResult:
    bound_circuit: QuantumCircuit
    optimal_parameters: np.ndarray  # values of the parameters kept after pruning
    num_pruned_parameters: int
    vqe_total_energy: float
    exact_total_energy: float


def _minimize(hamiltonian: QubitHamiltonian, ansatz: QuantumCircuit, initial_point: np.ndarray):
    """VQE with an exact statevector estimator (no shot noise, no hardware noise).

    SLSQP's default tolerance (ftol=1e-6) stops LiH ~0.5 mHa above the ground state; a tight
    tolerance lets it converge to the exact energy.
    """
    vqe = VQE(StatevectorEstimator(), ansatz, SLSQP(maxiter=5000, ftol=1e-12), initial_point=initial_point)
    return vqe.compute_minimum_eigenvalue(hamiltonian.operator)


def run_vqe(hamiltonian: QubitHamiltonian, ansatz: QuantumCircuit) -> VQERunResult:
    """Run VQE, prune parameters that converge to ~0, re-optimize, and bind the result.

    This is the classical pre-optimization step. Pruning matters because the ansatz is slightly
    over-parameterized: some rotations are forbidden by molecular symmetry and others are
    redundant, and they converge to small but nonzero values (1e-6 .. 1e-4) that would still
    cost CZ gates on hardware. ``NumPyMinimumEigensolver`` on the same qubit operator checks that
    VQE reached the ground state (an independent PySCF cross-check is in ``classical_reference.py``).
    """
    full = _minimize(hamiltonian, ansatz, np.zeros(ansatz.num_parameters))
    values = np.asarray(full.optimal_point)

    small = {p: 0.0 for p, v in zip(ansatz.parameters, values) if abs(v) < PRUNE_ANGLE_TOLERANCE}
    reduced_ansatz = drop_zero_rotations(ansatz.assign_parameters(small))
    kept_values = np.array([v for p, v in zip(ansatz.parameters, values) if p not in small])
    reduced = _minimize(hamiltonian, reduced_ansatz, kept_values) if reduced_ansatz.num_parameters else full

    if reduced.eigenvalue.real - full.eigenvalue.real > PRUNE_ENERGY_TOLERANCE_HA:
        raise ValueError(
            f"Pruning {len(small)} parameters raised the energy by "
            f"{reduced.eigenvalue.real - full.eigenvalue.real:.2e} Ha"
        )

    exact_result = NumPyMinimumEigensolver().compute_minimum_eigenvalue(hamiltonian.operator)
    return VQERunResult(
        bound_circuit=reduced_ansatz.assign_parameters(reduced.optimal_point),
        optimal_parameters=np.asarray(reduced.optimal_point),
        num_pruned_parameters=len(small),
        vqe_total_energy=reduced.eigenvalue.real + hamiltonian.energy_offset,
        exact_total_energy=exact_result.eigenvalue.real + hamiltonian.energy_offset,
    )
