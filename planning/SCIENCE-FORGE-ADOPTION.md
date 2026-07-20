# Science Forge adoption contract for all research teams

**Audience:** every long-lived classical, Einstein/bridge, nonlinear, quantum,
black-hole, or observer agent working in this repository.

**Purpose:** this is the single file a coordinator should point a team to when
adopting Science Forge. Read it before using `s-f`. It separates the shared
coordination workflow from optional mathematical substrates such as Conflux.

The repository's `AGENTS.md` remains authoritative. This document explains how
Science Forge operates underneath those rules; it does not weaken them.

## 1. What every team is adopting

Every team adopts the following operating contract immediately:

1. Work is represented by immutable work items and append-only events.
2. A generated work package defines the objective, current gate, stop
   condition, dependencies, allowed paths, and forbidden promotions.
3. Agents checkpoint their exact input and output commits, changed paths,
   tests, receipts, unresolved dependencies, and next recommendation.
4. Cross-stream needs are typed requests, not edits to a common planning file.
5. `DONE`, `OBSTRUCTED`, and `SHORTFALL` are distinct outcomes. A skipped,
   timed-out, stale, ambiguous, or incompletely evidenced calculation is never
   a pass.
6. Generated boards, briefs, graphs, and views are read-only products. Never
   edit them as sources.
7. Structure-seeking work is proof-first: formulate the candidate theorem,
   proof obligations, counterexample strategy, and exact finite remainder
   before launching a large coefficient search or exploratory Conflux run.

Science Forge coordinates work. It does not certify a scientific statement
merely because an agent reports that the work is complete. Scientific authority
still comes from the declared certificate, independent verifier, mutation
control, tests, assumptions, and claim boundary.

## 2. Current rollout modes

All teams use the same conventions, but mutating task-state commands are
introduced by stream:

| Stream | Team | Current mode |
| --- | --- | --- |
| `black-hole` | black-hole | **AUTHORITATIVE:** use `s-f` for pull, lease, report, block, request, and close-out |
| `observer` | observer/clock | **AUTHORITATIVE:** use `s-f` for pull, lease, report, block, request, and close-out |
| `nonlinear` | nonlinear | **AUTHORITATIVE:** use `s-f` for pull, lease, report, block, request, and close-out |
| `bridge` | Einstein/bridge | **AUTHORITATIVE:** use `s-f` for pull, lease, report, block, request, and close-out |
| `classical` | classical | **AUTHORITATIVE:** use `s-f` for pull, lease, report, block, request, and close-out |
| `quantum-qme` | quantum | **AUTHORITATIVE:** use `s-f` for pull, lease, report, block, request, and close-out |

All six resident streams are authoritative from 20 July 2026. Every team must
use one exclusive `s-f` lease at a time and must not create a parallel
lifecycle history in a team brief or shared roadmap. This coordination
cutover does **not** enable Conflux universally: the consumer-specific gates
below remain mandatory.  The resident-physics discovery pilots are `LANDED`;
each stream still requires its declared importer, independent replay, and
claim-specific activation gate before a Conflux candidate can affect physics.

### First proof-first pilot

The observer stream is the first authoritative proof-first case:

```text
sf:program/work/observer-common-action-compatibility-theorem
```

It consumes the certified full-rank common-action Ward obstruction. The agent
must first derive an invariant Ward/Noether compatibility theorem and a
complete bounded minimal-extension ansatz. Exact computation then checks the
finite proof obligations. Conflux may run only after its observer importer
independently rediscovers the known determinant, rank, nullity, persistent
witness, and decisive mutation from the raw payload.

For every later structure-seeking ticket, record these five objects in the work
item's `notes` or `resource_hint`:

1. **Mathematical target:** the invariant object being classified.
2. **Candidate theorem:** a statement that can be true or false.
3. **Proof obligations:** conceptual lemmas separated from finite identities.
4. **Counterexample strategy:** the smallest mutation or fixture that can
   falsify the theorem.
5. **Certificate boundary:** exactly which remaining identities require
   machine verification and which physical promotions remain forbidden.

This is not a requirement to prove a guessed theorem. A minimal exact
counterexample or obstruction is an equally valid close-out.

The nonlinear proof-first cutover is:

```text
sf:program/work/nonlinear-cyclic-extension-splitting-theorem
```

Its previous free-text blocker and search-before-proof successor are retired as
coordination objects only; their certified nonlinear obstructions remain
authoritative. The replacement asks whether the Einstein/additional exact
sequence splits in an admissible cyclic filtered category before Conflux is
allowed to search the large interaction payload.

The remaining proof-first cutovers are:

```text
sf:program/work/classical-relative-spencer-prolongation-theorem
sf:program/work/bridge-kernel-direction-incidence-normal-form
sf:program/work/quantum-berger-retained-bv-hadamard-restriction
```

They consume the teams' actual latest results: the classical obstruction
through order three, the bridge fixed-direction contraction shortfall, and
the quantum rank-40 Hadamard transport plus canonical-summand restriction
obstruction. The older stream heads are coordination-retired, not
scientifically withdrawn. Their still-open C-G2, mixed-cone, and M14 goals
return as new bounded work items after the current proof-first gates close.

## 3. Tool and capability boundary

Science Forge is a collection of separable capabilities. Adoption of one does
not imply adoption of all.

| Capability | Default status in this programme |
| --- | --- |
| `s-f` work coordination | adopted according to the rollout table above |
| Existing repository certificates and verifiers | authoritative within their declared scopes |
| Certlab audit and evidence graph | advisory unless a particular family has passed its explicit cutover gate |
| Forge exact-math kernels | use only when the work item names the kernel or an accepted Forge request supplies it |
| Claim language | use only for claims already represented by an accepted schema and kernel |
| **Conflux structure discovery** | **not adopted by default; explicit opt-in only** |
| `s-f work check` Git dry-run | staged pilot for reportable existing-path packages; new-file intent gate remains open |
| `s-f work commit` Git transaction | staged pilot: use after the new-file intent gate below is closed |
| TUI, resource governor, environment installer | not yet part of this workflow |

### Conflux rule

Do not use Conflux merely because the work package mentions Science Forge.
Conflux may be used only when all of the following hold:

1. The work item explicitly names Conflux as an allowed or required capability.
2. A consumer-specific typed importer exists for the declared inputs.
3. A known result has been independently reproduced on that consumer.
4. Mutation controls and a deterministic receipt pass.
5. Candidate discoveries remain `CANDIDATE` until an independent scientific
   certificate promotes them.

In particular, the **black-hole team must not use Conflux** as a mathematical
or evidentiary dependency until a black-hole-specific acceptance gate covers
Schwarzschild operators, rational-function coefficients, frequency parameters,
repeated roots, and asymptotic series. Continue using the established
Python/SymPy/FLINT certificate and verifier pipeline.

### Conflux documentation

An enabled Conflux ticket must begin by reading:

1. `/home/alstrup/area9/tango/forge/tools/science-forge/conflux/README.md` —
   production commands, typed importers, rediscovery, bounded exploration, and
   lifecycle boundaries;
2. `/home/alstrup/area9/tango/forge/tools/science-forge/conflux/DISCOVERY-SWEEP.md`
   — the family-by-family discovery method;
3. `/home/alstrup/area9/tango/forge/tools/science-forge/conflux/PROVENANCE.md`
   — source hashes and fixture provenance;
4. `/home/alstrup/area9/tango/forge/docs/structure-finding-thesis.md` — the
   mathematical discovery strategy and equivalence ladder;
5. `planning/forge-requests/README.md` — the physics-to-Forge request protocol.

Reading the general Conflux material does not enable Conflux for a ticket. The
ticket's own capability boundary remains decisive.

### Coordinating with the Forge/Conflux team

If an enabled physics ticket discovers that Conflux lacks an importer, exact
field, rule kind, verifier seam, resource limit, or CLI operation:

1. Preserve the physics result as `BLOCKED`, `OBSTRUCTED`, or `SHORTFALL`; do
   not silently replace the missing operation.
2. Create `planning/forge-requests/<slug>.json` using schema `work-v0` and the
   protocol in `planning/forge-requests/README.md`.
3. Name the exact physics consumer, input schemas and hashes, minimal
   reproduction command, stop condition, independent rail, and forbidden
   shortcuts.
4. Put the blocked physics work-item IDs in `depends_on`.
5. Commit and push the request in this repository. Do not edit the Tango
   repository from a resident physics ticket.
6. The Forge coordinator answers in the same request file with
   `REQUESTED -> ACCEPTED -> LANDED(commit,gate)` or `DECLINED(reason)`.
7. A resident physics team independently runs the delivered consumer gate
   before unblocking its work. The Forge producer's own successful rerun is
   reproduction, not independent verification.

Compiler or runtime bugs use `sf:forge-request/bug-<slug>` and must include a
minimal reproducer. Cross-physics dependencies continue to use `s-f work
block`; missing Forge/Conflux capabilities use `planning/forge-requests/`.

### Ranked Conflux successor tickets

| Priority | Work item | Scope |
| ---: | --- | --- |
| 1 | `sf:program/work/observer-common-action-compatibility-theorem` | first proof-first pilot; Ward compatibility and minimal carrier/action enlargement |
| 2 | `sf:program/work/nonlinear-conflux-branch-mixing-discovery` | branch selection, cyclic-redefinition invariants, and interaction-closed subcarriers |
| 3 | `sf:program/work/classical-relative-spencer-prolongation-theorem` | general fixed-family prolongation theorem; Conflux only after proof and resident gate |
| 4 | `sf:program/work/bridge-kernel-direction-incidence-normal-form` | deforming-kernel incidence topology; Conflux only after proof and resident gate |
| 5 | `sf:program/work/quantum-conflux-local-algebra-discovery` | local BV/anomaly/counterterm algebra only |

No black-hole Conflux successor exists yet. Hadamard, microlocal, positivity,
particle, scattering, and unitarity questions are outside these tickets.

## 4. Start of every session

Existing long-lived agent sessions should retain their context. They do not
need to be restarted for every task.

```bash
source /home/alstrup/.bashrc
cd /home/alstrup/area9/bp2transformer/physics/symplectic-reconstruction

git status --short --branch
git fetch origin master

command -v forge
command -v s-f
```

Expected tool paths:

```text
/home/alstrup/.local/bin/forge
/home/alstrup/.local/bin/s-f
```

From this repository or any descendant directory, `s-f` automatically selects:

```text
/home/alstrup/area9/bp2transformer/physics/symplectic-reconstruction/planning/work-items
```

Do not set `SF_PROGRAM` for the normal resident workflow. It remains available
as an explicit one-command override when a coordinator intentionally targets a
different programme. Non-interactive sessions also suppress terminal-title
writes automatically; `SF_NO_TITLE=1` is only an optional interactive override.

Record all pre-existing modified and untracked paths. They belong to other
agents unless proven otherwise. Never reset, stash, overwrite, reformat, or
include them in a commit.

## 5. Inspect the programme

Any team may use these read-only commands:

```bash
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

s-f streams-view \
  --streams "observer;black-hole;bridge;classical;nonlinear;quantum-qme" \
  --now "$NOW" \
  -o /tmp/science-forge-board.md

less /tmp/science-forge-board.md

s-f work ready --stream <STREAM> --now "$NOW"
```

An ambiguity, unresolved dependency, or empty ready queue is a real result.
Do not bypass it by reopening an old task or editing an item. Ask the
coordinator to append a causally ordered repair event or create a new bounded
item.

## 6. Acquire authoritative work

Only a stream in `AUTHORITATIVE` mode should run `work pull`.

```bash
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
EXPIRES="$(date -u -d '+12 hours' +%Y-%m-%dT%H:%M:%SZ)"

s-f work pull \
  --stream <STREAM> \
  --agent <STABLE-AGENT-ID> \
  --now "$NOW" \
  --expires "$EXPIRES" \
  -o /tmp/<STREAM>-brief.md

less /tmp/<STREAM>-brief.md
```

Recommended stable agent IDs are:

```text
black-hole-1
observer-1
bridge-1
classical-1
nonlinear-1
quantum-qme-1
```

If `work pull` reports no ready item, stop. Do not revive a completed objective,
reinterpret an old work item, or work around an unresolved dependency.

The generated brief is the assignment. Honor its stop condition and forbidden
promotions literally. If the requested construction fails, the first exact
obstruction is the deliverable.

## 7. Execute under repository Git discipline

The landed SF5 transaction layer mechanizes this repository's shared-master
discipline. It uses a private temporary Git index seeded from `HEAD`, computes
`report.changed_paths ∩ item.allowed_paths`, maps this nested programme into
the enclosing Git root, verifies the exact prospective commit tree, commits by
compare-and-swap, and appends a `WORK_COMMITTED` event. It neither reads nor
writes the process-global index, so other teams' staged, unstaged and untracked
files remain untouched.

Adoption proceeds without interrupting an active derivation:

1. At the next coherent checkpoint whose changed paths already exist in the
   declared `current_commit`, a team files its normal scoped report and runs:

   ```bash
   s-f work check --item <ITEM-ID> --agent <STABLE-AGENT-ID>
   ```

   The output must show every intended path under `would-stage`, no intended
   path under `REFUSED-outside-allowed`, and all unrelated work under
   `not-in-report-but-dirty`. This command is read-only.

2. Full `s-f work commit --push` is initially piloted on one complete package
   containing both a new file and a modified file, while unrelated live work is
   present. Acceptance requires the prospective-tree verifier receipt, the
   exact intended path set in the commit, an append-only `WORK_COMMITTED` event,
   a successful push, and byte-identical unrelated index/worktree state.

3. After that pilot, all streams use:

   ```bash
   s-f work commit \
     --item <ITEM-ID> \
     --agent <STABLE-AGENT-ID> \
     --push \
     --now "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
   ```

   Manual `git add`/`git commit` becomes a documented fallback only when the
   transaction refuses or the work item explicitly assigns integration to the
   coordinator.

One rollout blocker remains as of 20 July 2026:
`sf:forge-request/bug-science-forge-precommit-report-new-files`. The current
interface requires a report before `work commit`, but the report containment
gate cannot honestly name newly created deliverables before that commit exists.
Until that request lands and passes the new-file pilot, all teams adopt
`work check` only where a pre-commit report can be recorded honestly. Packages
containing new files retain the existing explicit-path manual audit, commit and
push, followed by a truthful report naming the resulting commit. Do not bypass
containment with a fake or unresolvable commit SHA.

Whether mechanized or manual, the invariant rules remain:

1. Preserve unrelated dirty work.
2. Never use `git add .`, `git commit -a`, stash, reset, or force-push.
3. Run the smallest tests capable of falsifying the changed claim.
4. Record elapsed times and why higher tiers were not required.
5. Commit coherent work directly to `master`.
6. Fetch again before pushing and integrate safely without rewriting published
   history.

Because the isolated index intentionally leaves the shared index untouched, a
just-committed file may appear as `MM` in `git status`. That is expected. Do
not “repair” it with `git reset` or broad staging.

## 8. Checkpoint and renew

Checkpoint material progress before the lease expires:

```bash
s-f work report \
  --item <ITEM-ID> \
  --agent <STABLE-AGENT-ID> \
  --now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --base-commit <BASE-SHA> \
  --current-commit <CURRENT-SHA> \
  --changed-paths "<EXPLICIT PATHS>" \
  --disposition "committed:<SHA> pushed" \
  --tests "<COMMANDS, RESULTS, ELAPSED TIMES, AND SKIPPED-TIER REASONS>" \
  --receipts "<STABLE CERTIFICATE, REPORT, OR GATE IDS>" \
  --next "<EARLIEST REACHABLE NEXT GATE>"
```

Renew a continuing lease:

```bash
s-f work renew \
  --item <ITEM-ID> \
  --agent <STABLE-AGENT-ID> \
  --now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --expires "$(date -u -d '+12 hours' +%Y-%m-%dT%H:%M:%SZ)"
```

After an agent-process restart, use `s-f work resume` rather than acquiring a
second lease.

## 9. Block on another stream

Do not edit another team's plan or wait silently.

```bash
s-f work block \
  --item <ITEM-ID> \
  --agent <STABLE-AGENT-ID> \
  --need "<EXACT ARTIFACT, THEOREM, SCHEMA, OR DISPOSITION REQUIRED>" \
  --to-stream <TARGET-STREAM> \
  --typed dependency-artifact \
  --now "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

The target team inspects:

```bash
s-f inbox --stream <TARGET-STREAM>
```

A delivery must use stable artifact or receipt IDs and must be verified by an
independent actor before the dependent item is unblocked. A chat message,
uncommitted path, prose promise, or producer rerun is not a verified delivery.

## 10. Close out honestly

The final human-readable report must end with exactly one disposition:

```text
CLOSE-OUT: DONE — the complete stop condition is met
EVIDENCE: <stable path or receipt id>
```

or:

```text
CLOSE-OUT: OBSTRUCTED — the exact no-go or first obstruction is certified
EVIDENCE: <stable path or receipt id>
```

or:

```text
CLOSE-OUT: SHORTFALL — useful work landed, but the stop condition is incomplete
EVIDENCE: <stable path or receipt id, if available>
```

Then:

```bash
s-f work close \
  --item <ITEM-ID> \
  --agent <STABLE-AGENT-ID> \
  --report <REPORT-PATH> \
  --now "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

`SHORTFALL` keeps the scientific gate open. `OBSTRUCTED` means a scoped
negative result was established. `DONE` without evidence must be refused.

## 11. Actions reserved for the coordinator

Teams should ask the coordinator to:

- create a new work item;
- repair ambiguous legacy chronology with a new append-only event;
- replace free-text dependencies with stable typed dependencies;
- change a stream between `SHADOW` and `AUTHORITATIVE`;
- add a new stream;
- approve a new Science Forge capability for a consumer;
- resolve overlapping ownership of scientifically consequential files.

Never recycle a completed item by changing its objective. New science receives
a new stable work-item ID.

## 12. Minimal team instruction

A coordinator may send this short instruction together with a stream name:

> Read `planning/SCIENCE-FORGE-ADOPTION.md` completely. Follow its current
> rollout mode and capability boundaries. If your stream is authoritative,
> pull exactly one ready item with `s-f`, work only within its brief, preserve
> unrelated dirty paths, commit and push by explicit pathspec, checkpoint all
> receipts and tests, and close as DONE, OBSTRUCTED, or SHORTFALL. If the queue
> is empty, ambiguous, stale, or dependency-blocked, stop and notify the
> coordinator; do not repair or reinterpret the queue yourself. Conflux is not
> adopted unless the work item explicitly enables a consumer-specific,
> acceptance-gated Conflux path.
