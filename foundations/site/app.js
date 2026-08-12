(() => {
  "use strict";
  const DATA = window.MATRIX_EXPLORER_DATA;
  if (!DATA) throw new Error("Generated matrix data are missing.");

  const STATUS = {
    LOCAL_RESULT: {label: "Local result", mark: "L", color: "#167958"},
    LITERATURE_RESULT: {label: "Literature result", mark: "R", color: "#2776a8"},
    PIECES_ONLY: {label: "Pieces only", mark: "P", color: "#c17b14"},
    PRIORITY_GAP: {label: "Priority gap", mark: "G", color: "#b94040"},
    MIGRATION_UNRESOLVED: {label: "Migration unresolved", mark: "?", color: "#7651a8"},
    NOT_MAPPED: {label: "Not mapped", mark: "·", color: "#87918c"},
  };
  const RELATION = {
    SUFFICIENT: "#167958", CONDITIONAL_SUFFICIENT: "#2776a8", REPRESENTATION_DEPENDENT: "#7651a8",
    COUNTEREXAMPLE_TO_METHOD: "#b94040", LITERATURE_CONTRAST: "#607069", OPEN_IMPLICATION: "#c17b14", NOT_SUFFICIENT: "#9a3c55",
  };
  const axis = Object.fromEntries(DATA.axes.map(a => [a.id, a]));
  const labels = Object.fromEntries(DATA.axes.flatMap(a => a.keys.map(k => [k.id, k])));
  const cellByKey = new Map(DATA.cells.map(c => [key(c), c]));
  const state = {
    view: "matrix", q: "", seededOnly: false, cell: null,
    selected: {
      FOUNDATION: new Set(axis.FOUNDATION.keys.map(x => x.id)),
      CARRIER: new Set(axis.CARRIER.keys.map(x => x.id)),
      REFINED_OBLIGATION: new Set(axis.REFINED_OBLIGATION.keys.map(x => x.id)),
      STATUS: new Set(Object.keys(STATUS)),
    },
    compare: [],
  };

  function key(c) { return `${c.foundation}|${c.carrier}|${c.obligation}`; }
  function esc(value) { return String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
  function title(id) { return labels[id]?.label || id.replaceAll("_", " ").toLowerCase(); }
  function list(value) { return Array.isArray(value) ? value : []; }
  function statusStyle(status) { return `--status:${STATUS[status].color}`; }
  function selected(axisId, id) { return state.selected[axisId].has(id); }
  function allSelected(axisId, ids) { return ids.every(id => selected(axisId, id)); }

  function parseHash() {
    const params = new URLSearchParams(location.hash.slice(1));
    if (params.get("view") && ["matrix", "graph", "ladder", "evidence"].includes(params.get("view"))) state.view = params.get("view");
    state.q = params.get("q") || "";
    state.seededOnly = params.get("seeded") === "1";
    state.cell = params.get("cell") || null;
    const mapping = {f: "FOUNDATION", c: "CARRIER", o: "REFINED_OBLIGATION", s: "STATUS"};
    for (const [param, axisId] of Object.entries(mapping)) {
      if (!params.has(param)) continue;
      const allowed = axisId === "STATUS" ? Object.keys(STATUS) : axis[axisId].keys.map(x => x.id);
      state.selected[axisId] = new Set(params.get(param).split(",").filter(x => allowed.includes(x)));
    }
  }

  function updateHash() {
    const params = new URLSearchParams();
    if (state.view !== "matrix") params.set("view", state.view);
    if (state.q) params.set("q", state.q);
    if (state.seededOnly) params.set("seeded", "1");
    if (state.cell) params.set("cell", state.cell);
    const mapping = {f: "FOUNDATION", c: "CARRIER", o: "REFINED_OBLIGATION", s: "STATUS"};
    for (const [param, axisId] of Object.entries(mapping)) {
      const allowed = axisId === "STATUS" ? Object.keys(STATUS) : axis[axisId].keys.map(x => x.id);
      if (!allSelected(axisId, allowed)) params.set(param, [...state.selected[axisId]].join(","));
    }
    history.replaceState(null, "", `${location.pathname}${location.search}${params.toString() ? "#" + params : ""}`);
  }

  function evidenceText(id) {
    const e = DATA.evidence[id];
    if (!e) return id;
    return [id, e.citation, e.result_kind, e.lifecycle, e.boundary, ...list(e.supported_statements), ...list(e.dependency_tags), ...list(e.does_not_establish)].join(" ");
  }

  function cellText(cell) {
    if (cell._search) return cell._search;
    cell._search = [title(cell.foundation), title(cell.carrier), title(cell.obligation), cell.status, cell.summary, cell.boundary, cell.parent_obligation, cell.migration_relation, ...cell.evidence.map(evidenceText)].join(" ").toLowerCase();
    return cell._search;
  }

  function matches(cell) {
    if (!selected("FOUNDATION", cell.foundation) || !selected("CARRIER", cell.carrier) || !selected("REFINED_OBLIGATION", cell.obligation) || !selected("STATUS", cell.status)) return false;
    if (state.seededOnly && !["PIECES_ONLY", "PRIORITY_GAP"].includes(cell.status)) return false;
    return !state.q || cellText(cell).includes(state.q.toLowerCase());
  }

  function filteredCells() { return DATA.cells.filter(matches); }

  function renderStats() {
    const items = [
      [DATA.counts.cartesian_total, "Cartesian coordinates", "#123d32"],
      [DATA.counts.emitted, "Emitted assessments", "#1c6b5a"],
      [DATA.counts.qualified, "Evidence-qualified", "#167958"],
      [DATA.counts.migration_unresolved, "Migration unresolved", STATUS.MIGRATION_UNRESOLVED.color],
      [DATA.counts.not_mapped, "Not mapped", STATUS.NOT_MAPPED.color],
      [DATA.counts.evidence_records, "Evidence records", "#2776a8"],
    ];
    document.getElementById("stats").innerHTML = items.map(([n, label, color]) => `<div class="stat" style="--tone:${color}"><b>${n}</b><span>${label}</span></div>`).join("");
  }

  function filterDefinition(id, label, options) {
    return `<details class="filter" data-filter="${id}"><summary>${esc(label)}: <b class="filter-count">${options.length}</b></summary><div class="filter-options">${options.map(o => `<label><input type="checkbox" value="${esc(o.id)}" checked><span>${esc(o.label)}${o.meaning ? `<small>${esc(o.meaning)}</small>` : ""}</span></label>`).join("")}</div></details>`;
  }

  function renderFilters() {
    const statuses = Object.entries(STATUS).map(([id, x]) => ({id, label: x.label, meaning: DATA.statuses.find(s => s.id === id)?.meaning}));
    document.getElementById("filters").innerHTML = [
      filterDefinition("FOUNDATION", "Regimes", axis.FOUNDATION.keys),
      filterDefinition("CARRIER", "Carriers", axis.CARRIER.keys),
      filterDefinition("REFINED_OBLIGATION", "Obligations", axis.REFINED_OBLIGATION.keys),
      filterDefinition("STATUS", "Evidence states", statuses),
    ].join("");
    document.querySelectorAll(".filter input").forEach(input => {
      const axisId = input.closest("details").dataset.filter;
      input.checked = selected(axisId, input.value);
      input.addEventListener("change", () => {
        input.checked ? state.selected[axisId].add(input.value) : state.selected[axisId].delete(input.value);
        updateFilterCount(axisId); refresh();
      });
    });
    Object.keys(state.selected).forEach(updateFilterCount);
  }

  function updateFilterCount(axisId) {
    const detail = document.querySelector(`[data-filter="${axisId}"]`);
    if (detail) detail.querySelector(".filter-count").textContent = state.selected[axisId].size;
  }

  function renderLegend() {
    return `<div class="legend">${Object.entries(STATUS).map(([id, x]) => `<span class="legend-item" title="${esc(DATA.statuses.find(s => s.id === id)?.meaning)}"><i class="swatch" style="--tone:${x.color}"></i><b>${x.mark}</b> ${esc(x.label)}</span>`).join("")}</div>`;
  }

  function renderMatrix() {
    const foundations = axis.FOUNDATION.keys;
    const carriers = axis.CARRIER.keys;
    const groups = DATA.groups.map(group => {
      const obligations = group.obligations.map(id => axis.REFINED_OBLIGATION.keys.find(x => x.id === id));
      const maps = obligations.map(obligation => {
        const rows = foundations.map(f => `<tr><th title="${esc(f.meaning)}">${esc(f.label)}</th>${carriers.map(c => {
          const cell = cellByKey.get(`${f.id}|${c.id}|${obligation.id}`);
          const visible = matches(cell);
          return `<td><button class="matrix-cell${visible ? "" : " filtered"}${state.cell === key(cell) ? " selected" : ""}" data-cell="${key(cell)}" data-mark="${STATUS[cell.status].mark}" style="${statusStyle(cell.status)}" aria-label="${esc(`${f.label}; ${c.label}; ${obligation.label}; ${STATUS[cell.status].label}`)}" title="${esc(`${STATUS[cell.status].label}: ${cell.summary}`)}"></button></td>`;
        }).join("")}</tr>`).join("");
        return `<article class="heatmap"><h4>${esc(obligation.label)}</h4><p class="meaning">${esc(obligation.meaning)}</p><table><thead><tr><th>Regime ↓ / carrier →</th>${carriers.map(c => `<th title="${esc(c.meaning)}"><span class="column-label">${esc(c.label)}</span></th>`).join("")}</tr></thead><tbody>${rows}</tbody></table></article>`;
      }).join("");
      return `<section class="matrix-group"><h3>${esc(group.label)}</h3><div class="heatmaps">${maps}</div></section>`;
    }).join("");
    document.getElementById("matrixGroups").innerHTML = renderLegend() + groups;
    document.querySelectorAll("[data-cell]").forEach(button => button.addEventListener("click", () => openCell(button.dataset.cell)));
  }

  function evidenceCard(id, compact = false) {
    const e = DATA.evidence[id];
    if (!e) return `<div class="evidence-link"><b>${esc(id)}</b><br>Unresolved evidence</div>`;
    if (e.kind === "LITERATURE") {
      const quality = e.artifact_status === "CONTENT_PINNED" ? "content" : "metadata";
      return `<article class="${compact ? "evidence-link" : "evidence-card"}"><span class="quality ${quality}">${esc(e.artifact_status)}</span><h3>${esc(id)}</h3><p>${esc(e.citation)}</p>${compact ? "" : `<p>${list(e.supported_statements).map(esc).join(" ")}</p><p class="boundary"><b>Boundary:</b> ${esc(e.boundary)}</p>`}<p>${e.stable_url ? `<a href="${esc(e.stable_url)}" target="_blank" rel="noreferrer">Primary record ↗</a> · ` : ""}<a href="${esc(e.ledger_link)}">Ledger</a></p></article>`;
    }
    return `<article class="${compact ? "evidence-link" : "evidence-card"}"><span class="quality content">LOCAL RESULT</span><h3>${esc(id)}</h3><p>${esc(e.result_kind || "Local certificate")} · ${esc(e.lifecycle || "")}</p>${compact ? "" : `<p>${list(e.dependency_tags).map(x => `<code>${esc(x)}</code>`).join(" ")}</p>${list(e.does_not_establish).length ? `<p class="boundary"><b>Does not establish:</b> ${esc(e.does_not_establish.join("; "))}</p>` : ""}`}<p><a href="${esc(e.result_link)}">Result JSON</a>${e.report_link ? ` · <a href="${esc(e.report_link)}">Report</a>` : ""}</p></article>`;
  }

  function neighbors(cell) {
    return DATA.cells.filter(other => {
      const differences = ["foundation", "carrier", "obligation"].filter(field => other[field] !== cell[field]).length;
      return differences === 1;
    });
  }

  function openCell(cellKey) {
    const cell = cellByKey.get(cellKey);
    if (!cell) return;
    state.cell = cellKey; updateHash();
    const directNeighbors = neighbors(cell);
    const body = `<p class="eyebrow">Cell inspector</p><h2 id="inspectorTitle">${esc(title(cell.obligation))}</h2><p class="coordinate">${esc(title(cell.foundation))} × ${esc(title(cell.carrier))} × ${esc(title(cell.obligation))}</p><p><span class="status-pill" style="${statusStyle(cell.status)}">${esc(STATUS[cell.status].label)}</span> ${cell.emitted ? "Emitted by the authoritative cube." : "Synthesized only to expose the full surface."}</p><h3>What is recorded</h3><p>${esc(cell.summary)}</p><p class="boundary"><b>Claim boundary:</b> ${esc(cell.boundary)}</p><dl><dt>Parent obligation</dt><dd>${esc(cell.parent_obligation || "none")}</dd><dt>Migration relation</dt><dd><code>${esc(cell.migration_relation)}</code></dd></dl><h3>Evidence (${cell.evidence.length})</h3><div class="evidence-list">${cell.evidence.length ? cell.evidence.map(id => evidenceCard(id, true)).join("") : "<p>No evidence is assigned. This is not an absence claim.</p>"}</div><h3>One-axis neighbors (${directNeighbors.length})</h3><div class="neighbor-list">${directNeighbors.map(n => `<button class="neighbor" data-neighbor="${key(n)}">${esc(title(n.foundation))} × ${esc(title(n.carrier))} × ${esc(title(n.obligation))}<i style="${statusStyle(n.status)}"></i><small>${esc(STATUS[n.status].label)}</small></button>`).join("")}</div><h3>Research actions</h3><div class="inspector-actions"><button id="pinCompare">Pin for comparison</button><button id="downloadBrief">Download investigation brief</button><button id="copyCellLink">Copy cell link</button></div>`;
    document.getElementById("inspectorBody").innerHTML = body;
    document.querySelectorAll("[data-neighbor]").forEach(x => x.addEventListener("click", () => openCell(x.dataset.neighbor)));
    document.getElementById("pinCompare").addEventListener("click", () => pinCompare(cellKey));
    document.getElementById("downloadBrief").addEventListener("click", () => downloadBrief(cell));
    document.getElementById("copyCellLink").addEventListener("click", copyPermalink);
    document.getElementById("inspector").classList.add("open");
    document.getElementById("inspector").setAttribute("aria-hidden", "false");
    document.getElementById("shade").hidden = false;
    renderMatrix();
  }

  function closeInspector() {
    document.getElementById("inspector").classList.remove("open");
    document.getElementById("inspector").setAttribute("aria-hidden", "true");
    document.getElementById("shade").hidden = true;
  }

  function openNodeInspector(node) {
    const incident = DATA.graph.edges.filter(e => e.from === node.id || e.to === node.id);
    document.getElementById("inspectorBody").innerHTML = `<p class="eyebrow">Implication node</p><h2 id="inspectorTitle">${esc(node.id)}</h2><p><span class="quality">${esc(node.kind)}</span></p><p>${esc(node.statement)}</p><h3>Typed relations</h3>${incident.map(e => `<p class="boundary" style="border-color:${RELATION[e.relation]}"><b>${esc(e.from)} → ${esc(e.to)}</b><br>${esc(e.relation)}${e.meaning ? `<br>${esc(e.meaning)}` : ""}<br><small>Evidence: ${esc(e.evidence.join(", ") || "none")}</small></p>`).join("")}`;
    document.getElementById("inspector").classList.add("open");
    document.getElementById("inspector").setAttribute("aria-hidden", "false");
    document.getElementById("shade").hidden = false;
  }

  function pinCompare(cellKey) {
    if (!state.compare.includes(cellKey)) state.compare.push(cellKey);
    state.compare = state.compare.slice(-2);
    renderCompareTray();
  }

  function renderCompareTray() {
    const tray = document.getElementById("compareTray");
    tray.hidden = state.compare.length === 0;
    document.getElementById("compareSummary").textContent = `${state.compare.length}/2 cells pinned`;
    document.getElementById("openCompare").disabled = state.compare.length !== 2;
  }

  function comparisonCard(cell) {
    return `<article><h3>${esc(title(cell.obligation))}</h3><p>${esc(title(cell.foundation))}<br>${esc(title(cell.carrier))}</p><p><span class="status-pill" style="${statusStyle(cell.status)}">${esc(STATUS[cell.status].label)}</span></p><p>${esc(cell.summary)}</p><p class="boundary">${esc(cell.boundary)}</p><p><b>Evidence:</b> ${esc(cell.evidence.join(", ") || "none")}</p></article>`;
  }

  function openComparison() {
    const cells = state.compare.map(x => cellByKey.get(x));
    document.getElementById("compareBody").innerHTML = `<p class="eyebrow">Controlled comparison</p><h2>Two cells, no implicit equivalence</h2><div class="comparison">${cells.map(comparisonCard).join("")}</div>`;
    document.getElementById("compareDialog").showModal();
  }

  function renderGraph() {
    document.getElementById("graphLegend").innerHTML = DATA.graph.relation_vocabulary.map(r => `<span class="legend-item"><i class="swatch" style="--tone:${RELATION[r]}"></i>${esc(r.replaceAll("_", " "))}</span>`).join("");
    const kinds = ["PHYSICAL_ASSUMPTION", "MATHEMATICAL_DATA", "MATHEMATICAL_CONSTRUCTION", "LITERATURE_RESULT"];
    const columns = {PHYSICAL_ASSUMPTION: 40, MATHEMATICAL_DATA: 395, MATHEMATICAL_CONSTRUCTION: 395, LITERATURE_RESULT: 790};
    const grouped = Object.fromEntries(kinds.map(k => [k, DATA.graph.nodes.filter(n => n.kind === k)]));
    const positions = {};
    let mathIndex = 0;
    for (const kind of kinds) for (const [i, node] of grouped[kind].entries()) {
      const index = ["MATHEMATICAL_DATA", "MATHEMATICAL_CONSTRUCTION"].includes(kind) ? mathIndex++ : i;
      positions[node.id] = {x: columns[kind], y: 55 + index * 105};
    }
    const edgePaths = DATA.graph.edges.map((e, i) => {
      const a = positions[e.from], b = positions[e.to];
      const sameColumn = a.x === b.x;
      const path = sameColumn ? `M ${a.x + 145} ${a.y + 35} C ${a.x + 260} ${a.y + 35}, ${b.x + 260} ${b.y + 35}, ${b.x + 145} ${b.y + 35}` : `M ${a.x + 290} ${a.y + 35} C ${(a.x + b.x) / 2 + 145} ${a.y + 35}, ${(a.x + b.x) / 2 + 145} ${b.y + 35}, ${b.x} ${b.y + 35}`;
      return `<path class="graph-edge" d="${path}" stroke="${RELATION[e.relation]}" marker-end="url(#arrow${i})"/><marker id="arrow${i}" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="${RELATION[e.relation]}"/></marker>`;
    }).join("");
    const nodes = DATA.graph.nodes.map(node => {
      const p = positions[node.id], words = node.statement.split(" ");
      const lines = []; let line = "";
      for (const word of words) { if ((line + " " + word).length > 38) { lines.push(line); line = word; } else line += (line ? " " : "") + word; }
      if (line) lines.push(line);
      return `<g class="graph-node" data-node="${esc(node.id)}" transform="translate(${p.x},${p.y})"><rect width="290" height="70"></rect><text x="12" y="17" class="node-kind">${esc(node.kind.replaceAll("_", " "))}</text>${lines.slice(0, 3).map((x, i) => `<text x="12" y="${36 + i * 14}">${esc(x)}</text>`).join("")}</g>`;
    }).join("");
    document.getElementById("graph").setAttribute("viewBox", "0 0 1120 780");
    document.getElementById("graph").innerHTML = `<defs></defs>${edgePaths}${nodes}`;
    document.querySelectorAll("[data-node]").forEach(g => g.addEventListener("click", () => openNodeInspector(DATA.graph.nodes.find(n => n.id === g.dataset.node))));
    document.getElementById("edgeTable").innerHTML = `<table class="edge-table"><thead><tr><th>From</th><th>Relation</th><th>To</th><th>Meaning / evidence</th></tr></thead><tbody>${DATA.graph.edges.map(e => `<tr><td>${esc(e.from)}</td><td><span class="quality" style="border-left:4px solid ${RELATION[e.relation]}">${esc(e.relation)}</span></td><td>${esc(e.to)}</td><td>${esc(e.meaning || "No stronger interpretation is licensed.")}<br><small>${esc(e.evidence.join(", ") || "No evidence assigned")}</small></td></tr>`).join("")}</tbody></table>`;
  }

  function renderLadder() {
    const colors = {CERTIFIED: STATUS.LOCAL_RESULT.color, FORMALIZATION_TARGET: STATUS.PIECES_ONLY.color, OPEN: STATUS.PRIORITY_GAP.color, CONDITIONAL_IMPORT_ONLY: STATUS.MIGRATION_UNRESOLVED.color};
    document.getElementById("ladder").innerHTML = DATA.ladder.map(step => {
      const established = step.establishes || step.establishes_if_formalized || [];
      const open = step.open || step.does_not_establish || (step.boundary ? [step.boundary] : []);
      return `<article class="ladder-step" style="--status:${colors[step.status] || STATUS.NOT_MAPPED.color}"><div><p class="ladder-level">${esc(step.level)}</p><span class="quality">${esc(step.status)}</span></div><div><h3>${esc(step.object)}</h3><p><b>Base:</b> ${esc(step.sufficient_base || step.candidate_upper_bound || "Not classified")}</p><div class="ladder-columns"><div><h4>Adds</h4><ul>${list(step.adds).map(x => `<li>${esc(x)}</li>`).join("")}</ul></div><div><h4>Establishes</h4><ul>${list(established).map(x => `<li>${esc(x)}</li>`).join("") || "<li>Conditional target only</li>"}</ul></div><div><h4>Still open / excluded</h4><ul>${list(open).map(x => `<li>${esc(x)}</li>`).join("")}</ul></div></div>${step.separation ? `<p class="boundary">${esc(step.separation)}</p>` : ""}</div></article>`;
    }).join("");
  }

  function renderEvidence() {
    const filtered = filteredCells();
    const referenced = new Set(filtered.flatMap(c => c.evidence));
    const q = state.q.toLowerCase();
    let ids = Object.keys(DATA.evidence).filter(id => referenced.has(id) || (q && evidenceText(id).toLowerCase().includes(q)));
    if (!state.q && filtered.length === DATA.cells.length) ids = Object.keys(DATA.evidence);
    document.getElementById("evidenceGrid").innerHTML = ids.length ? ids.map(id => evidenceCard(id)).join("") : `<p>No evidence records match the current cell filters.</p>`;
  }

  function setView(view) {
    state.view = view;
    document.querySelectorAll(".tab").forEach(x => x.classList.toggle("active", x.dataset.view === view));
    document.querySelectorAll(".view").forEach(x => x.classList.toggle("active", x.id === `${view}View`));
    updateHash();
  }

  function refresh() {
    renderMatrix(); renderEvidence();
    const cells = filteredCells();
    document.getElementById("filterSummary").textContent = `${cells.length} of ${DATA.cells.length} coordinates match. NOT_MAPPED remains an assessment state, not an absence claim.`;
    updateHash();
  }

  function resetFilters() {
    state.q = ""; state.seededOnly = false; state.cell = null;
    state.selected.FOUNDATION = new Set(axis.FOUNDATION.keys.map(x => x.id));
    state.selected.CARRIER = new Set(axis.CARRIER.keys.map(x => x.id));
    state.selected.REFINED_OBLIGATION = new Set(axis.REFINED_OBLIGATION.keys.map(x => x.id));
    state.selected.STATUS = new Set(Object.keys(STATUS));
    document.getElementById("search").value = ""; document.getElementById("seededOnly").checked = false;
    renderFilters(); refresh();
  }

  function download(filename, content, mime) {
    const blob = new Blob([content], {type: mime}); const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = filename; a.click(); URL.revokeObjectURL(url);
  }

  function exportJson() { download("foundations-matrix-filtered.json", JSON.stringify({filters: serializedFilters(), cells: filteredCells()}, null, 2), "application/json"); }
  function exportCsv() {
    const fields = ["foundation", "carrier", "obligation", "status", "emitted", "migration_relation", "evidence", "summary", "boundary"];
    const quote = value => `"${String(value ?? "").replaceAll('"', '""')}"`;
    download("foundations-matrix-filtered.csv", [fields.join(","), ...filteredCells().map(c => fields.map(f => quote(f === "evidence" ? c.evidence.join("; ") : c[f])).join(","))].join("\n") + "\n", "text/csv");
  }
  function serializedFilters() { return {query: state.q, seeded_only: state.seededOnly, selected: Object.fromEntries(Object.entries(state.selected).map(([k, v]) => [k, [...v]]))}; }
  function downloadBrief(cell) {
    const text = `# Candidate investigation: ${title(cell.obligation)}\n\n- Mathematical regime: ${title(cell.foundation)}\n- Carrier: ${title(cell.carrier)}\n- Evidence state: ${STATUS[cell.status].label}\n- Migration relation: ${cell.migration_relation}\n\n## Current record\n\n${cell.summary}\n\n## Boundary\n\n${cell.boundary}\n\n## Evidence to inspect\n\n${cell.evidence.length ? cell.evidence.map(x => `- ${x}`).join("\n") : "- No evidence assigned; run literature search without treating this as an absence result."}\n\n## Immediate research question\n\nWhat exact additional assumption, representation, or construction would move this coordinate one evidence state forward without crossing its declared boundary?\n`;
    download(`investigation-${cell.foundation}-${cell.carrier}-${cell.obligation}.md`.toLowerCase(), text, "text/markdown");
  }
  async function copyPermalink() {
    updateHash();
    try { await navigator.clipboard.writeText(location.href); } catch (_) {
      const input = document.createElement("textarea"); input.value = location.href; document.body.appendChild(input); input.select(); document.execCommand("copy"); input.remove();
    }
    document.getElementById("copyLink").textContent = "Copied"; setTimeout(() => document.getElementById("copyLink").textContent = "Copy permalink", 1200);
  }

  function bind() {
    document.querySelectorAll(".tab").forEach(button => button.addEventListener("click", () => setView(button.dataset.view)));
    document.getElementById("search").value = state.q;
    document.getElementById("search").addEventListener("input", event => { state.q = event.target.value.trim(); refresh(); });
    document.getElementById("seededOnly").checked = state.seededOnly;
    document.getElementById("seededOnly").addEventListener("change", event => { state.seededOnly = event.target.checked; refresh(); });
    document.getElementById("clearFilters").addEventListener("click", resetFilters);
    document.getElementById("copyLink").addEventListener("click", copyPermalink);
    document.getElementById("exportJson").addEventListener("click", exportJson);
    document.getElementById("exportCsv").addEventListener("click", exportCsv);
    document.getElementById("closeInspector").addEventListener("click", closeInspector);
    document.getElementById("shade").addEventListener("click", closeInspector);
    document.getElementById("openCompare").addEventListener("click", openComparison);
    document.getElementById("clearCompare").addEventListener("click", () => { state.compare = []; renderCompareTray(); });
    document.getElementById("closeCompare").addEventListener("click", () => document.getElementById("compareDialog").close());
    document.addEventListener("keydown", event => { if (event.key === "Escape") closeInspector(); });
  }

  parseHash(); renderStats(); renderFilters(); renderGraph(); renderLadder(); bind(); setView(state.view); refresh();
  document.getElementById("digest").textContent = `Canonical data digest: ${DATA.canonical_digest}`;
  if (state.cell) openCell(state.cell);
})();
