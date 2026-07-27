# Standalone provenance runtime repair

Date: 27 July 2026

## Outcome

Historical certificate pins remain byte-for-byte unchanged.  Git-attached
verification now resolves pre-extraction commit ids and the stripped
`physics/symplectic-reconstruction/` prefix at lookup time through
`ci/standalone_provenance.py`.

The resolver is fail-closed:

- it accepts only hexadecimal commit ids and safe repository-relative paths;
- it requires the committed `standalone-history-crosswalk-v1` schema;
- it rejects any crosswalk with unresolved in-repository rows;
- it verifies that the translated commit and object exist;
- it requires a blob and checks its exact recorded SHA-256;
- for abbreviated or structurally unindexed historical pins, it searches the
  filtered path history and accepts only exact content equality;
- absent mappings, absent blobs, unsafe paths and hash mutations are rejected.

## Triage

The load-bearing paper rails were repaired first:

- Paper 12's tau-adic all-loop and DR/MS obstruction chain;
- Paper 13's theorem-frozen third-order Kuranishi disposition;
- the residual-atlas committed-snapshot verifier used by cross-paper
  navigation.

The remaining quantum, Cartan, transfer, Lorentzian and observer verifiers
with ordinary blob pins were migrated to the same resolver.  Two
`d_quotient_classical` certificates hash their historical verifier source.
Editing those verifier files would invalidate their immutable source
manifests, so the original files were left unchanged and two append-only
standalone successor rails were added:

- `verify_berger_q26_finite_row_module_closure_standalone.py`;
- `verify_berger_q26_minimal_six_row_cyclic_obstruction_standalone.py`.

Four old Observer Tier-3 scripts are not current scientific rails:

- `verify_observer_tier3_fixed_point_after_historical_base_binding_repair_v1.py`;
- `verify_observer_tier3_fixed_point_after_legacy_crosswalk_extension_v2.py`;
- `verify_observer_tier3_git_attached_exact_materialization_rerun_v1.py`;
- `verify_observer_tier3_provenance_fixed_point_relock_after_berger84_handoff.py`.

They verify historical monorepo materialization and obstruction receipts,
including the outer monorepo tree identity and corpus size.  A subtree
crosswalk can preserve blobs and the extracted scope tree, but cannot
reconstruct the removed outer tree.  These scripts are therefore retained as
historical process records and are retired as standalone runtime rails.  They
are superseded operationally by
`PAPER09_PROMOTION_AFTER_GIT_ATTACHED_TIER3_V3_NO_PROMOTION`; none supports a
promoted theorem in the standalone repository.

## Superseded observer input

The five stale input pins were not silently repinned.

The two legacy certificates are explicitly historical-base replays and still
verify against their immutable old blob.  For the other three certificates,
their generators were evaluated against the current receiver-admissibility
input.  After removing provenance hashes and payload references—but no
scientific fields—the rebuilt certificates are identical to the recorded
ones.  Their scientific dispositions therefore survive; only their
provenance changed.

This result is recorded and independently replayed by:

- `closed_universe_observers/receipts/OBSERVER_SUPERSEDED_INPUT_REVALIDATION_2026_07_27_V1.json`;
- `closed_universe_observers/verify_superseded_input_revalidation_2026_07_27.py`.

Paper 09 remains `DRAFT_ALLOWED`: its claim map also pins later append-only
planning events whose hashes drifted.  This repair does not regenerate or
promote that map.

## Preventive rail

`ci/verify_paper_manuscript_pins.py` checks every explicit manuscript and PDF
hash binding in the paper claim maps.  It deliberately ignores historical or
superseded evidence pins.  Its mutation test changes a manuscript hash and
requires rejection.

## Editorial repair

The genuinely abbreviated bibliography records in Papers 02--04 now include
their titles.  The two Holdom records also had their Nuclear Physics B volume
and article numbers interchanged; they now read:

- *UV-complete 4-derivative scalar field theory*, **1000** (2024) 116472;
- *Making sense of ghosts*, **1008** (2024) 116696.

The Stucker and Gajic--Warnick entries in Paper 17 already contained their
titles in plain `\newblock` form and did not require alteration.

## Claim boundary

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

This repair restores exact provenance replay for the migrated and successor
rails.  It does not change any theorem, certificate payload, lifecycle state,
physical interpretation or numerical result.  It does not make Paper 09
current, restore the removed monorepo outer tree, establish a green Observer
Tier-3 traversal, or provide any `LORENTZIAN-CAUSAL` quantum construction.

## Verification receipt

The scoped test commands and elapsed times are recorded in the commit handoff.
Tier 0 and the affected verifier chain were run.  The full repository suite
was not run because no mathematical operator, certificate payload, schema or
theorem lifecycle was changed.
