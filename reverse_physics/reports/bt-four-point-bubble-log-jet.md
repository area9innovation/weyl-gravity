# Bateman--Turok four-point bubble logarithmic jet

**Result:** `COEFFICIENT_COMPUTED`

**Dependency:** `REDUCED-MODE`

**Certificate:**
[`REVERSE_PHYSICS_BT_FOUR_POINT_BUBBLE_LOG_JET_V1`](../certificates/REVERSE_PHYSICS_BT_FOUR_POINT_BUBBLE_LOG_JET_V1.json)

## Result

The complete two-quartic bubble sector of the PS one-loop four-point
amplitude has now been computed through its logarithmic four-external-mass
interference jet.  The result is nonzero and crossing symmetric, but the
bubble sector alone has collinear logarithms enhanced by two inverse powers of
the momentum-transfer ratio.  It is therefore not a candidate for direct
cancellation of the reduced real-emission `-3/8` coefficient: triangle and box
sectors must first be included.

This is the first actual virtual-amplitude coefficient in the BT loop stream.
It is not the full loop amplitude.

## Declared carrier

Take four all-incoming momenta with independent external virtualities

\[
 x_i=p_i^2,
\]

and hold

\[
 s=(p_1+p_2)^2,\qquad t=(p_1+p_3)^2
\]

fixed.  Momentum conservation then gives

\[
 u=x_1+x_2+x_3+x_4-s-t.
\]

The calculation is in the square-free jet algebra

\[
 \mathbb Q(s,t,L_s,L_t,L_u)[x_1,x_2,x_3,x_4]/(x_i^2),
\]

in the hard region `s t (s+t) != 0`.  This is a fixed-`(s,t)` amplitude
carrier before differentiating the external phase-space density or its moving
boundaries.

## Double-pole bubble cut

Consider a channel `(a,b)|(c,d)` with

\[
 S=(a+b)^2=(c+d)^2,\qquad T=(a+c)^2.
\]

Give the two internal lines independent squared masses `y,z`.  The ordinary
two-particle cut contains the density

\[
 \frac{\sqrt{\lambda(S,y,z)}}{S}.
\]

The quartic-vertex product is averaged over the internal direction.  Applying
one derivative in each internal mass and then setting `y=z=0` implements the
two squared propagators.  The result is

\[
 \left.\partial_y\partial_z\operatorname{Cut}_{y,z}\right|_{0}
 =\frac1{12}P_{ab|cd}(S,T),
\]

where

\[
\begin{aligned}
P_{ab|cd}={}&7S^2+ST+T^2-(7S+T)(x_a+x_b+x_c+x_d)\\
 &+x_ax_b+x_cx_d
 +7(x_ax_c+x_ax_d+x_bx_c+x_bx_d).
\end{aligned}
\]

On shell this reduces to

\[
 P_{ab|cd}|_{x=0}=7S^2+ST+T^2,
\]

exactly the channel polynomial in Holdom's published four-point logarithm.
This fixes the normalization of the arbitrary-mass continuation:

\[
 \Gamma_{\rm bubble,log}
 =\frac{\lambda_4^2}{(4\pi)^2}\frac83
 \sum_{S=s,t,u}P_S L_S.
\]

The independent verifier does not reuse the covariant moment derivation.  It
constructs explicit rational center-of-mass four-vectors, expands the vertex
product in three direction cosines, performs exact spherical monomial
averages, and differentiates the massive cut.  Three kinematically distinct
fixtures reproduce `P/12`.

## Interference with the PS tree amplitude

Write the complete PS tree amplitude as

\[
 M_{\rm tree}=4\lambda^2 M_{\rm tree}^{\rm red},
\]

with

\[
 M_{\rm tree}^{\rm red}
 =\sum_{S=s,t,u}
 \frac{\lambda(S,x_a,x_b)\lambda(S,x_c,x_d)}{4S^2}-Q_4.
\]

The ordinary on-shell value vanishes, as expected for the PS cancellation,
but its external-mass jet does not.

Define

\[
 J=[x_1x_2x_3x_4]\,
 M_{\rm tree}^{\rm red}(P_sL_s+P_tL_t+P_uL_u).
\]

Then

\[
 J=\frac{N_sL_s+N_tL_t+N_uL_u+N_0}
 {s^2t^2(s+t)^2},
\]

where each coefficient list below multiplies
`s^(6-k) t^k`, `k=0,...,6`:

| part | coefficients |
|---|---|
| `N_s` | `(7,-13,-49,-19,-13,-1,1)` |
| `N_t` | `(1,-1,-13,-19,-49,-13,7)` |
| `N_u` | `(7,-1,-43,-67,-43,-1,7)` |
| `N_0` | `(0,-28,-59,-63,-59,-28,0)` |

The reversal of the `N_s,N_t` rows and the palindromic `N_u,N_0` rows are
exact crossing controls.  A method-distinct subset-algebra verifier reproduces
all 28 integers without sequential differentiation.

Restoring the physical normalization gives

\[
 [x_1x_2x_3x_4] 2\operatorname{Re}
 (M_{\rm tree}^*M_{\rm bubble,log})
 =\frac{\lambda^6}{(4\pi)^2}\frac{16}{3}J.
\]

## Collinear behavior

In the physical region define

\[
 r=\frac ts,\qquad
 L=\log\frac{\mu^2}{s},\qquad
 \ell=\log\left(-\frac ts\right).
\]

Then `L_t=L-ell` and `L_u=L-log(1+r)`.  The exact jet gives

\[
 J=\frac{15L-\ell}{r^2}
 +\frac{-45L+3\ell-35}{r}
 +8\ell-30L+\frac{31}{2}+O(r).
\]

Thus the bubble contribution alone is much more singular than the finite
reduced real threshold.  This is not a contradiction: the bubble is only one
scalar-theory topology sector, and the PS relation ties it
to triangle, box, wave-function, and counterterm contributions.  The next
sharp test is whether the triangle cancels the `r^-2` and `r^-1` terms.

## Claim boundary

This result computes only the logarithmic two-quartic bubble contribution on
the declared fixed-`(s,t)` carrier.  It does not establish:

- the finite rational part of the bubble;
- the triangle or box sector;
- the complete connected one-loop amplitude;
- application of the external phase-space projector;
- a common real--virtual infrared prescription;
- cancellation or matching of the real `-3/8` coefficient;
- a physical NLO probability or beyond-tree positivity; or
- anything `LORENTZIAN-CAUSAL` or any tensor/BRST gravitational lift.

## Sources

- [Bateman and Turok, *Escape from Ostrogradsky via Hidden Ghost Parity*](https://arxiv.org/abs/2607.00096v1), Eq. (2) and Appendix B.
- [Holdom, *Running couplings and unitarity in a 4-derivative scalar field theory*](https://arxiv.org/abs/2303.06723), Eq. (22).
- [Holdom, *UV-complete 4-derivative scalar field theory*](https://arxiv.org/abs/2402.09223), Eqs. (8)--(12).

The arbitrary-mass cut polynomial and interference jet are this repository's
results.  No literature-priority claim is made.

## Verification

```text
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 \
  reverse_physics/bt_four_point_bubble_log_jet.py --check
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 \
  reverse_physics/verify_bt_four_point_bubble_log_jet.py
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 \
  -m unittest -v reverse_physics.tests.test_bt_four_point_bubble_log_jet
```

Final scoped receipt (wall time measured with `/usr/bin/time`, 2026-08-09):

| Tier | Command | Time | Peak RSS | Result |
|---|---|---:|---:|---|
| 0 | `python3 -m py_compile` on producer, verifier, and test | 0.02 s | 15,164 KB | PASS |
| 0 | `python3 -m json.tool` on certificate and schema | 0.08 s | 14,488 KB | PASS |
| 1 producer | covariant double-pole cut and sequential jet producer | 3.88 s | 78,984 KB | PASS, 16/16 |
| 1 independent | rational CM-frame cuts, subset jet, schema, and boundary verifier | 1.74 s | 76,372 KB | PASS, 10/10 |
| 1 new tests | bubble logarithmic jet tests | 9.61 s | 79,152 KB | PASS, 10/10 |
| affected predecessor | PS RG-separatrix tests | 1.08 s | 70,084 KB | PASS, 11/11 |

All symbolic jobs ran sequentially under a 500,000 KB virtual-memory cap; no
passing scoped job exceeded 79 MB.  The independent-mass predecessor is an
unchanged content-addressed input and was checked by its recorded SHA-256; its
expensive symbolic integration was not rerun.

The advisory `env -u SF_PROGRAM ci/science-forge-shadow.sh` was attempted
under the same cap and is **not** a pass.  Its `cbp` caller/where helper again
aborted at the memory ceiling before the advisory completed.  The cap was not
lifted after the earlier out-of-memory failure.  This incomplete advisory does
not promote or falsify the scoped result.

Tier 3 was not run because this is not a freeze, shared-core change, release,
or explicit full-suite request.  The incomplete advisory and skipped Tier 3
rail are not reported as passes.

CLOSE-OUT: SHORTFALL -- the bubble logarithmic jet is computed, but its
collinear powers require triangle and box completion before real matching.

EVIDENCE: `reverse_physics/certificates/REVERSE_PHYSICS_BT_FOUR_POINT_BUBBLE_LOG_JET_V1.json`

MISSING-DEP: triangle logarithmic four-mass jet

## Successor checkpoint

The triangle and box logarithmic dependency is now closed by
[`REVERSE_PHYSICS_BT_TRIANGLE_BOX_LOG_JET_V1`](../certificates/REVERSE_PHYSICS_BT_TRIANGLE_BOX_LOG_JET_V1.json).
The complete topology sum cancels every bubble `r^-2` and `r^-1` term and
reduces exactly to `15*(Ls+Lt+Lu)`.  The surviving ratio logarithm has not yet
been passed through the external four-mass phase-space projector, and cut-free
finite rational terms remain outside the cut calculation.
