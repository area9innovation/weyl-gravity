# Science Forge handoff — 2026-07-19

From the Science Forge experiment (tango/forge repo, `forge/tools/{science-forge,
certlab,claimlang,physics-moyal,physics-linalg}` + `forge/lib/math`). Everything
below is reproducible from that repo at master; commands assume its root with
`go build -o /tmp/forgebin ./cmd/forge && export FORGE_LIB=$PWD/lib`.

## 1. A NEW RESULT: the coprime-ratio hierarchy conjecture holds at 5:3 and 7:1

First computation of the order-6 obstructions (preregistered prediction, then
computed — the corpus's sympy pipeline stops at order 4):

    o6(5:3) = (3863828151875 / 6463101113204736) * sqrt(15) * (a1^3 a2b^5 - a1b^3 a2^5)
              numerator 5^4*521*1511*7853, denominator 2^25*3*7^4*11^2*13*17
    o6(7:1) = (28633766567 / 2656254925209600000) * sqrt(7) * (a1 a2b^7 - a1b a2^7)
              numerator 7^8*4967, denominator 2^25*3^11*5^5*11*13

Every preregistered clause held: orders 2-5 vanish (selection rule), order 6 is
nonzero on exactly the predicted antisymmetric conversion pair, real coefficient
(even-order parity), and the w2-scaling relation o6 ~ w2^-14 holds exactly
(computed at (10,6) = 2^-14 x (5,3)). The p+q-2 law now has five instances:
3:1, 3:2, 5:1, 5:3, 7:1.

Evidence rails: (i) the forge kernel on two independent code generators,
byte-identical, sanitizer-clean (31-check consistency battery including an
independent end-to-end Hermiticity assembly distinct from the kernel-projection
path); (ii) a from-scratch sympy recomputation using your own Moyal machinery
(self-validating, term-exact agreement; ~165-181 s/case vs ~2 s in forge).

Read: `forge/tools/physics-moyal/RESULT-5-3.md` (the writeup: prediction,
numbers, checks, falsifiers). Reproduce independently on your rail:
`python3 forge/tools/physics-moyal/golden/dump_golden_53.py` (~9 min).
Machine-readable: `forge/tools/claimlang/certificates/paper5_hierarchy53.json`.

## 2. Corpus findings (each with evidence; verify before acting)

Drift/staleness caught by wrapping your own verifiers and producers:

1. **Two duplicate `result_id`s**: `LOCAL_BV_MINIMAL_BOOTSTRAP` and
   `REDUCED_MODE_SPECTRAL_BOOTSTRAP` each name two distinct certificate files —
   identity collisions in any result_id-keyed tooling (including your DAG
   builder's by-id resolution).
2. **Committed `certificate_graph/certificate-dag.json` is stale**: 276
   bridge-internal ordering edges committed vs 348 on a fresh HEAD build.
3. **Four stale paper citations**: papers 07-08/09 `\path{}`-cite certificates
   that changed 15-22 h AFTER the citing TeX's last commit. Details:
   `forge/tools/science-forge/discover/reconcile_report.json`.
4. **Two stale certificates under their own `--check`**:
   `closed_universe_observers/generate_berger_clock_integrated_scalar_stream.py`
   and `generate_berger_high_order_profile_moment_rail.py` fail their own
   replay (re-confirmed twice, distinct sessions).
5. **A drifted source-manifest assertion**: `bridge/einstein_sector/
   verify_einstein_maxwell_weyl_circumference_ell2_extra_transport_primitive.py`
   fails with "source manifest changed" (a dependency cert's embedded
   provenance hash drifted).
6. **Nine drift findings in quantum-weyl** (stale dependencies /
   non-reproducing certificates across `verify_active_frontier`, the cartan
   paper09 signoff LaTeX hash, and 7 more in relative/spectral/transfer):
   `forge/tools/certlab/FAMILY-COVERAGE.quantum-weyl.md`.
7. **Three drift findings in d_quotient_classical** (dependency hash mismatch,
   stale .tex worktree hash, stale source-module replay):
   `forge/tools/certlab/FAMILY-COVERAGE.d_quotient_classical.md`.
8. **175 undeclared code dependencies** (a verifier/generator reads a
   certificate that its cert does not declare in `dependency_refs` — e.g.
   `BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD` reads 3 undeclared certs) and
   **128 orphaned certificates** (no inbound code or declared reference; 61 in
   covariant_completion): `forge/tools/science-forge/discover/DISCOVERY.md`.
9. **A corroboration asymmetry worth knowing**: code evidence independently
   confirms the declared dependency graph almost perfectly for
   closed_universe_observers (precision 0.98 / recall 0.87) but barely at all
   for the programmatic families (d_quotient_classical 0.13, quantum-weyl ~0)
   — where declared structure exists without code-level corroboration.
10. Non-finding, for the record: an earlier bh1b "failure" was a
   memory-pressure artifact on our box, not a corpus bug (re-ran clean).

## 3. What you can use today (all read-only over your tree)

- **Fail-closed audit + replay of your certificates** (typed manifests, sha256
  locks, DAG checks, your own verifiers as gated checks, `--check` producers
  replayed with content-addressed caching): `forge/tools/certlab/` — README has
  per-family commands. 300+ of your certs are already wrapped.
- **Impact queries over the mined evidence graph** ("what is affected if the
  q3 convention changes" -> 473 nodes with per-edge file:line provenance):
  `forge/tools/science-forge/discover/query.py`.
- **Three-rail exact recomputation** of the zero-mode/cohomology/Moyal results
  (sympy == Julia/Nemo == forge, incl. H^4 = C^2 from your real differentials,
  with a proof-carrying block-decomposition certificate of the vacuum d4's
  8-mode structure): `forge/tools/physics-linalg/`.
- **Generated claim pages + claims tables** for the ported results:
  `forge/tools/science-forge/views/`.

Suggested adoption posture (details in the tango session log): run the certlab
audits in CI as an advisory shadow rail now; author NEW verifications as claims
files once the release-toolchain stamping lands (~weeks); flip families to the
substrate by gate, not by date.

Contact: the Science Forge working area is `forge/tools/science-forge/` (SPEC,
IR, program work items); the coordination model matches the work-item/event
sketch circulating in your notes.
