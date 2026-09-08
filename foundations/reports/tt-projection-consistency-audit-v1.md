# Projection follow-up: the serialized differential fails before positivity

The original 28 projection mismatches are symptoms of an inconsistent
serialized graph differential, not merely an unfortunate projection choice.
The exact result is `TT_PROJECTION_CONSISTENCY_AUDIT_V1`, tagged
`LOCAL-ALGEBRAIC`. It independently exhibits two nonzero blocks of the square
of the published differential. This invalidates using these particular bytes
as a verified complex for the full Green/Hadamard transfer. It does not refute
the abstract classical BRST construction or decide full physical positivity.

## A two-path sign witness

All indices below are the published zero-based global component indices;
entries are target row, source column. In the graph differential Q:

| Entry | Value | Source table |
| --- | --- | --- |
| Q[10,2] | derivative 1 | ENDPOINT_G_TO_M |
| Q[2,313] | -1/4 | GRAPH_Y_ID_SHARP_TO_ENDPOINT_G |
| Q[10,332] | +1/4 | GRAPH_Y_EQ_SHARP_TO_ENDPOINT_M |
| Q[332,313] | -derivative 1 | CONE_Y_ID_SHARP_TO_Y_EQ_SHARP |

These are all paths from `Y_Id_sharp[7]` (313) to `h_12` (10).
Consequently `(Q squared)[10,313] = -derivative 1/2`, whereas a differential
must square to zero. Each path has one constant factor and one first-order
factor. No interchange of two covariant derivatives is involved; under the
published parallel-coefficient interpretation this is an exact operator
witness, not a naive commuting-symbol calculation.

The earlier projection witness uses the same ingredients: `p[10,252]=-1/4`,
`Q[252,233]=derivative 1`, and `p[2,233]=+1/4`. Thus `pQ` gives -1/4 while
`Q_endpoint p` gives +1/4 at derivative 1. The inverse-shear ghost sign is
faithfully exported: the forward B cotangent partner has -1/4 and its inverse
has +1/4. It is not a JSON formatting or single copied-coefficient error.

The source builder obtains the cotangent partners using the serialized BV
pairing, then the graph builder removes attachment terms using formal
adjoint-chain identities. Those identities do not hold for these combined
component tables. In particular it declares `Asharp NcurvSharp = K Bsharp`
instead of verifying that equality coefficient by coefficient. The exact
obstruction is therefore at the interface between the imported primal maps,
suspended/pairing conventions and the formal cancellations. This audit does
not select a unique replacement convention for the entire classical export.

## A separate trace witness

The primal chain relation `N A = B C` itself has 16 first-order defects in the
exported coordinates. Its derivative-1 row `X_Id[6]` is

    (h_star00 - h_star11 - h_star22 - h_star33)/8.

The three other derivative directions give the corresponding identity rows.
Here N and C are first order and A and B are order zero. The existing graph
checker acknowledges 16 raw coefficients, then declares them reduced using
a pinned formal relation. Curvature/PBW derivative commutation cannot remove
this principal first-order defect.

It also appears directly in Q squared, from the endpoint equation rows to
`Y_Id`. For example the only contributing path to target 218, source 15,
derivative 1 is `Q[218,210]=(derivative 1)/3` and `Q[210,15]=3/8`. Their
product is `(derivative 1)/8`. The independent rail checks the full 16-entry
block as well as this readable witness.

## What the attempted repairs actually do

Changing the sign of the graph B cotangent attachment alone leaves 16 defects
in the first square block. Keeping the existing projection and inserting the
28 missing metric attachment coefficients dictated by `Q_endpoint p-pQ`
repairs both the original projection block and its associated square block.
For the example, the missing entry is `Q[10,233]=(derivative 1)/2`.

But this candidate leaves the separate 16-entry equation/identity square
block untouched. The candidate coefficients are recorded as an experiment;
no authoritative classical or quantum operator was changed. Changing only
the ghost projection to Gamma likewise cannot repair Q squared because it
does not change Q. A consistent invertible change of basis cannot turn a
nonzero Q squared into zero: `(S Q S^-1)^2=S Q^2 S^-1`.

## Consequence for Green/Hadamard transfer

The represented construction transfers an endpoint kernel by the graph
inclusion and projection (`i_end_graph lambda_endpoint p_end_graph`). Its
BRST justification requires a genuine differential and chain maps. The
published graph certificate still passes its old verifier, but these new
independent witnesses reject that prerequisite on the same input bytes.
The full-transfer acceptance flag in this audit is therefore false. This is
an audit disposition, not a silent rewrite of historical certificates, and
not a claim that every analytic property of the displayed kernels fails.

The local TT source factorization from the preceding report remains an exact
identity, and the reduced cutoff positivity result remains conditional in its
original model. Calling those sources cohomology classes in this particular
full exported complex now requires repairing the complex first. No all-energy
TT commutator or full Hadamard-state positivity conclusion follows here.

The next constructive task is to reconcile the primal trace map and suspended
adjoint conventions against the authoritative classical operators, regenerate
the actual conjugation without discarding nonzero attachment terms, and replay
nilpotency, both chain maps, contraction and cyclicity on the same coordinates.
Only after that gate passes should Green/Hadamard transfer and the normalized
physical tensor commutator be re-evaluated. More positivity calculations on the
current full export would not resolve this prerequisite.

## Reproduction and scope

```
python3 foundations/build_tt_projection_consistency_audit.py --check
PYTHONPATH=/tmp/tt-hadamard-check-deps python3 foundations/verify_tt_projection_consistency_audit.py
PYTHONPATH=/tmp/tt-hadamard-check-deps python3 -m unittest foundations.tests.test_tt_projection_consistency_audit
```

The producer uses sparse rational path composition. The independent verifier
imports no producer code and uses SymPy polynomial matrices, rejecting every
path containing two positive-order factors before multiplying. Mutation tests
reject changed witnesses, candidate coefficients, hashes and promoted claims.
Only the displayed composition-safe blocks are certified: exploratory raw
higher-order polynomial residuals are deliberately excluded because they
would require a genuine curved-jet composition law.

This user-directed foundations audit reads the resident teams' operators but
does not replace their data or alter their coordination state. The receipt
records exact commands, times, provenance, hashes and skipped-tier reasons.

CLOSE-OUT: OBSTRUCTED — current serialized differential fails an exact prerequisite for the full transfer; a projection-only repair is insufficient.
EVIDENCE: foundations/results/TT_PROJECTION_CONSISTENCY_AUDIT_V1.json
