import pytest

from vqe_native.classical_reference import pyscf_casci_total_energy, pyscf_fci_total_energy
from vqe_native.measurement import build_measurement_groups
from vqe_native.molecules import H2, LIH
from vqe_native.pipeline import run_pipeline

# LiH freeze-core active space: Li 1s frozen -> 2 active electrons / 5 active orbitals.
LIH_ACTIVE_ORBITALS = 5
LIH_ACTIVE_ELECTRONS = 2


@pytest.fixture(scope="session")
def h2_pipeline():
    return run_pipeline(H2)


@pytest.fixture(scope="session")
def lih_pipeline():
    return run_pipeline(LIH)


@pytest.fixture(scope="session")
def h2_measurement_groups(h2_pipeline):
    return build_measurement_groups(h2_pipeline.vqe_result.bound_circuit, h2_pipeline.hamiltonian.operator)


@pytest.fixture(scope="session")
def lih_measurement_groups(lih_pipeline):
    return build_measurement_groups(lih_pipeline.vqe_result.bound_circuit, lih_pipeline.hamiltonian.operator)


@pytest.fixture(scope="session")
def h2_classical_energy():
    return pyscf_fci_total_energy(H2)


@pytest.fixture(scope="session")
def lih_classical_energy():
    return pyscf_casci_total_energy(LIH, LIH_ACTIVE_ORBITALS, LIH_ACTIVE_ELECTRONS)
