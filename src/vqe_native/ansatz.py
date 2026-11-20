"""Compact, hardware-friendly ansatz for two electrons in a singlet (one alpha + one beta).

Both target problems reduce to exactly this case: H2 (STO-3G) and LiH with the Li 1s core frozen
(2 active electrons). Any such ground state can be written as

    |psi> = sum_ij C_ij |alpha_i> |beta_j>,     C real symmetric (singlet, real orbitals),

and every real symmetric C factorizes as C = U diag(s) U^T with U orthogonal. The circuit
builds exactly that factorization, so it can represent the exact (FCI) ground state:

1. **Split**: spread the alpha electron over the alpha qubits with real amplitudes s_k, using a
   tree of "splits". The first split starts from |0...0> and costs a single CZ; the others are
   real Givens rotations between a qubit that holds amplitude and a fresh |0> qubit.
2. **Copy**: CNOT(k, n+k) for every orbital k. All of them act on disjoint qubit pairs, so they
   form a single parallel CZ layer. Result: sum_k s_k |alpha_k>|beta_k>.
3. **Orbital rotation**: the same rotation U on the alpha and on the beta register, as real Givens
   rotations over all orbital pairs. Pairs are grouped into rounds of disjoint pairs, and the
   alpha and beta copies of each rotation act on disjoint qubits, so they can run in parallel.

With all parameters 0 the circuit prepares the Hartree-Fock determinant, so VQE starts from HF.

Qubit layout matches qiskit-nature's Jordan-Wigner block ordering: qubits 0..n-1 are the alpha
spin-orbitals, n..2n-1 the beta ones. Within a register that holds exactly one electron, the JW
parity string between the two modes of a Givens rotation only crosses empty modes, so these
two-qubit rotations equal the fermionic ones.

Compared with UCCSD compiled gate by gate, this needs far fewer CZ layers (H2: 2 instead of 42,
LiH: ~12 instead of ~500), because UCCSD's excitation operators are each compiled into long
CNOT ladders that must be correct for every input state, not just for |0...0>.
"""

from __future__ import annotations

from qiskit.circuit import ParameterVector, QuantumCircuit
from qiskit.circuit.library import XXPlusYYGate

from vqe_native.hamiltonian import QubitHamiltonian

# XXPlusYYGate(2*theta, beta=pi/2) is the real Givens rotation
#   |1_i 0_j> -> cos(theta) |1_i 0_j> + sin(theta) |0_i 1_j>
# (other beta values would introduce complex phases, which a real singlet C does not need).
_GIVENS_BETA = 1.5707963267948966  # pi / 2


def _givens(circuit: QuantumCircuit, theta, i: int, j: int) -> None:
    circuit.append(XXPlusYYGate(2 * theta, _GIVENS_BETA), [i, j])


def split_rounds(num_orbitals: int) -> list[list[tuple[int, int]]]:
    """Rounds of (source, fresh) splits after the initial 0 -> 1 split, as a doubling tree."""
    holders = [0, 1]
    rounds = []
    next_orbital = 2
    while next_orbital < num_orbitals:
        current_round = []
        for source in list(holders):
            if next_orbital >= num_orbitals:
                break
            current_round.append((source, next_orbital))
            holders.append(next_orbital)
            next_orbital += 1
        rounds.append(current_round)
    return rounds


def rotation_rounds(num_orbitals: int) -> list[list[tuple[int, int]]]:
    """All orbital pairs (i < j), grouped into rounds of disjoint pairs (round-robin schedule).

    Using every pair directly (instead of a nearest-neighbour mesh) relies on the all-to-all
    connectivity of the atom array, and lets orbitals of the same symmetry mix directly instead
    of through symmetry-forbidden intermediate orbitals, which made VQE stall in testing.
    """
    padded = num_orbitals + (num_orbitals % 2)
    order = list(range(padded))
    rounds = []
    for _ in range(padded - 1):
        pairs = [tuple(sorted((order[k], order[padded - 1 - k]))) for k in range(padded // 2)]
        rounds.append([pair for pair in pairs if pair[1] < num_orbitals])
        order = [order[0], order[-1], *order[1:-1]]
    return rounds


def build_pair_ansatz(hamiltonian: QubitHamiltonian) -> QuantumCircuit:
    """Build the split / copy / orbital-rotation ansatz described in the module docstring."""
    if tuple(hamiltonian.num_particles) != (1, 1):
        raise ValueError(
            f"This ansatz is exact only for one alpha + one beta electron, got {hamiltonian.num_particles}"
        )
    n = hamiltonian.num_spatial_orbitals
    splits = split_rounds(n)
    rotations = [pair for rnd in rotation_rounds(n) for pair in rnd]
    params = ParameterVector("theta", (n - 1) + len(rotations))
    circuit = QuantumCircuit(2 * n, name="pair_ansatz")

    # 1. Split. First split from |0...0>: Ry on qubit 1, X on qubit 0, CNOT 1 -> 0 gives
    #    cos|alpha_0> + sin|alpha_1> with a single entangling gate.
    circuit.ry(2 * params[0], 1)
    circuit.x(0)
    circuit.cx(1, 0)
    index = 1
    for rnd in splits:
        for source, fresh in rnd:
            _givens(circuit, params[index], source, fresh)
            index += 1

    # 2. Copy alpha occupation to beta: one parallel layer of CNOTs on disjoint pairs.
    for orbital in range(n):
        circuit.cx(orbital, n + orbital)

    # 3. Same orbital rotation on alpha and beta.
    for i, j in rotations:
        _givens(circuit, params[index], i, j)
        _givens(circuit, params[index], n + i, n + j)
        index += 1

    return circuit


def drop_zero_rotations(circuit: QuantumCircuit) -> QuantumCircuit:
    """Remove ``ry`` / Givens gates whose angle is bound to exactly 0 (they are identities).

    Gates that still depend on a free parameter are kept.
    """
    pruned = circuit.copy_empty_like()
    for instruction in circuit.data:
        operation = instruction.operation
        if operation.name in ("xx_plus_yy", "ry"):
            try:
                angle = float(operation.params[0])
            except TypeError:  # still parameterized
                angle = None
            if angle == 0.0:
                continue
        pruned.append(instruction)
    return pruned
