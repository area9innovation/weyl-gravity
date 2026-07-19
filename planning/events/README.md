# planning/events — append-only work-item transition log

This directory is the append-only event log for the programme work items in
`planning/work-items/`. It follows the Science Forge model (GUIDE.md "law 2:
append-only history"):

- A work item's `.json` file is **never rewritten**. Its state changes by
  appending ONE content-addressed event file here — a `WORK_ITEM_TRANSITIONED`
  record with `{event_kind, actor, when, payload:{target, to_state, note}}` and
  a `TRANSITIONS -> <work-id>` edge.
- The **effective state** of an item is its file's base `state` folded over
  these events: the event with the latest `(when, id)` wins.
- Events are written by `sfc work-event`, not by hand — see `planning/README.md`.
  The tool is pointed at `planning/work-items/` and resolves this log through
  `planning/work-items/events` (a symlink to this directory), so a transition
  lands here as one immutable file.

Nothing in this directory is a claim; it is coordination state. Repairs,
re-assignments, and obstructions are all new events, never edits.
