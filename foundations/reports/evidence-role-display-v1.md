# Per-evidence roles and the dual local+literature cell mark

**Scope:** additive metadata across cube v1–v4 and the static explorer.

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## What was wrong

A cell carried a single scalar `status`, and the explorer rendered exactly one
glyph from it.  The migration rule at `foundations/refine_intersection_cube.py`
ranks a direct local result above a direct literature result, so a coordinate
supported by both showed only `L`.  The direct literature record was appended
into the same flat `evidence` array as the ingredient-level records, and its
role was discarded at that point.  The status facet filtered the same scalar,
so a reader asking for literature-backed cells never saw them.

## What changed

Each cell now carries `evidence_roles`, mapping every attached record to its
role **at that obligation alone**:

| Role | Meaning |
|---|---|
| `DIRECT_LOCAL` | A bounded local result registered as directly supporting this obligation. |
| `DIRECT_LITERATURE` | A reviewed source registered as directly treating this obligation within its boundary. |
| `SUPPORTING` | Registered as an ingredient; it does not compose the refined result. |
| `UNREVIEWED` | No capability registration covers this record here. Neither directness nor its absence is claimed. |

Across the 452 emitted cells: **76 direct local**, **84 direct literature**,
**267 supporting**, **191 unreviewed** record-obligation pairs.

**Seven cells carry a direct local result and a direct literature result at the
same coordinate.**  They now render as `LR` with a corner wedge in the second
grade's colour, the inspector shows both status pills and a per-record role
badge, and the status filter finds them under either grade.

| Regime | Carrier | Obligation |
|---|---|---|
| Classical/standard | Krein/indefinite | State existence |
| Classical/standard | Algebraic/C* | State existence |
| Topos/internal | Finite/exact | State representation |
| Topos/internal | Finite/exact | Probability rule |
| Finite/discrete | Algebraic/C* | Generator/spectral dynamics |
| Finite/discrete | Algebraic/C* | Evolution/well-posedness |
| Finite/discrete | Algebraic/C* | Interaction construction |

Filtering by *Literature result* now returns 100 cells rather than 93; by
*Local result*, 88 rather than 81.  No status, count, or coverage number moved.

## Case separates a grade from an ingredient

A single letter also hid the ingredient mix.  All 160 pieces-only cells looked
alike, although a coordinate one local certificate short of composing is a
different research prospect from one holding only literature fragments.

The mark is now compound.  **Upper case is a certified direct grade; lower case
is a supporting ingredient of that kind.**  A lower-case letter is suppressed
when its kind already shows as a grade, so an `L` cell never renders `Ll`, and
records whose directness is unreviewed add no letter at all.

| Mark | Cells | Reading |
|---|---:|---|
| `·` | 205 | Not mapped |
| `R` | 90 | Direct literature result |
| `L` | 76 | Direct local result |
| `Pl` | 75 | Pieces only, local ingredients |
| `Pr` | 51 | Pieces only, literature ingredients |
| `G` | 30 | Priority gap |
| `P` | 20 | Pieces only, no reviewed ingredient |
| `Plr` | 14 | Pieces only, ingredients of both kinds |
| `LR` | 7 | Direct local **and** direct literature result |
| `Lr` | 5 | Direct local result, literature ingredients |
| `Rl` | 3 | Direct literature result, local ingredients |

A lower-case letter never promotes a cell and never changes the status colour:
`Plr` is still pieces-only.  The status filter is unaffected — selecting
*Pieces only* returns exactly the 160 `P`-family cells.

## What was deliberately not done

Roles are derived **only** where an existing certificate already determines
them: the v1 evidence-capability registry for split children, and the explicit
per-overlay declarations added to the eleven v1 overlays.  Everything else is
`UNREVIEWED` and fails closed:

- Records attached at an unsplit one-to-one obligation.  The registry covers
  split children only.
- Records added by the v3 normally-hyperbolic atlas and the v4 coded-wave
  frontier.  Those certificates attach evidence without declaring per-record
  directness, and their own overlay bases say some attachments are adjacent —
  `pischke-2025-semigroups` is recorded as *"adjacent formal quantitative
  semigroup evidence, not the local RCA_0 proof."*  One v4 promotion attaches
  three records for a single status change, so reading the action's evidence
  as uniformly direct would over-claim.

`UNREVIEWED` is **not** a finding that a record fails to support its cell.

## Remaining review backlog

Nineteen cells hold both evidence kinds while the registry judges only one kind
direct; those are correctly single-marked and need no action.  Fourteen cells
hold both kinds with the second kind unreviewed, and could become `LR` if
reviewed:

| Coordinate | Status | Unreviewed records |
|---|---|---|
| `WEAK_CHOICE_ZF \| ALGEBRAIC_CSTAR \| KINEMATICS_OBSERVABLES` | `LOCAL_RESULT` | blackadar-farah-2026 |
| `FINITE_DISCRETE \| ALGEBRAIC_CSTAR \| KINEMATICS_OBSERVABLES` | `LITERATURE_RESULT` | zohar-burrello-2014 |
| `CLASSICAL_STANDARD \| SMOOTH_DISTRIBUTIONAL \| EVOLUTION_WELLPOSEDNESS` | `LOCAL_RESULT` | baer-2015 |
| `WEAK_ARITHMETIC \| HILBERT_OPERATOR \| EVOLUTION_WELLPOSEDNESS` | `LOCAL_RESULT` | pischke-2025-semigroups |
| `WEAK_ARITHMETIC \| SMOOTH_DISTRIBUTIONAL \| EVOLUTION_WELLPOSEDNESS` | `PIECES_ONLY` | simpson-1984-ode |
| `CLASSICAL_STANDARD \| SMOOTH_DISTRIBUTIONAL \| CAUSAL_PROPAGATION_GREEN` | `LOCAL_RESULT` | baer-2015, muehlhoff-2010 |
| `WEAK_CHOICE_ZF \| HILBERT_OPERATOR \| CAUSAL_PROPAGATION_GREEN` | `PIECES_ONLY` | blackadar-farah-karagila-2026 |
| `CONSTRUCTIVE_COMPUTABLE \| SMOOTH_DISTRIBUTIONAL \| CAUSAL_PROPAGATION_GREEN` | `PIECES_ONLY` | selivanova-selivanov-2013, zhong-weihrauch-2003-distributions, weihrauch-zhong-2006-fundamental |
| `FINITE_DISCRETE \| ALGEBRAIC_CSTAR \| CAUSAL_PROPAGATION_GREEN` | `PIECES_ONLY` | nachtergaele-raz-schlein-sims-2007 |
| `WEAK_CHOICE_ZF \| KREIN_INDEFINITE \| GAUGE_BV_COHOMOLOGY` | `PIECES_ONLY` | mostafazadeh-2001, gottschalk-2004 |
| `WEAK_CHOICE_ZF \| ALGEBRAIC_CSTAR \| GAUGE_BV_COHOMOLOGY` | `PIECES_ONLY` | blackadar-farah-2026, fredenhagen-rejzner-2011 |
| `FINITE_DISCRETE \| ALGEBRAIC_CSTAR \| GAUGE_BV_COHOMOLOGY` | `PIECES_ONLY` | zohar-burrello-2014 |
| `WEAK_CHOICE_ZF \| ALGEBRAIC_CSTAR \| RECONSTRUCTION_LIMITS` | `LITERATURE_RESULT` | blackadar-farah-2026, fredenhagen-rejzner-2011 |
| `TOPOS_INTERNAL \| FINITE_EXACT \| RECONSTRUCTION_LIMITS` | `LITERATURE_RESULT` | constantin-doring-2020, abramsky-coecke-2004 |

Reviewing one means registering that record's `direct`/`pieces` capability at
that obligation, not editing the emitted cube.

## Verification

The four cube canonical digests are **unchanged** from before this work,
which is the receipt that no claim moved:

```text
v1 37e04717bec0e78aaa9c6187a39fe6edb7dd512cdf8d9597455dc526d637fa9d
v2 34996392dc7b7d4548f7bbf76cf1b6f8b50402da16e1789a637661a96f8fddc3
v3 157a88c2580d6d66ae34cddb8b6ca626649deb2111079e84e21fa2b8fd4b7209
v4 b9de7709da88279abf0a47a93aad38047ab4a6b0c2c85e99c421c9bd36aff7c9
```

Those digests project status, evidence, and migration fields only, so the
additive role field cannot mask a status change.  The site data digest does
move, because the roles live inside its cell projection.

```text
python3 foundations/refine_intersection_cube.py --check
python3 foundations/refine_intersection_cube_v2.py --check
python3 foundations/refine_intersection_cube_v3.py --check
python3 foundations/refine_intersection_cube_v4.py --check
python3 foundations/build_matrix_site_v2.py --check
python3 foundations/verify_refined_intersection_cube.py
python3 foundations/verify_matrix_site_v2.py
python3 -m unittest discover -s foundations/tests -p 'test_*.py'
```

The independent checkers verify role closure against the evidence list, role
vocabulary, role/status agreement, and — in `check_matrix_site_v2.py` — that
each declared role kind agrees with the kind the evidence registry resolved
independently for that record.  That checker also recomputes every displayed
mark from the roles, compares the histogram against the generated counts, and
asserts that the upper-case part of each mark agrees with the cell's scalar
status, so a lower-case ingredient letter cannot move a cell between families.

Role and status are written by different passes: v3 and v4 change a status
without touching roles.  `check_refined_intersection_cube_v3.py` and
`check_refined_intersection_cube_v4.py` therefore assert role/status agreement
at the cube boundary as well; a stranded `DIRECT_LOCAL` under a `PIECES_ONLY`
cell is caught there rather than assumed absent.

## Boundaries

This work does not establish:

- that an `UNREVIEWED` role is an absence of direct support;
- that a dual `LR` mark composes its two records into a stronger result;
- that a lower-case ingredient letter is a result, a grade, or a promotion;
- any new coverage, status promotion, or literature completeness;
- a directness review for records the capability registry does not cover;
- a new Lorentzian-causal result.
