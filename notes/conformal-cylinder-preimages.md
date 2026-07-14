# Sprint 1A: exact all-energy cylinder metric preimages

## Result

The previously missing algebraic metric preimage is now explicit on every
physical `E/A/L` block.  Work in the rational Euler chart

```text
r=tan(beta/2),  z=1+r^2,
q=d beta+i sin(beta)d gamma.
```

For a positive-chirality highest weight, the normalized metric waves are the
Hamada--Horata radiation-gauge modes

```text
E_n: J=n/2,       h_ij=N_E(J) T[J]_ij exp(-i n tau),
A_n: J=(n-1)/2,   h_0i=N_A(J) V[J]_i exp(-i n tau),
L_n: J=(n-2)/2,   h_ij=N_L(J) T[J]_ij exp(-i n tau),
```

where the unit `S3` highest weights are

```text
V[J]=-sqrt(2J)/(4 pi) cos(beta/2)^(2J-1)
      exp[-i((J+1/2)alpha+(J-1/2)gamma)] q,

T[J]=sqrt(2(2J-1))/(16 pi) cos(beta/2)^(2J-2)
      exp[-i((J+1)alpha+(J-1)gamma)] q tensor q,
```

and

```text
N_E=1/[4 sqrt(J(2J+1))],
N_A=1/[2 sqrt((2J-1)(2J+1)(2J+3))],
N_L=1/[4 sqrt((J+1)(2J+1))].
```

`bridge/cylinder_harmonics/linearized_geometry.py` differentiates these
expressions with symbolic integer `n`.  It suppresses only the common factor

```text
exp[-i(E tau+m_L alpha+m_R gamma)] z^(-a)
```

and retains every rational coordinate component.  The engine constructs the
background connection, linearized Riemann, Ricci, scalar, and Weyl tensors,
then independently applies

```text
(C^sharp U)_mn=nabla^r nabla^s U_mrns+(1/2)Ricci^rs U_mrns.
```

For symbolic `n` the three full Weyl images are nonzero, algebraically
trace-free, have a common Hodge eigenvalue, and obey `C^sharp C_1 h=0`.
After the common factor is suppressed, convenient nonzero pivots are

```text
E_n: (C_1 h)_(0202)
  =sqrt(n(n-1)(n+1))/[16 pi z^2],

A_n: (C_1 h)_(0102)
  =sqrt(n(n-2)(n-1))/[32 pi sqrt(n+2) z],

L_n: (C_1 h)_(0202)
  =sqrt(n(n-3)(n-1))/[16 pi z^2].
```

They are nonzero at every allowed tower energy.  Since `C_1` is an
`SO(4)` intertwiner and every target irrep occurs with multiplicity one, the
highest-weight calculation extends to the whole magnetic block.  Define the
normalized geometric curvature basis by

```text
U_(F,n,M)=C_1 h_(F,n,M).
```

Then the exact right inverse is

```text
R_n U_(F,n,M)=h_(F,n,M),
C_n R_n=id
```

within the same compact energy and `SO(4)` type.  The orientation-reversing
isometry `alpha <-> gamma` supplies the opposite chirality and swaps the two
`SU(2)` labels.

The block dimensions are exactly

```text
dim E_n=(n+3)(n-1),
dim A_n=(n+1)(n-1),
dim L_n=(n+1)(n-3),
```

and parity completion gives `(10,40,82,136,202)` at energies `2,...,6`.
Together with the chiral BGG character, the nonzero curvature intertwiner and
explicit finite-mode preimages identify the geometric positive-energy
curvature system with the abstract `E/A/L` module.

## Independent guards

The certificate also verifies that:

- the rational cylinder metric has `Ricci=(0,2 gamma)` and `R=6`;
- every metric representative is trace-free;
- the Weyl image has zero algebraic trace;
- `alpha <-> gamma` preserves the metric and reverses orientation;
- a deliberately mistuned `E_2` frequency produces a nonzero Bach tensor.

The last check prevents a vacuous implementation of `C^sharp` from passing.

## Scope

This closes the physical-block right inverse and the algebraic `E/A/L`
intertwiner.  It does **not** yet construct every off-shell gauge, metric,
curvature, compatibility, and equation block of the finite harmonic BGG
complex.  It also does not compute the complete local BV rows or a conformal
cyclic retract.

Run

```bash
python3 symbolic/verify_conformal_cylinder_preimages.py
```

Regenerate the JSON and LaTeX artifacts with

```bash
python3 symbolic/verify_conformal_cylinder_preimages.py --emit
```

The stronger off-shell claim must fail:

```bash
python3 symbolic/verify_conformal_cylinder_preimages.py \
  --claim-complete-harmonic-complex
```
