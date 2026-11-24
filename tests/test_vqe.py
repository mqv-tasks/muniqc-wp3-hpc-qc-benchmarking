"""VQE must agree with two independent classical references, for every ansatz:

1. NumPyMinimumEigensolver, exact diagonalization of the *same* qubit Hamiltonian (checks the
   optimizer actually found the ground state).
2. Direct PySCF FCI/CASCI, computed from the mol/mf objects without going through qiskit-nature
   at all (checks the Hamiltonian itself is correct).
"""

import pytest

from conftest import MOLECULES, cached_pipeline, classical_energy

TOLERANCE_HA = 1e-6


def test_vqe_matches_exact_diagonalization(result):
    assert abs(result.vqe_result.vqe_total_energy - result.vqe_result.exact_total_energy) < TOLERANCE_HA


def test_vqe_matches_pyscf(case, result):
    molecule, _ = case
    assert abs(result.vqe_result.vqe_total_energy - classical_energy(molecule)) < TOLERANCE_HA


@pytest.mark.parametrize("molecule", MOLECULES)
def test_exact_diagonalization_matches_pyscf(molecule):
    exact = cached_pipeline(molecule, "pair").vqe_result.exact_total_energy
    assert abs(exact - classical_energy(molecule)) < TOLERANCE_HA
