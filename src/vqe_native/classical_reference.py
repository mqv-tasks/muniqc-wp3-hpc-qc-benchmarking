"""Independent classical ground truth, computed directly with plain PySCF.

This deliberately bypasses qiskit-nature's driver/Hamiltonian machinery: it
builds the PySCF ``Mole``/``RHF`` objects itself and runs PySCF's own FCI (H2)
or CASCI (LiH, over the same frozen-core active space) solver. Agreement with
the qiskit-nature/VQE total energy is the real confidence check, since a bug
in how the qubit Hamiltonian was built would not be caught by comparing VQE
against ``NumPyMinimumEigensolver`` on that same (potentially wrong) operator.
"""

from __future__ import annotations

from pyscf import fci, gto, mcscf, scf

from vqe_native.molecules import MoleculeSpec


def pyscf_fci_total_energy(spec: MoleculeSpec) -> float:
    """Full CI total energy (electrons + nuclear repulsion) for a molecule with no frozen core."""
    if spec.freeze_core:
        raise ValueError("pyscf_fci_total_energy expects a molecule with no frozen core")
    mol = gto.M(atom=spec.atom, basis=spec.basis, verbose=0)
    mean_field = scf.RHF(mol).run()
    total_energy, _ = fci.FCI(mean_field).kernel()
    return float(total_energy)


def pyscf_casci_total_energy(spec: MoleculeSpec, num_active_orbitals: int, num_active_electrons: int) -> float:
    """CASCI total energy over an explicit active space, matching a FreezeCoreTransformer reduction."""
    mol = gto.M(atom=spec.atom, basis=spec.basis, verbose=0)
    mean_field = scf.RHF(mol).run()
    casci = mcscf.CASCI(mean_field, ncas=num_active_orbitals, nelecas=num_active_electrons)
    total_energy = casci.kernel()[0]
    return float(total_energy)
