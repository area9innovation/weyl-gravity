# Fully rearranged BT q10 frame-typed loop ledger

Certificate:
REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_FRAME_TYPED_LOOP_LEDGER_V1

Tags: LOCAL-ALGEBRAIC, REDUCED-MODE.
Lifecycle: CLASSIFIED.

## Result

The previous q10 next gate mixed two action frames. Its four rows

\[
 V_4^3,\qquad V_3^2V_4^2,\qquad V_3^4V_4,\qquad V_3^6
\]

are the order-six vertex-count classes of the original perfect-square scalar
action

\[
 S_\phi=-\frac12\int
 [\Box\phi+\lambda(\partial\phi)^2]^2.
\]

The finite-time triangle computed by the successor certificate instead
belongs to the direct auxiliary action

\[
 S_{1,1}=\int d^4x\left[
 \partial\Omega\,\partial\Upsilon+
 {\lambda^2\over2}\Omega^2\Upsilon^2\right].
\]

This auxiliary action has no cubic vertex. Therefore there is no auxiliary
\(V_3^2V_4^2\) graph to compute after the auxiliary triangle. Adding the three
original-\(\phi\) families to that triangle would combine two reorganizations
of the same dynamics without the required field/projector transfer and would
double count.

The triangle coefficient and its finite-time affiliation remain valid. What
is superseded is only the untyped instruction about which graph to add next.

## Original scalar frame

Let \(V_3,V_4,I,E,L\) denote cubic vertices, quartic vertices, internal lines,
external lines and loops. The public vertices have coupling degrees one and
two. At \(E=6\) and coupling degree six,

\[
 3V_3+4V_4=2I+6,\qquad
 V_3+2V_4=6,\qquad
 L=I-(V_3+V_4)+1.
\]

The four nonnegative solutions are

| \(V_3\) | \(V_4\) | \(I\) | \(L\) |
|---:|---:|---:|---:|
| 0 | 3 | 3 | 1 |
| 2 | 2 | 4 | 1 |
| 4 | 1 | 5 | 1 |
| 6 | 0 | 6 | 1 |

This reproduces the old ledger exactly, but now types it as an
original-\(\phi\) statement. These are vertex-count classes, not complete
renormalized graph topologies. Their derivative numerators, counterterms,
external composite operators and generalized-projector derivatives remain
uncomputed at one loop.

## Direct auxiliary frame

In the auxiliary action every interaction vertex is quartic and carries
\(\lambda^2\). Consequently

\[
 4V=2I+6,\qquad L=I-V+1,\qquad 2V=6
\]

forces

\[
 V=I=3,\qquad L=1.
\]

The remaining classification is not by cubic/quartic count but by connected
three-vertex multigraph shape.

Represent a graph by a symmetric \(3\)-by-\(3\) adjacency matrix. An
off-diagonal entry counts edges between two vertices, while a diagonal entry
counts self-loops and contributes twice to the internal degree. Requiring
three edges, connected off-diagonal support and internal degree at most four
gives sixteen vertex-labeled matrices. Quotienting by \(S_3\) gives four
orbits:

| orbit | internal degrees | external legs | orbit size | loop subgraph |
|---|---|---|---:|---|
| triangle | \((2,2,2)\) | \((2,2,2)\) | 1 | none |
| double-edge bubble plus bridge | \((1,2,3)\) | \((1,2,3)\) | 6 | four-point bubble |
| tadpole at tree centre | \((1,1,4)\) | \((0,3,3)\) | 3 | two-point tadpole |
| tadpole at tree leaf | \((1,2,3)\) | \((1,2,3)\) | 6 | two-point tadpole |

The independent verifier obtains the same list from the classification of a
connected unicyclic three-vertex multigraph by cycle length:

- cycle length three gives the triangle;
- cycle length two gives the doubled edge plus one bridge;
- cycle length one gives a self-loop, with its tree attachment rooted either
  at the centre or at a leaf.

The four orbit sizes sum to sixteen.

## Renormalization and normal ordering

Every complete six-point graph has superficial degree

\[
 \omega=4L-2I=4-6=-2.
\]

There is therefore no primitive six-point counterterm. This does not remove
proper divergent subgraphs:

- the triangle has none and is UV finite;
- the bubble-with-bridge contains a degree-zero four-point bubble and requires
  the matched quartic coupling counterterm;
- the two tadpole graphs contain local two-point mass structures.

The repository has a selected normal-ordered, massless, unit-residue
auxiliary scheme. If that same scheme is declared for the fully rearranged
experiment, both tadpole orbits vanish. This is not a public-unique
prescription. Without it the tadpole and matched mass-counterterm ledger must
remain.

In the selected scheme the complete direct-auxiliary connected order-six
amplitude therefore has exactly two classes:

\[
 T_{6,\mathrm{aux}}=
 T_{6,\triangle}+T_{6,\mathrm{bubble\mbox{-}bridge}}.
\]

The first term is already computed at finite duration. The finite-time
renormalized four-point bubble entering the second term is also separately
computed, but its attachment to the third vertex over every labeled
three--three channel has not yet been assembled. This is the single remaining
connected dynamical class in the selected auxiliary scheme.

## Why the frames cannot be added

The public relation

\[
 S_\phi=R_\infty^\dagger S_{\Omega\Upsilon}R_{-\infty}
\]

states an interaction-picture equivalence. It does not identify a standard
scalar projector with a directly prepared auxiliary packet projector.
Transporting the scalar experiment requires

\[
 R_tP_\chi^{(\phi)}R_t^\dagger,
\]

which is exactly the missing Eq. (19) object. At loop order, a complete
transfer must also match composite external operators, local contact terms,
the functional Jacobian and counterterms.

The certified leading residue coincidence is useful but insufficient for
that transfer. It proves neither that the two packet experiments are the
same beyond leading order nor that their graph lists can be summed.

Thus there are now two honest routes:

1. **Direct auxiliary physical route:** compute the bubble-with-bridge, then
   assemble source/detector and normalization terms for auxiliary q10.
2. **Standard scalar route:** compute the original-\(\phi\) loop amplitude and
   the \(R_t\)/projector transfer. Eq. (19) remains load-bearing.

## Corrected next gate

Join the certified finite-time active four-point bubble, including its local
quartic counterterm, to one auxiliary tree vertex on every labeled
three--three channel. The result must retain the third-Dyson ordering,
compact packet bound, total-\(\kappa\) audit and tadpole scheme declaration.

Do not construct an auxiliary \(V_3^2V_4^2\) graph: the public auxiliary action
contains no such vertex.

Even after the connected auxiliary block is complete, q10 still requires the
full \(y_5\) norm, source/detector dressing, vacuum/survival normalization and
a total common-Born audit.

## Claim boundary

This classification does not establish:

- the bubble-with-bridge value or interference sign;
- a unique public normal-ordering or finite coupling scheme;
- loop-level equality of the scalar and auxiliary packet experiments;
- the complete original-\(\phi\) or auxiliary six-leg one-loop amplitude;
- complete q10 or finite-coupling positivity;
- Eq. (19), the standard scalar projector transfer, gravity/BV--BRST, or
  anything LORENTZIAN-CAUSAL.

## Verification receipt

All scientific Python and TeX commands ran sequentially below the 500 MB
virtual-memory cap.

- Tier 0 passes.  The three changed Python files compile, all four changed
  JSON files parse, the Draft-2020-12 schema is valid and rejects unexpected
  top-level properties through the focused mutation suite, and the scoped
  diff has no whitespace error.
- The exact producer passes `28/28` checks in `0.02 s` at `16096 KiB`.  The
  method-distinct verifier passes `45/45`, including strict schema validation,
  in `0.07 s` at `23832 KiB`.  The focused suite contains `36` tests: one
  positive certificate check and `35` adversarial mutations.  All pass in
  `0.080 s` (`0.15 s` enclosing wall time) at `24908 KiB`.
- The ten-command Tier-2 predecessor chain passes for the previous q10 object
  ledger, six-point shell-tree normalization, finite-time triangle,
  finite-time active loop, and normal-ordered spectator reduction.  The
  enclosing command times sum to `5.56 s`, with peak memory `79184 KiB`.
- Papers V and VI compile twice with no undefined citation or reference and no
  new overfull box.  Their PDFs are `80` and `69` pages and contain `746120`
  and `703606` bytes, with SHA-256
  `8b42c3d1762d90bbbcf0bcbf012fdfafe6069a24b4e639138734526abafbc488`
  and
  `cc6faed9259f4bc265d76d36953a5cdc43d0d55857094860d16f26b60de5d492`.
  The four-pass build took `2.12 s` at `51140 KiB`.  Paper V retains six
  known overfull boxes and Paper VI two.
- The append-only planning fold accepts `1577` nodes with zero invalid items
  and zero malformed events in `1.48 s` at `13900 KiB`.
- The advisory Science Forge shadow wrapper exits zero by design in `1.94 s`
  at `331736 KiB`, but its bridge audit remains fail-closed at the known
  toolchain/standard-library `E9118` mismatch.  Its read-only census finds
  `1628` certificates and `1409` verifier files.  This advisory exit is not
  theorem evidence.

Tier 3 is not required because this result corrects a `CLASSIFIED` next gate
without changing shared core algebra or promoting a coefficient, QME state,
residual transfer, freeze, release, or `LORENTZIAN-CAUSAL` lifecycle.  The
most recent full-suite receipt remains the fail-closed `3241`-test run in the
finite-time triangle report; its established `31` failures and `9` skips are
not counted as a pass.  The final certificate SHA-256 before staging is
`33fc45521d72ef46ddd902e4fa21655f9826ee105a3ce6059d5dfa1b17940107`.

CLOSE-OUT: DONE -- the q10 loop ledger is now action-frame typed; in the
selected direct auxiliary scheme the triangle is followed by one
bubble-with-bridge class, not by three nonexistent auxiliary cubic families.

EVIDENCE:
reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_FRAME_TYPED_LOOP_LEDGER_V1.json
