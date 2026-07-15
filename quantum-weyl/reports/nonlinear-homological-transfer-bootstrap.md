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

The portable input schema requires full and residual graded bases, `q1`,
`q2`, `q3`, `iota_cl`, `pi_cl`, `s_cl`, the cyclic pairing, normalized
Weyl-square representative vectors, verification artifacts, and canonical
hashes.  It therefore cannot silently substitute class names or expected
answers for coefficient data.

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
| HT1 | Import classical Taylor data; compute `ell_2` | Residual cubic bracket, local Bach seeds, and selected residual `D`-derivation computed; complete support-local lift blocked on export |
| HT2 | Compute `ell_3`; dynamical/topological mixing and centrality ledgers | Not computed |
| HT3 | Higher arities and particle-filtration spectral sequence | Not computed |
| HT4 | Cyclic minimal action and formal moduli/deformation interpretation | Not computed |
| HTQ | Transfer renormalized corrections | Blocked pending `QME_RESTORED` |

## Verification receipt

| Command | Elapsed seconds | Status | Tier |
|---|---:|---|---:|
| `python3 quantum-weyl/transfer/local_bach_seed_certificate.py --emit` | 3.77 | PASS | 1 |
| `python3 quantum-weyl/transfer/local_bach_seed_direct_audit.py --emit --jobs 4` | 665.68 | PASS (8 direct probes) | 2 |
| `python3 quantum-weyl/transfer/d_derivation_certificate.py --emit` | 3.37 | PASS | 1 |
| `python3 quantum-weyl/transfer/residual_cubic_certificate.py --check` | 46.20 | PASS | 2 |
| `python3 quantum-weyl/transfer/nonlinear_transfer_certificate.py --check` | 0.04 | PASS | 2 |
| `python3 -m unittest discover -s quantum-weyl/transfer/tests -v` | 46.87 | PASS (42 tests) | 1 |
| Compile, JSON/YAML parsing, and scoped `git diff --check` | 0.24 | PASS | 0 |

An optional Draft-2020-12 meta-schema check was attempted but was **not
run** because the environment does not provide the `jsonschema` module.  It
is not counted as a pass; deterministic JSON parsing did pass.

The nonlinear bootstrap regeneration is the affected Tier-2 consumer check.
Tier 3 was not run: this changes no imported classical mathematical input or
shared algebra and promotes no lifecycle or paper claim.
