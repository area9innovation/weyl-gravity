# Contributing to the Forge substrate from the physics programme

The Forge toolchain + `lib/math` live in the tango repo
(default checkout `/home/alstrup/area9/tango/forge`). The physics programme
runs ON that substrate, and its agents are welcome to improve it directly —
under the substrate's own discipline, which is stricter than "it works here".
This page is the minimum you need; the authoritative operating manual is
`forge/CLAUDE.md` (read it before your first change).

## Which path to take

| Change | Path |
| --- | --- |
| Small fix or addition to an existing `lib/math` module (a missing accessor, a bug with a repro, a doc repair) | **Do it directly** under the rules below |
| A new mathematical layer or algorithm (a COMPLETENESS.md `M*` item) | **File a request** in `planning/forge-requests/` first — the forge side may already have it in flight, and the consumer-driven design conversation belongs in the request |
| A compiler or tooling defect | File `planning/forge-requests/bug-<slug>.json` with a minimal repro; do NOT work around it silently in your code |
| Physics-domain operators (Bach, Lee–Wald, tractors...) | Neither — those are domain packages above `lib/math`, in whichever repo owns them |

## The non-negotiables (from forge/CLAUDE.md, abbreviated)

1. **Pin or rebuild honestly.** CI pins `forge-v0.0.1` (see
   `ci/science-forge-shadow.sh`). For development, build from tango master:
   `cd forge && go build -o /tmp/forgebin ./cmd/forge; export FORGE_LIB=$PWD/lib`
   (absolute). `TMPDIR` must be disk-backed (`/home/alstrup/tmp` on this box).
2. **Everything you write must run, on both backends, under sanitizers.**
   `forge verify <file>` is the one command: type-check + C + native + ASan,
   cross-checked to one PASS/FAIL. Code that hasn't run on both backends
   doesn't exist.
3. **Every change ships its gate.** A new fn or module gets an expect-gated
   example (`forge/examples/<name>_gate.forge`, `// expect: N` header) whose
   checks are independent of the code under test (known-by-construction
   fixtures, cross-module rails, hand-derived recurrences coded in the gate).
   Run the touched module's existing gates too — no regressions.
4. **Exact vs numeric stay distinct types.** Never a float path inside an
   exact-tier module. Fail closed on unsupported inputs — a loud refusal,
   never a silent wrong answer.
5. **Ledger first.** A gap or defect you find gets filed
   (`forge/docs/limitations.md` for compiler/tooling; a forge-request for
   math layers) BEFORE or WITH the workaround — never silently absorbed.
6. **Shared-workspace git.** The tango working tree is shared by several
   agent sessions and is almost always dirty. Commit ONLY your files, by
   explicit pathspec, directly to master
   (`git commit -m "..." -- path/one path/two`), push immediately, never
   `commit -a`, never stash, never revert files you didn't change.
7. **Docs discipline.** `lib/math/COMPLETENESS.md` is the plan — if your
   change closes or moves one of its items, update that entry in the same
   commit. Do NOT grow `forge/AGENTS.md`/`CHEATSHEET.md` (map, not
   changelog).

## Style anchors

Study `lib/math/fmat.forge` (Field<T> genericity, witness threading) and
`lib/math/interval.forge` (exact/numeric separation, fail-closed
certification) before writing; match the surrounding module's conventions —
borrow-in operators where the family has them, scoped ownership, doc comments
on every pub fn, module banner first sentence ≤ 110 chars.

## The loop back

Anything you land that a certificate then depends on enters the certlab locks
automatically on the next re-lock sweep — your improvement becomes part of
the audited evidence chain. That is the point: the substrate and the science
harden together.
