# BT tagged-spectator physical packet probability

Certificate:
`REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

The first overlap stratum omitted by the fully rearranged detector is now
closed at leading order. There is a nonempty class of hard nonforward
three-particle detectors with exactly one tagged unchanged spectator. On this
stratum the complete leading transition is not the connected six-point tree:
it is the physical four-point BT tree on the active pair, tensored with the
identity on the spectator.

For active pair invariant `s`, angular acceptance `DeltaOmega`, and the
declared BT transverse beam area `Area`, the complete leading click is

\[
 \boxed{
 q_{\rm tag}=
 \frac{3\lambda^4}{32\pi^2s}\,
 \frac{\Delta\Omega}{\mathrm{Area}}+O(\lambda^5).
 }
\]

At the exact rational witness `s=64/25`, this becomes

\[
 \boxed{
 q_{\rm tag}=
 \frac{75\lambda^4}{2048\pi^2}\,
 \frac{\Delta\Omega}{\mathrm{Area}}+O(\lambda^5).
 }
\]

The spectator packet is normalized and appears unchanged in the detector, so
its identity overlap is exactly one. The active detector is nonforward, so the
identity and unknown forward/survival graph do not enter the leading click.

This is a complete leading physical coefficient on a selected detector
stratum. It is not an all-order probability or all-time scattering theorem.

## Exact detector witness

Use the rational rotation about the `x` axis with

\[
 \cos\alpha=31/481,\qquad \sin\alpha=480/481.
\]

The incoming momenta are

\[
\begin{split}
 p_0&=(6/5,6/5,0,0),\\
 p_1&=(1,-3/5,124/2405,384/481),\\
 p_2&=(1,-3/5,-124/2405,-384/481),
\end{split}
\]

and the outgoing momenta are

\[
\begin{split}
 k_0&=p_0,\\
 k_1&=(1,-3/5,-384/481,124/2405),\\
 k_2&=(1,-3/5,384/481,-124/2405).
\end{split}
\]

All six are future null and both totals are `(16/5,0,0,0)`. The active pair
has

\[
 s=(p_1+p_2)^2=64/25,\qquad
 t=(p_1-k_1)^2=-32/25,\qquad
 u=(p_1-k_2)^2=-32/25.
\]

It is therefore exactly at a hard ninety-degree two-to-two scattering point,
not at a forward, backward, soft, or collinear boundary.

Put all external momenta in incoming convention,

\[
 \ell=(p_0,p_1,p_2,-k_0,-k_1,-k_2).
\]

Exact rational enumeration of every subset of sizes one, two, and three gives

\[
 \left\{S:\sum_{i\in S}\ell_i=0\right\}
 =\begin{cases}
 \varnothing,&|S|=1,\\
 \{\{0,3\}\},&|S|=2,\\
 \varnothing,&|S|=3.
 \end{cases}
\]

The minimum positive Euclidean squares of these component sums are

\[
 2,\qquad 32/25,\qquad 2
\]

for sizes one, two, and three. Thus the tagged spectator is the only component
delta reached by the detector, and every competing support remains separated
by a positive exact margin. Continuity supplies compact neighborhoods on the
smooth `p0=k0` spectator cylinder with the same property.

## Exhaustive partition and order classification

There are `B6=203` set partitions of the six labels. A disconnected graph is
supported only when every connected component has its own conserved external
momentum. At the displayed witness, exactly two partitions pass this support
test:

\[
 \{0,1,2,3,4,5\}
\]

and

\[
 \{0,3\}\mid\{1,2,4,5\}.
\]

The first is the connected six-leg partition. The second is the tagged
identity spectator times an active four-leg component. Every other one of the
202 disconnected partitions misses at least one component delta.

The perturbative orders then decide which supported partition leads:

- the `2+2+2` identity partition is absent because only one two-leg delta is
  supported;
- a one-cubic order-`lambda` contribution cannot cover the six labels without
  a forbidden singleton or unsupported component;
- at order `lambda^2`, the unique contribution is the connected four-point
  tree on the active pair times the spectator identity;
- the connected six-point tree and the active one-loop four-point correction
  both start at order `lambda^4` in amplitude.

Consequently

\[
 P_Y(U-I)P_X=\lambda^2
 (I_{\rm spectator}\otimes A_{4,\rm active})+O(\lambda^3).
\]

An unknown order-`lambda` correction to the dressed scalar preparation can
enter this amplitude at order `lambda^3`, so the conservative probability
remainder is `O(lambda^5)`.

## Positive four-point jet factorization

The complete reduced four-point tree imported from the certified physical
factorization is

\[
 M_4=4\lambda^2H,\qquad
 H^{(2)}=\frac12\sum_{i<j}x_ix_j.
\]

Hence its square-free mass-jet vector is

\[
 r_4=2(e_{12}+e_{13}+e_{14}+e_{23}+e_{24}+e_{34}).
\]

The four delta-prime external legs pair a two-subset with its complementary
two-subset. Let `J4 e_ij=e_complement(ij)`. This metric has inertia `(3,3)`,
but `r4` is entirely in its positive complement-symmetric eigenspace and

\[
 r_4^\sharp r_4=24.
\]

Equivalently, direct expansion gives

\[
 \left.\partial_{x_1}\partial_{x_2}\partial_{x_3}\partial_{x_4}
 |M_4|^2\right|_{x=0}=24\lambda^4.
\]

Multiplication by the massless two-body phase density
`1/(256*pi^2*s)` yields

\[
 \frac{d\sigma}{d\Omega}
 =\frac{3\lambda^4}{32\pi^2s},
\]

exactly reproducing the independently certified public BT Born coefficient.
The equality is therefore an operator-jet factorization check, not an imported
cross-section number used as its own proof.

## What this adds to the physical route

The hard nonforward three-particle detector now has two locally complete
strata:

1. with no unchanged spectator, the fully rearranged theorem gives a complete
   leading `3 -> 3` probability at order `lambda^8`;
2. with exactly one tagged spectator, this theorem gives a complete leading
   active `2 -> 2` probability at order `lambda^4`.

Two unchanged labeled particles force the third to be unchanged by total
momentum conservation, so there is no separate generic two-spectator
nonforward stratum. What remains is not another generic disconnected graph:
it is the identity/forward diagonal, the collinear `3+3` support, and detectors
whose finite resolution crosses between strata.

This result does not yet construct one coherent detector crossing the
spectator cylinder and fully rearranged bulk. Such a detector can contain
interference between the order-`lambda^2` spectator column and the
order-`lambda^4` connected column at probability order `lambda^6`. That is the
next calculational gate.

## Claim boundary

The result is finite-order reduced-model physics. It does not establish the
identity/forward coefficient, collinear three-point sectors, loop/KLN
completion, an exact all-order probability, an all-time Møller/LSZ/S operator,
general Eq. (19), gravity or metric BV--BRST transfer, or anything
`LORENTZIAN-CAUSAL`.

## Verification

The producer uses exact `Fraction` arithmetic to reconstruct the momenta,
enumerate all 203 set partitions, classify their momentum support, and compute
the complement-pairing jet norm. The independent verifier uses the Stirling
recurrence for `B6` and direct monomial expansion of
`(2 sum_(i<j) x_i x_j)^2`; it does not import the producer. Thirteen tests include
twelve decisive mutations of support, order, coefficient, normalization, scope, and claim
boundaries.

Final scoped receipt, 2026-08-12, with every scientific command run
sequentially under `ulimit -v 500000`:

| Tier | Command | Result | Elapsed | Peak RSS |
|---|---|---:|---:|---:|
| 0 | Python byte-compile; JSON parse of certificate, schema, work item, event | PASS | below 0.2 s | below 25 MB |
| 1 producer | exact support, partition, order, and jet calculation | PASS, 34/34 | 0.04 s | 16,760 KB |
| 1 independent | Stirling/direct-monomial verifier | PASS, 26/26 | 0.08 s | 23,440 KB |
| 1 focused | baseline plus twelve decisive mutations | PASS, 13/13 | 0.11 s | 24,216 KB |
| papers | Paper 05, second PDF pass | PASS, 55 pages | 0.48 s | 50,572 KB |
| papers | Paper 06, second PDF pass | PASS, 52 pages | 0.49 s | 51,000 KB |
| planning | append-only fold | PASS, 1,495 nodes, zero invalid items and zero malformed events | 1.48 s | 13,520 KB |

No new overfull boxes were introduced. Paper 05 retains its pre-existing
overfull boxes at lines 416--474, 544, 555--565, 949--955, 2983--2993, and
2994--2999; Paper 06 retains its pre-existing boxes at lines 2327--2404 and
2412--2423.

The advisory Science Forge shadow script exited zero in 3.96 s at 59,672 KB,
but its bridge audit is explicitly **not** recorded as a pass: the Go helper
could not reserve page-summary virtual memory under the cap. Its independent
coverage census completed and reported the already known baseline drift (1,587
certificates versus the 2026-07-19 baseline of 976). The native cached `sfc`
planning fold above passed separately.

Tier 2 is satisfied by unchanged content-addressed predecessor certificates
plus the direct input-hash and predecessor-pass checks on both rails. Tier 3
was not run because this is a new reduced-mode leading coefficient, not a
freeze, release, shared-core algebra change, QME promotion, or Lorentzian
claim. A skipped higher tier and the advisory bridge failure are not passes.

Commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_tagged_spectator_physical_packet_probability.py --write --check
ulimit -v 500000; python3 reverse_physics/verify_bt_tagged_spectator_physical_packet_probability.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_tagged_spectator_physical_packet_probability
```

CLOSE-OUT: DONE — the exact support theorem, complete order classification,
positive four-point jet factorization, physical probability coefficient,
independent verifier, mutation suite, and paper updates close the selected
tagged-spectator leading transition.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1.json`
