PULLED by agent quantum-qme-1 — stream quantum-qme — lease exclusive (acquired 2026-07-20T20:26:18Z, expires 2026-07-21T00:26:18Z)

WORK PACKAGE sf:program/work/quantum-scalar-flat-berger-primed-schur-spectral-measure  (state: ACTIVE, owner: quantum-qme)

## Objective
Construct or sharply obstruct the complete primed Schur resolvent and insertion spectral measure on the selected compact scalar-flat Euclidean Berger datum, thereby supplying the first actual global input to the parameterized five-form-factor theorem.

## Stop condition (what DONE means)
Import BACKGROUND_SPECIFIC_FIVE_FORM_FACTOR_SPECTRAL_REALIZATION_SHORTFALL and the exact datum M=S1_(2pi) x SU(2), g=dtheta^2+sigma1^2+sigma2^2+4sigma3^2 by hashes.  Derive the Fourier-n/SU(2)-representation decomposition of the scalar and longitudinal-vector domains, the exact finite block matrices for Delta_0, delta W d and S_L=I+(1/3)Delta_0^{-1}delta W d, normalized primed projectors, all zero and matched zero-pole factors, and the self-adjoint/Agmon-ray disposition.  Construct the block resolvent and the metric-insertion eigenprojector matrix elements required through third variation.  Prove uniform high-mode estimates strong enough for the declared relative traces and det3 tail; evaluate every finite row exactly where summable and otherwise with certified interval tails.  Feed the resulting ten labelled quotient coordinates into the frozen affine-family receiver and independently verify scale derivatives, local Wodzicki residues, priming, orientation and truncation bounds.  If the complete measure cannot be constructed, prove the first representation block, analytic-continuation or uniform-tail obstruction and split only that smaller missing theorem.

## Current gate
content-addressed scalar-flat Berger primed Schur spectral measure and finite five-form-factor specialization

## Forbidden
no local heat-kernel or Wodzicki coefficient substituted for a finite global trace; no flat-T4, round-S4 or S2xS2 interpolation; no unprimed inverse hidden at a zero mode; no floating eigenvalue or truncated representation sum without a certified tail and domain provenance; no Lorentzian PBW/Green carrier substituted for the compact Euclidean resolvent; no universal finite table, QME, Hadamard, positivity, particle, scattering or unitarity promotion

## Activates (downstream this unlocks)
- a background-specific evaluation of all five finite parity-even form factors
- or the next strictly smaller exact global spectral theorem

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["quantum-weyl/spectral/","quantum-weyl/reports/","quantum-weyl/transfer/receipts/","reports/","paper/12-pure-weyl-one-loop-bv-anomaly.tex","paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json","notes/d-quotient-quantum-team-brief.md","planning/forge-requests/"]
- `resource_hint`: "QUANTUM GLOBAL-SPECTRAL SUCCESSOR.  Use exact SU(2) representation theory and certified tails; reuse Forge harmonic/spectral/interval kernels where valid and answer sf:forge-request/scalar-flat-berger-spectral-measure rather than waiting for a second team."
- `notes`: ["This is the consumer-specific counterpart of the generic global-spectral-resolvent-relative-determinant Forge request.","The background is non-Einstein, non-conformally-flat and scalar-flat, so it probes Schur-sensitive rows that the existing special fixtures cannot determine.","Local symbol and scale data have already been proved insufficient: the ambiguity matrix has rank ten and zero transpose kernel."]
- `input_commit`: "384d46761"
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
