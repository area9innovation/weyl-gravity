# Certificate construction graph

This directory turns the repository's certificate provenance into two
reproducible Graphviz views.

- `certificate-dag.*` is the full technical dependency/import graph, laid
  out on a landscape canvas with prerequisite arrows running top to bottom.
  Outer boxes identify programme families; nested boxes organize dense
  families into topics such as causal propagation, nonlinear Cartan
  structure, anomaly/QME work, and Einstein-sector tests.
- `universe-building-dag.*` is the public milestone view used by Papers 98
  and 99.
- `certificate-graph-receipt.json` records input and output hashes, counts,
  lifecycle colors, and the evidence behind every public milestone.
- `certificate-graph-render-receipt.json` records the hashes of the rendered
  publication artifacts.
- `unresolved-dependencies.json` keeps duplicate identifiers, unresolved
  references, support-artifact references, hash mismatches, and cycles
  visible rather than silently dropping them.

The full graph is derived from JSON artifacts in a declared Git tree. The
public graph is curated in `universe_milestones.json`, but the generator fails
if any declared evidence certificate is missing. Neither graph changes a
certificate's lifecycle or promotes local/reduced evidence to a causal or
quantum claim.

Reciprocal certificate/verification-receipt, claim-table/team-signoff, and
preflight/readiness-ledger references are recorded as visible nonordering
cross-links. They are not scientific prerequisite arrows and therefore do not
manufacture dependency cycles in the DAG.

The nested topic is stored as `layout_group` in every generated node. It is
inferred only from the certificate path and identifier and is
presentation-only: it creates no dependency, changes no status color, and
does not alter the DAG's edge set.

Generate and verify:

```bash
python3 certificate_graph/build_certificate_dag.py --tree-ish HEAD
python3 -m unittest certificate_graph.test_build_certificate_dag
python3 certificate_graph/build_certificate_dag.py --tree-ish HEAD --check
```

The publication check fails on dependency cycles or missing public evidence.
The stronger maintenance gate also fails on duplicate result identifiers,
unresolved declared JSON references, or stale declared hashes:

```bash
python3 certificate_graph/build_certificate_dag.py --tree-ish HEAD \
  --check --strict-integrity
```

That strict gate is expected to remain red while any entry in
`unresolved-dependencies.json` is outstanding; the ordinary check does not
erase or misreport those inherited issues.

With Graphviz installed, render the publication artifacts:

```bash
python3 certificate_graph/build_certificate_dag.py --tree-ish HEAD --check --render
```

The committed render was produced with Graphviz 15.0.0 through
`@viz-js/viz` 3.28.0 because the build host had no system `dot` binary. The
fallback accepts the WebAssembly module path explicitly and therefore does
not create a hidden project dependency:

```bash
npm install --prefix /tmp/certificate-graph-viz @viz-js/viz@3.28.0
node certificate_graph/render_vizjs.mjs \
  /tmp/certificate-graph-viz/node_modules/@viz-js/viz/dist/viz.js \
  certificate_graph/universe-building-dag.dot svg \
  certificate_graph/universe-building-dag.svg
```

After rendering, record and verify the presentation artifacts:

```bash
python3 certificate_graph/record_render_receipt.py
python3 certificate_graph/record_render_receipt.py --check
```

The DOT and JSON files are the authoritative graph data. SVG, PNG, and PDF
are deterministic presentation views; changing a renderer cannot change a
certificate edge or lifecycle state.

The graph reads from Git rather than the working tree so another team's
uncommitted files cannot leak into a publication receipt.
