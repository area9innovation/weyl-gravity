PULLED by agent quantum-qme-1 — stream quantum-qme — lease exclusive (acquired 2026-07-20T14:37:31Z, expires 2026-07-21T02:37:31Z)

WORK PACKAGE sf:program/work/quantum-strict-anomaly-restriction-zero-charge-sectors  (state: ACTIVE, owner: quantum)

## Objective
Decide whether the strict one-loop Weyl-anomaly classes remain nontrivial after restriction to the programme's selected zero-charge conformal-cylinder and fixed-coupling Berger fluctuation complexes, without confusing background vanishing with cohomological triviality.

## Stop condition (what DONE means)
Import LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT at commit c6d1c0ba and the certified classical cylinder/Taub and Berger contractions by exact artifact hashes. Define the local-to-background and local-to-residual chain maps, domains, boundary terms and charge-sector inclusions before evaluating any cocycle. Pull back [omega C^2], [omega E4] and the odd [omega C Ctilde] class through the full allowed fluctuation complexes, not merely the conformally flat background value. Determine separately whether each pullback is zero, exact with an explicit primitive compatible with the selected quotient, nontrivial, or undefined because a required chain map is absent. Compute the induced obstruction, if defined, to the raw-D cylinder Cartan identity and to the Berger K_Berger identity while preserving their distinction. Certify the first perturbative order at which each class can appear. If the map is missing, land a typed receiver schema and producer request rather than declaring sector anomaly freedom. Include independent descent/restriction verification and decisive mutations that replace fluctuation pullback by background evaluation or raw D by K_Berger.

## Current gate
cohomological pullback of the strict anomaly basis to the selected cylinder and Berger sectors

## Forbidden
no anomaly class called zero because C vanishes on the background; no integrated Euler number substituted for local descent; no full-theory anomaly freedom inferred from a restricted sector; no raw-D/K_Berger identification; no local Euclidean class promoted to a Lorentzian QME or state theorem; no missing local-to-residual chain map silently guessed from row names

## Activates (downstream this unlocks)
- quantum verdict for the selected zero-charge cylinder sector
- sector-specific necessity or dispensability of the Wess-Zumino compensator
- a precise local-anomaly-to-Cartan bridge

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["quantum-weyl/local_bv/","quantum-weyl/transfer/","quantum-weyl/reports/","quantum-weyl/atlas/","reports/","residual_atlas/","notes/d-quotient-quantum-team-brief.md","planning/forge-requests/"]
- `resource_hint`: "SECOND INDEPENDENT FALLBACK. The key adversarial distinction is background evaluation versus pullback to the entire allowed fluctuation complex. If a classical chain map is missing, stop at the exact missing-object theorem and issue a typed request."
- `notes`: ["The cylinder is conformally flat, but the strict anomaly cocycles can begin at nonzero order in fluctuations.","The Taub-zero derived fibre and Berger fixed-coupling sector are different restrictions and require separate maps.","A positive restricted-sector result would not rescue strict Weyl gravity universally."]
- `input_commit`: "c6d1c0bad4d7e609fccb8dc5581fab107a819d33"
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
