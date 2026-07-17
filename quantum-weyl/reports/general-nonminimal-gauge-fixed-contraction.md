# General nonminimal and gauge-fixed local BV contraction

This report accompanies
`GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION`. It closes the local-algebraic
G2 gate on the imported regular Bach-locus chart. It does not construct a
gauge-fixed Green operator, a Hadamard state, renormalized products, or a
quantum master equation.

## General nonminimal contraction

The four Diff directions and one Weyl direction each contribute two
contractible BV pairs in the suspended convention:

```text
b_A          -> bar_c_A
bar_c_star_A -> b_star_A
```

Thus the general local nonminimal sector has 20 atoms and 10 pairs. The rows
are pointwise and prolong covariantly to every finite jet. The implementation
checks `Q^2=0` on every atom and

```text
Q h + h Q = 1 - inclusion projection
```

on 25,080 canonical supermonomials, including even and odd coefficients from
the minimal algebra. The homotopy side conditions and horizontal-differential
compatibility follow from the explicit pointwise rows and their jet
prolongation.

## Gauge-fixing transport

Let `U` be any invertible local BV-canonical transformation and `V=U^-1`.
The unfixed contraction transports as

```text
Q' = U Q V
S' = U S V
J' = U J
R' = R V
```

A free-word normal-form calculation uses only `UV=VU=1` and the unfixed SDR
relations. All six target identities reduce to the zero normal form:
`Q'^2`, `S'^2`, `R'J'-1`, `R'S'`, `S'J'`, and
`Q'S'+S'Q'-(1-J'R')`.

The landed 54-row Berger nonminimal and gauge-fixed packages are replayed as
a specialization regression. Their pointwise supports and BV-canonical shear
agree with the general construction, but no Berger spectral or causal claim
is promoted to a general background.

## Cohomology consequence

The minimal-to-nonminimal inclusion and projection, followed by canonical
gauge-fixing transport, are explicit chain isomorphisms. On the regular Bach
locus:

| Group | Even dimension | Odd dimension | Representatives |
|---|---:|---:|---|
| `H04` | 2 | 1 | `CT_C2`, `CT_E4`, `CT_C_DUAL_C` |
| `H14` | 2 | 1 | `ANOM_OMEGA_C2`, `ANOM_OMEGA_E4`, `ANOM_OMEGA_C_DUAL_C` |

`CT_BOX_R` and `ANOM_OMEGA_BOX_R` remain exact with their previously stored
primitives. No extra pure-Diff, mixed Diff--Weyl, antifield-dependent, or
nonminimal class appears.

The next gate is `REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING`. Background
heat-kernel coefficients do not by themselves satisfy that gate.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m local_bv.nonminimal_gauge_fixed_contraction_certificate --check
PYTHONPATH=quantum-weyl python3 -m local_bv.verify_nonminimal_gauge_fixed_contraction
PYTHONPATH=quantum-weyl python3 -m unittest local_bv.tests.test_nonminimal_gauge_fixed_contraction
```

The scoped suite exercises exact rational arithmetic only. The full repository
suite is unnecessary because no shared algebra engine or upstream classical
producer was modified.
