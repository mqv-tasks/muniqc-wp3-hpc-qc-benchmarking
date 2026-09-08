"""Map an electronic-structure problem to a qubit Hamiltonian."""

from __future__ import annotations

from dataclasses import dataclass

from qiskit.quantum_info import SparsePauliOp
from qiskit_nature.second_q.mappers import JordanWignerMapper
from qiskit_nature.second_q.problems import ElectronicStructureProblem


@dataclass(frozen=True)
class QubitHamiltonian:
    """A mapped qubit Hamiltonian plus everything needed to report total energies."""

    operator: SparsePauliOp
    # Sum of all classical energy shifts (nuclear repulsion, and the frozen-core
    # inactive-space energy when a FreezeCoreTransformer was applied). Total
    # molecular energy = <operator> + energy_offset.
    energy_offset: float
    num_spatial_orbitals: int
    num_particles: tuple[int, int]


def build_qubit_hamiltonian(problem: ElectronicStructureProblem) -> QubitHamiltonian:
    """Map the problem's fermionic Hamiltonian to qubits via Jordan-Wigner.

    ``problem.hamiltonian.constants`` holds every classical energy shift that
    is not part of the qubit operator itself: at minimum the nuclear repulsion
    energy, and additionally the frozen-core energy when a
    FreezeCoreTransformer was applied upstream. Both must be summed back in to
    get a total energy comparable to a direct classical (PySCF) calculation.
    """
    mapper = JordanWignerMapper()
    operator = mapper.map(problem.hamiltonian.second_q_op())
    energy_offset = sum(problem.hamiltonian.constants.values())
    return QubitHamiltonian(
        operator=operator,
        energy_offset=energy_offset,
        num_spatial_orbitals=problem.num_spatial_orbitals,
        num_particles=problem.num_particles,
    )
