(() => {
  "use strict";
  const DATA = window.MATRIX_EXPLORER_DATA;
  if (!DATA || DATA.schema_version !== "foundational-matrix-explorer-data-v2") return;

  const cells = new Map(DATA.cells.map(cell => [`${cell.foundation}|${cell.carrier}|${cell.obligation}`, cell]));
  const esc = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));

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
  for (const event of ["click", "input", "change"]) {
    document.addEventListener(event, () => window.setTimeout(enhanceInterface, 0));
  }
})();
