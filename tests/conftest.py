"""Shared fixtures: every test that takes ``result`` / ``groups`` runs once per (molecule, ansatz).

Pipelines are cached, so each (molecule, ansatz) VQE runs only once per test session.
The 'uccsd-pennylane' cases are skipped if PennyLane is not installed (uv sync --extra pennylane).

Two levels:

    uv run pytest            # fast (about 30 s): everything except the tests marked slow
    uv run pytest --full     # everything (about 25 min)

Tests marked ``slow`` are those for LiH with the two UCCSD ansätze (long VQE, ~500-CZ circuits).
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


def pytest_addoption(parser):
    parser.addoption("--full", action="store_true", help="also run the slow tests (about 25 min in total)")


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: long test, only run with --full")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--full"):
        return
    skip_slow = pytest.mark.skip(reason="slow test: run with --full")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


def is_slow(molecule: str, ansatz: str) -> bool:
    """LiH with a UCCSD ansatz: long VQE and ~500-CZ circuits."""
    return molecule == "lih" and ansatz != "pair"


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
    marks = [pytest.mark.slow] if is_slow(molecule, ansatz) else []
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
