"""UCCSD ansatz construction with a Hartree-Fock initial state."""

from __future__ import annotations

from qiskit.circuit import QuantumCircuit
from qiskit_nature.second_q.circuit.library import UCCSD, HartreeFock
from qiskit_nature.second_q.mappers import JordanWignerMapper

from vqe_native.hamiltonian import QubitHamiltonian


def build_uccsd_ansatz(hamiltonian: QubitHamiltonian) -> QuantumCircuit:
    """Build UCCSD (singles + doubles) on top of the Hartree-Fock reference state.

    Uses the same Jordan-Wigner mapper as the Hamiltonian, so the excitation
    operators act on the same qubit encoding as ``hamiltonian.operator``.
    """
    mapper = JordanWignerMapper()
    hartree_fock = HartreeFock(
        hamiltonian.num_spatial_orbitals,
        hamiltonian.num_particles,
        mapper,
    )
    return UCCSD(
        hamiltonian.num_spatial_orbitals,
        hamiltonian.num_particles,
        mapper,
        initial_state=hartree_fock,
    )
