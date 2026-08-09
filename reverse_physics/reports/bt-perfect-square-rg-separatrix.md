# Bateman--Turok perfect-square one-loop RG separatrix

**Result:** `COEFFICIENT_COMPUTED`

**Dependency:** `LOCAL-ALGEBRAIC`

**Certificate:**
[`REVERSE_PHYSICS_BT_PERFECT_SQUARE_RG_SEPARATRIX_V1`](../certificates/REVERSE_PHYSICS_BT_PERFECT_SQUARE_RG_SEPARATRIX_V1.json)

## Result

The Bateman--Turok perfect-square (PS) theory is closed under Holdom's
published one-loop renormalization-group flow.  It is not necessary to enlarge
the PS action to the generic two-coupling shift-symmetric theory merely to
absorb the one-loop ultraviolet poles.

This clears the ultraviolet-algebraic part of the virtual gate.  It does **not**
compute the finite four-leg loop jet needed to meet the independent-mass real
threshold.  In fact, an exact top-jet mutation proves that the published beta
functions and on-shell loop/cut data cannot determine that missing finite
coefficient.

## Coupling map

After integrating Holdom's kinetic term by parts, his conventions are

\[
 \mathcal{L}=-\frac12(\Box\phi)^2
 +\lambda_3(\partial\phi)^2\Box\phi
 +\lambda_4((\partial\phi)^2)^2.
\]

Expanding the PS action gives the exact map

\[
 \lambda_3=-\lambda,
 \qquad
 \lambda_4=-\frac12\lambda^2,
 \qquad
 F:=\lambda_3^2+2\lambda_4=0.
\]

The source equations are Bateman--Turok Eq. (2) and Holdom Eq. (1).

## The separatrix identity

Remove the common factor `K=5/(4 pi^2)` from Holdom's one-loop beta
functions.  Exact polynomial reduction gives

\[
 \frac{\beta_3}{K}
 =-\left(\lambda_4\lambda_3+\frac34\lambda_3^3\right),
 \qquad
 \frac{\beta_4}{K}
 =-\left(\lambda_4^2+\lambda_4\lambda_3^2\right),
\]

and hence

\[
 \frac{\beta(F)}{K}
 =-F\left(\lambda_4+\frac32\lambda_3^2\right).
\]

Therefore `F=0` is exactly invariant at one loop.  On it,

\[
 \beta_\lambda=-\frac{5}{16\pi^2}\lambda^3,
 \qquad
 \frac1{\lambda(\mu)^2}
 =\frac1{\lambda(\mu_0)^2}
 +\frac5{8\pi^2}\log\frac{\mu}{\mu_0}.
\]

The PS coupling is asymptotically free.  This agrees with the qualitative
statement in Bateman--Turok, but here the restriction and integrated
coefficient are retained as an exact certificate.

There is also a small classification result.  For a monomial parabola
`lambda4=c lambda3^2`, tangency reduces to

\[
 c(c+\tfrac12)=0.
\]

Thus the invariant parabolas of that form are the cubic-only line `c=0` and
the PS curve `c=-1/2`; PS is the unique one with a nonzero quartic coupling.
Holdom's 2024 flow plot identifies this red curve as a boundary, but the
factorized invariant-ideal calculation is what certifies it here.

## Counterterm closure

On the PS locus, Holdom's pole residues become, with

\[
 A=\frac{5\lambda_3^2}{8\pi^2\varepsilon},
\]

\[
 Z_\phi=1+A,
 \quad Z_\phi^{3/2}Z_3=1+A,
 \quad Z_\phi^2 Z_4=1+A.
\]

To first order in the one-loop pole,

\[
 Z_3=1-\frac A2,
 \qquad Z_4=1-A=Z_3^2+O(A^2).
\]

Consequently the bare relation
`lambda4_0=-lambda3_0^2/2` is preserved.  Equivalently, the divergent
counterterm restricted to the locus is `A` times the whole PS Lagrangian.

## Four-point one-loop sectors

For a connected one-loop four-point graph with `V3` cubic vertices, `V4`
quartic vertices, and `I` internal lines,

\[
 3V_3+4V_4=2I+4,
 \qquad I=V_3+V_4.
\]

There are exactly three vertex-count sectors:

| sector | `(V3,V4)` | `I` | PS order |
|---|---:|---:|---:|
| box | `(4,0)` | 4 | `lambda^4` |
| triangle | `(2,1)` | 3 | `lambda^4` |
| bubble | `(0,2)` | 2 | `lambda^4` |

This is a complete vertex-count enumeration, not a graph-isomorphism list.
The connected scattering amplitude also requires the appropriate lower-point
insertions and counterterms.  Holdom reports that the simple 1PI diagrams
with more than two propagators are finite; the two-quartic bubble supplies the
direct four-point vertex pole, while wave-function renormalization accounts
for the mixed term in `beta4`.

## The on-shell cut vanishes, but the BT jet does not follow

Holdom's general-coupling high-energy two-particle optical-theorem result is

\[
 \frac{s^2}{6\pi}
 (6\lambda_3^2+7\lambda_4)
 (\lambda_3^2+2\lambda_4).
\]

It vanishes identically on the PS separatrix.  This is a useful exact boundary
check, but it is not the NLO differential probability at issue here.  The BT
projector needs the finite square-free jet in four independent external
virtualities, including the one-loop/tree interference.

The insufficiency of on-shell and RG data is exact.  In the hard region
`s^2+t^2+u^2 != 0`, add the crossing-symmetric finite mutation

\[
 \Delta M_1=
 c\lambda^4\frac{x_1x_2x_3x_4}{s^2+t^2+u^2}.
\]

It has the required mass dimension, is finite and scale independent, and
vanishes on shell.  It therefore changes none of the quoted beta functions or
on-shell amplitudes/cuts, but changes the `x1 x2 x3 x4` jet slot.  This is a
data-nonuniqueness witness only: the certificate does not claim that this term
comes from a PS loop integral or is an allowed scheme change.

## Consequence for the real threshold

The predecessor found the reduced real-emission term

\[
 -\frac38 x_0x_1\log(x_1/x_0),
\]

with a normalization-dependent finite part.  The RG calculation here neither
cancels nor fixes it.  The next calculation must evaluate the bubble,
triangle, and box sectors with four independent external masses under one
common infrared prescription, form the BT projected interference, and compare
its mass-ratio logarithm with `-3/8`.

This result does not establish a finite one-loop PS amplitude, a real--virtual
cancellation, a canonical finite part, beyond-tree positivity, a physical
inclusive map, or anything `LORENTZIAN-CAUSAL`.

## Sources

- [Bateman and Turok, *Escape from Ostrogradsky via Hidden Ghost Parity*](https://arxiv.org/abs/2607.00096v1), especially Eq. (2) and Appendix B.
- [Holdom, *Running couplings and unitarity in a 4-derivative scalar field theory*](https://arxiv.org/abs/2303.06723), especially Eqs. (1), (14)--(22).
- [Holdom, *UV-complete 4-derivative scalar field theory*](https://arxiv.org/abs/2402.09223), especially Eqs. (2)--(3) and (11)--(13).

No literature-priority claim is made for the separatrix observation.

## Verification

```text
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 \
  reverse_physics/bt_perfect_square_rg_separatrix.py --check
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 \
  reverse_physics/verify_bt_perfect_square_rg_separatrix.py
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 \
  -m unittest -v reverse_physics.tests.test_bt_perfect_square_rg_separatrix
```

Final scoped receipt (wall time measured with `/usr/bin/time`, 2026-08-09):

| Tier | Command | Time | Peak RSS | Result |
|---|---|---:|---:|---|
| 0 | `python3 -m py_compile` on producer, verifier, and test | 0.02 s | 14,632 KB | PASS |
| 0 | `python3 -m json.tool` on certificate and schema | 0.07 s | 14,744 KB | PASS |
| 1 producer | exact certificate reproduction | 0.02 s | 15,956 KB | PASS, 17/17 |
| 1 independent | SymPy polynomial, dual-number, sector, schema, and boundary verifier | 0.32 s | 70,220 KB | PASS, 20/20 |
| 1 new tests | PS RG-separatrix tests | 1.08 s | 70,344 KB | PASS, 11/11 |
| affected predecessor | off-shell jet obstruction tests | 0.37 s | 24,112 KB | PASS, 10/10 |
| affected predecessor | independent-mass threshold tests | 34.71 s | 95,764 KB | PASS, 11/11 |

All symbolic and predecessor jobs ran sequentially under a 500,000 KB
virtual-memory cap.  No job in the passing certificate chain exceeded 96 MB.

The advisory `env -u SF_PROGRAM ci/science-forge-shadow.sh` was attempted
under the same cap and is **not** a pass.  Its `cbp` caller/where helper aborted
at the memory ceiling before the advisory completed.  The cap was deliberately
not lifted after the earlier out-of-memory failure.  This incomplete advisory
does not promote or falsify the scoped certificate.

Tier 2 consisted of the two direct content-addressed predecessor consumers;
their mathematical inputs were unchanged and their hashes are recorded in the
new certificate.  Tier 3 was not run because this is not a freeze, shared-core
change, release, or explicit full-suite request.  The incomplete advisory and
skipped Tier 3 rail are not reported as passes.

CLOSE-OUT: SHORTFALL -- the PS locus is one-loop RG closed and asymptotically
free, but published loop data do not determine its finite four-leg BT jet.

EVIDENCE: `reverse_physics/certificates/REVERSE_PHYSICS_BT_PERFECT_SQUARE_RG_SEPARATRIX_V1.json`

MISSING-DEP: finite independent-mass bubble, triangle, and box interference jet

## Successor checkpoint

The bubble logarithmic part of that dependency is now closed by
[`REVERSE_PHYSICS_BT_FOUR_POINT_BUBBLE_LOG_JET_V1`](../certificates/REVERSE_PHYSICS_BT_FOUR_POINT_BUBBLE_LOG_JET_V1.json).
The arbitrary-mass double-pole cut polynomial and its fixed-`(s,t)` four-mass
interference jet are computed independently.  The bubble collinear expansion
contains uncancelled `r^-2` and `r^-1` logarithms, so it cannot yet be matched
to the reduced real threshold.  The immediate missing dependency is the
triangle logarithmic jet; the box and finite parts remain behind it.
