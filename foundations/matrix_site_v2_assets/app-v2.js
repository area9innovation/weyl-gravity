(() => {
  "use strict";
  const DATA = window.MATRIX_EXPLORER_DATA;
  if (!DATA || DATA.schema_version !== "foundational-matrix-explorer-data-v2") return;
  const ATLAS = DATA.completion_atlas;

  const cells = new Map(DATA.cells.map(cell => [`${cell.foundation}|${cell.carrier}|${cell.obligation}`, cell]));
  const esc = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
  const words = value => String(value ?? "").toLowerCase().replaceAll("_", " ").replace(/\b\w/g, char => char.toUpperCase());

  function renderCompletionAtlas() {
    const root = document.getElementById("completionExplorer");
    if (!root || !ATLAS) return;
    const vocabulary = new Map(ATLAS.status_vocabulary.map(item => [item.id, item.meaning]));
    const statusCounts = {};
    ATLAS.branches.flatMap(branch => branch.stages).forEach(cell => { statusCounts[cell.status] = (statusCounts[cell.status] || 0) + 1; });
    const gateHeads = ATLAS.stages.map((stage, index) => `<th title="${esc(stage.completion_test)}"><span>S${index}</span><b>${esc(stage.name)}</b></th>`).join("");
    const branchRows = ATLAS.branches.map(branch => `<tr><th><b>${esc(branch.name)}</b><small>${esc(words(branch.relation_to_target))}</small></th>${branch.stages.map(cell => `<td><details class="completion-cell status-${esc(cell.status.toLowerCase())}"><summary title="${esc(vocabulary.get(cell.status))}">${esc(cell.status.replace("_CERTIFIED", ""))}</summary><p>${esc(cell.statement)}</p><p><b>Boundary:</b> ${esc(cell.boundary)}</p></details></td>`).join("")}</tr>`).join("");
    const legend = ATLAS.status_vocabulary.map(item => `<li><span class="completion-swatch status-${esc(item.id.toLowerCase())}"></span><b>${esc(words(item.id))}</b><small>${esc(item.meaning)}</small><em>${statusCounts[item.id] || 0}</em></li>`).join("");
    const routes = ATLAS.route_selection.map(item => `<article class="route-card"><p class="route-rank">${item.rank}</p><div><p class="eyebrow">${esc(words(item.branch))}</p><h3>${esc(words(item.route))}</h3><p>${esc(item.recommendation)}</p><dl><div><dt>Scientific leverage</dt><dd>${esc(words(item.scientific_leverage))}</dd></div><div><dt>Tractability</dt><dd>${esc(words(item.tractability))}</dd></div><div><dt>Dependency depth</dt><dd>${esc(words(item.dependency_depth))}</dd></div></dl></div></article>`).join("");
    const decisionChain = ATLAS.berger_h26_c26_decision_chain.map(item => `<li class="decision-${item.classification === "RANK_ONLY_FEASIBLE" ? "control" : "boundary"}"><span>${item.sequence}</span><div><h4>${esc(words(item.classification))}</h4><p>${esc(item.implication)}</p><p class="muted"><b>Does not imply:</b> ${esc(item.does_not_imply)}</p></div></li>`).join("");
    const gate = ATLAS.classical_import_reconciliation || {};
    const finite = ATLAS.strict_gate_a_progress?.finite_control || {};
    const minimal = ATLAS.strict_gate_a_progress?.minimal_cyclic_control || {};
    const causal = ATLAS.strict_causal_sign_transport || {};
    const gateProgress = finite.full_coordinates ? `<article class="completion-intro gate-progress"><div><p class="eyebrow">Two real repairs, with a hard boundary</p><h3>Finite residual control plus rank-${esc(minimal.pairing_rank)} minimal cyclicity</h3><p>The finite contraction retains ${Number(finite.full_coordinates).toLocaleString()} full and ${Number(finite.residual_coordinates).toLocaleString()} residual coordinates. On the separate minimal carrier, the canonical sign repair reduces ${esc(minimal.source_defects)} cyclicity defects to ${esc(minimal.translated_defects)} among ${esc(minimal.expanded_coefficients)} expanded coefficients.</p><p><a href="${esc(DATA.source_links.completion_sdr_report)}">Finite SDR</a> · <a href="${esc(DATA.source_links.completion_cyclic_report)}">Minimal cyclicity</a></p></div><aside><b>Gate A still closed</b><p>${esc(gate.receiver_verified_scoped_exports)} of 20 exports and ${esc(gate.receiver_verified_scoped_checks)} of 10 checks are receiver-verified in a same-theory scope, but there are still ${esc(gate.accepted_common_snapshot_hashes)} accepted common-snapshot hashes.</p><a href="${esc(DATA.source_links.completion_gate_report)}">Read Gate V5 reconciliation</a></aside></article>` : "";
    const causalProgress = causal.full_dimension ? `<article class="completion-intro gate-progress"><div><p class="eyebrow">New causal crosswalk</p><h3>The sign repair does not invalidate the ${esc(causal.full_dimension)}-row strict causal route</h3><p>The carrier splits as ${esc(causal.full_dimension)}=${esc(causal.algebraic_complement_dimension)}+${esc(causal.endpoint_dimension)}. Its transported convention has ${esc(causal.positive_signs)} positive and ${esc(causal.negative_signs)} negative signs and preserves the unary causal identities exactly.</p><p><a href="${esc(DATA.source_links.completion_transport_report)}">Read the causal transport result</a> · <a href="${esc(DATA.source_links.completion_transport)}">Inspect the certificate</a></p></div><aside><b>What remains open</b><p>Types and dimensions match, but common operator bytes and nonlinear q2/D compatibility are not established. The fixed finite transport wrapper is PRA; the analytic Green theorem's weakest base remains open.</p></aside></article>` : "";
    root.innerHTML = `
      <article class="completion-intro"><div><p class="eyebrow">Long-running programme objective</p><h3>Complete one causal route—or certify the first impossible gate</h3><p>${esc(ATLAS.answer)}</p></div><aside><b>Current fronts</b><p>Strict pure Weyl preserves the target theory. Berger is analytically furthest along. Neither is Lorentzian-quantum complete.</p><a href="${esc(DATA.source_links.completion_atlas_report)}">Read the audited V4 report</a></aside></article>
      ${gateProgress}
      ${causalProgress}
      <div class="section-head compact-head"><div><p class="eyebrow">77 separately typed cells</p><h2>Branch × causal-quantum gate</h2></div><p>Open any cell for its exact statement and boundary. Horizontal order is dependency order, not a numerical score.</p></div>
      <div class="completion-layout"><div class="completion-table-wrap"><table class="completion-table"><thead><tr><th>Architecture</th>${gateHeads}</tr></thead><tbody>${branchRows}</tbody></table></div><aside class="completion-legend"><h3>Evidence states</h3><ul>${legend}</ul></aside></div>
      <div class="section-head compact-head"><div><p class="eyebrow">Decision aid, not theorem ranking</p><h2>Where effort has the highest expected value</h2></div><p>Scientific leverage, tractability, and dependency depth remain visible instead of being collapsed into one opaque score.</p></div>
      <div class="route-grid">${routes}</div>
      <details class="decision-chain"><summary><span><b>Why the Berger 104-row route is no longer low-hanging fruit</b><small>Open the 11-step exact decision chain</small></span></summary><ol>${decisionChain}</ol><p class="completion-boundary"><b>Essential boundary:</b> the rational non-cone feasibility control proves that nilpotence and cohomology ranks are jointly possible. The scoped failures do not establish a general non-cone 104-row no-go.</p></details>
      <p class="completion-links"><a href="${esc(DATA.source_links.completion_atlas)}">Machine-readable atlas and pinned evidence</a> · <a href="${esc(DATA.source_links.completion_atlas_report)}">Human-readable report</a></p>`;
  }

  for (const cell of DATA.cells) {
    const migrationText = [cell.migration_status, cell.migration_rationale, ...(cell.migration_evidence || [])]
      .map(value => typeof value === "string" ? value : "")
      .join(" ")
      .toLowerCase();
    cell._search = `${cell._search || ""} ${migrationText}`;
  }

  function evidenceLink(id) {
    const item = DATA.evidence[id];
    if (!item) return `<li><code>${esc(id)}</code> — unresolved</li>`;
    const href = item.kind === "LITERATURE" ? item.ledger_link : item.result_link;
    const label = item.citation || item.result_kind || id;
    return `<li><a href="${esc(href)}"><code>${esc(id)}</code></a> — ${esc(label)}</li>`;
  }

  function selectedCell() {
    const key = new URLSearchParams(location.hash.slice(1)).get("cell");
    return key ? cells.get(key) : null;
  }

  function relabelStats() {
    document.querySelectorAll("#stats .stat span").forEach(label => {
      if (label.textContent === "Evidence-qualified") label.textContent = "Coverage classified";
      if (label.textContent === "Migration unresolved") label.textContent = "Migration pending";
    });
  }

  function removeLegacyPendingStatus() {
    const pending = document.querySelector('[data-filter="STATUS"] input[value="MIGRATION_UNRESOLVED"]');
    pending?.closest("label")?.remove();
    const count = document.querySelector('[data-filter="STATUS"] .filter-count');
    if (count) count.textContent = document.querySelectorAll('[data-filter="STATUS"] input').length;
    document.querySelectorAll(".legend-item").forEach(item => {
      if (item.textContent.includes("Migration unresolved")) item.remove();
    });
  }

  function enhanceInterface() {
    relabelStats();
    removeLegacyPendingStatus();
    enhanceInspector();
    renderCompletionAtlas();
    if (document.querySelector('[data-view="completion"]')?.classList.contains("active")) document.querySelector(".controls").hidden = true;
  }

  function enhanceInspector() {
    relabelStats();
    const cell = selectedCell();
    const body = document.getElementById("inspectorBody");
    if (!cell || !body || !document.getElementById("inspector")?.classList.contains("open")) return;
    body.querySelector("#migrationReview")?.remove();
    const oldLabel = [...body.querySelectorAll("dt")].find(node => node.textContent === "Migration relation");
    if (oldLabel) oldLabel.textContent = "V1 migration relation";
    const anchor = [...body.querySelectorAll("h3")].find(node => node.textContent.startsWith("One-axis neighbors"));
    if (!anchor) return;
    const section = document.createElement("section");
    section.id = "migrationReview";
    section.innerHTML = `<h3>Migration review</h3>
      <p><span class="quality">${esc(cell.migration_status)}</span></p>
      <p>${esc(cell.migration_rationale)}</p>
      <p><b>Evidence inspected for migration (${(cell.migration_evidence || []).length})</b></p>
      ${(cell.migration_evidence || []).length ? `<ul>${cell.migration_evidence.map(evidenceLink).join("")}</ul>` : "<p>No parent evidence was assigned. This is not an absence claim.</p>"}
      <p><a href="${esc(DATA.source_links.migration_audit)}">112-decision migration audit</a> · <a href="${esc(DATA.source_links.full_surface_audit)}">175-coordinate surface audit</a> · <a href="${esc(DATA.source_links.full_surface_audit_report)}">Surface-audit report</a></p>`;
    body.insertBefore(section, anchor);
  }

  enhanceInterface();
  if (new URLSearchParams(location.hash.slice(1)).get("view") === "completion") {
    document.querySelector('[data-view="completion"]')?.click();
  }
  for (const event of ["click", "input", "change"]) {
    document.addEventListener(event, () => window.setTimeout(enhanceInterface, 0));
  }
})();
