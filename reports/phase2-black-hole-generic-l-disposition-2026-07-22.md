# Phase 2 generic-ell Schwarzschild parity disposition

Result: `BH_PHASE2_GENERIC_L_AXIAL_COUNTEREXAMPLE_POLAR_FINITE_LINE_Q21_WALL`

Dependency tags: `LOCAL-ALGEBRAIC` + `REDUCED-MODE`

Lifecycle: `CLASSIFIED`

## Joined disposition

The generic-ell Einstein-only formal radial selection claim is false.  The
corrected axial `X0` carrier is non-Einstein, extends formally to all radial
orders in its declared class, and has finite fixed-representative Lee--Wald
pairing for every integer `ell>=2` and real `omega!=0`.  Axial `X2` remains
unclassified.

The terminal polar closure proves a different scoped structure.  Its ordered
oscillatory `(E,X0,X1,X2)` current has generic rank three and a one-dimensional
mixed Einstein/additional filtered radical through `p=0,-1`.  The first finite
`p=-2` form on that line is generically nonzero.  Its exact exceptional wall is

```text
Q21(ell*(ell+1), omega^2) = 0.
```

At that wall the deeper filtration is open; it is not interpreted as a
physical radical, positivity wall, or scattering threshold.

## Exact exceptional-frequency count

Writing `x=omega^2>0`, `Q21` has bidegree `(21,21)` and 282 terms.  Its leading
`x` coefficient is

```text
-7253554917687775048237056*(Lambda+2)*(5*Lambda+8),
```

which is nonzero for `Lambda>=6`.  The exact `x=0` boundary factorization and
the exact `x`-discriminant show six transition roots above `Lambda=6`: five
discriminant roots and one boundary root.  Rational isolating intervals place
them in `(6.588,6.589)`, `(6.796,6.797)`, `(8.226,8.227)`,
`(13.983,13.984)`, `(111.320,111.322)`, and
`(1640.901,1640.902)`.  Exact `x`-Sturm counts then give:

| harmonic | positive `x` roots | real nonzero `omega` roots |
|---|---:|---:|
| `ell=2` | 0 | 0 |
| `ell=3` | 3 | 6 |
| `4<=ell<=10` | 1 | 2 |
| `11<=ell<=40` | 3 | 6 |
| `ell>=41` | 1 | 2 |

The continuous-`Lambda` chamber counts are recorded separately in the
certificate.  At the legacy fixture `Lambda=6`, `omega^2=9/25`, `Q21` equals

```text
-174226120816040380076641138108451235935620694016/227373675443232059478759765625
```

and is exactly nonzero.

The previously recorded longer rational is also replayed exactly, but it is
`Q21(6,81/625)`: it arose by substituting `omega=9/25` into the serialized
even-`omega` polynomial and hence squaring the intended `x` a second time.
It is not the value of `Q21(6,x)` at `x=9/25`, and it is not a normalized
Hilbert norm.  Separately, the denominator-cleared `p=-2` induced-current
coefficient has the certified factorization
`C*omega^51*Lambda^3*(Lambda-2)^5*P6^2*P20*Q21`.

## Claim boundary

This is a formal infinity-mode classification in a fixed Lee--Wald
representative.  It does not classify axial `X2`, extend the terminal-only
polar prefixes, resolve the deeper `Q21=0` filtration, construct a global
asymptotic phase space, perform horizon-to-infinity matching, or establish
scattering, QNMs, stability, particles, positivity, or a quantum theory.

CLOSE-OUT: DONE — exact axial and terminal polar inputs are joined into a scoped generic-ell phase diagram, including the independently certified Q21 exceptional-frequency count and every unresolved boundary.
EVIDENCE: black_hole_programme/phase2/generic_l_synthesis/certificate.json
