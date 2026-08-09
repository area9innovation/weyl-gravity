# Bateman--Turok external-virtuality jet obstruction

**Result:** `CLASSIFIED`

**Dependency:** `LOCAL-ALGEBRAIC`

**Certificate:**
[`REVERSE_PHYSICS_BT_OFFSHELL_JET_OBSTRUCTION_V1`](../certificates/REVERSE_PHYSICS_BT_OFFSHELL_JET_OBSTRUCTION_V1.json)

## Result

The first real-plus-virtual Bateman--Turok probability is **not defined by the
published on-shell amplitude results**. Their delta-prime external-state
prescription needs an off-shell virtuality jet:

- the one-loop `2→2` interference needs a four-variable jet; and
- the tree `2→3` real channel needs a five-variable jet.

The public action and Feynman rules are starting data from which the missing
jets can in principle be calculated; the existing on-shell results cannot
replace that calculation. This is an exact nondefinition result about that
on-shell shortcut, not a claim that the perfect-square theory is ambiguous or
inconsistent. A complete
off-shell Feynman calculation may provide the jets. It would also have to show
that counterterms, interpolating fields, and projectors transform together so
the final projected probability is independent of off-shell convention.

## Why an on-shell amplitude is insufficient

Bateman--Turok define an amputated **off-shell** amplitude in their Eq. (9).
For `2→2`, their Eq. (13) differentiates the squared amplitude and
kinematic factor once with respect to each independent external mass squared,
then sets all four masses to zero. They emphasize that the squared amplitude,
not the amplitude, is put on shell. Their general `n`-particle projection in
Eq. (18) contains one delta-prime Wightman factor per external leg.

Let

\[
x_i=m_i^2,
\qquad
D_n=\left.\frac{\partial^n}
 {\partial x_1\cdots\partial x_n}\right|_{x=0}.
\]

Because each variable is differentiated only once, the exact finite carrier is

\[
J_n=\mathbb Q[x_1,\ldots,x_n]/(x_1^2,\ldots,x_n^2).
\]

It has one square-free basis element `x_S` for every subset `S`, hence
dimension `2^n`. The projector `D_n` selects the coefficient of
`X = x_1 ... x_n`.

The ordinary on-shell map remembers only the constant coefficient. It loses
information that the probability sees. The sharp witness is

\[
M_a=1+aX.
\]

For every rational `a`,

\[
M_a(0)=1=M_0(0),
\qquad
D_n(M_a^\dagger M_a)=2a,
\qquad
D_n(M_0^\dagger M_0)=0.
\]

The `a^2 X^2` term vanishes in `J_n`. Thus the projected probability does
not descend to the equivalence relation “same on-shell amplitude.”

With an analytic kinematic factor `K`, the same mutation changes the result
by

\[
2K(0)\operatorname{Re}(M(0)^\dagger a).
\]

The certificate uses the exact normalization `K(0)=M(0)=1`. It does not
assume that this fixture is the physical PS amplitude; it proves that an
on-shell value alone cannot determine the functional used by the BT rule.

## Every jet slot can matter

The result is not confined to the top monomial. For every subset `S`, let
`S^c` be its complement. Then

\[
D_n\bigl((x_S+x_{S^c})^2\bigr)=2.
\]

Consequently every square-free coefficient can pair with a complementary
coefficient in the squared amplitude. The producer exhausts all 16 complement
pairs for `n=4` and all 32 for `n=5`. The independent verifier recomputes
the top coefficient by subset convolution rather than importing the producer's
jet multiplication.

This gives a useful size estimate for the analytic project:

| channel | external legs | generic square-free amplitude slots |
|---|---:|---:|
| virtual `2→2` | 4 | 16 |
| real `2→3` | 5 | 32 |

These are coefficient slots before imposing momentum conservation, crossing,
shift Ward identities, or the perfect-square coupling relation. Those
relations may reduce the actual calculation, but the reduction must be
derived; setting all external virtualities to zero at the start is not valid.

## The first NLO pair

The perfect-square interactions contain a cubic vertex of order `λ`
and a quartic vertex of order `λ²`. Therefore:

\[
M^{(0)}_{2\to2}=O(\lambda^2),\qquad
M^{(1)}_{2\to2}=O(\lambda^4),\qquad
M^{(0)}_{2\to3}=O(\lambda^3).
\]

At probability order `λ⁶`, the first pair is schematically

\[
D_4\!\left[K_4\,2\operatorname{Re}
  \bigl((M^{(0)}_{2\to2})^\dagger M^{(1)}_{2\to2}\bigr)\right]
\; + \;
D_5\!\left[K_5\,|M^{(0)}_{2\to3}|^2\right].
\]

The five-derivative statement is an inference from BT Eq. (18): two incoming
and three outgoing delta-prime Wightman factors. The Letter only prints the
explicit phase-space reduction for `2→2`, so no five-body normalization is
asserted here.

The certificate uses independent exact ambiguity parameters in the two
channels:

\[
a=\frac37,\qquad b=\frac5{11},
\]

which shift the normalized virtual and real functionals by `6/7` and
`10/11`. Their sum is `136/77`. This is a non-vacuity fixture showing that
on-shell agreement in both channels does not force agreement of the inclusive
sum. These are not physical NLO coefficients.

## Literature boundary as of 2026-08-09

The primary-source audit found:

1. [Bateman--Turok v1](https://arxiv.org/abs/2607.00096v1) supplies the
   off-shell Born prescription, the tree `2→2` Feynman rules, and the
   general projection. It says the beyond-tree obstacle is collinear infrared
   structure requiring regulation and resummation.
2. [Holdom 2023](https://arxiv.org/abs/2303.06723) supplies one-loop
   renormalization for the general shift-symmetric four-derivative scalar and
   selected optical-theorem calculations.
3. [Holdom 2024](https://arxiv.org/abs/2402.09223) supplies high-energy
   two-body optical-theorem and differential-cross-section results. It does
   not supply the BT four- and five-leg multi-affine jets.
4. Bateman--Turok's detailed positivity paper and the
   Anderson--Bateman--Herzog--Turok renormalization paper are still references
   19 and 25 marked “to appear” in v1. No public primary source for their
   claimed absence of PS infrared loop divergences was located.

This reconciles statements that can otherwise look contradictory. “No IR
loop divergences” concerns loop integrals; the Letter separately says massless
collinear divergences affect asymptotic states. Neither statement supplies a
regulated real-emission jet or a real--virtual process map.

## Scheme and field-redefinition gate

Off-shell amplitudes depend on choices that ordinary on-shell S-matrix elements
do not. Therefore the next construction cannot simply choose an arbitrary
off-shell continuation of a published on-shell answer. It needs one of the
following equivalent kinds of receipt:

- a fixed renormalized interpolating field and external-state projector, with
  all counterterms and jets computed in that convention; or
- a proof that a change of field/renormalization convention transforms the
  amplitude and projection together while leaving the differentiated
  probability invariant.

The certificate does **not** prove that this invariance fails. It identifies
it as a necessary object that the public argument has not yet provided.

## What moved and what did not

| object | state |
|---|---|
| necessity of a square-free external-virtuality jet | `PROVED` |
| descent to on-shell amplitude data | `DISPROVED` |
| finite Eq. (20) charge-radical closure | `PROVED` by predecessor |
| four-leg virtual NLO jet | `NOT_COMPUTED` |
| five-leg real NLO jet | `NOT_COMPUTED` |
| common infrared regulator | `NOT_SELECTED` |
| real--virtual cancellation | `NOT_COMPUTED` |
| physical NLO process map | `NOT_CONSTRUCTED` |
| underlying PS theory ambiguous | `NOT_ESTABLISHED` |
| positivity beyond tree level | `NOT_ESTABLISHED` |

The next analytic gate is now precise: generate the complete tree `2→3`
amplitude without imposing `x_i=0`, reduce it only to its 32-slot
square-free jet using momentum conservation and Ward identities, and classify
its soft/collinear faces on a regulator that can also be used for the
renormalized four-leg loop jet.

## Claim boundary

This certificate does not establish:

- a loop or `2→3` amplitude, KLN theorem, regulator cancellation, or
  finite cross section;
- that the PS theory itself is ambiguous or inconsistent;
- failure of scheme/field-redefinition invariance in a completed BT
  construction;
- existence or trace-class control of the inclusive process operator;
- positivity beyond tree level;
- a tensor/BRST gravitational lift; or
- anything `LORENTZIAN-CAUSAL`.

It also makes no literature-priority claim for the elementary jet lemma.

## Verification

```text
python3 reverse_physics/bt_offshell_jet_obstruction.py --check
python3 reverse_physics/verify_bt_offshell_jet_obstruction.py
python3 -m unittest -v reverse_physics.tests.test_bt_offshell_jet_obstruction
```

The verifier uses complement/subset convolution instead of the producer's
truncated-polynomial multiplication. Mutation tests zero the recorded virtual
ambiguity and falsely promote the physical process map; both must be rejected.

Final scoped receipt (wall time measured with `/usr/bin/time`, 2026-08-09):

| Tier | Command | Time | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile` on producer, verifier, and test | 0.04 s | PASS |
| 0 | `python3 -m json.tool` on certificate and schema | 0.08 s | PASS |
| 1 | `python3 reverse_physics/bt_offshell_jet_obstruction.py --check` | 0.04 s | PASS, 11/11 |
| 1 independent | `python3 reverse_physics/verify_bt_offshell_jet_obstruction.py` | 0.14 s | PASS, 10/10 |
| 1 plus pure-Python consumers | `python3 -m unittest -v reverse_physics.tests.test_bt_offshell_jet_obstruction reverse_physics.tests.test_bt_inclusive_radical_closure reverse_physics.tests.test_bt_ir_regulator_trilemma` | 1.11 s | PASS, 31/31 |
| 1 SymPy consumer | `/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_born_trace` | 0.67 s | PASS, 23/23 |

The first combined consumer attempt under system Python is recorded as an
**error**, not a pass: `test_bt_born_trace` could not import `sympy`. Re-running
that consumer under the repository's documented Mise Python passed 23/23. The
two successful commands above therefore cover 54 tests without silently
turning the unavailable dependency into a skip.

The advisory command `env -u SF_PROGRAM ci/science-forge-shadow.sh` completed
in 3.84 s with exit 0 but is **not** recorded as a pass. It repeated the
repository-wide Forge binary/stdlib hash mismatch, the bridge audit's stale
`bp2transformer` verifier path under a Python without `sympy`, and corpus
baseline drift (1490 certificates versus the 2026-07-19 baseline of 976).
These findings do not promote or falsify this scoped result.

Tier 2 was not run because the new certificate consumes unchanged,
content-addressed inputs and changes no imported mathematical object or shared
operator; the direct predecessor consumers ran at Tier 1. Tier 3 was not run
because this is not a freeze, lifecycle promotion, shared-core change, release,
or explicit full-suite request. Skipped higher tiers are not reported as
passes.

CLOSE-OUT: DONE -- the public-data/non-descent question is classified; the
Bateman loop-completion project remains active at the explicit four-plus-five
leg jet and common-regulator gate.

SUCCESSOR CHECKPOINT (2026-08-09):
`REVERSE_PHYSICS_BT_FIVE_POINT_TREE_JET_V1` constructs the complete 25-graph
tree `2→3` amplitude jet. All degree-zero, one, and two virtuality slots vanish
identically, so the pointwise fivefold projector of the squared amplitude is
zero. The nonzero degree-three coefficients have simple soft/collinear poles;
therefore the physical five-body phase-space distribution and the order of
regulator removal remain open rather than being silently identified with this
pointwise result.

EVIDENCE: `reverse_physics/certificates/REVERSE_PHYSICS_BT_OFFSHELL_JET_OBSTRUCTION_V1.json`
