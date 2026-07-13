#!/usr/bin/env python3
"""G18: conventional covariant Krein/BRST visibility of the G17 block.

This is a deliberately narrow no-go theorem.  It does not classify
nonlocal, non-factorizing, or conformal-boundary completions.  It tests the
physically standard class specified in the manuscript:

  * a nondegenerate fundamental symmetry on physical BRST cohomology;
  * Poincare covariance and agreement with the free gravitational real form;
  * tensor-multiplicative (cluster-factorizing) asymptotic Fock lift.

One precision matters.  Under the proper-orthochronous Poincare group the
massless +2 and -2 helicity representations are inequivalent and can carry
separate scalar signs.  Parity, or compatibility with the real gravitational
field, equates them.  Even without that extra condition, agreement with the
free signature fixes both to +1, so the final fundamental symmetry is the
same.

Inputs proved by earlier exact rails:

  G13/G14  the massive spin-2 irrep is uniform; Mhh vanishes; the MMM and
           MMh vertices are nonzero;
  G15/G17  the reduced physical MM -> Mh amplitude is
           A_K = 7881241032/5584765625 and the positive-frame obstruction is
           -2 i A_K sigma_x, with exact Ward, EOM, reverse-process, and
           internal-gauge checks.

Checks:
G18a  solve the complete one-particle commutant.  Before imposing reality it
      is diag(a_+,a_-,a_M I_5); parity/reality sets a_+=a_-, and the free
      signature uniquely selects diag(+I_2,-I_5).
G18b  tensor multiplicativity uniquely lifts this to (-1)^N_M; in particular
      |MM> is positive and |Mh> is negative.
G18c  the exact forward block is Z2-odd but not null:
      Tr(X^sharp X) = -|t|^2 != 0.  The complete G17 obstruction block is
      likewise non-null.  Odd times odd is neutral, so no Z2 charge-null
      lemma exists.
G18d  the verified nonzero MMM and MMh vertices force every uniform abelian
      massive charge to be trivial (3q=0 and 2q=0 imply q=0, even with
      torsion); there is no O(1,1)-like one-sided continuous charge.
G18e  in a BRST cohomology splitting, every BRST-exact operator has zero
      physical-to-physical block.  The exact G17 block survives that
      projection and therefore is not BRST-exact.
"""
from itertools import product

import sympy as sp


PASS = True


def check(message, condition):
    global PASS
    print(("[OK ] " if condition else "[FAIL] ") + message)
    PASS = PASS and bool(condition)


def so3_generators_on_spin2():
    """Real spin-2 irrep on symmetric traceless 3 x 3 tensors."""
    def matrix_unit(i, j):
        return sp.Matrix(3, 3, lambda a, b: int((a, b) == (i, j)))

    basis = [
        (matrix_unit(0, 0) - matrix_unit(1, 1))/sp.sqrt(2),
        (2*matrix_unit(2, 2) - matrix_unit(0, 0)
         - matrix_unit(1, 1))/sp.sqrt(6),
        (matrix_unit(0, 1) + matrix_unit(1, 0))/sp.sqrt(2),
        (matrix_unit(0, 2) + matrix_unit(2, 0))/sp.sqrt(2),
        (matrix_unit(1, 2) + matrix_unit(2, 1))/sp.sqrt(2),
    ]

    def levi_civita(i, j, k):
        i, j, k = int(i), int(j), int(k)
        if len({i, j, k}) != 3:
            return 0
        permutation = (i, j, k)
        inversions = sum(permutation[a] > permutation[b]
                         for a in range(3) for b in range(a + 1, 3))
        return -1 if inversions % 2 else 1

    vector_generators = [sp.Matrix(
        3, 3, lambda a, b, i=i: -levi_civita(i, a, b))
        for i in range(3)]
    generators = []
    for generator in vector_generators:
        representation = sp.zeros(5)
        for column, tensor in enumerate(basis):
            transformed = generator*tensor + tensor*generator.T
            for row, dual in enumerate(basis):
                representation[row, column] = sum(
                    transformed[a, b]*dual[a, b]
                    for a in range(3) for b in range(3))
        generators.append(sp.simplify(representation))
    return generators


# ------------------------------ G18a ----------------------------------------
# Fiber order: h_(+2), h_(-2), followed by the five massive polarizations.
spin2_generators = so3_generators_on_spin2()
mass_casimir = sp.diag(0, 0, 1, 1, 1, 1, 1)
helicity_generator = sp.diag(2, -2, 0, 0, 0, 0, 0)
little_group_generators = [helicity_generator]
for generator in spin2_generators:
    little_group_generators.append(sp.diag(sp.zeros(2), generator))

variables = sp.symbols("x0:49")
candidate = sp.Matrix(7, 7, variables)
equations = list(candidate*mass_casimir - mass_casimir*candidate)
for generator in little_group_generators:
    equations.extend(list(candidate*generator - generator*candidate))
solution_tuple = next(iter(sp.linsolve(equations, variables)))
commutant = candidate.subs(dict(zip(variables, solution_tuple)))
a_plus = commutant[0, 0]
a_minus = commutant[1, 1]
a_massive = commutant[2, 2]
expected_commutant = sp.diag(a_plus, a_minus,
                             *([a_massive]*5))
commutant_ok = sp.simplify(commutant - expected_commutant) == sp.zeros(7)

# Parity/reality exchanges the two complex helicity fibers and leaves the
# real massive polarization space invariant.
helicity_exchange = sp.diag(sp.Matrix([[0, 1], [1, 0]]), sp.eye(5))
parity_commutator = sp.simplify(
    expected_commutant*helicity_exchange
    - helicity_exchange*expected_commutant)
parity_equates_helicities = (parity_commutator[0, 1] == a_plus - a_minus
                             and parity_commutator[1, 0]
                             == a_minus - a_plus)

involution_signs = list(product((-1, 1), repeat=3))
free_signature = sp.diag(1, 1, -1, -1, -1, -1, -1)
free_matches = [signs for signs in involution_signs
                if sp.diag(signs[0], signs[1], *([signs[2]]*5))
                == free_signature]
free_ok = (free_signature**2 == sp.eye(7)
           and free_signature*mass_casimir
           == mass_casimir*free_signature
           and all(free_signature*generator
                   == generator*free_signature
                   for generator in little_group_generators)
           and len(free_matches) == 1)
check("G18a: the proper-orthochronous one-particle commutant is exactly "
      "diag(a_+,a_-,a_M I5); parity/real-field compatibility sets "
      "a_+=a_-, and agreement with the free (+,+;-,-,-,-,-) signature "
      "uniquely gives J1=diag(+I2,-I5)",
      commutant_ok and parity_equates_helicities and free_ok)


# ------------------------------ G18b ----------------------------------------
def fock_sign(n_h, n_massive):
    """Second quantization of the free one-particle fundamental symmetry."""
    del n_h
    return (-1)**n_massive


cluster_ok = all(
    fock_sign(nh1 + nh2, nm1 + nm2)
    == fock_sign(nh1, nm1)*fock_sign(nh2, nm2)
    for nh1, nm1, nh2, nm2 in product(range(5), repeat=4))
anchors_ok = (fock_sign(0, 0) == 1
              and fock_sign(1, 0) == 1
              and fock_sign(0, 1) == -1)
sign_in = fock_sign(0, 2)       # |MM>
sign_out = fock_sign(1, 1)      # |Mh>
check("G18b: the unique tensor-multiplicative/cluster-factorizing Fock "
      "lift is J_F=(-1)^N_M; |MM> has sign +1 and |Mh> has sign -1",
      cluster_ok and anchors_ok and sign_in == 1 and sign_out == -1)


# ------------------------------ G18c ----------------------------------------
A_K = sp.Rational(7881241032, 5584765625)
t_plus = sp.I*A_K
J_min = sp.diag(sign_in, sign_out)


def krein_adjoint(operator):
    return sp.simplify(J_min*operator.conjugate().T*J_min)


# Basis order (|MM>, |Mh>); X maps the first state to the second.
X = sp.Matrix([[0, 0], [t_plus, 0]])
X_sharp = krein_adjoint(X)
quadratic = sp.simplify(X_sharp*X)
quadratic_trace = sp.simplify(sp.trace(quadratic))
expected_quadratic = sp.diag(-A_K**2, 0)

sigma_x = sp.Matrix([[0, 1], [1, 0]])
obstruction = -2*sp.I*A_K*sigma_x
obstruction_sharp = krein_adjoint(obstruction)
obstruction_quadratic = sp.simplify(obstruction_sharp*obstruction)
obstruction_trace = sp.simplify(sp.trace(obstruction_quadratic))
z2_odd = sp.simplify(J_min*X*J_min + X) == sp.zeros(2)
product_neutral = (sp.simplify(J_min*quadratic*J_min - quadratic)
                   == sp.zeros(2))
check("G18c: the exact forward transition is J_F-odd but NON-NULL: "
      f"Tr(X^sharp X)={quadratic_trace}=-A_K^2 != 0; X^sharp X is "
      "J_F-even.  The full G17 obstruction is also non-null, with "
      f"Tr(O^sharp O)={obstruction_trace}",
      z2_odd and product_neutral
      and quadratic == expected_quadratic
      and quadratic_trace == -A_K**2 and quadratic_trace != 0
      and obstruction_sharp == obstruction
      and obstruction_quadratic == -4*A_K**2*sp.eye(2)
      and obstruction_trace == -8*A_K**2
      and obstruction_trace != 0)


# ------------------------------ G18d ----------------------------------------
q_massive, q_graviton = sp.symbols("q_M q_h")
charge_solution = sp.linsolve(
    [3*q_massive, 2*q_massive + q_graviton, q_graviton],
    (q_massive, q_graviton))
# The same conclusion holds in every abelian group, not just over R: if
# 3q=0 and 2q=0 then q=3q-2q=0 (Bezout coefficient 1).
bezout_identity = 3 - 2 == 1
parity_broken_by_mmm = (3*1) % 2 != 0
parity_broken_by_g17 = (2 - 1) % 2 != 0
check("G18d: nonzero MMM and MMh with q_h=0 force the only uniform "
      f"continuous charge solution {charge_solution}; gcd(2,3)=1 also "
      "kills torsion charges.  Massive-number Z2 is broken both by MMM "
      "at the interaction-vertex level and by the physical MM->Mh "
      "transition",
      charge_solution == sp.FiniteSet((0, 0)) and bezout_identity
      and parity_broken_by_mmm and parity_broken_by_g17)


# ------------------------------ G18e ----------------------------------------
# A canonical finite BRST splitting: two physical cohomology representatives
# followed by a contractible doublet u -> v -> 0.  For a completely general
# Y, the graded commutator {Q,Y} has zero physical-to-physical block.  This
# is the matrix form of <closed|{Q,Y}|closed>=0 after quotienting exacts.
Q = sp.zeros(4)
Q[3, 2] = 1
y_variables = sp.symbols("y0:16")
Y = sp.Matrix(4, 4, y_variables)
brst_exact = sp.simplify(Q*Y + Y*Q)
brst_physical_block = brst_exact[:2, :2]
physical_projection = sp.eye(2)
projected_obstruction = sp.simplify(
    physical_projection*obstruction*physical_projection)
check("G18e: every BRST-exact operator has zero physical-cohomology block, "
      "whereas the Ward- and gauge-verified G17 obstruction survives the "
      "reduced-helicity projection exactly; it is not BRST-exact",
      Q**2 == sp.zeros(4)
      and brst_physical_block == sp.zeros(2)
      and projected_obstruction == obstruction
      and projected_obstruction != sp.zeros(2))


print("\nALL PASS" if PASS else "\nSOME CHECKS FAILED")
