# Nonlinear homological-transfer bootstrap

Dependency tag: `LOCAL-ALGEBRAIC`

Result state: `ENGINE_READY_HT1_PARTIAL_INPUT_BLOCKED`

## Established

The new exact engine verifies a finite strong deformation retract and
transfers a suspended graded-symmetric BV vector field through arity three.
It separates the transferred ternary operation into the direct `q3` contact
term and the three `q2 s_cl q2` exchange trees.  Koszul symmetry, parity, SDR
side conditions, exact arithmetic, and the full/transferred `Q^2=0`
identities through arity three are executable checks.

HT1 now additionally composes the already-certified endpoint Taub map,
closed-cylinder BV--BFV suspension, all-energy moment map, and strict
centered HPL transfer.  This computes the residual ghost--matter and
ghost--ghost cubic charge blocks exactly.

The portable input schema requires full and residual graded bases, `q1`,
`q2`, `q3`, `iota_cl`, `pi_cl`, `s_cl`, the cyclic pairing, normalized
Weyl-square representative vectors, verification artifacts, and canonical
hashes.  It therefore cannot silently substitute class names or expected
answers for coefficient data.

## Not established

No complete conformal-gravity nonlinear tensor has yet passed the portable
input gate.  The partial residual cubic block does not compute the
matter--matter bracket sourced by the nonlinear Bach tensor.  It therefore
does not prove closure of the dynamical direction, prove that the
topological direction is central or inert, exclude sector re-entry by higher
brackets, or establish a complete interacting particle/deformation
interpretation.

The centered free statement must be tested through a particle-number
filtration once interactions are present.  It is not promoted merely by
reusing the free cohomology basis.  Likewise, no quantum operation is
transferred before `QME_RESTORED`.

## Programme

| Stage | Exact deliverable | Status |
|---|---|---|
| HT0 | Engine, convention, schema, blocker ledger | Ready |
| HT1 | Import classical Taylor data; compute `ell_2` | Partial residual ghost--matter block computed; matter--matter block blocked on export |
| HT2 | Compute `ell_3`; dynamical/topological mixing and centrality ledgers | Not computed |
| HT3 | Higher arities and particle-filtration spectral sequence | Not computed |
| HT4 | Cyclic minimal action and formal moduli/deformation interpretation | Not computed |
| HTQ | Transfer renormalized corrections | Blocked pending `QME_RESTORED` |

## Verification receipt

| Command | Elapsed seconds | Status | Tier |
|---|---:|---|---:|
| `python3 quantum-weyl/transfer/nonlinear_transfer_certificate.py --emit` | 0.03 | PASS | 1 |
| `python3 quantum-weyl/transfer/residual_cubic_certificate.py --emit` | 5.51 | PASS | 1 |
| `python3 -m unittest discover -s quantum-weyl/transfer/tests -v` | 5.61 | PASS (12 tests) | 1 |
| `python3 -m json.tool quantum-weyl/transfer/schema/nonlinear_classical_export.schema.json` | 0.02 | PASS | 0 |
| `python3 -m py_compile quantum-weyl/transfer/*.py quantum-weyl/transfer/tests/*.py` | 0.03 | PASS | 0 |
| `python3 quantum-weyl/transfer/nonlinear_transfer_certificate.py --check` | 0.03 | PASS | 1 |
| `git diff --check -- quantum-weyl/README.md quantum-weyl/transfer quantum-weyl/reports/nonlinear-homological-transfer-bootstrap.md` | <0.01 | PASS | 0 |

An optional Draft-2020-12 meta-schema check was attempted but was **not
run** because the environment does not provide the `jsonschema` module.  It
is not counted as a pass; deterministic JSON parsing did pass.

Tiers 2 and 3 were not run.  Their escalation criteria are not met: this
work adds an isolated engine and contract, changes no imported classical
mathematical input or shared algebra, and promotes no lifecycle or paper
claim.
