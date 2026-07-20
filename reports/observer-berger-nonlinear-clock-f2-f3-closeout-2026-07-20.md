# Observer close-out: Berger nonlinear clock `F2/F3`

Work item: `sf:program/work/berger-nonlinear-clock-canonical-map-f2-f3`
Owner: observer
Authority snapshot: repository `master` at `b1daa708eeb9f8bf40f47eac832bcb2fc12b2e0f`

## Stop-condition audit

The work item permits closure either when the canonical component/PBW map and
cotangent lift reproduce the completed unary, or when an exact first
action/chart incompatibility is exported with every interaction and
second-order-cone activation false.  The second branch is now satisfied.

| Requirement | Evidence | Disposition |
| --- | --- | --- |
| Combined same-background `F2/F3` field map | `BERGER_NONLINEAR_CLOCK_COMBINED_CANONICAL_MAP_F2_F3`, SHA-256 `b35f50e238a15c1e226edf59779716987a6aee13c1917d7c9e65b9a39033f40a` | `CERTIFIED`: 55 `F2` and 174 `F3` field entries, exact radial/temporal restrictions |
| Signed BV cotangent lift | same certificate | `CERTIFIED`: 132 `F2` and 268 `F3` cotangent entries; degree-two and degree-three canonical inverse defects vanish |
| Completed unary compatibility | `BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET`, SHA-256 `cacbd3be6bde8e80d142ca9012b024abd7a10472a2759b8f6e8b8af19b310481` | `CERTIFIED` on the declared same-background quotient; all second-jet blocks are odd-cyclic |
| Executable scalar interactions | `BERGER_108_ROW_COMPLETE_Q2_PBW`, SHA-256 `c87285276113391dc70dfb2bd4b66052d8bd78a1c94fc9a1e6a6adc724b4a605`; `BERGER_108_ROW_COMPLETE_Q3_PBW`, SHA-256 `9c574a78877ba14f197acf407a10d3b98c6b055608c2131442ab4d571f9a891f` | Both source-labelled payloads are exported; this does not certify their coderivation identities |
| First component arity gate | `BERGER_108_ROW_ARITY_TWO_OBSTRUCTION`, SHA-256 `5976a3b4162ceafa2b2b132f394846c19b8c709cba7c0a560d615cfe47bf502a` | `OBSTRUCTED`: the switch-specialized `(0,0)` residual has 2,340 keys and 2,388 monomials on 21 rows |
| Chart-versus-action disposition | `form_clock_chart_gate` in the same obstruction certificate | Exact 248-key Maxwell/emitter form chart induces a `q1`-cocycle in all four retained bidegrees and changes the existing obstruction by zero.  A canonical chart change cannot repair the raw Ward defect. |
| Downstream lifecycle | obstruction certificate plus observer atlas fragment, SHA-256 `eb722e773daa4cb27507d5a53978e37c58ea605181625f70879e633ee955cab3` | Arity three, `K_Berger`, observer-morphism stability, `O_detector|Z2^C`, nonlinear rank and physical Bridge 3 remain false or `NO_CERTIFIED_MAP` |

The first exact witness remains

```text
tau_star <- (e0 e1 A_0, K0_01)    coefficient +g0 h0.
```

It is source-isolated to the emitter Diff--BV `q2` block crossed with the
emitter unary.  The canonical form-clock correction has zero arity residual,
so this is an action/component Ward incompatibility on the present carrier,
not evidence for fitting `q2/q3` or choosing another clock chart.

## Independent rails

The following independent verifier chain passed on 2026-07-20:

```text
python3 -m closed_universe_observers.verify_berger_nonlinear_clock_combined_canonical_map_f2_f3
python3 -m closed_universe_observers.verify_berger_108_row_nonlinear_clock_second_jet
python3 -m closed_universe_observers.verify_berger_108_row_complete_q2_pbw
python3 -m closed_universe_observers.verify_berger_108_row_complete_q3_pbw
python3 -m closed_universe_observers.verify_berger_108_row_arity_two_obstruction
python3 -m closed_universe_observers.atlas.verify_observer_atlas_fragment
python3 residual_atlas/validate_fragment.py closed_universe_observers/atlas/observer-atlas-fragment.json
```

Combined elapsed time was 265.46 seconds; peak RSS was 875,072 KiB.  The
exhaustive arity verifier had already passed for the same committed
certificate in the preceding gate receipt.

The read-only advisory command `ci/science-forge-shadow.sh` completed in 4.92
seconds.  It reported two pre-existing programme-wide findings rather than a
pass: bridge lock drift and growth from the 976-certificate baseline to 1,151
certificates.  These findings are outside this observer pathspec and are not
silently treated as passing evidence.

## Honest boundary

This closes the work item through its exact-incompatibility branch.  It does
not establish `q1q2=0`, does not authorize `q2q2+q1q3`, and does not establish
`K_Berger` equivariance, observer-morphism stability, tangent-cone detector
response, a physical-branch dictionary, finite-parameter causality, or a
quantum result.  A future successor may re-export the raw temporal
gravity-clock-Maxwell-emitter Ward orbit from one common action, but that is a
new work item rather than an implicit reopening of this append-only package.

CLOSE-OUT: DONE — the stop condition is met by an exact first action/chart incompatibility with every downstream activation fail-closed.
EVIDENCE: closed_universe_observers/certificates/BERGER_108_ROW_ARITY_TWO_OBSTRUCTION.json
