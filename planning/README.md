# planning/ — the programme coordination model (Science Forge work items)

This directory coordinates the programme's forward workstreams as **Science
Forge work items**: one file per stream, an append-only event log, and briefs
that the coordinator renders *from* the items instead of inventing them ad hoc.
It is the operational face of `notes/universe-building-roadmap.md` (which remains
the scientific planning authority); this directory holds the machine-readable
state the roadmap describes in prose.

## The model

```
planning/
  work-items/            THE sfc PROGRAM DIRECTORY (flat *.json work items)
    bridge.json          Einstein--Maxwell mixed-cone quadratic-source
    berger.json          Positive Berger clock — two_j=6 feedback binding
    nonlinear.json       filtered ell3 obstruction / branch crosswalk
    quantum-qme.json     M14 disposition + renormalized Q1 / QME
    black-hole.json      polar extra/cross flux blocks; Zerilli master scalar
    classical.json       C-G2 open-background causal transfer
    AGENT-CONSTRAINTS.md  standing constraints spliced into every brief
    events -> ../events   symlink so sfc writes transitions into planning/events/
  events/                append-only WORK_ITEM_TRANSITIONED log (see its README)
  examples/              rendered briefs (planning/examples/<item>-brief.md)
  README.md              this file
```

- **One file per stream.** A work item is `work-v0`: `id` (`sf:program/work/<name>`),
  `kind:"work"`, and a `body` with `owner / state / objective / depends_on /
  activates / current_gate / stop_condition / forbid`. `activates` and
  `current_gate` are a faithful superset of the base schema, mirroring the
  roadmap's own "which calculation unlocks which later question" language.
- **The item file is never rewritten.** State changes by APPENDING one
  content-addressed event under `events/`. The **effective state** is the base
  `state` folded over those events (latest `(when, id)` wins). This is Science
  Forge law 2: append-only history.
- **Briefs are generated, not authored.** `sfc work-package` renders a brief
  from the live item (effective state, dependency states, standing constraints,
  orientation) — reproducible and byte-deterministic. `views` are derived; edit
  the sources and regenerate.
- **States** follow the spec: `PROPOSED / ACTIVE / BLOCKED / DONE / OBSTRUCTED /
  RETIRED`. A work item terminates in a certificate either way — a result or an
  obstruction (roadmap: "If the main construction fails, the exact first
  obstruction is the deliverable").

## The commands (Science Forge's `sfc`, in the tango/forge repo)

The substrate is NOT vendored here. Point `sfc` at `planning/work-items/`:

```bash
FORGE=/home/alstrup/area9/tango/forge          # the Science Forge repo
BIN=/tmp/forgebin; ( cd "$FORGE" && go build -o "$BIN" ./cmd/forge )
export FORGE_LIB="$FORGE/lib"
SF="$BIN -run $FORGE/tools/science-forge/sfc.forge --"
PDIR=planning/work-items

# validate + merge the program into one IR graph
$SF import-program "$PDIR" /tmp/planning_graph.json

# render an agent brief (your entire assignment) from a live item
$SF work-package "$PDIR" sf:program/work/berger -o planning/examples/berger-brief.md

# transition an item — appends ONE immutable event under planning/events/
$SF work-event "$PDIR" sf:program/work/berger --transition ACTIVE \
    --by observer --stamp "$(date -u +%Y-%m-%d)" --note "assigned and started"
```

## The advisory audit rail

`ci/science-forge-shadow.sh` runs the substrate's certlab audits + coverage
census READ-ONLY over this tree and reports drift WITHOUT failing the build
(advisory by default; `--strict` to fail closed). This is the handoff's adoption
posture — audit now, flip families to fail-closed by gate, not by date.

## The operating rule (from the roadmap's shared cadence)

Each team completes the earliest reachable item, commits it coherently, and
continues **without waiting for another team**:

1. **Opening audit** — start from committed `master`; pin every imported object
   by result id, hash and source commit; run the smallest regression that can
   falsify the proposed consumer.
2. **Primary construction** — pursue the item's `current_gate`; never wait on an
   uncommitted producer (work the declared fallback, import only after commit).
3. **Adversarial pass** — mutate one decisive sign/coefficient/boundary/grading;
   the verifier must reject it. Recompute independently, not by re-serializing
   one calculation.
4. **Handoff pass** — leave a strict certificate/schema, verifier, focused
   tests, human report, assumptions and missing-object ledger, exact commands,
   elapsed times and dependency tags.
5. **Commit discipline** — commit each passed or obstructed gate separately by
   explicit pathspec; never bundle another team's dirty files.

When a priority differs, `notes/universe-building-roadmap.md` controls what is
attempted next; a certificate controls what is true.

## Five-line quickstart (adopting a stream)

1. Read `notes/universe-building-roadmap.md` (planning authority) and your
   stream's `planning/work-items/<name>.json` (objective / current_gate / forbid).
2. Render your brief: `sfc work-package planning/work-items sf:program/work/<name>
   -o planning/examples/<name>-brief.md` — it is your entire assignment.
3. Mark it started (coordinator, by pathspec): `sfc work-event
   planning/work-items sf:program/work/<name> --transition ACTIVE --by <team>
   --stamp <date> --note "…"`.
4. Do the science under AGENT-CONSTRAINTS.md; land a certificate (result OR the
   first exact obstruction) with an independent rail; run
   `ci/science-forge-shadow.sh` to check you introduced no drift.
5. Record close-out with a `--transition DONE|OBSTRUCTED` event; the item file
   is never edited — the event is the history.
