"""Molecular problem definitions for the VQE benchmark (H2 and LiH, STO-3G)."""

from __future__ import annotations

from dataclasses import dataclass

from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.problems import ElectronicStructureProblem
from qiskit_nature.second_q.transformers import FreezeCoreTransformer

# Equilibrium bond lengths (Angstrom), standard STO-3G/HF geometries.
H2_BOND_LENGTH_ANGSTROM = 0.735
LIH_BOND_LENGTH_ANGSTROM = 1.5949

BASIS = "sto3g"


@dataclass(frozen=True)
class MoleculeSpec:
    """Everything needed to reproduce a molecule's classical geometry/basis."""

    name: str
    atom: str
    basis: str
    freeze_core: bool


H2 = MoleculeSpec(
    name="h2",
    atom=f"H 0 0 0; H 0 0 {H2_BOND_LENGTH_ANGSTROM}",
    basis=BASIS,
    freeze_core=False,
)

LIH = MoleculeSpec(
    name="lih",
    atom=f"Li 0 0 0; H 0 0 {LIH_BOND_LENGTH_ANGSTROM}",
    basis=BASIS,
    freeze_core=True,
)


def build_problem(spec: MoleculeSpec) -> ElectronicStructureProblem:
    """Run the PySCF driver and apply the frozen-core reduction if requested.

    H2 has no core orbital worth freezing (2 electrons, 2 orbitals total), so
    ``freeze_core=False``. LiH freezes the Li 1s core, leaving 2 active
    electrons in 5 active orbitals (10 qubits with Jordan-Wigner).
    """
    driver = PySCFDriver(atom=spec.atom, basis=spec.basis)
    problem = driver.run()
    if spec.freeze_core:
        problem = FreezeCoreTransformer().transform(problem)
    return problem
