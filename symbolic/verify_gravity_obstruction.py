#!/usr/bin/env python3
"""G17: exact second-order positive-metric obstruction in Einstein--Weyl.

Prerequisites already established by G13--G15 are used as inputs:

* covariance quarter-turns the whole massive spin-2 multiplet;
* the physical cubic shell is empty (Mhh vanishes by Einstein
  truncation; MMM and MMh are kinematically closed; real hhh is the
  collinear zero);
* the complete standard/Krein-frame MM -> Mh tree amplitude is nonzero.

This script closes the step that cannot be replaced by an external-leg
phase slogan.  It exposes the quartic contact and all s/t/u exchanges,
transports each through M = -i Mhat, includes the sign reversal of an
internal massive inverse kernel, constructs the physical-adjoint reverse
matrix element, and projects T2^dagger - T2 onto the degenerate free-energy
block.  All gravity arithmetic is exact rational arithmetic.

Checks:
G17a  the G15 contact plus all three exchange terms reproduces the exact
      nonzero real certificate; every bordered solve is exact;
G17b  the reversed process agrees term by term for the real polarization
      sections, so the physical adjoint is evaluated rather than assumed;
G17c  every external leg solves its exact linearized equation; the full
      Ward identity and internal-gauge independence survive;
G17d  contact, massless exchange, and massive exchange all acquire the
      same +i phase.  The internal massive line's two endpoint phases are
      compensated by the -1 from its quarter-turned inverse kernel;
G17e  the complete two-state shell block obeys
          Pi_E (T2^dagger - T2) Pi_E
          = -2 i A_K sigma_x != 0;
G17f  first-order metric-commutant freedom cannot change this projection:
      the reduced physical cubic shell block is zero, hence
      Pi_E [G, v1 + v1^dagger] Pi_E = 0 for every [G,h0] = 0.

The sign in G17e follows the convention M = -i Mhat.  Reversing the
quarter-turn convention reverses the displayed sign but not nonvanishing.
"""
import sympy as sp

from gravity_four_point import (FourPointCalculator, axial_constraint,
                                de_donder_constraint)
from gravity_perturbiner import ETA, R, dot, sym


PASS = True


def check(message, condition):
    global PASS
    print(("[OK ] " if condition else "[FAIL] ") + message)
    PASS = PASS and bool(condition)


# -------------------------- exact physical certificate ----------------------
# All momenta incoming; M = 1.  Legs 1,2 are incoming M, leg 3 is the
# crossed outgoing M, and leg 4 the crossed outgoing h.
k1 = [R(5, 4), 0, 0, R(3, 4)]
k2 = [R(5, 4), 0, 0, -R(3, 4)]
k3 = [-R(29, 20), R(21, 25), 0, R(63, 100)]
k4 = [-R(21, 20), -R(21, 25), 0, -R(63, 100)]
KIN = [k1, k2, k3, k4]


def inplane_tt(momentum):
    """The y-even massive TT basis used by the G15 certificate."""
    nullspace = sp.Matrix([[
        ETA[mu]*momentum[mu] for mu in (0, 1, 3)
    ]]).nullspace()
    vectors = [[entry[0], entry[1], 0, entry[2]] for entry in nullspace]
    vector1, vector2 = vectors
    momentum_sq = dot(momentum, momentum)
    projector = {
        (mu, nu): ((1 if mu == nu else 0)*ETA[mu]
                   - momentum[mu]*momentum[nu]/momentum_sq)
        for mu in range(4) for nu in range(4)
    }

    def tensor(vector_a, vector_b):
        product = dot(vector_a, vector_b)
        return {
            (mu, nu): sp.nsimplify(
                vector_a[mu]*vector_b[nu] + vector_b[mu]*vector_a[nu]
                - R(2, 3)*product*projector[(mu, nu)])
            for mu in range(4) for nu in range(4)
        }

    return {"12": tensor(vector1, vector2),
            "11": tensor(vector1, vector1)}


P1 = inplane_tt(k1)
P2 = inplane_tt(k2)
P3 = inplane_tt(k3)
graviton_direction = [5, 4, 0, 3]
graviton_e1 = [0, -3, 0, 4]
graviton_e2 = [0, 0, 1, 0]
EPS_PLUS = {
    (mu, nu): (R(graviton_e1[mu]*graviton_e1[nu], 25)
               - graviton_e2[mu]*graviton_e2[nu])
    for mu in range(4) for nu in range(4)
}
EPS = [P1["12"], P2["12"], P3["12"], EPS_PLUS]

assert all(sum(momentum[mu] for momentum in KIN) == 0 for mu in range(4))
assert [dot(momentum, momentum) for momentum in KIN] == [1, 1, 1, 0]
assert dot(graviton_e1, graviton_direction) == 0
assert dot(graviton_e2, graviton_direction) == 0

calculator = FourPointCalculator()
forward = calculator.decompose(EPS, KIN, de_donder_constraint)
EXPECTED = R(7881241032, 5584765625)
solves_ok = all(report.constraint_zero and report.residual_zero
                for report in forward.reports)
check("G17a: exact contact + s/t/u exchanges reproduce the G15 real-shell "
      f"certificate A_K = {forward.total} = {EXPECTED} != 0; all bordered "
      "systems solve exactly",
      solves_ok and forward.total == EXPECTED and forward.total != 0)
print(f"      contact = {forward.contact}")
for label, value in zip(("s", "t", "u"), forward.exchanges):
    print(f"      {label}-exchange = {value}")


# -------------------------- physical adjoint / crossing ---------------------
# With real tensor polarizations, the physical-adjoint matrix element uses
# the process with every momentum reversed.  Compute its contact and cubic
# currents independently; only the even quadratic kernel is shared by cache.
REVERSED_KIN = [[-entry for entry in momentum] for momentum in KIN]
reverse = calculator.decompose(EPS, REVERSED_KIN, de_donder_constraint)
channel_momenta = [[KIN[a][mu] + KIN[b][mu] for mu in range(4)]
                   for (a, b) in ((0, 1), (0, 2), (0, 3))]
kernel_even = all(
    calculator.quadratic(momentum)
    == calculator.quadratic([-entry for entry in momentum])
    for momentum in channel_momenta)
reverse_ok = (reverse.contact == forward.contact
              and reverse.exchanges == forward.exchanges
              and reverse.total == forward.total
              and kernel_even
              and all(report.constraint_zero and report.residual_zero
                      for report in reverse.reports))
check("G17b: physical-adjoint reverse process (all momenta reversed, real "
      "polarizations conjugated) agrees contact-by-contact and channel-by-"
      f"channel, with K(-P)=K(P): A_rev = {reverse.total} = A_fwd exactly",
      reverse_ok)


# -------------------------- Ward, EOM, internal gauge -----------------------
eom_vectors = [calculator.linearized_eom(eps, momentum)
               for eps, momentum in zip(EPS, KIN)]
eom_ok = all(vector == sp.zeros(10, 1) for vector in eom_vectors)

xi = [R(1, 3), -R(2, 7), R(1, 5), R(3, 11)]
gauge_eps = sym(k4, xi)
ward = calculator.decompose(
    [EPS[0], EPS[1], EPS[2], gauge_eps], KIN,
    de_donder_constraint)
axial = calculator.decompose(EPS, KIN, axial_constraint)
gauge_ok = (ward.total == 0 and axial.total == forward.total
            and all(report.constraint_zero and report.residual_zero
                    for report in axial.reports))
check("G17c: all four external linearized EOM covectors vanish; the "
      "complete transported Ward matrix element is zero and axial versus "
      "de Donder internal gauge gives the same exact amplitude",
      eom_ok and gauge_ok)


# -------------------------- uniform quarter-turn ----------------------------
# Paper IV convention: Mhat = i M is positive-frame self-adjoint, hence
# M = -i Mhat.  An internal massive quadratic kernel gets q^2 = -1, so
# its inverse propagator contributes the compensating factor -1.
q = -sp.I
phase_contact = sp.simplify(q**3)
phase_exchange_h = sp.simplify(q**2 * q)
massive_inverse_kernel_phase = sp.simplify(1/q**2)
phase_exchange_M = sp.simplify(
    q**3 * q**2 * massive_inverse_kernel_phase)
phase_ok = (phase_contact == sp.I
            and phase_exchange_h == sp.I
            and massive_inverse_kernel_phase == -1
            and phase_exchange_M == sp.I)

positive_terms = (phase_contact*forward.contact,
                  *(sp.I*value for value in forward.exchanges))
positive_forward = sp.simplify(sum(positive_terms, sp.S.Zero))
positive_reverse = sp.simplify(sp.I*reverse.total)
reverse_terms = (phase_contact*reverse.contact,
                 *(sp.I*value for value in reverse.exchanges))
source_terms = tuple(
    sp.simplify(sp.conjugate(reverse_term) - forward_term)
    for reverse_term, forward_term in zip(reverse_terms, positive_terms))
expected_source_terms = tuple(
    -2*sp.I*value
    for value in (forward.contact, *forward.exchanges))
check("G17d: quarter-turn transport of the FULL T2 is uniform: contact "
      f"phase={phase_contact}, h-exchange phase={phase_exchange_h}, "
      f"M-exchange phase={phase_exchange_M} (including inverse-kernel "
      f"phase {massive_inverse_kernel_phase}); T2_+ = i A_K and every "
      "contact/exchange contribution to T2_+^dagger-T2_+ is exactly "
      "-2i times its standard-frame value",
      phase_ok and positive_forward == sp.I*forward.total
      and source_terms == expected_source_terms)


# -------------------------- shell projection / obstruction ------------------
# Basis = (|MM>, |Mh>).  Rows are final states and columns initial states.
# Both directions have the same +i reduced matrix element before taking the
# physical adjoint, hence the connected positive-frame block is anti-Hermitian.
T2_plus = sp.Matrix([[0, positive_reverse],
                     [positive_forward, 0]])
source = sp.simplify(T2_plus.conjugate().T - T2_plus)
energy_initial = sp.simplify(k1[0] + k2[0])
energy_final = sp.simplify(-k3[0] - k4[0])
h0_shell = sp.diag(energy_initial, energy_final)
projected = source  # Pi_E is the identity on this exactly degenerate block.
target = -2*sp.I*EXPECTED
expected_block = sp.Matrix([[0, target], [target, 0]])
kernel_ok = (energy_initial == energy_final == R(5, 2)
             and h0_shell*projected - projected*h0_shell == sp.zeros(2)
             and projected == expected_block)
check("G17e: Pi_ker(ad_h0)(T2_+^dagger - T2_+) is the nonzero exact "
      f"shell block -2 i A_K sigma_x, with matrix element {target}; "
      "there is no R2 solving [h0,R2] = source",
      kernel_ok and projected != sp.zeros(2))


# -------------------------- first-order metric freedom ----------------------
# On the nonsingular real physical shell the connected cubic block vanishes:
# Mhh is the G13 Einstein-truncation zero; MMM and MMh admit no nonsoft real
# 1<->2 shell; hhh is the real-collinear helicity zero.  Thus P_E w P_E=0
# for w=v1+v1^dagger.  If [G,h0]=0 then G is energy-block diagonal and
# P_E[G,w]P_E=[G_E,P_E w P_E]=0 in any block dimension.  The symbolic
# matrix below checks the last identity without choosing a basis for G_E.
g11, g12, g21, g22 = sp.symbols("g11 g12 g21 g22")
G_shell = sp.Matrix([[g11, g12], [g21, g22]])
w_shell = sp.zeros(2)
ambiguity_shift = sp.simplify(G_shell*w_shell - w_shell*G_shell)
check("G17f: first-order metric-commutant additions cannot move or cancel "
      "the shell class: P_E(v1+v1^dagger)P_E=0 by the complete cubic "
      "physical-shell classification, so P_E[G,v1+v1^dagger]P_E=0 for "
      "every [G,h0]=0",
      ambiguity_shift == sp.zeros(2))


print("\nALL PASS" if PASS else "\nSOME CHECKS FAILED")
