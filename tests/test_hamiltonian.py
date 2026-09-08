from vqe_native.hamiltonian import build_qubit_hamiltonian
from vqe_native.molecules import H2, LIH, build_problem


def test_h2_maps_to_4_qubits():
    hamiltonian = build_qubit_hamiltonian(build_problem(H2))
    assert hamiltonian.operator.num_qubits == 4
    assert hamiltonian.num_particles == (1, 1)
    assert len(hamiltonian.operator) > 0


def test_lih_frozen_core_maps_to_10_qubits():
    hamiltonian = build_qubit_hamiltonian(build_problem(LIH))
    assert hamiltonian.operator.num_qubits == 10
    assert hamiltonian.num_particles == (1, 1)
    assert len(hamiltonian.operator) > 0


def test_h2_energy_offset_is_nuclear_repulsion_only():
    problem = build_problem(H2)
    hamiltonian = build_qubit_hamiltonian(problem)
    assert hamiltonian.energy_offset == problem.hamiltonian.nuclear_repulsion_energy


def test_lih_energy_offset_includes_frozen_core_shift():
    problem = build_problem(LIH)
    hamiltonian = build_qubit_hamiltonian(problem)
    # Freezing the core changes the classical energy offset: it must be strictly
    # more negative than nuclear repulsion alone, since it also carries the
    # frozen orbitals' contribution to the total energy.
    assert hamiltonian.energy_offset < problem.hamiltonian.nuclear_repulsion_energy
