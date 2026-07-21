PULLED by agent quantum-qme-1 — stream quantum-qme — lease exclusive (acquired 2026-07-21T01:30:36Z, expires 2026-07-21T05:30:36Z)

WORK PACKAGE sf:program/work/quantum-scalar-flat-berger-vector-schur-low-blocks  (state: ACTIVE, owner: quantum-qme)

## Objective
Derive the correctly normalized Fourier/SU(2) vector pencil and the first exact coupled longitudinal Schur blocks on the selected scalar-flat Berger datum, supplying a domain-specific receiver and independent holdouts for the Forge global-spectral implementation.

## Stop condition (what DONE means)
Import SCALAR_FLAT_BERGER_SCHUR_SURROGATE_OBSTRUCTION and GENERIC_BACKGROUND_GHOST_LONGITUDINAL_SCHUR_RESUMMATION by hash.  Fix one convention-explicit left/right SU(2) basis, orthonormal coframe, vector one-form basis, measure and adjoint.  Derive d_jmn, delta_jmn, the full finite vector block A_jmn(t)=F_jmn+tW and S_L,jmn(t)=(2/3)I+(1/3)delta_jmn A_jmn(t)^(-1)d_jmn for every block with 2j<=2 and |n|<=1, retaining rational/algebraic t and every denominator.  Identify scalar and vector zero modes, common primed domains, matched zero-pole cancellations and exceptional denominator loci.  Independently reconstruct the j=1/2 blocks from explicit Pauli matrices and the j=1 blocks from a separately generated representation, and verify the scalar restriction and first derivative -64/81.  Export a strict block schema, normalization crosswalk and low-mode oracle bundle for the Forge request.  If the vector operator F is not uniquely defined by frozen inputs, prove the first missing convention or gauge-fixed Hessian component rather than guessing it.

## Current gate
correct coupled-vector Schur low-block theorem and Forge receiver

## Forbidden
no scalar one-inverse surrogate; no diagonal scalar eigenvalue substituted for the vector pencil; no unprimed inverse at a zero mode; no numerical diagonalization used as exact block data; no extrapolation from low j to all representations; no finite determinant, five-function, QME, Lorentzian, Hadamard, state or particle promotion

## Activates (downstream this unlocks)
- the exact high-mode coercivity and priming theorem for the true vector pencil
- a content-addressed low-mode oracle for sf:forge-request/scalar-flat-berger-coupled-vector-schur-blocks

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["quantum-weyl/spectral/","quantum-weyl/reports/","quantum-weyl/transfer/receipts/","reports/","notes/d-quotient-quantum-team-brief.md","planning/forge-requests/"]
- `resource_hint`: "PROOF-FIRST GLOBAL-SPECTRAL RESTART.  Compute small exact vector blocks before any infinite representation sum; use Forge Wigner/harmonic kernels only as one rail and preserve an independently generated holdout."
- `notes`: ["The preceding attempt usefully failed because its scalar surrogate had the wrong principal symbol; this item starts from the frozen normalized Schur factor instead.","This is domain physics input for the math backend, not a duplicate implementation of the complete M21/M23 spectral machinery."]
- `input_commit`: "0200fc87b"
- `stream`: "quantum-qme"

## Standing constraints
# Standing constraints for programme agents (included in every work package)

- This tree is the READ-authority. Follow the repo AGENTS.md exactly:
  shared-master discipline (explicit pathspec, never `git add .`, never
  force-push, preserve other teams' dirty files), the quantum claim boundary
  (LOCAL-ALGEBRAIC / EUCLIDEAN-SPECTRAL / REDUCED-MODE / LORENTZIAN-CAUSAL tags;
  never promote one implicitly), exact rational/algebraic arithmetic in every
  canonical form/rank/cocycle test, and the receipts requirement.
- Follow this repository's shared-master Git discipline. At the next coherent
  checkpoint whose changed paths already exist in the declared current commit,
  run `s-f work check --item <id> --agent <you>` and confirm that only
  report∩allowed paths would stage and every unrelated dirty path is left
  alone. Until
  `sf:forge-request/bug-science-forge-precommit-report-new-files` lands and its
  new-file pilot passes, packages that create new files use the manual
  explicit-path audit/commit/push fallback and then report the resulting commit
  through `s-f`; never bypass containment with a fake SHA. After that gate, prefer
  `s-f work commit --item <id> --agent <you> --push --now <ISO>`, whose isolated
  index and prospective-tree verifier mechanize the same discipline. Do NOT
  edit generated views, IR graphs, gate/receipt files, or another team's
  certificates, snapshots, or history.
- Research leases do not edit `notes/universe-building-roadmap.md` or maintain
  lifecycle prose in a shared planning document.  The certificate, report,
  atlas fragment, `s-f work report`, and append-only close-out event are the
  complete team handoff; the coordinator integrates those committed handoffs
  into the roadmap in a separate scoped pass.  A legacy `allowed_paths` entry
  for the roadmap is not authorization to touch it unless the work item's
  objective explicitly is roadmap integration.
- Honor the work item's `stop_condition`, `current_gate`, and `forbid`
  LITERALLY. If the main construction fails, the exact first obstruction is the
  deliverable — do not spend the run polishing prose around an unclosed gate.
- The five Science Forge laws are MANDATORY: fail closed (a skip/timeout is
  never a pass); append-only history (repairs and transitions are new events,
  never edits); independent rails (re-running a producer is reproduction, not
  verification — agreement across independent implementations is the evidence);
  honest boundaries (does_not_establish is not a claim; never promote past the
  evidence); exact and numeric are distinct types with distinct lifecycle labels.
- Test tiers per AGENTS.md: run the smallest deterministic suite that can
  falsify the changed claim (Tier 0/1 always; Tier 2 on shared-input change;
  Tier 3 only for a freeze/tag/release). Record exact commands, elapsed time,
  pass/fail, and which higher tiers were skipped with the criterion.
- The Science Forge substrate (certlab audits, three-rail recomputation, the
  evidence-graph impact queries) lives in the `tango/forge` repo under
  `forge/tools/{science-forge,certlab,claimlang,physics-*}`. It runs READ-ONLY
  over this tree; the advisory CI rail is `ci/science-forge-shadow.sh`.
- Conflux is OPT-IN, not implied by Science Forge adoption. Use it only when the
  work item explicitly enables a consumer-specific Conflux gate. Read
  `planning/SCIENCE-FORGE-ADOPTION.md` and the Conflux README, discovery-sweep,
  provenance, and structure-finding-thesis documents named there. If an
  importer, rule kind, independent replay, resource control, or CLI seam is
  missing, file a committed `work-v0` request under `planning/forge-requests/`
  following its README; do not patch Tango from a physics ticket or negotiate
  an unrecorded workaround. Conflux candidates never promote physics claims.
- Report at the end: deliverables, gate results, deviations from the work item,
  and anything `stop_condition` required that you could not meet (honest
  shortfall, never silent narrowing).

## Orientation
Read tools/science-forge/views/agent_context.md, docs/structure-finding-thesis.md, docs/math-roadmap.md, and lib/math/COMPLETENESS.md before starting.
