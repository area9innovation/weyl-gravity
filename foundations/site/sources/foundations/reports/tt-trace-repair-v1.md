# Trace and ghost cleanup: a partial repair with a direct rejection gate

The two previously exhibited square blocks can both be repaired in an
explicit experiment: four Weyl-derivative terms repair the primal trace
relation, and the corresponding ghost attachment correction removes the
28-term metric defect. Twelve changes to the graph differential repair all
44 coefficients in those two blocks. This is **not yet a repaired full
complex**: full nilpotency, both chain-map identities and cyclicity
have not been supplied for the candidate, and no authoritative operator has
been replaced. The evidence is `TT_TRACE_REPAIR_V1`, tagged `LOCAL-ALGEBRAIC`.

## The missing Weyl derivative

Let D = N A - B C, using the imported tables. The Weyl row of C is

    C[29,:] = 2 (h_star00 - h_star11 - h_star22 - h_star33).

The complete 16-term defect factors as D = L C, where L has exactly four
nonzero coefficients:

| Target | Source | Coefficient |
| --- | --- | --- |
| X_Id[12] (144) | omega_star (29) | derivative 0 / 16 |
| X_Id[6] (138) | omega_star (29) | derivative 1 / 16 |
| X_Id[7] (139) | omega_star (29) | derivative 2 / 16 |
| X_Id[8] (140) | omega_star (29) | derivative 3 / 16 |

Thus B_new = B + L satisfies N A = B_new C on every coefficient, with A,
N and C unchanged. The repair requires allowing B to contain first
derivatives, whereas the published B is order zero. This identifies a
concrete missing term for the fixed A/N/C tables; it does not prove which
upstream convention or reduction should be changed in the authoritative
classical construction.

There is a short exact reason that changing only constant coefficients of A
cannot do the job. Sum row 144 of N's derivative-0 coefficient, row 138 of its
derivative-1 coefficient, row 139 of derivative 2 and row 140 of derivative 3.
Their sum is the zero row on all 40 equation components. Applying the same
sum to the required correction -D in source column 15 gives -1/2. Hence
N delta_A = -D has no constant solution, even allowing all 40 entries in that
column to vary. No floating-point rank decision is used for this obstruction.

## The ghost correction and its boundary

In the graph attachment from Y_Id_sharp to endpoint ghosts, change the four
vector entries from -1/4 to +1/4, and add -derivative_axis/16 from the matching
Y_Id_sharp component to the Weyl ghost. This is the negative of the corrected
Gamma off-diagonal map found in the earlier source-lift calculation. In the
primal attachment from endpoint identities to Y_Id, add -L.

The two audited blocks of Q_candidate squared now vanish exactly. These
changes were tested on a separate in-memory candidate; no classical or
quantum certificate has been overwritten. The candidate changes the ghost
and identity attachments, so it must be accompanied by consistently derived
projection/inclusion maps and suspension/pairing checks before acceptance.
A successful test of these two blocks alone is insufficient.

The corresponding inclusion and projection have also been constructed and
checked. Add L to the primal inclusion and replace the ghost projection by
Gamma (four vector sign changes and four Weyl derivative entries). Keeping H
unchanged gives, on the entire 386-row carrier,

    pi = identity_30,   Q_candidate H + H Q_candidate = identity_386 - ip,
    Hi = 0,            pH = 0.

Both independent rails verify these identities without composing two
positive-order factors. These are contraction identities for the candidate
operators; they do not turn those operators into a certified complex without
nilpotency and the chain-map identities. Cyclicity and the transported
suspension remain separate checks.

## Current acceptance check

Run this dependency-free command before relying on the present full export:

```
python3 foundations/check_current_strict386_transfer.py
```

It reads the actual graph coefficients and returns **exit 1, FAIL_CLOSED**,
with 28 metric and 16 trace defects for the unchanged published export.
This is the expected scientific rejection, not a crashed test. Unlike the
older historical checker, it does not replace the nonzero coefficients by a
formal chain relation. It tests only these necessary prerequisites; even an
export passing both blocks is labelled `SELECTED_PREREQUISITES_PASS_FULL_GATE_REQUIRED`
and is never marked as accepted for the full transfer.

The older checker and historical certificates remain available for
reproduction. Their PASS results are not current transfer acceptance.
The website now displays this distinction prominently, links to the direct
square audit and this repair experiment, and retains the conditional reduced
positivity result without promoting the full theory.

## Validation and next gate

```
python3 foundations/build_tt_trace_repair.py --check
PYTHONPATH=/tmp/tt-hadamard-check-deps python3 foundations/verify_tt_trace_repair.py
PYTHONPATH=/tmp/tt-hadamard-check-deps python3 -m unittest foundations.tests.test_tt_trace_repair
```

The sparse rational producer and independent polynomial-matrix verifier
check D = L C, the corrected square blocks, the full-carrier contraction
identities, and the left-null obstruction.
Mutation controls reject changed trace/ghost terms and promoted claims.
A separate standard-library gate directly checks the current graph, and a
candidate-fixture test ensures that fixing these blocks never becomes full
acceptance. Every product used here has an order-zero factor.

The next gate is the complete candidate complex, beginning with consistent
shear/projection/suspension transport and nilpotency on the remaining blocks.
That task needs the actual curved-jet composition law where two positive-order
operators meet; commuting symbols cannot certify the lower-order terms. Until
it passes, the full propagator and physical tensor commutator remain open.

CLOSE-OUT: SHORTFALL — both exhibited square blocks have an exact candidate repair and current acceptance fails closed; the full repaired complex remains unverified.
EVIDENCE: foundations/results/TT_TRACE_REPAIR_V1.json
