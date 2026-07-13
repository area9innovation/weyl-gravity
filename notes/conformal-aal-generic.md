# Generic-spin conformal AAL reduction

This note records the analytic and machine-verification rail behind the
same-chirality highest-weight conformal-cylinder vertex

```text
A_{J1} A_{J2} -> L_{J1+J2}.
```

It separates three statements that were previously easy to conflate:

1. the closed Hamada--Horata highest-weight harmonic formula;
2. the generic-spin metric Weyl curvature reduction in those harmonics;
3. the still-open BRST, auxiliary-field, and canonical-Hamiltonian descent.

The closed harmonic identity is exact.  The generic-spin curvature formula
below is the sharply isolated remaining lemma: it is verified at the four
existing curvature points, but the attempted fully symbolic two-spin
curvature expansion did not finish within the imposed resource bound.  It is
therefore not promoted to a theorem here.  The BRST/global-constraint descent
is a second, logically separate obligation.

## Closed highest-weight harmonics

Use Euler coordinates `(alpha,beta,gamma)` on the unit three-sphere with

```text
ds^2_{S3}=1/4(d alpha^2+d beta^2+d gamma^2
                    +2 cos(beta)d alpha d gamma)
```

and define the complex null covector

```text
q=d beta+i sin(beta)d gamma.
```

Starting from the Wigner-function/Clebsch--Gordan constructions in
Hamada--Horata, Eqs. (A.26) and (A.37), the positive-chirality highest
weights reduce to

```text
A_J =-sqrt(2J)/(4 pi) cos(beta/2)^(2J-1)
      exp[-i((J+1/2)alpha+(J-1/2)gamma)] q,

L_S = sqrt(2(2S-1))/(16 pi) cos(beta/2)^(2S-2)
      exp[-i((S+1)alpha+(S-1)gamma)] q tensor q.
```

The elementary identities

```text
q_i gamma^(ij) q_j=0,
q_i^* gamma^(ij) q_j=8
```

give the trace and normalization checks immediately.  The relevant right
Clebsch--Gordan recurrences are

```text
J tensor 1/2 -> J-1/2:
  (sqrt(2J/(2J+1)), -1/sqrt(2J+1)),

J tensor 1 -> J-1:
  (sqrt((2J-1)/(2J+1)),
   -sqrt((2J-1)/(J(2J+1))),
   1/sqrt(J(2J+1))).
```

Together with the unique maximal left coupling, these recurrences prove the
collapse to `q` and `q tensor q`; they do not fit a curvature coefficient.
`symbolic/verify_conformal_aal_highest_harmonics.py` reconstructs the
original finite sums and checks the phase conventions, recurrences, null
identities, and normalization at several integer and half-integer spins.

For completeness, the recurrences do not require a table of Clebsch--Gordan
coefficients.  In the highest-weight subspace of
`J tensor 1/2 -> J-1/2`, orthogonality to the lowered maximal-spin state fixes
the two coefficients, and normalization gives the first displayed pair.  In
the three-dimensional highest-weight subspace of
`J tensor 1 -> J-1`, orthogonality to the `J+1` and `J` coupled states fixes
the three ratios; normalization gives the second displayed triple.  Inserting
those ratios into the ambient `tau_(1)` and `tau_(2)` sums leaves respectively
one copy and two symmetric copies of the same tangent covector `q`.  The
highest Wigner row supplies the indicated power of `cos(beta/2)` and its
Euler-angle phase.  This is the generic harmonic derivation; the finite-spin
constructor runs only audit signs and phase conventions.

## Generic metric Weyl density: precise remaining lemma

Set

```text
n1=2J1, n2=2J2, N=n1+n2=2S,
z=1+t^2, t=tan(beta/2),
```

and retain abstract real oscillator coefficients `a1,a2,ell`.  In the
closed highest-weight representatives the only nonzero perturbations are

```text
h[A_r]_{0i}=-a_r z^(-(n_r-1)/2)q_i,
h[L]^*_{ij}=ell z^(-(N-2)/2)q_i^*q_j^*.
```

The finite-spin multilinear expansions of

```text
sqrt(-g)(R_{mu nu}R^{mu nu}-R^2/3)
```

at the coefficient containing all three waves give the pre-`d beta`
coordinate density pattern

```text
D_{n1,n2}(t)
 =32(n1+1)(n2+1)(N-2)a1 a2 ell
   t[(N-2)t^2-1]/(1+t^2)^(N-1).
```

At each tested spin this calculation uses the curvature action directly,
without applying a field equation or discarding a boundary term before
extracting the coefficient.  Modulo the four-dimensional Euler density and
an overall action convention, the invariant is the Weyl-squared action.
What remains to prove is that the displayed expression follows for symbolic
independent integers `n1,n2>=2` from the closed `q` harmonics and their first
radial recurrences.  Four exact points and the normalization fit do not by
themselves prove this statement.

The measured radial differential includes

```text
d beta=2dt/(1+t^2).
```

With `u=t^2/(1+t^2)`, it becomes

```text
I_{n1,n2}(u)du
 =C_{n1,n2}(1-u)^(N-3)
   P_1^(N-3,0)(2u-1)du,

C_{n1,n2}=32(n1+1)(n2+1)(N-2)a1 a2 ell.
```

**Conditional on that remaining curvature lemma**, the quotient by the beta
weight and degree-one Jacobi polynomial is exactly `C_{n1,n2}`, independent
of `u`.  Equivalently,

```text
I du=d[-C_{n1,n2}u(1-u)^(N-2)].
```

For the oscillator towers `n1,n2>=2`, the primitive vanishes at both ends of
`[0,1]`.  The same result is Jacobi orthogonality against the constant
polynomial.  Thus the radial integration implication is proved for arbitrary
spin once the local-density lemma is supplied.  The existing normalized
finite-spin coefficients reproduce the displayed prefactor, but remain
regressions rather than a generic derivation.

## Representation-theory reach

For fixed `(J1,J2)`, the extremal same-chirality product contains the target
`(S+1,S-1)` oscillator representation with multiplicity one.
Wigner--Eckart would therefore extend a proved vanishing highest-weight
oscillator matrix element to every magnetic component in this orbit.  Parity
would supply the opposite chirality.

This does **not** by itself prove that every resonant conformal cubic shell
vanishes.  The EAA and both EAL parity orbits are separate reduced families;
they require their own identities.  The exact channel enumerator excludes a
mixed-chirality AAL family, so the same-chirality orbit treated here is the
complete AAL representation-theory obligation, subject still to the local-
density and BRST/global-charge lemmas below.

## Open descent lemma

The finite curvature calculations use radiation-gauge mode representatives
in the covariant metric action.  They must not yet be called complete
physical-BRST matrix elements.  A manuscript-level selection theorem needs a
descent and global-charge lemma proving all of the following:

1. replacing an external representative by a BRST-exact one changes the
   integrated shell operator only by a BRST-exact or compact boundary term;
2. eliminating the auxiliary tensor and Stueckelberg variables preserves the
   reduced matrix element and its normalization;
3. the integrations by parts and constraint terms that relate the covariant
   action coefficient to the canonical cylinder Hamiltonian do not generate
   an endpoint or contact contribution;
4. the forward and reverse entries use the induced physical left-right
   normalization;
5. compact conformal-Killing reducibility parameters and the associated
   linearization-stability/global-charge constraints neither remove the
   oscillator states nor add compensating constraint currents.

Until those lemmas are supplied, the exact generic statement is the closed
Hamada--Horata oscillator-harmonic identity.  The full generic curvature
factorization and its BRST/cohomological interpretation remain open.

## Reproduction

```bash
python3 symbolic/verify_conformal_aal_highest_harmonics.py
```

The expected final lines are

```text
CONFORMAL AAL HIGHEST HARMONICS: ALL PASS
```
