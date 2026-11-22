"""Shared fixtures: every test that takes ``result`` / ``groups`` runs once per (molecule, ansatz).

Pipelines are cached, so each (molecule, ansatz) VQE runs only once per test session.
The 'uccsd-pennylane' cases are skipped if PennyLane is not installed (uv sync --extra pennylane).
"""

import functools
import importlib.util
import itertools

import pytest

from vqe_native.ansatz import ANSATZE
from vqe_native.classical_reference import pyscf_casci_total_energy, pyscf_fci_total_energy
from vqe_native.measurement import build_measurement_groups
from vqe_native.molecules import H2, LIH
from vqe_native.pipeline import run_pipeline

MOLECULES = {"h2": H2, "lih": LIH}
HAS_PENNYLANE = importlib.util.find_spec("pennylane") is not None

# LiH freeze-core active space: Li 1s frozen -> 2 active electrons / 5 active orbitals.
LIH_ACTIVE_ORBITALS = 5
LIH_ACTIVE_ELECTRONS = 2


@functools.cache
def cached_pipeline(molecule: str, ansatz: str):
    return run_pipeline(MOLECULES[molecule], ansatz)


@functools.cache
def cached_groups(molecule: str, ansatz: str):
    result = cached_pipeline(molecule, ansatz)
    return build_measurement_groups(result.vqe_result.bound_circuit, result.hamiltonian.operator)


@functools.cache
def classical_energy(molecule: str) -> float:
    if molecule == "h2":
        return pyscf_fci_total_energy(H2)
    return pyscf_casci_total_energy(LIH, LIH_ACTIVE_ORBITALS, LIH_ACTIVE_ELECTRONS)


def _case_param(molecule: str, ansatz: str):
    marks = []
    if ansatz == "uccsd-pennylane" and not HAS_PENNYLANE:
        marks.append(pytest.mark.skip(reason="PennyLane not installed: uv sync --extra pennylane"))
    return pytest.param((molecule, ansatz), id=f"{molecule}-{ansatz}", marks=marks)


CASES = [_case_param(m, a) for m, a in itertools.product(MOLECULES, ANSATZE)]


@pytest.fixture(params=CASES)
def case(request):
    """(molecule, ansatz) pair, e.g. ("lih", "pair")."""
    return request.param


@pytest.fixture
def result(case):
    return cached_pipeline(*case)


@pytest.fixture
def groups(case):
    return cached_groups(*case)
