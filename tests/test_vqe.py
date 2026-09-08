"""VQE must agree with two independent classical references:

1. NumPyMinimumEigensolver, exact diagonalization of the *same* qubit
   Hamiltonian (checks the optimizer actually found the ground state).
2. Direct PySCF FCI/CASCI, computed from the mol/mf objects without going
   through qiskit-nature at all (checks the Hamiltonian itself is correct).
"""

CHEMICAL_ACCURACY_HA = 1.6e-3  # ~1 kcal/mol, the standard quantum chemistry target
EXACT_DIAGONALIZATION_TOLERANCE_HA = 1e-6


def test_h2_vqe_matches_exact_diagonalization(h2_pipeline):
    result = h2_pipeline.vqe_result
    assert abs(result.vqe_total_energy - result.exact_total_energy) < EXACT_DIAGONALIZATION_TOLERANCE_HA


def test_h2_vqe_matches_pyscf_fci(h2_pipeline, h2_classical_energy):
    assert abs(h2_pipeline.vqe_result.vqe_total_energy - h2_classical_energy) < CHEMICAL_ACCURACY_HA


def test_h2_exact_diagonalization_matches_pyscf_fci(h2_pipeline, h2_classical_energy):
    assert abs(h2_pipeline.vqe_result.exact_total_energy - h2_classical_energy) < EXACT_DIAGONALIZATION_TOLERANCE_HA


def test_lih_vqe_matches_exact_diagonalization(lih_pipeline):
    result = lih_pipeline.vqe_result
    assert abs(result.vqe_total_energy - result.exact_total_energy) < EXACT_DIAGONALIZATION_TOLERANCE_HA


def test_lih_vqe_matches_pyscf_casci(lih_pipeline, lih_classical_energy):
    assert abs(lih_pipeline.vqe_result.vqe_total_energy - lih_classical_energy) < EXACT_DIAGONALIZATION_TOLERANCE_HA


def test_lih_exact_diagonalization_matches_pyscf_casci(lih_pipeline, lih_classical_energy):
    assert abs(lih_pipeline.vqe_result.exact_total_energy - lih_classical_energy) < EXACT_DIAGONALIZATION_TOLERANCE_HA
