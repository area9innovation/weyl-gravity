# BT tagged-connected finite-time tree interference

Certificate:
`REVERSE_PHYSICS_BT_TAGGED_CONNECTED_FINITE_TIME_INTERFERENCE_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

The leading tagged spectator tree and the connected six-point tree do **not**
decouple on their common external-mass/species carrier. At the certified hard
nonforward fixture their exact tree cross kernel is

\[
 I_{\rm tree}^{(6)}(T)
 =16\sqrt2\,\lambda^6 W(T),
\]

where

\[
 \begin{split}
 W(T)={}&12T+\frac{125}{256}\sin\frac{16T}{5}
 +\frac{125}{128}\sin\frac{8T}{5}\\
 &+\frac{125}{8}\sin\!\left(\frac{2(\sqrt{17}-3)T}{5}\right).
 \end{split}
\]

For every finite `T` this is finite. For every `T>0` it is strictly positive,
and

\[
 \lim_{T\to\infty}\frac{W(T)}T=12.
\]

The linear term comes from four connected factorization channels that become
exactly resonant on the spectator cylinder. Thus the next barrier is not a
vanishing-overlap theorem. It is an inclusive resonant completion problem.

This coefficient is an exact external-jet cross kernel. It is not yet a
dimensionless packet probability and is not the complete order-`lambda^6`
probability.

## One common positive carrier

The public neutral six-leg external-mass carrier has ten unordered complement
pairs, represented by masks

```text
7, 11, 19, 13, 21, 25, 14, 22, 26, 28.
```

Its ghost-even positive frame is

\[
 U_+=\frac1{\sqrt2}\binom{I_{10}}{I_{10}},
 \qquad U_+^T\eta U_+=I_{10}.
\]

For finite-time channel kernels `beta_A,T`, the connected coefficient is

\[
 a_T=\sqrt2\,U_+c_T,
 \qquad
 c_T=\frac14(J-I)\beta_T.
\]

The tagged pair is `{0,3}` and the active labels are `{1,2,4,5}`. Spectator
identity requires one Omega and one Upsilon on the tag, while the active
quartic block requires two Omega and two Upsilon. Therefore the active
four-point jet occupies exactly the six neutral masks containing one tag
label:

\[
 R=\{7,19,21,14,26,28\}.
\]

The other four masks are

\[
 N=\{11,13,25,22\}.
\]

In the same positive ten-frame the tagged vector is

\[
 d_S=\begin{cases}2,&S\in R,\\0,&S\in N.\end{cases}
\]

Consequently

\[
 d^Td=6\cdot2^2=24,
\]

exactly reproducing the certified active four-point jet norm. The embedding
is therefore norm preserving; it does not identify the two sectors by an
arbitrary choice of coordinates.

## Why the incidence weights are five and six

For every output assignment `S`,

\[
 c_{S,T}=\frac14\sum_{A\ne S}\beta_{A,T}.
\]

Pairing with the six nonzero tagged coordinates gives

\[
 \langle d,a_T\rangle
 =2\sqrt2\sum_{S\in R}c_{S,T}
 =\frac{\sqrt2}{2}
 \left(5\sum_{A\in R}\beta_{A,T}
       +6\sum_{A\in N}\beta_{A,T}\right).
\]

An intermediate channel in `R` is omitted by one of the six `R` output rows,
so it occurs five times. A channel in `N` is never an `R` output row, so it
occurs six times. The producer obtains this from the exact `(J-I)` matrix; the
independent verifier rebuilds the ten complement classes and performs the
nested incidence sums directly.

## Exact tagged channel geometry

Orient every unordered channel momentum toward nonnegative energy and write

\[
 \delta_A=q_A^0-|\mathbf q_A|,
 \qquad D_A=q_A^0+|\mathbf q_A|,
 \qquad q_A^2=\delta_AD_A.
\]

At the certified rational fixture the ten channels reduce to four exact
classes:

| masks | carrier | multiplicity | `delta_A` | `D_A` | `q_A^2` |
| --- | --- | ---: | --- | --- | --- |
| `7` | `R` | 1 | `16/5` | `16/5` | `256/25` |
| `19,21,26,28` | `R` | 4 | `2(3-sqrt(17))/5` | `2(3+sqrt(17))/5` | `-32/25` |
| `14` | `R` | 1 | `-8/5` | `16/5` | `-128/25` |
| `11,13,25,22` | `N` | 4 | `0` | `2` | `0` |

The last row is the new point. These are connected six-point channels, but on
the tagged cylinder their intermediate momenta are exactly null. Finite time
does not make them divergent:

\[
 \beta_{A,T}=\frac{F_T(\delta_A)}{D_A},
 \qquad
 F_T(\delta)=\int_0^T e^{i\delta\tau}\,d\tau,
\]

has continuous resonant value `T/D_A=T/2`. Their incidence-weighted real
contribution is therefore

\[
 6\sum_{A\in N}\Re\beta_{A,T}
 =6\cdot4\cdot\frac T2=12T.
\]

The other six channels produce the three bounded sine terms in `W(T)`.

## Restoring the tree normalization

The tagged reduced four-point coefficient is `lambda^2 d`, while the global
connected reduced column is normalized as `16 lambda^4 a_T`.  Both are
compared in the certified common-phase reduced-amplitude convention.  The
omitted common phase cancels, while the two displayed real reduced
normalizations fix their relative sign. Thus

\[
 \begin{split}
 2\Re\langle\lambda^2d,16\lambda^4a_T\rangle
 &=16\sqrt2\,\lambda^6
 \Re\left(5\sum_R\beta+6\sum_N\beta\right)\\
 &=16\sqrt2\,\lambda^6W(T).
 \end{split}
\]

This normalization restores the common Hamiltonian tree factor only. It does
not supply the missing distributional packet/coarea or finite-volume factor.

## Exact positivity and secular behavior

All three sine arguments in `W(T)` are positive for `T>0`. Applying
`sin(x)>=-x` separately gives

\[
 W(T)\geq\frac{221-50\sqrt{17}}8T.
\]

The coefficient is strictly positive because

\[
 221^2=48841>42500=50^2\,17.
\]

As a local check,

\[
 W'(0)=\frac{-29+50\sqrt{17}}8>0.
\]

Since every sine term is bounded, the large-time coefficient is exactly 12.
This does not define an all-time scattering amplitude: secular perturbative
growth normally signals that the resonant contribution must be assembled
with survival, dressing, or resummation before taking a long-time limit.

## Physical meaning

In ordinary language, the unchanged spectator does not isolate the active
two-to-two collision from every connected three-to-three history. Four
connected histories can carry precisely the same energy at the tagged
configuration. Their phases therefore remain aligned and accumulate with the
observation time instead of averaging away.

This is a genuine dynamical statement inside the finite-time BT scalar model.
It is not a new spacetime dimension, a graviton result, or a proof of
Bateman--Turok Eq. (19). It also shows why simply adding the already certified
`lambda^4` and `lambda^8` probabilities would be wrong for a detector that
does not resolve the two strata: their amplitudes generate an intervening
`lambda^6` term.

## Why this is not yet the NLO probability

The tagged amplitude contains a spectator identity distribution, while the
connected amplitude is a continuous finite-time kernel. Their pointwise
external-mass/species pairing is well defined and is what was computed here.
A physical probability needs both objects tested on one compact packet family
with the correct transverse coarea and finite-volume dimensions. Multiplying
this kernel by the leading tagged cross-section density would silently mix
incompatible normalizations.

Moreover, probability order `lambda^6` also contains objects not evaluated by
this tree pairing:

- the active four-point tree/one-loop interference, including finite terms and
  counterterms;
- a possible order-`lambda` correction to the dressed scalar source;
- the matching virtual or survival coefficient required by pseudo-unitarity;
- the forward, collinear and real--virtual completion of the resonant boundary.

The next calculation must put all of these terms on the same compact
finite-time packet carrier and determine whether the `12T` term cancels,
exponentiates into survival, or remains as a detector-dependent secular
coefficient. Only that sum can be called the complete tagged-stratum NLO
probability.

## Claim boundary

The result does not establish a normalized packet probability, the complete
order-`lambda^6` coefficient, loop or survival completion, real--virtual/KLN
cancellation, an all-time Møller/LSZ/S operator, general Eq. (19), gravity or
metric BV--BRST transfer, or anything `LORENTZIAN-CAUSAL`. No literature-
priority claim is made.

## Verification receipt

- Tier 0: the new Python and JSON files parse; the scoped diff passes
  `git diff --check`; Papers 05 and 06 compile twice.
- Tier 1: the exact producer passes 40/40 checks, the method-distinct verifier
  passes 36/36 checks, and 22 tests including 21 adversarial mutations pass.
  Each rail is executed under a 500 MB virtual-memory cap.
- Tier 2: the input certificates are unchanged and content addressed. Their
  hashes and passing states are checked by both new rails; no predecessor
  producer was rerun because the mathematical inputs did not change.
- Tier 3 was not run: this result changes no shared core algebra, freeze,
  lifecycle promotion beyond `COEFFICIENT_COMPUTED`, release, QME state, or
  Lorentzian claim.
- The Science Forge planning fold is clean with the new work item and its
  append-only DONE transition.

Commands:

```text
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_tagged_connected_finite_time_interference.py --write --check
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_tagged_connected_finite_time_interference.py
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_tagged_connected_finite_time_interference
```
