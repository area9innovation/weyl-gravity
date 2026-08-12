# BT hard-nonforward physical stratified atlas

Certificate:
`REVERSE_PHYSICS_BT_HARD_NONFORWARD_PHYSICAL_STRATIFIED_ATLAS_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

The fully rearranged and tagged-spectator calculations are not merely two
examples. They exhaust the **distributionally local hard nonforward**
three-particle strata.

Write the six external labels in all-incoming convention as

\[
 (p_0,p_1,p_2,-k_0,-k_1,-k_2),
 \qquad \sum_i p_i=\sum_a k_a=P,
\]

where every momentum is future null, `P` is timelike, every same-side pair
invariant is strictly positive, same-side momenta are distinct, and the six
forward permutation diagonals have been removed. On this domain the support
of every disconnected contribution is contained in the union of the nine
spectator cylinders

\[
 \Delta_{ia}=\{p_i=k_a\},\qquad 0\leq i,a\leq2.
\]

The cylinders are pairwise disjoint after equal-particle and forward loci are
removed. Consequently there are exactly two local cases:

1. In the bulk, where no `p_i=k_a`, every disconnected term vanishes by
   support and the complete leading probability is the connected
   three-to-three result

   \[
    q_{\rm bulk}=\lambda^8
    \langle\Psi,A_{YX}^{*}A_{YX}\Psi\rangle+O(\lambda^9).
   \]

   For the declared scalar source,

   \[
    q_{\rm bulk}=16\lambda^8
    \left\|\sum_{B=1}^{9}P_YK_{B,T}P_XF\right\|^2+O(\lambda^9).
   \]

2. On exactly one `Delta_ia`, with the complementary active pair hard and
   nonforward, the unique leading transition is the active four-point tree
   tensored with spectator identity. Its complete leading probability is

   \[
    q_{ia}=\frac{3\lambda^4}{32\pi^2s_{ia}}
    \frac{\Delta\Omega}{\mathrm{Area}}+O(\lambda^5),
    \qquad s_{ia}=(P-p_i)^2=(P-k_a)^2.
   \]

There is no generic two-spectator nonforward case: two distinct spectator
equalities and total momentum conservation force the third equality, placing
the configuration on a removed forward permutation diagonal.

“Complete” here modifies the local first nonzero coefficient. It does not
mean that one unresolved finite-resolution detector spanning different
strata has been computed, nor that higher orders or all-time scattering are
known.

## Exhaustive disconnected census

A disconnected graph partitions the six external labels among at least two
connected components. The producer enumerates all set partitions. The
independent verifier instead enumerates integer partitions of six and applies

\[
 N(s_1,\ldots,s_r)=
 \frac{6!}{\prod_j s_j!\prod_m n_m!},
\]

where `n_m` is the multiplicity of component size `m`. Both routes give
`B_6=203`, hence 202 disconnected partitions:

| component profile | count |
| --- | ---: |
| `1+1+1+1+1+1` | 1 |
| `1+1+1+1+2` | 15 |
| `1+1+1+3` | 20 |
| `1+1+2+2` | 45 |
| `1+1+4` | 15 |
| `1+2+3` | 60 |
| `1+5` | 6 |
| `2+2+2` | 15 |
| `2+4` | 15 |
| `3+3` | 10 |

The first seven rows contain a singleton and total 162. A one-leg component
would require a nonzero future null external momentum to vanish, so all 162
are off support.

This leaves only 40 partitions in three profiles. Each can be classified
without evaluating a Feynman numerator.

### The fifteen `2+4` partitions

There are fifteen unordered two-label blocks. Nine pair one incoming with one
outgoing label. Their conservation equation is

\[
 p_i-k_a=0,
\]

and these are exactly the nine spectator cylinders. The other six pair two
labels with the same time orientation. A sum of two nonzero future null
momenta cannot vanish, so these blocks are impossible on the declared domain.

### The ten `3+3` partitions

One partition separates all three incoming from all three outgoing labels.
Its component momentum is `P` or `-P`, which is nonzero.

The other nine partitions have orientations `2+1` and `1+2`. A representative
conservation equation is

\[
 p_i+p_j=k_a.
\]

Squaring it gives

\[
 0=k_a^2=(p_i+p_j)^2=2p_i\mathbin{\cdot}p_j.
\]

Two future null momenta with zero inner product are collinear. This contradicts
the strictly positive same-side pair invariant in the hard domain. Thus none
of the ten `3+3` partitions is supported. This explicit one-plus-nine
orientation split replaces a mere topology count with the required
kinematic proof.

### The fifteen `2+2+2` partitions

There are fifteen perfect matchings of six labels. Six match every incoming
label with an outgoing label. They are precisely the six permutations

\[
 p_i=k_{\sigma(i)},\qquad \sigma\in S_3,
\]

and hence the removed forward diagonals. Each of the other nine matchings
contains a same-side pair and is impossible by the preceding positive-energy
argument.

The 162 singleton partitions, fifteen `2+4` partitions, ten `3+3` partitions,
and fifteen `2+2+2` partitions total all 202 disconnected possibilities.

## Incidence of the nine spectator cylinders

There are 36 unordered pairs of distinct cylinders. Exact enumeration gives
three cases:

| intersection type | count | disposition |
| --- | ---: | --- |
| `Delta_ia intersect Delta_ib`, `a!=b` | 9 | forces `k_a=k_b`, excluded |
| `Delta_ia intersect Delta_ja`, `i!=j` | 9 | forces `p_i=p_j`, excluded |
| `Delta_ia intersect Delta_jb`, `i!=j`, `a!=b` | 18 | conservation forces the remaining `p_l=k_c`, hence forward |

Thus distinct spectator cylinders do not intersect inside the hard
nonforward domain. In particular, “two spectators” is not a third generic
stratum.

## Why the census controls generalized-Born distributions

Each connected external component carries its own conservation distribution

\[
 \delta^{(4)}\!\left(\sum_{r\in S}\ell_r\right).
\]

Derivative vertices, delta-prime external measures, and the independent
external-mass differentiations used by the BT generalized Born prescription
can differentiate such distributions, but

\[
 \operatorname{supp}(\partial^\alpha T)
 \subseteq \operatorname{supp}(T).
\]

They cannot create support away from the classified loci. The theorem is
therefore about the full leading external-mass jet, not only about ordinary
pointwise on-shell amplitudes.

Vacuum components do not change the leading atlas. In normalized transition
probabilities they cancel in the usual vacuum normalization; before that
normalization any nontrivial vacuum component has positive coupling degree.
Likewise, an interacting two-point correction on a spectator line raises the
order. The leading cylinder contribution remains the order-`lambda^2`
four-point tree times the free identity spectator.

## Importing the two physical coefficients

The support proof is independent of the numerical coefficients. Only after
the two strata have been shown exhaustive are the predecessor results
imported.

In the fully rearranged bulk, a connected six-leg graph first occurs at
amplitude order `lambda^4`. The complete connected topology and species sum
and its global finite-time Hilbert--Schmidt realization were already
certified. Removing every disconnected support makes that connected column
the complete leading amplitude, so the click starts at order `lambda^8`.

On one spectator cylinder, the active connected four-leg tree starts at
amplitude order `lambda^2`. Its square-free external-mass jet has positive
complement-pairing norm 24, giving

\[
 \frac{d\sigma}{d\Omega}
 =\frac{3\lambda^4}{32\pi^2s}.
\]

The normalized spectator has unit overlap, and the declared transverse beam
normalization converts the active cross section into the displayed detector
probability. Possible order-`lambda` corrections to the dressed source are
retained conservatively in the `O(lambda^5)` probability remainder.

## What the theorem means physically

Within the finite-time BT scalar model, there is now a complete map of which
process supplies the first click coefficient at every local hard nonforward
distributional stratum:

```text
no unchanged particle       -> connected 3->3 amplitude lambda^4
                               -> probability lambda^8

exactly one unchanged label -> active 2->2 amplitude lambda^2
                               -> probability lambda^4

two unchanged labels        -> forces all three unchanged
                               -> removed forward diagonal
```

This is more than a pair of rational witnesses: all labelings and all 202
disconnected external connectivity types have been classified. It is still a
reduced scalar-model theorem, not a new spacetime dimension or a theorem
about the metric gravitational field.

## The next physical gate

One physical detector with finite momentum resolution need not resolve
whether an event lies exactly on a spectator cylinder or in its neighboring
bulk. On a common record the amplitudes have orders

\[
 A_{\rm spec}=\lambda^2S_2+\cdots,
 \qquad A_{\rm conn}=\lambda^4C_4+\cdots.
\]

Its probability therefore contains the new term

\[
 2\lambda^6\operatorname{Re}\langle S_2,C_4\rangle.
\]

The next gate is to thicken the nine disjoint cylinders by a physical
resolution profile, construct `S_2` and `C_4` on one common compact
finite-time packet domain, and decide whether this interference has a finite,
resolution-independent limit. A finite limit would produce one coherent
detector spanning the atlas. A failure would identify an exact scaling or
distribution-product obstruction. Forward and collinear supports remain a
separate later problem because they also require the unknown virtual/survival
coefficient.

## Claim boundary

The result does not establish one cross-stratum finite-resolution detector,
the order-`lambda^6` interference, the forward or collinear boundary, loop or
KLN completion, an all-order probability, an all-time Møller/LSZ/S operator,
general Eq. (19), gravity or metric BV--BRST transfer, or anything
`LORENTZIAN-CAUSAL`. It makes no literature-priority claim.

## Verification

The producer uses exact set-partition enumeration and orientation
classification. The independent verifier does not import it: it uses integer
partitions and the closed profile-count formula, a separate recursive perfect
matching enumeration, and an independent cylinder-incidence loop. Mutation
tests alter the census, kinematic exclusions, coefficients, incidence data,
and every important claim boundary.

Final scoped receipt, 2026-08-12, with every scientific command run
sequentially under `ulimit -v 500000`:

| Tier | Command | Result | Elapsed | Peak RSS |
| --- | --- | ---: | ---: | ---: |
| 0 | Python byte-compile; JSON parse of certificate, schema, work item, event | PASS, 3 modules and 4 JSON files | 0.03 s | 15,344 KB |
| 1 producer | exact partition and support classification | PASS, 33/33 | 0.03 s | 16,260 KB |
| 1 independent | integer-partition/matching verifier | PASS, 33/33 | 0.11 s | 23,512 KB |
| 1 focused | baseline plus eighteen decisive mutations | PASS, 19/19 | 0.11 s | 24,780 KB |
| papers | Paper 05, second PDF pass | PASS, 55 pages | 0.47 s | 50,764 KB |
| papers | Paper 06, second PDF pass | PASS, 52 pages | 0.49 s | 50,916 KB |
| planning | append-only fold | PASS, 1,497 nodes, zero invalid items and zero malformed events | 1.48 s | 13,580 KB |

No new overfull boxes were introduced. Paper 05 retains its pre-existing
boxes at lines 416--474, 544, 555--565, 949--955, 2983--2993, and 2994--2999.
Paper 06 retains its pre-existing boxes at lines 2327--2404 and 2412--2423.

Tier 2 is limited to the four content-addressed predecessor certificates: the
atlas changes no predecessor mathematical input or shared operator. Tier 3 is
not required because this result neither freezes the programme nor promotes a
Lorentzian, gravity, all-order, or all-time theorem.
