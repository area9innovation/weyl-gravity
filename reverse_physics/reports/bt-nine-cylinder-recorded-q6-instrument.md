# BT nine-cylinder recorded probability through lambda six

Certificate:
`REVERSE_PHYSICS_BT_NINE_CYLINDER_RECORDED_Q6_INSTRUMENT_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`.

Lifecycle: `COEFFICIENT_COMPUTED`.

## Result

The selected tagged Bateman--Turok probability through \(\lambda^6\) extends
exactly to all nine choices of incoming and outgoing spectator labels.  With
an explicit record of which spectator cylinder occurred, the nine transported
tagged sectors and one fully rearranged bulk sector form a ten-outcome direct
sum.  For the equal group-invariant mixed preparation, the complete recorded
click probability through \(\lambda^6\) is

\[
 \boxed{
 q_{\rm rec}[f;T]
 ={9\over10}\,q_4
 \left[1+\lambda^2R_6[f;T,\mu]\right]
 +O(\lambda^8),}
\]

where

\[
 q_4={75\lambda^4\Delta\Omega
 \over2048\pi^2\kappa^2\operatorname{Area}},
\]

\[
 R_6[f;T,\mu]
 ={2\sqrt2\over3}\operatorname{Re}C_{ff}(T)
 +{5\over24\pi^2}B_*(T,\mu)
\]

are the already certified selected-cylinder coefficients.  Each labelled
cylinder outcome carries one tenth of the selected expression.  The bulk
outcome has no coefficient through \(\lambda^6\), because its first amplitude
is order \(\lambda^4\) and its first probability is order \(\lambda^8\).

This is one recorded, randomized reduced-mode experiment.  It is not a
coherent detector that forgets which stratum occurred, and it is not yet the
coefficient at generic continuous hard kinematics.

## The nine-cylinder orbit

The exhaustive hard-nonforward atlas has nine pairwise-disjoint spectator
cylinders

\[
 \Delta_{ia}=\{p_i=k_a\},\qquad i,a\in\{0,1,2\}.
\]

Independent relabelling of incoming and outgoing identical scalars gives the
group

\[
 G=S_3^{\rm in}\times S_3^{\rm out},\qquad |G|=36,
\]

with action

\[
 (\sigma,\tau)\Delta_{ia}=\Delta_{\sigma(i),\tau(a)}.
\]

The orbit of \(\Delta_{00}\) consists of all nine cylinders.  Its stabilizer
has order four, so the exact orbit--stabilizer identity is

\[
 9\cdot4=36.
\]

Every cylinder is therefore a relabelled copy of the selected tagged fixture,
provided its packets, angular record and normalization are transported by the
same label permutation.  This is label covariance, not a claim that one
rational fixture determines the coefficient as a function of arbitrary
\(s,t,u\).

The nontrivial tree-cross incidence is also recomputed rather than assumed.
The ten three-subset channels modulo complementation have canonical bit masks

\[
 7,11,13,14,19,21,22,25,26,28.
\]

For every tag pair \(\{i,a+3\}\), exactly six representatives contain one tag
label and receive incidence weight five; the other four receive weight six.
At \(\Delta_{00}\), these two lists exactly reproduce the independently
certified tagged finite-time interference masks.  Repeating the calculation
for all nine pairs proves that the ten-channel combinatorics, not merely the
leading \(q_4\) normalization, is transported around the orbit.

## Exact record algebra

Let the ten record labels be

\[
 \mathcal R=\{\mathrm{bulk},\Delta_{00},\ldots,\Delta_{22}\}.
\]

On \(\mathbb Q^{10}\), define the characteristic record effects

\[
 \Pi_c=|c\rangle\langle c|,
 \qquad
 \Pi_c\Pi_d=\delta_{cd}\Pi_c,
 \qquad
 \Pi_{\rm bulk}+\sum_{i,a}\Pi_{ia}=I_{10}.
\]

The group acts by permutation matrices, fixes the bulk label, and transports
the cylinder effects covariantly.  Direct enumeration gives

\[
 {1\over4}\sum_{g\in G}U_g\Pi_{00}U_g^{-1}
 =\sum_{i,a}\Pi_{ia}.
\]

Choose the positive normalized group-invariant block state

\[
 \rho={I_{10}\over10}.
\]

Then

\[
 \operatorname{tr}(\rho\Pi_{ia})={1\over10},\qquad
 \operatorname{tr}\!\left(\rho\sum_{i,a}\Pi_{ia}\right)={9\over10},
 \qquad
 \operatorname{tr}(\rho\Pi_{\rm bulk})={1\over10}.
\]

Because the record is retained, probabilities are summed across these
orthogonal blocks.  Amplitudes from different blocks are not added.  This is
the point that distinguishes the construction from the still-open unresolved
cross-stratum detector.

## Coefficient assembly

On every transported cylinder, the complete selected probability is

\[
 q_{ia}^{\rm sel}
 =q_4\left[1+\lambda^2R_6[f;T,\mu]\right]+O(\lambda^8).
\]

Multiplying by its record weight gives

\[
 q_{ia}
 ={1\over10}q_4
 \left[1+\lambda^2R_6[f;T,\mu]\right]+O(\lambda^8).
\]

The hard-nonforward atlas proves that there is no additional generic
disconnected stratum.  Its fully rearranged bulk result starts at
\(\lambda^8\), so it contributes zero to the coefficient truncation being
assembled.  Summing the nine cylinder records yields the boxed formula.

The factor \(9/10\) is not a new interaction coefficient.  It is the declared
classical preparation weight of the nine cylinder blocks in \(I_{10}/10\).
A different declared positive block mixture would give the corresponding
weighted sum.  The dynamical content is that every cylinder has the same
complete transported \(q_4,q_6\) pair and that the bulk cannot enter before
the remainder order.

## What this advances

Previously, one tagged cylinder had a complete probability through
\(\lambda^6\), while the atlas classified all nine cylinders only at leading
order.  The present result closes that mismatch on the selected permutation
orbit:

```text
one selected cylinder through lambda6
        + exact S3_in x S3_out covariance
        + nine-cylinder support atlas
        + explicit orthogonal record
        = all nine labelled cylinder outcomes through lambda6
```

It is a larger physical experiment than the original single tagged channel,
but it is still finite-time, reduced-mode, perturbative and deliberately
recorded.

## Exact boundary

Established:

- the exact transitive \(S_3^{\rm in}\times S_3^{\rm out}\) action on all
  nine cylinders;
- the order-four stabilizer and orbit--stabilizer identity;
- a complete ten-effect orthogonal record algebra;
- a positive normalized invariant equal-block preparation;
- all nine transported tagged probabilities through \(\lambda^6\);
- zero bulk contribution through \(\lambda^6\); and
- the displayed recorded total and its small-coupling perturbative
  positivity.

Not established:

- a coherent detector effect that erases the stratum record;
- the \(q_6\) coefficient at generic continuous \(s,t,u\);
- forward, collinear, real--virtual or KLN completion;
- an all-order probability or all-time Møller/LSZ/S operator;
- the standard scalar projector or general Eq. (19);
- gravity, metric BV--BRST, QME or residual transfer;
- anything `LORENTZIAN-CAUSAL`; or
- literature priority.

## Next physical gate

The next nontrivial calculation is no longer another label permutation.  It
is to replace the selected orbit by a compact continuous family of active
hard kinematics.  The connected tree-cross kernel and the finite-time loop
coefficient must be derived as functions of \(s,t,u\), with uniform hard-gap
bounds, and then assembled fibrewise over the nine recorded cylinders.  Only
after that is it scientifically meaningful to erase the record and confront
products of spectator-supported distributions with neighboring bulk
amplitudes.

## Verification receipt

The exact producer passes 43 internal checks in 1.27 s at 17,280 kB peak RSS.
The independent verifier uses set actions and characteristic functions on a
ten-point record space rather than importing the producer's rational matrices.
It passes 47 checks in 0.08 s at 24,468 kB.  Twenty tests, including nineteen
adversarial certificate mutations, pass in 0.19 s at 24,736 kB.  Final Python
byte compilation passes in 0.04 s at 15,264 kB, and all four new JSON files
parse.  All scientific processes run sequentially under `ulimit -v 500000`.

The direct mathematical predecessor files are unchanged and content
addressed.  Both rails recompute their hashes and passing flags; the
ten-channel predecessor is imported directly for the mask comparison.  This
is the applicable Tier 2 chain, with no shared producer or operator changed.

Papers 05 and 06 compile twice under the same cap.  Their final passes take
0.48 s at 50,656 kB and 0.50 s at 50,984 kB, producing respectively 59 pages
(657,407 bytes) and 56 pages (642,878 bytes).  No new overfull boxes occur.

Tier 3 was run after the final mathematical inputs and all nine incidence
checks were in place and is **not** a pass.  It ran 2,236 tests in 778.041 s
(779.05 s wall time) at 391,296 kB peak RSS, with 32 failures and 9 skips.
Every one of the 20 new tests passed inside that run.  A subsequent
provenance-wording correction and final paper prose build changed no
mathematical input and were covered by the final scoped rails.  The Tier 3
failures remain in unchanged older BT provenance/hash/executable rails and the
existing `chain_imports` scan.  This blocks a paper freeze or release promotion
but does not convert the passing scoped rails into a repository-wide claim.

The Science Forge planning import is also **not** a pass.  The configured
launcher exited 3 in 0.07 s at 7,508 kB because its cached `sfc` build failed.
It did not reach the fold.  The work-item and append-only event JSON parse and
are content pinned, but no graph acceptance is claimed.  A failed or skipped
higher tier is never counted as a pass.

Commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_nine_cylinder_recorded_q6_instrument.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_nine_cylinder_recorded_q6_instrument.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_nine_cylinder_recorded_q6_instrument
ulimit -v 500000; python3 -m unittest discover -v
```
