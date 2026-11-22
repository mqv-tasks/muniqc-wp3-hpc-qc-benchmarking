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


def _minimize(hamiltonian: QubitHamiltonian, ansatz: QuantumCircuit, initial_point: np.ndarray, tight: bool):
    """VQE with an exact statevector estimator (no shot noise, no hardware noise).

    ``tight=False`` uses SLSQP's defaults, exactly as in the first delivery. ``tight=True`` uses
    ftol=1e-12: with the default (1e-6) the pair ansatz stops ~0.5 mHa above the LiH ground state.
    """
    optimizer = SLSQP(maxiter=5000, ftol=1e-12) if tight else SLSQP()
    vqe = VQE(StatevectorEstimator(), ansatz, optimizer, initial_point=initial_point)
    return vqe.compute_minimum_eigenvalue(hamiltonian.operator)


def run_vqe(
    hamiltonian: QubitHamiltonian, ansatz: QuantumCircuit, *, tight_convergence: bool, prune: bool
) -> VQERunResult:
    """Run VQE from all-zero parameters (Hartree-Fock) and bind the optimum into the ansatz.

    This is the classical pre-optimization step. With ``prune=True``, parameters that converge to
    ~0 are removed and VQE is re-run on the smaller circuit: some rotations of the pair ansatz are
    forbidden by molecular symmetry or redundant, and converge to small nonzero values
    (1e-6 .. 1e-4) that would still cost CZ gates on hardware. ``NumPyMinimumEigensolver`` on the
    same qubit operator checks that VQE reached the ground state (an independent PySCF cross-check
    is in ``classical_reference.py``).
    """
    full = _minimize(hamiltonian, ansatz, np.zeros(ansatz.num_parameters), tight_convergence)
    exact_result = NumPyMinimumEigensolver().compute_minimum_eigenvalue(hamiltonian.operator)
    exact_total_energy = exact_result.eigenvalue.real + hamiltonian.energy_offset

    if not prune:
        return VQERunResult(
            bound_circuit=ansatz.assign_parameters(full.optimal_point),
            optimal_parameters=np.asarray(full.optimal_point),
            num_pruned_parameters=0,
            vqe_total_energy=full.eigenvalue.real + hamiltonian.energy_offset,
            exact_total_energy=exact_total_energy,
        )

    values = np.asarray(full.optimal_point)
    small = {p: 0.0 for p, v in zip(ansatz.parameters, values) if abs(v) < PRUNE_ANGLE_TOLERANCE}
    reduced_ansatz = drop_zero_rotations(ansatz.assign_parameters(small))
    kept_values = np.array([v for p, v in zip(ansatz.parameters, values) if p not in small])
    reduced = (
        _minimize(hamiltonian, reduced_ansatz, kept_values, tight_convergence)
        if reduced_ansatz.num_parameters
        else full
    )
    if reduced.eigenvalue.real - full.eigenvalue.real > PRUNE_ENERGY_TOLERANCE_HA:
        raise ValueError(
            f"Pruning {len(small)} parameters raised the energy by "
            f"{reduced.eigenvalue.real - full.eigenvalue.real:.2e} Ha"
        )
    return VQERunResult(
        bound_circuit=reduced_ansatz.assign_parameters(reduced.optimal_point),
        optimal_parameters=np.asarray(reduced.optimal_point),
        num_pruned_parameters=len(small),
        vqe_total_energy=reduced.eigenvalue.real + hamiltonian.energy_offset,
        exact_total_energy=exact_total_energy,
    )
