# Nonlinear homological-transfer bootstrap

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

Result state: `ENGINE_READY_HT1_RESIDUAL_AND_LOCAL_SEEDS_COMPUTED_INPUT_BLOCKED`

## Established

The new exact engine verifies a finite strong deformation retract and
transfers a suspended graded-symmetric BV vector field through arity three.
It separates the transferred ternary operation into the direct `q3` contact
term and the three `q2 s_cl q2` exchange trees.  Koszul symmetry, parity, SDR
side conditions, exact arithmetic, and the full/transferred `Q^2=0`
identities through arity three are executable checks.

HT1 now additionally composes the already-certified endpoint Taub map,
closed-cylinder BV--BFV suspension, all-energy moment map, and strict
centered HPL transfer.  The Hamiltonian vector field computes the selected
residual matter--matter Kuranishi output, ghost--matter action, ghost bracket,
and ghost-momentum coadjoint action exactly.

HT1b now begins the reverse comparison from the curvature side.  Two
independent mode-specialized mixed `B^(2)` channels retain exact local radial
densities.  Their exact integrals reproduce two raw-normalized entries of the
portable residual `q2` tensor.  This establishes real local lift seeds while
leaving the arbitrary-input Bach tensor and all ghost/antifield completions
fail-closed.

ND1 additionally computes the complete arity-two `D`-derivation defect on all
four selected residual `q2` blocks.  All 529,470 defect coefficients and all
`D`-weight violations vanish.  This excludes a cubic counterexample within
the selected residual BFV model, but does not construct the full interacting
Cartan homotopy because the support-local BV tensor and contraction remain
outside the import gate.

ND2 now supplies the exact consumer and correction/obstruction machinery for
that next gate.  A canonical rational local-expression AST, independent jet
checks, exact arity-two Cartan complex, admissibility subcomplex, boundary
solver, and normalized dual witness are executable.  Nonzero fixtures certify
both the primitive and obstruction branches and reject a deliberately broken
`D` action.  They do not supply a conformal-gravity coefficient: the physical
expression evaluator and support-local `q1/q2/D/iota_cl/pi_cl/s_cl` data remain
absent.

The waiting-time hardening now separates the stable ND2 engine from the
physical execution receipt.  A content-addressed evaluator registry and
three-artifact physical-run manifest reject unknown expression semantics,
source drift, incomplete contraction data, and missing admissibility policy.
The exact arity-two solver can partition by conserved additive labels and use
sparse rational elimination inside occupied blocks.

ND3 additionally implements the next Cartan recurrence.  It retains the
direct `[q3,iota_D]` and exchange `[q2,iota_D^(2)]` tensors separately, checks
the arity-three `Q^2`, Cartan, and `D` identities, and returns either an exact
`iota_D^(3)` or normalized obstruction witness.  This is an engine result;
physical `q3`, the physical arity-two correction, and quartic mixing remain
behind the input gate.

The support-local `q2` handoff is now executable rather than implicit.  Its
preflight requires a declared local-polydifferential support category, all
minimal field/ghost/antifield roles, complete output-row ledgers for `q1`,
`q2`, and the local `D` action, exact expression payloads, seven proof
receipts, and reproducible hashes.  It explicitly rejects finite-mode or
endpoint data as a support-local substitute.  The broader arity-three schema
continues to require `q3`, `iota_cl`, `pi_cl`, `s_cl`, the cyclic pairing, and
the normalized Weyl-square representatives for the later transfer gate.

## Not established

No complete conformal-gravity nonlinear tensor has yet passed the portable
input gate.  The selected residual bracket is certified through the endpoint
projection but the complete support-local nonlinear Bach/BV tensor has not
been serialized.  The result does not prove closure of the dynamical direction, prove that the
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
| HT1 | Import classical Taylor data; compute `ell_2` | Residual cubic bracket, local Bach seeds, selected residual `D`-derivation, and ND2 Cartan solver computed; complete support-local lift blocked on export |
| HT2 | Compute `ell_3`; dynamical/topological mixing and centrality ledgers | Arity-three Cartan recurrence engine ready; physical `q3` and mixing input blocked |
| HT3 | Higher arities and particle-filtration spectral sequence | Not computed |
| HT4 | Cyclic minimal action and formal moduli/deformation interpretation | Not computed |
| HTQ | Transfer renormalized corrections | Blocked pending `QME_RESTORED` |

## Verification receipt

| Command | Elapsed seconds | Status | Tier |
|---|---:|---|---:|
| `python3 quantum-weyl/transfer/local_bach_seed_certificate.py --emit` | 3.77 | PASS | 1 |
| `python3 quantum-weyl/transfer/local_bach_seed_direct_audit.py --emit --jobs 4` | 665.68 | PASS (8 direct probes) | 2 |
| `python3 quantum-weyl/transfer/d_derivation_certificate.py --emit` | 3.37 | PASS | 1 |
| `python3 quantum-weyl/classical_import/support_local_q2_contract_certificate.py --check` | 0.04 | PASS | 1 |
| `python3 quantum-weyl/classical_import/verify_snapshot.py --check` | 0.14 | PASS | 2 |
| `python3 -m unittest discover -s quantum-weyl/classical_import/tests -v` | 0.46 | PASS (28 tests) | 1 |
| Focused ND1 and nonlinear aggregate consumer tests | 8.08 | PASS (11 tests) | 2 |
| `python3 quantum-weyl/transfer/residual_cubic_certificate.py --check` | 46.20 | PASS | 2 |
| `python3 quantum-weyl/transfer/nonlinear_transfer_certificate.py --check` | 0.04 | PASS | 2 |
| `python3 -m unittest discover -s quantum-weyl/transfer/tests -v` | 47.76 | PASS (42 tests) | 2 |
| Compile, JSON/YAML parsing, and scoped `git diff --check` | 0.24 | PASS | 0 |
| Waiting hardening: ND1/ND2/ND3/aggregate certificate chain | 6.01 | PASS | 2 |
| Waiting hardening: complete transfer suite | 57.99 | PASS (85 tests) | 2 |
| Waiting hardening: classical import suite | 0.36 | PASS (28 tests) | 1 |

An optional Draft-2020-12 meta-schema check was attempted but was **not
run** because the environment does not provide the `jsonschema` module.  It
is not counted as a pass; deterministic JSON parsing did pass.

The nonlinear bootstrap regeneration is the affected Tier-2 consumer check.
Tier 3 was not run: this changes no imported classical mathematical input or
shared algebra and promotes no lifecycle or paper claim.
