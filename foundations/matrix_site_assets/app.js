(() => {
  "use strict";
  const DATA = window.MATRIX_EXPLORER_DATA;
  if (!DATA) throw new Error("Generated matrix data are missing.");
  const VIABILITY = window.THEORY_VIABILITY_DATA;
  if (!VIABILITY) throw new Error("Generated theory-profile assessment is missing.");
  const ASSEMBLIES = window.THEORY_ASSEMBLY_DATA;
  if (!ASSEMBLIES) throw new Error("Generated theory-assembly assessment is missing.");

  const STATUS = {
    LOCAL_RESULT: {label: "Local result", mark: "L", color: "#167958"},
    LITERATURE_RESULT: {label: "Literature result", mark: "R", color: "#2776a8"},
    PIECES_ONLY: {label: "Pieces only", mark: "P", color: "#c17b14"},
    PRIORITY_GAP: {label: "Priority gap", mark: "G", color: "#b94040"},
    REVIEWED_GAP: {label: "Reviewed open gap", mark: "O", color: "#6f5b9a"},
    MIGRATION_UNRESOLVED: {label: "Migration unresolved", mark: "?", color: "#7651a8"},
    NOT_MAPPED: {label: "Not mapped", mark: "·", color: "#87918c"},
  };

  // A cell status names only its strongest grade: a direct local result outranks
  // a direct literature result, so a coordinate holding both used to show only
  // "L".  The per-evidence roles carried by the cube let both be displayed.
  const ROLE = {
    DIRECT_LOCAL: {label: "Direct local result", kind: "LOCAL", badge: "L"},
    DIRECT_LITERATURE: {label: "Direct literature result", kind: "LITERATURE", badge: "R"},
    SUPPORTING: {label: "Supporting ingredient", kind: null, badge: "·"},
    UNREVIEWED: {label: "Directness unreviewed", kind: null, badge: "?"},
  };
  const KIND_STATUS = {LOCAL: "LOCAL_RESULT", LITERATURE: "LITERATURE_RESULT"};
  const KIND_UPPER = {LOCAL: "L", LITERATURE: "R"};
  const KIND_LOWER = {LOCAL_RESULT: "l", LITERATURE: "r"};
  const DUAL = {mark: "LR", label: "Local + literature result", meaning: "This coordinate carries a direct local result and a direct literature result. Both are certified direct for this obligation; the status colour keeps the higher-ranked grade."};
  const RELATION = {
    SUFFICIENT: "#167958", CONDITIONAL_SUFFICIENT: "#2776a8", REPRESENTATION_DEPENDENT: "#7651a8",
    COUNTEREXAMPLE_TO_METHOD: "#b94040", LITERATURE_CONTRAST: "#607069", OPEN_IMPLICATION: "#c17b14", NOT_SUFFICIENT: "#9a3c55",
  };
  const RELATION_LABEL = {
    SUFFICIENT: "Enough for this step",
    CONDITIONAL_SUFFICIENT: "Enough with conditions",
    REPRESENTATION_DEPENDENT: "Depends on the coding",
    COUNTEREXAMPLE_TO_METHOD: "This method fails",
    LITERATURE_CONTRAST: "Literature contrast",
    OPEN_IMPLICATION: "Unproved bridge",
    NOT_SUFFICIENT: "Not enough by itself",
  };
  const RELATION_DESCRIPTION = {
    SUFFICIENT: "The source supplies what this particular target step needs.",
    CONDITIONAL_SUFFICIENT: "The source is enough only after named extra conditions are supplied.",
    REPRESENTATION_DEPENDENT: "The implication relies on what information is included in the representation.",
    COUNTEREXAMPLE_TO_METHOD: "The source exposes why this proposed route cannot establish the target.",
    LITERATURE_CONTRAST: "The results use different assumptions or representations and should be compared, not merged.",
    OPEN_IMPLICATION: "This is a concrete research bridge; no proof is currently certified.",
    NOT_SUFFICIENT: "The source is useful but additional mathematical input is required.",
  };
  const RELATION_DASH = {OPEN_IMPLICATION: "8 6", COUNTEREXAMPLE_TO_METHOD: "3 5", NOT_SUFFICIENT: "10 5"};
  const GRAPH_PATHWAYS = [
    {
      id: "coded-evolution", title: "1. Coded evolution toward causal propagation",
      subtitle: "The main construction chain, with two physical inputs shown as open bridges.",
      panel: [20, 20, 1160, 800],
      nodes: {
        "P-ERROR-CONTROL": [470, 85], "M-TAIL-MODULUS": [470, 200], "M-CODED-HILBERT": [470, 315],
        "M-COEFFICIENT-WEAK": [470, 430], "M-SPACETIME-DISTRIBUTION": [470, 545], "M-CAUSAL-GREEN": [470, 660],
        "P-FINITE-ENERGY": [70, 200], "P-LOCAL-CAUSALITY": [70, 660],
      },
      edges: [
        ["P-ERROR-CONTROL", "M-TAIL-MODULUS"], ["M-TAIL-MODULUS", "M-CODED-HILBERT"],
        ["P-FINITE-ENERGY", "M-TAIL-MODULUS"], ["M-CODED-HILBERT", "M-COEFFICIENT-WEAK"],
        ["M-COEFFICIENT-WEAK", "M-SPACETIME-DISTRIBUTION"], ["M-SPACETIME-DISTRIBUTION", "M-CAUSAL-GREEN"],
        ["P-LOCAL-CAUSALITY", "M-CAUSAL-GREEN"],
      ],
    },
    {
      id: "finite-route", title: "2. The finite spectral route and its causal obstruction",
      subtitle: "Finite exact dynamics is certified; using that projection to prove causal support is ruled out.",
      panel: [20, 840, 1160, 220],
      nodes: {"P-FINITE-RESOLUTION": [80, 930], "M-FINITE-LAURENT": [475, 930], "M-CAUSAL-GREEN": [870, 930]},
      edges: [["P-FINITE-RESOLUTION", "M-FINITE-LAURENT"], ["M-FINITE-LAURENT", "M-CAUSAL-GREEN"]],
    },
    {
      id: "literature-contrast", title: "3. A representation-sensitive literature contrast",
      subtitle: "The computable and noncomputable results are not contradictory because their representations differ.",
      panel: [20, 1080, 1160, 220],
      nodes: {"L-WEIHRAUCH-ZHONG": [220, 1170], "L-POUR-EL-RICHARDS": [730, 1170]},
      edges: [["L-WEIHRAUCH-ZHONG", "L-POUR-EL-RICHARDS"]],
    },
  ];
  const CAMP_KIND_LABEL = {
    REFERENCE_TRADITION: "Reference tradition",
    RESEARCH_TRADITION: "Research tradition",
    NAMED_RESEARCH_PROGRAMME: "Named programme",
    METHODOLOGICAL_TRADITION: "Methodological tradition",
    REPOSITORY_PROGRAMME: "This repository's programme",
  };
  const GUIDE_GROUPS = {
    FOUNDATION: [
      {title: "The familiar baseline", summary: "Use the ordinary classical mathematics found in most physics textbooks.", ids: ["CLASSICAL_STANDARD"]},
      {title: "Audit the hidden axioms", summary: "Keep classical reasoning, but ask how much arithmetic, set existence, or Choice a proof actually consumes.", ids: ["WEAK_ARITHMETIC", "WEAK_CHOICE_ZF"]},
      {title: "Change what proof or truth means", summary: "Demand constructions, algorithms, or truth interpreted inside a different logical universe.", ids: ["CONSTRUCTIVE_COMPUTABLE", "TOPOS_INTERNAL"]},
      {title: "Restrict the size of the world", summary: "Work with finite data or finitely many modes and separately account for any return to an infinite continuum.", ids: ["FINITE_DISCRETE"]},
    ],
    CARRIER: [
      {title: "Small enough to check exactly", summary: "Use finite matrices and algebraic data whose identities can be decided without approximation.", ids: ["FINITE_EXACT"]},
      {title: "States as vectors with geometry", summary: "Use positive or indefinite inner products to encode amplitudes, norms, gauge directions, and evolution.", ids: ["HILBERT_OPERATOR", "KREIN_INDEFINITE"]},
      {title: "Observables and regions first", summary: "Begin with algebras, regions, or logical relations instead of a preferred wavefunction or set of points.", ids: ["ALGEBRAIC_CSTAR", "LOCALIC_SYNTHETIC"]},
      {title: "Continuum fields on spacetime", summary: "Use geometry, differential equations, distributions, and response operators for fields that vary continuously.", ids: ["SMOOTH_DISTRIBUTIONAL"]},
    ],
    REFINED_OBLIGATION: [
      {title: "1. Define the physical possibilities", summary: "Specify what exists, how states are encoded, what can be measured, and how probabilities arise.", ids: ["KINEMATICS_OBSERVABLES", "STATE_EXISTENCE", "STATE_REPRESENTATION", "PROBABILITY_RULE", "PHYSICAL_STATE_SELECTION"]},
      {title: "2. Make the theory evolve and carry signals", summary: "Construct time evolution, prove it behaves well, and identify causal response.", ids: ["GENERATOR_SPECTRAL_DYNAMICS", "EVOLUTION_WELLPOSEDNESS", "CAUSAL_PROPAGATION_GREEN"]},
      {title: "3. Handle redundancy and genuine coupling", summary: "Separate gauge description from physical content and build nontrivial interactions.", ids: ["GAUGE_BV_COHOMOLOGY", "INTERACTION_CONSTRUCTION"]},
      {title: "4. Keep an interacting quantum theory consistent", summary: "Classify possible corrections and failures, renormalize singular products, and restore quantum gauge consistency before transferring corrections.", ids: ["COUNTERTERM_CLASSIFICATION", "ANOMALY_CLASSIFICATION", "RENORMALIZED_PRODUCTS", "QME_RESTORATION", "RESIDUAL_QUANTUM_TRANSFER"]},
      {title: "5. Return to observation or a known limit", summary: "Connect the formal construction to measured quantities, a continuum limit, or an established theory.", ids: ["RECONSTRUCTION_LIMITS"]},
    ],
  };
  const GUIDE_GLOSSARY = [
    ["Axiom of Choice", "A principle that permits simultaneous selections from many nonempty sets. Ordinary physics mathematics often uses it indirectly through bases, compactness, or extension theorems."],
    ["Hilbert space", "A complete positive-inner-product vector space: the standard home for quantum states and spectral operators."],
    ["Krein space", "An inner-product space with positive and negative directions. It can retain gauge or ghost structure, but needs extra work to identify physical probabilities."],
    ["PDE / Green operator", "A partial differential equation governs a continuum field; a retarded or advanced Green operator describes its response to a source."],
    ["Gauge / BV / BRST", "Tools for theories with redundant descriptions. They organize the physical content and the consistency conditions of interactions and quantization."],
    ["QME", "The quantum master equation: the BV condition that quantum corrections still respect gauge consistency."],
    ["Topos", "A mathematical universe with its own internal logic, often used to express contextual or point-free versions of spaces and observables."],
  ];
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
    viability: {
      preset: VIABILITY.presets[0].id,
      obligations: new Set(VIABILITY.presets[0].obligations),
      foundation: axis.FOUNDATION.keys[0].id,
      carriers: new Set(axis.CARRIER.keys.map(x => x.id)),
      profile: null,
      paretoOnly: false,
    },
    assembly: ASSEMBLIES.assemblies[0].id,
    assemblyPanel: "models",
  };

  function key(c) { return `${c.foundation}|${c.carrier}|${c.obligation}`; }
  function esc(value) { return String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
  function title(id) { return labels[id]?.label || id.replaceAll("_", " ").toLowerCase(); }
  function list(value) { return Array.isArray(value) ? value : []; }
  function statusStyle(status) { return `--status:${STATUS[status].color}`; }
  function cellRoles(cell) { return cell.evidence_roles || {}; }
  function directKinds(cell) {
    const present = new Set(Object.values(cellRoles(cell)).map(role => ROLE[role]?.kind).filter(Boolean));
    return ["LOCAL", "LITERATURE"].filter(kind => present.has(kind));
  }
  function isDual(cell) { return directKinds(cell).length === 2; }
  function supportingKinds(cell) {
    const kinds = new Set();
    Object.entries(cellRoles(cell)).forEach(([id, role]) => {
      if (role === "SUPPORTING" && DATA.evidence[id]) kinds.add(KIND_LOWER[DATA.evidence[id].kind]);
    });
    return kinds;
  }
  // Upper case is a certified direct grade; lower case is a supporting ingredient
  // of that kind.  A lower-case letter is suppressed when its kind already shows
  // as a grade, so an "L" cell never renders "Ll".  Unreviewed records add
  // nothing: an ingredient claim is a claim, and they have not been reviewed.
  function cellMark(cell) {
    const direct = directKinds(cell).map(kind => KIND_UPPER[kind]);
    const upper = direct.length ? direct.join("") : STATUS[cell.status].mark;
    const support = supportingKinds(cell);
    return upper + ["l", "r"].filter(x => support.has(x) && !upper.includes(x.toUpperCase())).join("");
  }
  function supportingLabels(cell) {
    const support = supportingKinds(cell), direct = directKinds(cell);
    return [["l", "LOCAL", "local"], ["r", "LITERATURE", "literature"]]
      .filter(([letter, kind]) => support.has(letter) && !direct.includes(kind)).map(([, , name]) => name);
  }
  function markExplanation(cell) {
    const support = supportingLabels(cell);
    return gradeLabels(cell) + (support.length ? `; supporting ${support.join(" and ")} ingredients` : "");
  }
  // Every grade this cell may be read as: its status, plus any certified direct kind.
  function cellGrades(cell) {
    const grades = new Set([cell.status]);
    directKinds(cell).forEach(kind => grades.add(KIND_STATUS[kind]));
    return grades;
  }
  function cellStyle(cell) {
    if (!isDual(cell)) return statusStyle(cell.status);
    const alt = cell.status === "LOCAL_RESULT" ? STATUS.LITERATURE_RESULT.color : STATUS.LOCAL_RESULT.color;
    return `${statusStyle(cell.status)};--alt:${alt}`;
  }
  function gradeLabels(cell) { return [...cellGrades(cell)].map(grade => STATUS[grade].label).join(" + "); }
  function selected(axisId, id) { return state.selected[axisId].has(id); }
  function allSelected(axisId, ids) { return ids.every(id => selected(axisId, id)); }

  function parseHash() {
    const params = new URLSearchParams(location.hash.slice(1));
    if (params.get("view") && ["matrix", "viability", "assemblies", "guide", "graph", "ladder", "evidence"].includes(params.get("view"))) state.view = params.get("view");
    if (ASSEMBLIES.assemblies.some(item => item.id === params.get("assembly"))) state.assembly = params.get("assembly");
    if (["models", "programmes", "ledgers"].includes(params.get("panel"))) state.assemblyPanel = params.get("panel");
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
    if (state.view === "assemblies") {
      params.set("assembly", state.assembly);
      if (state.assemblyPanel !== "models") params.set("panel", state.assemblyPanel);
    }
    if (state.view === "passports") {
      const requestedPassport = new URLSearchParams(location.hash.slice(1)).get("passport");
      if (DATA.theory_passports?.passports?.some(item => item.id === requestedPassport)) params.set("passport", requestedPassport);
    }
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
    cell._search = [title(cell.foundation), title(cell.carrier), title(cell.obligation), cell.status, cell.summary, cell.boundary, cell.parent_obligation, cell.migration_relation, ...Object.values(cellRoles(cell)).map(role => ROLE[role]?.label || role), ...cell.evidence.map(evidenceText)].join(" ").toLowerCase();
    return cell._search;
  }

  function matches(cell) {
    if (!selected("FOUNDATION", cell.foundation) || !selected("CARRIER", cell.carrier) || !selected("REFINED_OBLIGATION", cell.obligation)) return false;
    if (![...cellGrades(cell)].some(grade => selected("STATUS", grade))) return false;
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
      [DATA.counts.reviewed_gap, "Reviewed open gaps", STATUS.REVIEWED_GAP.color],
      [DATA.counts.not_mapped, "Not mapped", STATUS.NOT_MAPPED.color],
      [DATA.counts.evidence_records, "Evidence records", "#2776a8"],
    ].filter(([count, label]) => !["Migration unresolved", "Not mapped"].includes(label) || count > 0);
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
    const statuses = Object.entries(STATUS).map(([id, x]) => `<span class="legend-item" title="${esc(DATA.statuses.find(s => s.id === id)?.meaning || x.label)}"><i class="swatch" style="--tone:${x.color}"></i><b>${x.mark}</b> ${esc(x.label)}</span>`).join("");
    const dual = `<span class="legend-item" title="${esc(DUAL.meaning)}"><i class="swatch swatch-dual" style="--tone:${STATUS.LOCAL_RESULT.color};--tone-alt:${STATUS.LITERATURE_RESULT.color}"></i><b>${DUAL.mark}</b> ${esc(DUAL.label)}</span>`;
    const note = `<p class="legend-note"><b>Upper case is a certified direct grade; lower case is a supporting ingredient of that kind.</b> So <b>Pl</b> holds local ingredients, <b>Pr</b> literature ingredients, <b>Plr</b> both, and <b>Lr</b> or <b>Rl</b> a result of one kind with ingredients of the other. An ingredient is not a result, and a record whose directness is unreviewed adds no letter.</p>`;
    return `<div class="legend">${statuses}${dual}</div>${note}`;
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
          const dual = isDual(cell);
          return `<td><button class="matrix-cell${visible ? "" : " filtered"}${state.cell === key(cell) ? " selected" : ""}" data-cell="${key(cell)}" data-mark="${cellMark(cell)}" data-marklen="${cellMark(cell).length}"${dual ? ' data-dual="1"' : ""} style="${cellStyle(cell)}" aria-label="${esc(`${f.label}; ${c.label}; ${obligation.label}; ${markExplanation(cell)}`)}" title="${esc(`${cellMark(cell)} — ${markExplanation(cell)}: ${cell.summary}`)}"></button></td>`;
        }).join("")}</tr>`).join("");
        return `<article class="heatmap"><h4>${esc(obligation.label)}</h4><p class="meaning">${esc(obligation.meaning)}</p><table><thead><tr><th>Regime ↓ / carrier →</th>${carriers.map(c => `<th title="${esc(c.meaning)}"><span class="column-label">${esc(c.label)}</span></th>`).join("")}</tr></thead><tbody>${rows}</tbody></table></article>`;
      }).join("");
      return `<section class="matrix-group"><h3>${esc(group.label)}</h3><div class="heatmaps">${maps}</div></section>`;
    }).join("");
    document.getElementById("matrixGroups").innerHTML = renderLegend() + groups;
    document.querySelectorAll("[data-cell]").forEach(button => button.addEventListener("click", () => openCell(button.dataset.cell)));
  }

  function roleBadge(role) {
    if (!role || !ROLE[role]) return "";
    const direct = ROLE[role].kind ? " role-direct" : "";
    return `<span class="role-badge${direct}" title="${esc(roleMeaning(role))}">${esc(ROLE[role].label)}</span>`;
  }

  function roleMeaning(role) {
    return list(DATA.evidence_role_vocabulary).find(x => x.id === role)?.meaning || ROLE[role]?.label || role;
  }

  function evidenceCard(id, compact = false, role = null) {
    const e = DATA.evidence[id];
    if (!e) return `<div class="evidence-link"><b>${esc(id)}</b><br>Unresolved evidence</div>`;
    const badge = roleBadge(role);
    if (e.kind === "LITERATURE") {
      const quality = e.artifact_status === "CONTENT_PINNED" ? "content" : "metadata";
      return `<article class="${compact ? "evidence-link" : "evidence-card"}"><span class="quality ${quality}">${esc(e.artifact_status)}</span>${badge}<h3>${esc(id)}</h3><p>${esc(e.citation)}</p>${compact ? "" : `<p>${list(e.supported_statements).map(esc).join(" ")}</p><p class="boundary"><b>Boundary:</b> ${esc(e.boundary)}</p>`}<p>${e.stable_url ? `<a href="${esc(e.stable_url)}" target="_blank" rel="noreferrer">Primary record ↗</a> · ` : ""}<a href="${esc(e.ledger_link)}">Ledger</a></p></article>`;
    }
    return `<article class="${compact ? "evidence-link" : "evidence-card"}"><span class="quality content">LOCAL RESULT</span>${badge}<h3>${esc(id)}</h3><p>${esc(e.result_kind || "Local certificate")} · ${esc(e.lifecycle || "")}</p>${compact ? "" : `<p>${list(e.dependency_tags).map(x => `<code>${esc(x)}</code>`).join(" ")}</p>${list(e.does_not_establish).length ? `<p class="boundary"><b>Does not establish:</b> ${esc(e.does_not_establish.join("; "))}</p>` : ""}`}<p><a href="${esc(e.result_link)}">Result JSON</a>${e.report_link ? ` · <a href="${esc(e.report_link)}">Report</a>` : ""}</p></article>`;
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
    const body = `<p class="eyebrow">Cell inspector</p><h2 id="inspectorTitle">${esc(title(cell.obligation))}</h2><p class="coordinate">${esc(title(cell.foundation))} × ${esc(title(cell.carrier))} × ${esc(title(cell.obligation))}</p><p><span class="status-pill" style="${statusStyle(cell.status)}">${esc(STATUS[cell.status].label)}</span>${isDual(cell) ? ` <span class="status-pill" style="${statusStyle(KIND_STATUS[directKinds(cell).find(kind => KIND_STATUS[kind] !== cell.status)])}">${esc(STATUS[KIND_STATUS[directKinds(cell).find(kind => KIND_STATUS[kind] !== cell.status)]].label)}</span>` : ""} ${cell.emitted ? "Emitted by the authoritative cube." : "Synthesized only to expose the full surface."}</p><h3>What is recorded</h3><p>${esc(cell.summary)}</p><p class="boundary"><b>Claim boundary:</b> ${esc(cell.boundary)}</p><dl><dt>Parent obligation</dt><dd>${esc(cell.parent_obligation || "none")}</dd><dt>Migration relation</dt><dd><code>${esc(cell.migration_relation)}</code></dd></dl><h3>Evidence (${cell.evidence.length})</h3>${directKinds(cell).length ? `<p class="direct-grades">Directly supported by: <b>${esc(directKinds(cell).map(kind => STATUS[KIND_STATUS[kind]].label.toLowerCase()).join(" and "))}</b>.${supportingLabels(cell).length ? ` Supporting ${esc(supportingLabels(cell).join(" and "))} ingredients are also attached and do not compose the result.` : ""} A record shown as unreviewed is not a finding that it fails to support this cell.</p>` : `<p class="direct-grades">No attached record is registered as a direct support at this obligation.${supportingLabels(cell).length ? ` Supporting ${esc(supportingLabels(cell).join(" and "))} ingredients are attached; they do not compose the result.` : ""} That is a review gap, not an absence claim.</p>`}<div class="evidence-list">${cell.evidence.length ? cell.evidence.map(id => evidenceCard(id, true, cellRoles(cell)[id])).join("") : "<p>No evidence is assigned. This is not an absence claim.</p>"}</div><h3>One-axis neighbors (${directNeighbors.length})</h3><div class="neighbor-list">${directNeighbors.map(n => `<button class="neighbor" data-neighbor="${key(n)}">${esc(title(n.foundation))} × ${esc(title(n.carrier))} × ${esc(title(n.obligation))}<i style="${statusStyle(n.status)}"></i><small>${esc(gradeLabels(n))}</small></button>`).join("")}</div><h3>Research actions</h3><div class="inspector-actions"><button id="pinCompare">Pin for comparison</button><button id="downloadBrief">Download investigation brief</button><button id="copyCellLink">Copy cell link</button></div>`;
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
    document.getElementById("inspectorBody").innerHTML = `<p class="eyebrow">Implication node</p><h2 id="inspectorTitle">${esc(node.label || node.id)}</h2><p><span class="quality">${esc(node.kind.replaceAll("_", " "))}</span> <code>${esc(node.id)}</code></p><p>${esc(node.statement)}</p><h3>Typed relations</h3>${incident.map(e => `<p class="boundary" style="border-color:${RELATION[e.relation]}"><b>${esc(DATA.graph.nodes.find(x => x.id === e.from)?.label || e.from)} → ${esc(DATA.graph.nodes.find(x => x.id === e.to)?.label || e.to)}</b><br><strong>${esc(RELATION_LABEL[e.relation])}</strong><br>${esc(e.meaning)}<br><small>Evidence: ${esc(e.evidence.join(", ") || "No direct certificate yet")}</small></p>`).join("")}`;
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
    const nodeById = Object.fromEntries(DATA.graph.nodes.map(node => [node.id, node]));
    const edgeByPair = new Map(DATA.graph.edges.map((edge, index) => [`${edge.from}|${edge.to}`, {...edge, index}]));
    const usedRelations = DATA.graph.relation_vocabulary.filter(relation => DATA.graph.edges.some(edge => edge.relation === relation));
    document.getElementById("graphLegend").innerHTML = usedRelations.map(relation => `<span class="legend-item relation-legend" title="${esc(RELATION_DESCRIPTION[relation])}"><i class="swatch" style="--tone:${RELATION[relation]}"></i><b>${esc(RELATION_LABEL[relation])}</b></span>`).join("");

    const width = 250, height = 88;
    const wrap = (text, limit = 39) => {
      const lines = []; let line = "";
      for (const word of text.split(" ")) { if (line && `${line} ${word}`.length > limit) { lines.push(line); line = word; } else line += (line ? " " : "") + word; }
      if (line) lines.push(line);
      return lines;
    };
    const panels = GRAPH_PATHWAYS.map(pathway => {
      const [x, y, w, h] = pathway.panel;
      return `<g class="graph-panel"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="14"></rect><text x="${x + 20}" y="${y + 28}" class="panel-title">${esc(pathway.title)}</text><text x="${x + 20}" y="${y + 49}" class="panel-copy">${esc(pathway.subtitle)}</text></g>`;
    }).join("");
    const edgeRecords = [];
    for (const pathway of GRAPH_PATHWAYS) for (const [from, to] of pathway.edges) {
      const edge = edgeByPair.get(`${from}|${to}`), a = pathway.nodes[from], b = pathway.nodes[to];
      if (!edge || !a || !b) continue;
      const vertical = Math.abs(a[0] - b[0]) < 2;
      const sourceOnLeft = a[0] < b[0];
      const sx = vertical ? a[0] + width / 2 : sourceOnLeft ? a[0] + width : a[0];
      const sy = vertical ? a[1] + height : a[1] + height / 2;
      const tx = vertical ? b[0] + width / 2 : sourceOnLeft ? b[0] : b[0] + width;
      const ty = vertical ? b[1] : b[1] + height / 2;
      const bend = Math.max(18, Math.abs(tx - sx) / 2);
      const d = vertical ? `M ${sx} ${sy} L ${tx} ${ty}` : Math.abs(sy - ty) < 2 ? `M ${sx} ${sy} L ${tx} ${ty}` : `M ${sx} ${sy} C ${sx + (sourceOnLeft ? bend : -bend)} ${sy}, ${tx + (sourceOnLeft ? -bend : bend)} ${ty}, ${tx} ${ty}`;
      const lx = vertical ? sx + 105 : (sx + tx) / 2, ly = vertical ? (sy + ty) / 2 : Math.min(sy, ty) - 11;
      edgeRecords.push({...edge, d, sx, sy, tx, ty, lx, ly});
    }
    const definitions = usedRelations.map(relation => `<marker id="arrow-${relation}" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,8 L9,4 z" fill="${RELATION[relation]}"></path></marker>`).join("");
    const edgePaths = edgeRecords.map(edge => `<g class="graph-edge-group" data-edge="${edge.index}" data-from="${esc(edge.from)}" data-to="${esc(edge.to)}" tabindex="0" role="button" aria-label="${esc(`${RELATION_LABEL[edge.relation]}: ${nodeById[edge.from].label} to ${nodeById[edge.to].label}`)}"><path class="graph-edge" d="${edge.d}" stroke="${RELATION[edge.relation]}" stroke-dasharray="${RELATION_DASH[edge.relation] || "none"}" marker-end="url(#arrow-${edge.relation})"></path><path class="graph-edge-hit" d="${edge.d}"></path></g>`).join("");
    const nodes = GRAPH_PATHWAYS.flatMap(pathway => Object.entries(pathway.nodes).map(([id, p]) => {
      const node = nodeById[id], lines = wrap(node.statement).slice(0, 3);
      return `<g class="graph-node" data-node="${esc(id)}" transform="translate(${p[0]},${p[1]})" tabindex="0" role="button"><rect width="${width}" height="${height}"></rect><text x="11" y="16" class="node-kind">${esc(node.kind.replaceAll("_", " "))}</text><text x="11" y="35" class="node-title">${esc(node.label)}</text>${lines.map((line, i) => `<text x="11" y="${55 + i * 13}" class="node-copy">${esc(line)}</text>`).join("")}</g>`;
    })).join("");
    const decorations = edgeRecords.map(edge => {
      const label = RELATION_LABEL[edge.relation], labelWidth = Math.max(58, label.length * 5.8 + 14);
      return `<g class="edge-decoration" data-edge-decoration="${edge.index}"><circle cx="${edge.sx}" cy="${edge.sy}" r="4" fill="${RELATION[edge.relation]}"></circle><circle cx="${edge.tx}" cy="${edge.ty}" r="4" fill="${RELATION[edge.relation]}"></circle><rect x="${edge.lx - labelWidth / 2}" y="${edge.ly - 12}" width="${labelWidth}" height="18" rx="9"></rect><text x="${edge.lx}" y="${edge.ly + 1}" text-anchor="middle">${esc(label)}</text></g>`;
    }).join("");
    const graph = document.getElementById("graph");
    graph.setAttribute("viewBox", "0 0 1200 1320");
    graph.innerHTML = `<defs>${definitions}</defs>${panels}${edgePaths}${nodes}${decorations}`;

    const endpoint = id => { const node = nodeById[id]; return `<strong>${esc(node.label)}</strong><small>${esc(node.statement)}</small><code>${esc(id)}</code>`; };
    const evidence = edge => edge.evidence.length ? `<ul class="edge-evidence">${edge.evidence.map(id => { const item = DATA.evidence[id], href = item ? (item.kind === "LITERATURE" ? item.ledger_link : item.result_link) : ""; return `<li>${href ? `<a href="${esc(href)}"><code>${esc(id)}</code></a>` : `<code>${esc(id)}</code>`}</li>`; }).join("")}</ul>` : `<span class="open-evidence">No direct certificate yet</span>`;
    document.getElementById("edgeTable").innerHTML = `<h3>Relation ledger</h3><p class="muted">Each row states exactly what its arrow asserts. An empty evidence field marks an open bridge; it is not replaced by a generic interpretation.</p><table class="edge-table"><thead><tr><th>From</th><th>Relation</th><th>To</th><th>What this arrow asserts</th><th>Evidence</th></tr></thead><tbody>${DATA.graph.edges.map((edge, index) => `<tr data-edge-row="${index}" tabindex="0"><td class="edge-endpoint">${endpoint(edge.from)}</td><td><span class="quality relation-badge" style="border-left-color:${RELATION[edge.relation]}" title="${esc(RELATION_DESCRIPTION[edge.relation])}">${esc(RELATION_LABEL[edge.relation])}</span><small><code>${esc(edge.relation)}</code></small></td><td class="edge-endpoint">${endpoint(edge.to)}</td><td>${esc(edge.meaning || "ERROR: missing edge explanation")}</td><td>${evidence(edge)}</td></tr>`).join("")}</tbody></table>`;

    const clearFocus = () => document.querySelectorAll(".graph-edge-group, .edge-decoration, .graph-node, [data-edge-row]").forEach(item => item.classList.remove("focused", "dimmed"));
    const focusEdge = index => {
      const edge = DATA.graph.edges[index];
      document.querySelectorAll(".graph-edge-group").forEach(item => item.classList.toggle("dimmed", Number(item.dataset.edge) !== index));
      document.querySelectorAll("[data-edge-decoration]").forEach(item => item.classList.toggle("dimmed", Number(item.dataset.edgeDecoration) !== index));
      document.querySelectorAll(".graph-node").forEach(item => item.classList.toggle("dimmed", ![edge.from, edge.to].includes(item.dataset.node)));
      document.querySelectorAll("[data-edge-row]").forEach(item => { item.classList.toggle("focused", Number(item.dataset.edgeRow) === index); item.classList.toggle("dimmed", Number(item.dataset.edgeRow) !== index); });
    };
    document.querySelectorAll(".graph-edge-group, [data-edge-row]").forEach(item => {
      const index = Number(item.dataset.edge ?? item.dataset.edgeRow);
      item.addEventListener("mouseenter", () => focusEdge(index)); item.addEventListener("focus", () => focusEdge(index));
      item.addEventListener("mouseleave", clearFocus); item.addEventListener("blur", clearFocus);
    });
    document.querySelectorAll("[data-node]").forEach(item => {
      item.addEventListener("mouseenter", () => {
        const incident = new Set(DATA.graph.edges.map((edge, index) => ({edge, index})).filter(x => x.edge.from === item.dataset.node || x.edge.to === item.dataset.node).map(x => x.index));
        document.querySelectorAll(".graph-edge-group").forEach(edge => edge.classList.toggle("dimmed", !incident.has(Number(edge.dataset.edge))));
        document.querySelectorAll("[data-edge-decoration]").forEach(edge => edge.classList.toggle("dimmed", !incident.has(Number(edge.dataset.edgeDecoration))));
        document.querySelectorAll(".graph-node").forEach(node => node.classList.toggle("dimmed", node.dataset.node !== item.dataset.node));
      });
      item.addEventListener("mouseleave", clearFocus);
      item.addEventListener("click", () => openNodeInspector(nodeById[item.dataset.node]));
      item.addEventListener("keydown", event => { if (event.key === "Enter" || event.key === " ") openNodeInspector(nodeById[item.dataset.node]); });
    });
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

  function renderGuide() {
    const dimensions = DATA.axes.map((dimension, index) => {
      const optionById = new Map(dimension.keys.map(option => [option.id, option]));
      const groups = GUIDE_GROUPS[dimension.id].map(group => `<section class="guide-option-group"><div class="guide-group-heading"><h4>${esc(group.title)}</h4><p>${esc(group.summary)}</p></div><div class="guide-options">${group.ids.map(id => {
        const option = optionById.get(id);
        return `<article><h4>${esc(option.label)}</h4><p>${esc(option.plain_meaning)}</p><details><summary>Technical scope and cautions</summary><p>${esc(option.meaning)}</p>${list(option.includes).length ? `<p><b>Includes:</b> ${esc(option.includes.join(", "))}</p>` : ""}${option.warning ? `<p class="boundary">${esc(option.warning)}</p>` : ""}</details></article>`;
      }).join("")}</div></section>`).join("");
      return `<section class="guide-dimension"><div class="guide-heading"><span>${index + 1}</span><div><p class="eyebrow">${esc(dimension.plain_name)}</p><h3>${esc(dimension.guide_question)}</h3><p class="guide-axis-answer"><b>In this atlas:</b> ${esc(dimension.question)} Select exactly one option to define this part of a cell.</p></div></div>${groups}</section>`;
    }).join("");
    const glossary = GUIDE_GLOSSARY.map(([term, meaning]) => `<article><h4>${esc(term)}</h4><p>${esc(meaning)}</p></article>`).join("");
    document.getElementById("dimensionGuide").innerHTML = `
      <article class="guide-hero"><p class="eyebrow">The idea without the jargon</p><h2>Every result answers three different questions</h2><p>A physical conclusion never comes from equations alone. It also depends on what counts as a valid proof, what mathematical objects are allowed, and which physical job has actually been completed.</p><div class="guide-equation"><div><span>1</span><b>Rules</b><small>What may exist, and what counts as proof?</small></div><i>×</i><div><span>2</span><b>Container</b><small>What kind of object carries the physics?</small></div><i>×</i><div><span>3</span><b>Job</b><small>What must this piece of the theory accomplish?</small></div></div><p class="guide-caution">The three axes are disciplined bookkeeping questions. The atlas does not claim that they are mathematically independent, exhaustive, or the only possible way to organize foundational physics.</p></article>
      <section class="guide-examples"><article><p class="eyebrow">A familiar example</p><h3>Why “general relativity works” is too compressed</h3><p>The Cassini assembly uses <b>classical-standard rules</b>, <b>smooth continuum geometry</b>, and a bounded chain of jobs from field equations to a measured delay parameter. It succeeds in that declared sector without claiming that every quantum, cosmological, or ultraviolet job is complete.</p></article><article><p class="eyebrow">Change one coordinate</p><h3>The question changes even when the equation does not</h3><p><b>Classical-standard × continuum fields × causal propagation</b> asks whether a Green operator exists. Replacing the first coordinate by <b>constructive/computable</b> asks for an explicit algorithm and represented input-output control as well. Those are related but different theorems.</p></article></section>
      <article class="guide-intro"><p class="eyebrow">How to read one cell</p><h3>Regime × carrier × obligation = one precise research question</h3><p>A cell is not a miniature theory and its color is not a score. It records the strongest evidence currently registered for one exact combination of rules, mathematical container, and physical job.</p></article>
      ${dimensions}
      <section class="guide-glossary"><div class="section-head compact-head"><div><p class="eyebrow">Small glossary</p><h2>Seven terms that unlock the map</h2></div><p>These are orientation-level descriptions. Open each option's technical scope for the research boundary used by the atlas.</p></div><div>${glossary}</div></section>
      <article class="guide-intro"><p class="eyebrow">Open does not mean impossible</p><h3>Reviewed gap versus priority gap</h3><p>A <b>reviewed open gap (O)</b> is a formulated research question with a typed missing certificate, but no direct result. A <b>priority gap (G)</b> is an open question selected for the current programme. Neither says that the literature is empty, the idea is false, or no proof can exist.</p></article>
      <details class="guide-reviewer"><summary>For reviewers: how the evidence letters and migration audit work</summary><div><h3>Why some cells are marked LR, Plr, Lr, or Rl</h3><p>A cell color reports one strongest status. A direct local result outranks a direct literature result, while an <b>LR</b> corner mark preserves the fact that both exist. Upper-case letters are direct grades; lower-case letters are supporting ingredients. Thus <b>Plr</b> is still pieces-only, not a result. <b>Unreviewed directness is not a finding that evidence fails to support a cell.</b></p><h3>Coverage is not migration</h3><p><b>Coverage status</b> records the present result, ingredient, or gap. <b>Migration review</b> records whether evidence from an older broad category was checked before transfer into this finer cell. Migration review is an audit fact, not extra physical evidence.</p></div></details>`;
  }

  const READINESS_RANK = {NOT_MAPPED: 0, REVIEWED_GAP: 1, PRIORITY_GAP: 1, PIECES_ONLY: 2, LOCAL_RESULT: 3, LITERATURE_RESULT: 3};
  const DIRECT = new Set(["LOCAL_RESULT", "LITERATURE_RESULT"]);

  function profileCells(profile, obligations = axis.REFINED_OBLIGATION.keys.map(x => x.id)) {
    return obligations.map(obligation => cellByKey.get(`${profile.foundation}|${profile.carrier}|${obligation}`));
  }

  function profileMetrics(profile, obligations) {
    const cells = profileCells(profile, obligations);
    return {
      direct: cells.filter(cell => DIRECT.has(cell.status)).length,
      assessed: cells.filter(cell => cell.status !== "NOT_MAPPED").length,
      partial: cells.filter(cell => cell.status === "PIECES_ONLY").length,
      gap: cells.filter(cell => ["PRIORITY_GAP", "REVIEWED_GAP"].includes(cell.status)).length,
      unknown: cells.filter(cell => cell.status === "NOT_MAPPED").length,
      total: cells.length,
      allDirect: profile.direct,
      reconstruction: READINESS_RANK[profile.reconstruction_status],
    };
  }

  function paretoProfiles(obligations) {
    const values = VIABILITY.profiles.map(profile => ({profile, metrics: profileMetrics(profile, obligations)}));
    const dominates = (a, b) => {
      const left = [a.direct, a.assessed, a.allDirect, a.reconstruction];
      const right = [b.direct, b.assessed, b.allDirect, b.reconstruction];
      return left.every((value, index) => value >= right[index]) && left.some((value, index) => value > right[index]);
    };
    return new Set(values.filter(candidate => !values.some(other => other !== candidate && dominates(other.metrics, candidate.metrics))).map(item => `${item.profile.foundation}|${item.profile.carrier}`));
  }

  function selectedEnvelope() {
    const carriers = [...state.viability.carriers];
    return axis.REFINED_OBLIGATION.keys.map(obligation => {
      const candidates = carriers.map(carrier => cellByKey.get(`${state.viability.foundation}|${carrier}|${obligation.id}`));
      const rank = candidates.length ? Math.max(...candidates.map(cell => READINESS_RANK[cell.status])) : 0;
      const contributors = candidates.filter(cell => READINESS_RANK[cell.status] === rank);
      return {obligation, rank, contributors};
    });
  }

  function renderTheoryProfiles() {
    const obligations = [...state.viability.obligations];
    const frontier = paretoProfiles(obligations);
    const profiles = VIABILITY.profiles.map(profile => ({profile, metrics: profileMetrics(profile, obligations)}))
      .filter(item => !state.viability.paretoOnly || frontier.has(`${item.profile.foundation}|${item.profile.carrier}`))
      .sort((a, b) => b.metrics.direct - a.metrics.direct || b.metrics.assessed - a.metrics.assessed || b.metrics.allDirect - a.metrics.allDirect || title(a.profile.foundation).localeCompare(title(b.profile.foundation)));
    const selectedProfile = VIABILITY.profiles.find(profile => `${profile.foundation}|${profile.carrier}` === state.viability.profile) || profiles[0]?.profile;
    if (selectedProfile) state.viability.profile = `${selectedProfile.foundation}|${selectedProfile.carrier}`;
    const selectedMetrics = selectedProfile ? profileMetrics(selectedProfile, obligations) : null;
    const envelope = selectedEnvelope();
    const envelopeDirect = envelope.filter(item => item.rank === 3 && obligations.includes(item.obligation.id)).length;
    const preset = VIABILITY.presets.find(item => item.id === state.viability.preset);
    const rails = VIABILITY.global_rails.map(rail => `<article class="rail-card ${rail.status === "COMPUTED_FROM_ATLAS" ? "computed" : rail.status === "PARTIALLY_ASSESSED" ? "partial" : "missing"}"><span class="quality">${esc(rail.status)}</span><h3>${esc(rail.label)}</h3><p>${esc(rail.meaning)}</p></article>`).join("");
    const mapRows = axis.FOUNDATION.keys.map(foundation => `<tr><th>${esc(foundation.label)}</th>${axis.CARRIER.keys.map(carrier => {
      const profile = VIABILITY.profiles.find(item => item.foundation === foundation.id && item.carrier === carrier.id);
      const metrics = profileMetrics(profile, obligations);
      const key = `${foundation.id}|${carrier.id}`;
      const tone = metrics.total ? Math.round(18 + 72 * metrics.direct / metrics.total) : 18;
      return `<td><button class="profile-cell${key === state.viability.profile ? " selected" : ""}" data-profile="${key}" style="--readiness:${tone}%" title="${esc(`${foundation.label} × ${carrier.label}: ${metrics.direct}/${metrics.total} selected obligations direct; ${metrics.gap} reviewed or priority gaps; ${metrics.unknown} unknown`)}"><b>${metrics.direct}/${metrics.total}</b><small>${frontier.has(key) ? "Pareto" : metrics.unknown ? `${metrics.unknown} ?` : `${metrics.gap} open`}</small></button></td>`;
    }).join("")}</tr>`).join("");
    const obligationChecks = axis.REFINED_OBLIGATION.keys.map(obligation => `<label><input type="checkbox" data-viability-obligation="${obligation.id}" ${state.viability.obligations.has(obligation.id) ? "checked" : ""}>${esc(obligation.label)}</label>`).join("");
    const carrierChecks = axis.CARRIER.keys.map(carrier => `<label><input type="checkbox" data-portfolio-carrier="${carrier.id}" ${state.viability.carriers.has(carrier.id) ? "checked" : ""}>${esc(carrier.label)}</label>`).join("");
    const profileBlocks = selectedProfile ? profileCells(selectedProfile, obligations).filter(cell => !DIRECT.has(cell.status)).map(cell => `<li><button data-cell-jump="${key(cell)}"><span class="status-dot" style="${statusStyle(cell.status)}"></span>${esc(title(cell.obligation))}: ${esc(STATUS[cell.status].label)}</button></li>`).join("") : "";
    const bundleRows = selectedProfile ? VIABILITY.bundles.map(bundle => {
      const metrics = profileMetrics(selectedProfile, bundle.obligations);
      return `<tr><th>${esc(bundle.label)}</th><td><div class="readiness-bar"><i style="width:${100 * metrics.direct / metrics.total}%"></i></div></td><td>${metrics.direct}/${metrics.total} direct</td><td>${metrics.partial} partial · ${metrics.gap} gap · ${metrics.unknown} unknown</td></tr>`;
    }).join("") : "";
    const envelopeRows = envelope.map(item => {
      const statuses = [...new Set(item.contributors.map(cell => cell.status))];
      return `<tr class="${obligations.includes(item.obligation.id) ? "required-row" : ""}"><th>${esc(item.obligation.label)}</th><td>${statuses.map(status => `<span class="status-pill" style="${statusStyle(status)}">${esc(STATUS[status].label)}</span>`).join(" ")}</td><td>${item.contributors.map(cell => esc(title(cell.carrier))).join(", ") || "No carrier selected"}</td></tr>`;
    }).join("");
    const rankingRows = profiles.map(({profile, metrics}) => {
      const profileKey = `${profile.foundation}|${profile.carrier}`;
      return `<tr class="${profileKey === state.viability.profile ? "focused" : ""}"><td><button data-profile="${profileKey}">${esc(title(profile.foundation))}<br><small>${esc(title(profile.carrier))}</small></button></td><td>${metrics.direct}/${metrics.total}</td><td>${metrics.partial}</td><td>${metrics.gap}</td><td>${metrics.unknown}</td><td>${profile.direct}/16</td><td>${esc(STATUS[profile.reconstruction_status].label)}</td><td>${frontier.has(profileKey) ? "Yes" : ""}</td></tr>`;
    }).join("");
    document.getElementById("viabilityExplorer").innerHTML = `
      <article class="viability-warning"><p class="eyebrow">What can be concluded now</p><h3>No complete observationally validated theory is certified by this atlas.</h3><p>The first rail below is computable. The other two are independent missing prerequisites. A high coverage profile is therefore a research map, not a validity verdict.</p></article>
      <div class="rail-grid">${rails}</div>
      <section class="viability-controls"><div><label><b>Required-obligation preset</b><select id="viabilityPreset">${state.viability.preset === "CUSTOM" ? '<option value="CUSTOM" selected disabled>Custom selection</option>' : ""}${VIABILITY.presets.map(item => `<option value="${item.id}" ${item.id === state.viability.preset ? "selected" : ""}>${esc(item.label)}</option>`).join("")}</select></label><p>${esc(preset?.description || "Custom selection")}</p></div><details><summary>Choose individual hard gates (${obligations.length})</summary><div class="obligation-picker">${obligationChecks}</div></details><label class="check"><input id="paretoOnly" type="checkbox" ${state.viability.paretoOnly ? "checked" : ""}> Show current Pareto set only</label></section>
      <div class="section-head compact-head"><div><p class="eyebrow">Single-carrier profiles</p><h2>Coverage readiness map</h2></div><p>Each tile is direct selected obligations / selected obligations. “Pareto” means nondominated on the four declared coverage metrics, not physically preferred.</p></div>
      <div class="profile-map-wrap"><table class="profile-map"><thead><tr><th>Regime ↓ / carrier →</th>${axis.CARRIER.keys.map(carrier => `<th><span class="column-label">${esc(carrier.label)}</span></th>`).join("")}</tr></thead><tbody>${mapRows}</tbody></table></div>
      ${selectedProfile ? `<section class="profile-detail"><div><p class="eyebrow">Selected formulation profile</p><h3>${esc(title(selectedProfile.foundation))} × ${esc(title(selectedProfile.carrier))}</h3><p><b>${selectedMetrics.direct}/${selectedMetrics.total}</b> selected hard gates direct; <b>${selectedProfile.direct}/16</b> obligations direct overall.</p><h4>Selected-gate blockers</h4>${profileBlocks ? `<ul class="blocker-list">${profileBlocks}</ul>` : `<p class="good-news">All selected gates have direct evidence—but composition and observation rails remain open.</p>`}</div><table class="bundle-table"><thead><tr><th>Obligation bundle</th><th>Direct share</th><th>Direct</th><th>Other states</th></tr></thead><tbody>${bundleRows}</tbody></table></section>` : ""}
      <div class="section-head compact-head"><div><p class="eyebrow">Carrier portfolio composer</p><h2>Coverage envelope, not a composed theory</h2></div><p>Choose carriers under one mathematical regime. For each obligation the table shows the strongest recorded cell and its source carrier. Taking maxima does not prove the pieces coexist consistently.</p></div>
      <section class="portfolio-controls"><label><b>Mathematical regime</b><select id="portfolioFoundation">${axis.FOUNDATION.keys.map(item => `<option value="${item.id}" ${item.id === state.viability.foundation ? "selected" : ""}>${esc(item.label)}</option>`).join("")}</select></label><fieldset><legend>Carriers in envelope</legend>${carrierChecks}</fieldset><div class="portfolio-summary"><b>${envelopeDirect}/${obligations.length}</b><span>selected gates direct somewhere in the envelope</span><strong>Composition: NOT ASSESSED</strong></div></section>
      <div class="envelope-table-wrap"><table class="envelope-table"><thead><tr><th>Obligation</th><th>Best recorded state</th><th>Contributing carrier(s)</th></tr></thead><tbody>${envelopeRows}</tbody></table></div>
      <details class="ranking-details"><summary>Show all formulation profiles as a coverage-ranked research table (${profiles.length})</summary><div class="ranking-wrap"><table class="profile-ranking"><thead><tr><th>Profile</th><th>Selected direct</th><th>Partial</th><th>Open gaps</th><th>Unknown</th><th>All direct</th><th>Reconstruction proxy</th><th>Pareto</th></tr></thead><tbody>${rankingRows}</tbody></table></div></details>
      <article class="viability-warning boundary"><b>Fail-closed boundary.</b> ${esc(VIABILITY.pareto_definition.warning)} ${esc(VIABILITY.unit)}</article>`;
    document.querySelectorAll("[data-profile]").forEach(button => button.addEventListener("click", () => { state.viability.profile = button.dataset.profile; const [foundation, carrier] = button.dataset.profile.split("|"); state.viability.foundation = foundation; state.viability.carriers = new Set([carrier]); renderTheoryProfiles(); }));
    document.querySelectorAll("[data-cell-jump]").forEach(button => button.addEventListener("click", () => openCell(button.dataset.cellJump)));
    document.getElementById("viabilityPreset").addEventListener("change", event => { const next = VIABILITY.presets.find(item => item.id === event.target.value); state.viability.preset = next.id; state.viability.obligations = new Set(next.obligations); renderTheoryProfiles(); });
    document.querySelectorAll("[data-viability-obligation]").forEach(input => input.addEventListener("change", () => { input.checked ? state.viability.obligations.add(input.dataset.viabilityObligation) : state.viability.obligations.delete(input.dataset.viabilityObligation); state.viability.preset = "CUSTOM"; renderTheoryProfiles(); }));
    document.getElementById("paretoOnly").addEventListener("change", event => { state.viability.paretoOnly = event.target.checked; renderTheoryProfiles(); });
    document.getElementById("portfolioFoundation").addEventListener("change", event => { state.viability.foundation = event.target.value; renderTheoryProfiles(); });
    document.querySelectorAll("[data-portfolio-carrier]").forEach(input => input.addEventListener("change", () => { input.checked ? state.viability.carriers.add(input.dataset.portfolioCarrier) : state.viability.carriers.delete(input.dataset.portfolioCarrier); renderTheoryProfiles(); }));
  }

  const ASSEMBLY_GATE_STYLE = {
    SATISFIED: "complete", OPEN: "open", PARTIALLY_CERTIFIED: "partial",
    NOT_ASSESSED: "missing", NOT_EVALUABLE: "neutral", NOT_REGISTERED: "missing",
    NO_RECORDS: "missing", BLOCKED: "blocked", FAILED: "blocked",
    COARSE_REPRODUCTION_ONLY: "partial",
    REGISTERED_IN_DOMAINS: "control", SUPPORTED_IN_DOMAINS: "complete", MULTI_DOMAIN_SUPPORT: "complete",
    CERTIFIED_EXACT: "complete", LITERATURE_SCOPED: "control", SUPPORTED_REPORTED_BAND: "complete",
    SATISFIED_WITH_TYPED_BOUNDARY: "control", SUPPORTED_IN_DECLARED_SCOPE: "complete",
    DECLARED_MODEL_INPUT: "control", CERTIFIED_LOCAL_PREDECESSOR: "complete",
    PUBLISHED_MODEL_TRANSCRIPTION: "control", CONTENT_PINNED_TRANSCRIPTION: "control",
    COARSE_NUMERICAL_REPRODUCTION: "partial", MIXED_RANDOM_ERROR_GATE_FAILED: "blocked",
    SATISFIED_WITH_MATTER_BOUNDARY: "control", SATISFIED_WITH_PUBLISHED_MODEL_INPUT: "control",
    COARSE_ENDPOINT_REPRODUCED: "partial"
  };

  function assemblyFraction(value) { return value.denominator === 1 ? `${value.numerator}` : `${value.numerator}/${value.denominator}`; }

  function mannheimResidualSvg(model) {
    const points = model.empirical_comparison_rail.points;
    const width = 820, height = 250, left = 62, right = 18, top = 18, bottom = 44;
    const xmax = model.numerical_reproduction_rail.published_last_radius_kpc;
    const residualLimit = Math.max(4, Math.ceil(Math.max(...points.map(point => Math.abs(point.standardized_residual)))));
    const x = value => left + value / xmax * (width - left - right);
    const y = value => top + (residualLimit - value) / (2 * residualLimit) * (height - top - bottom);
    const stems = points.map(point => `<line x1="${x(point.rescaled_radius_kpc).toFixed(2)}" x2="${x(point.rescaled_radius_kpc).toFixed(2)}" y1="${y(0).toFixed(2)}" y2="${y(point.standardized_residual).toFixed(2)}"></line>`).join("");
    const residuals = points.map(point => `<circle class="${Math.abs(point.standardized_residual) <= 2 ? "inside" : "outside"}" cx="${x(point.rescaled_radius_kpc).toFixed(2)}" cy="${y(point.standardized_residual).toFixed(2)}" r="3.2"><title>r = ${point.rescaled_radius_kpc.toFixed(2)} kpc; standardized residual = ${point.standardized_residual.toFixed(2)}</title></circle>`).join("");
    const xTicks = [0, 10, 20, 30, 38.6].map(value => `<g><line x1="${x(value)}" x2="${x(value)}" y1="${height-bottom}" y2="${height-bottom+5}"></line><text x="${x(value)}" y="${height-bottom+20}" text-anchor="middle">${value}</text></g>`).join("");
    const yTicks = Array.from({length: 2 * residualLimit + 1}, (_, index) => index - residualLimit).filter(value => value % 2 === 0).map(value => `<g><line x1="${left-5}" x2="${left}" y1="${y(value)}" y2="${y(value)}"></line><text x="${left-9}" y="${y(value)+4}" text-anchor="end">${value}</text></g>`).join("");
    const bandTop = y(2), bandHeight = y(-2) - y(2);
    return `<div class="curve-panel residual-panel"><div class="residual-panel-head"><div><p class="eyebrow">Where the no-refit model misses</p><h3>Residual audit against SPARC random errors</h3></div><p>Each dot is (prediction − observation) ÷ reported random error. Distance from zero, not curve resemblance, drives χ².</p></div><div class="curve-legend"><span><i class="residual-dot inside"></i>Within ±2 random errors</span><span><i class="residual-dot outside"></i>Beyond ±2 random errors</span><span><i class="residual-band-key"></i>±2 pointwise reference band—not the aggregate gate</span></div><svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Signed standardized residual audit for the no-refit Mannheim model against SPARC NGC 3198 random errors"><rect class="residual-band" x="${left}" y="${bandTop}" width="${width-left-right}" height="${bandHeight}"></rect><g class="curve-axes"><line x1="${left}" x2="${width-right}" y1="${height-bottom}" y2="${height-bottom}"></line><line x1="${left}" x2="${left}" y1="${top}" y2="${height-bottom}"></line>${xTicks}${yTicks}<text x="${(left+width-right)/2}" y="${height-5}" text-anchor="middle">Radius at 14.1 Mpc (kpc)</text><text transform="translate(14 ${(top+height-bottom)/2}) rotate(-90)" text-anchor="middle">Standardized residual</text></g><line class="residual-zero" x1="${left}" x2="${width-right}" y1="${y(0)}" y2="${y(0)}"></line><g class="residual-stems">${stems}</g><g class="residual-points">${residuals}</g></svg></div>`;
  }

  function commonFitCurveSvg(comparison) {
    const width = 820, height = 330, left = 54, right = 18, top = 18, bottom = 48, xmax = 38.6, ymax = 180;
    const x = value => left + value / xmax * (width - left - right);
    const y = value => top + (ymax - value) / ymax * (height - top - bottom);
    const labels = {NEWTONIAN_BARYONS_ONLY: "Baryons only", GR_NFW_DARK_HALO: "GR + NFW halo", MANNHEIM_CONFORMAL_GRAVITY: "Mannheim conformal"};
    const classes = {NEWTONIAN_BARYONS_ONLY: "baryons", GR_NFW_DARK_HALO: "nfw", MANNHEIM_CONFORMAL_GRAVITY: "mannheim"};
    const reference = comparison.models[0].predictions;
    const observations = reference.map(point => `<circle cx="${x(point.radius_kpc).toFixed(2)}" cy="${y(point.observed_km_s).toFixed(2)}" r="2.6"></circle>`).join("");
    const errors = reference.map(point => `<line x1="${x(point.radius_kpc).toFixed(2)}" x2="${x(point.radius_kpc).toFixed(2)}" y1="${y(Math.min(ymax, point.observed_km_s + point.error_km_s)).toFixed(2)}" y2="${y(Math.max(0, point.observed_km_s - point.error_km_s)).toFixed(2)}"></line>`).join("");
    const curves = comparison.models.map(model => `<polyline class="fit-curve ${classes[model.model_id]}" points="${model.predictions.map(point => `${x(point.radius_kpc).toFixed(2)},${y(point.predicted_km_s).toFixed(2)}`).join(" ")}"></polyline>`).join("");
    const legend = comparison.models.map(model => `<span><i class="fit-swatch ${classes[model.model_id]}"></i>${labels[model.model_id]}</span>`).join("");
    const xTicks = [0,10,20,30,38.6].map(value => `<g><line x1="${x(value)}" x2="${x(value)}" y1="${height-bottom}" y2="${height-bottom+5}"></line><text x="${x(value)}" y="${height-bottom+20}" text-anchor="middle">${value}</text></g>`).join("");
    const yTicks = [0,50,100,150].map(value => `<g><line x1="${left-5}" x2="${left}" y1="${y(value)}" y2="${y(value)}"></line><text x="${left-9}" y="${y(value)+4}" text-anchor="end">${value}</text></g>`).join("");
    return `<div class="curve-panel common-fit-curve"><div class="curve-legend">${legend}<span><i class="curve-point"></i>SPARC ± random error</span></div><svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Common-protocol NGC 3198 fits for baryons only, GR plus NFW, and Mannheim conformal gravity"><g class="curve-axes"><line x1="${left}" x2="${width-right}" y1="${height-bottom}" y2="${height-bottom}"></line><line x1="${left}" x2="${left}" y1="${top}" y2="${height-bottom}"></line>${xTicks}${yTicks}<text x="${(left+width-right)/2}" y="${height-5}" text-anchor="middle">Radius at 14.1 Mpc (kpc)</text><text transform="translate(14 ${(top+height-bottom)/2}) rotate(-90)" text-anchor="middle">Circular speed (km/s)</text></g><g class="curve-errors">${errors}</g>${curves}<g class="curve-observed">${observations}</g></svg></div>`;
  }

  function renderAssemblies() {
    const assembly = ASSEMBLIES.assemblies.find(item => item.id === state.assembly) || ASSEMBLIES.assemblies[0];
    state.assembly = assembly.id;
    const options = ASSEMBLIES.assemblies.map(item => `<option value="${item.id}" ${item.id === assembly.id ? "selected" : ""}>${esc(item.short_label)}</option>`).join("");
    const campCards = ASSEMBLIES.assemblies.map(item => `<button class="camp-card ${item.id === assembly.id ? "selected" : ""}" data-camp="${esc(item.id)}"><small>${esc(CAMP_KIND_LABEL[item.camp_kind] || item.camp_kind)}</small><b>${esc(item.short_label)}</b><span>${esc(item.camp_summary)}</span><em>${item.coverage.direct}/${item.coverage.total} jobs have direct records</em></button>`).join("");
    const campLineage = assembly.lineage.map(item => `<li>${esc(item)}</li>`).join("");
    const campIdeas = assembly.signature_ideas.map(item => `<li>${esc(item)}</li>`).join("");
    const gates = assembly.maturity_rails.map((gate, index) => `<article class="assembly-gate ${ASSEMBLY_GATE_STYLE[gate.status] || "missing"}"><span>${index + 1}</span><div><small>${esc(gate.status.replaceAll("_", " "))}</small><h3>${esc(gate.label)}</h3><p>${esc(gate.basis)}</p></div></article>`).join("");
    const cells = assembly.selected_cells.map(cell => {
      const source = cellByKey.get(`${cell.foundation}|${cell.carrier}|${cell.obligation}`);
      const roles = Object.values(cell.evidence_roles || {});
      const directness = [roles.includes("DIRECT_LOCAL") ? "local" : "", roles.includes("DIRECT_LITERATURE") ? "literature" : ""].filter(Boolean).join(" + ") || "no reviewed direct kind";
      return `<tr><th>${esc(title(cell.obligation))}</th><td>${esc(title(cell.foundation))}<br><small>${esc(title(cell.carrier))}</small></td><td><button class="status-pill assembly-cell-jump" data-cell-jump="${esc(`${cell.foundation}|${cell.carrier}|${cell.obligation}`)}" style="${statusStyle(cell.status)}">${esc(STATUS[cell.status].label)}</button></td><td>${esc(directness)}</td><td>${cell.evidence.length}</td></tr>`;
    }).join("");
    const interfaces = assembly.interfaces.map(item => {
      const evidence = item.evidence.map(id => DATA.evidence[id] ? `<a href="${esc(DATA.evidence[id].result_link)}"><code>${esc(id)}</code></a>` : `<code>${esc(id)}</code>`).join(" · ");
      return `<tr><th>${esc(item.label)}</th><td>${item.source_obligations.map(title).map(esc).join(" + ")}</td><td><span class="interface-relation relation-${item.relation.toLowerCase()}">${item.certification_status === "CERTIFIED" ? "CERTIFIED · " : ""}${esc(item.relation.replaceAll("_", " "))}</span></td><td>${item.target_obligations.map(title).map(esc).join(" + ")}</td><td>${esc(item.rationale)}${evidence ? `<p class="interface-evidence">${evidence}</p>` : ""}</td></tr>`;
    }).join("");
    const vocabulary = ASSEMBLIES.interface_vocabulary.map(item => `<details><summary>${esc(item.id.replaceAll("_", " "))}</summary><p>${esc(item.meaning)}</p></details>`).join("");
    const carrierInterfaces = ASSEMBLIES.certified_carrier_interface_records.map(item => {
      const source = item.source_coordinates.map(x => `${title(x.foundation)} × ${title(x.carrier)} · ${title(x.obligation)}`).map(esc).join(" + ");
      const target = item.target_coordinates.map(x => `${title(x.foundation)} × ${title(x.carrier)} · ${title(x.obligation)}`).map(esc).join(" + ");
      const evidence = item.evidence.map(id => DATA.evidence[id] ? `<a href="${esc(DATA.evidence[id].result_link)}"><code>${esc(id)}</code></a>` : `<code>${esc(id)}</code>`).join(" · ");
      return `<tr><th>${esc(item.label)}</th><td>${source}</td><td><span class="interface-relation relation-${item.relation.toLowerCase()}">CERTIFIED · ${esc(item.relation.replaceAll("_", " "))}</span></td><td>${target}</td><td>${esc(item.scope)}<p class="interface-evidence">${evidence}</p><p><b>Open:</b> ${esc(item.does_not_establish)}</p></td></tr>`;
    }).join("");
    const benchmarks = ASSEMBLIES.empirical_ledger.benchmarks.map(item => `<article><span class="quality">${esc(item.status.replaceAll("_", " "))}</span><h3>${esc(item.label)}</h3><p>${esc(item.question)}</p></article>`).join("");
    const control = ASSEMBLIES.calibration_controls[0];
    const model = ASSEMBLIES.model_scoped_assemblies.find(item => item.result_id === "FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1");
    const mannheim = ASSEMBLIES.model_scoped_assemblies.find(item => item.result_id === "FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1");
    const modelStages = model.stages.map((stage, index) => `<article class="model-stage ${ASSEMBLY_GATE_STYLE[stage.status] || "missing"}"><span>${index + 1}</span><small>${esc(stage.status.replaceAll("_", " "))}</small><h3>${esc(stage.label)}</h3><p>${esc(stage.establishes)}</p></article>`).join("");
    const modelRails = model.maturity_rails.map(rail => `<article class="model-rail ${ASSEMBLY_GATE_STYLE[rail.status] || "missing"}"><small>${esc(rail.status.replaceAll("_", " "))}</small><h3>${esc(title(rail.id))}</h3><p>${esc(rail.basis)}</p></article>`).join("");
    const applicability = model.applicability_mask.map(item => `<tr><th>${esc(title(item.obligation))}</th><td><span class="applicability-pill applicability-${item.status.toLowerCase()}">${esc(item.status.replaceAll("_", " "))}</span></td><td>${esc(item.reason)}</td></tr>`).join("");
    const empirical = model.empirical_comparison_rail;
    const mannheimStages = mannheim.stages.map((stage, index) => `<article class="model-stage ${ASSEMBLY_GATE_STYLE[stage.status] || "missing"}"><span>${index + 1}</span><small>${esc(stage.status.replaceAll("_", " "))}</small><h3>${esc(stage.label)}</h3><p>${esc(stage.establishes)}</p></article>`).join("");
    const mannheimRails = mannheim.maturity_rails.map(rail => `<article class="model-rail ${ASSEMBLY_GATE_STYLE[rail.status] || "missing"}"><small>${esc(rail.status.replaceAll("_", " "))}</small><h3>${esc(title(rail.id))}</h3><p>${esc(rail.basis)}</p></article>`).join("");
    const mannheimNumeric = mannheim.numerical_reproduction_rail;
    const mannheimEmpirical = mannheim.empirical_comparison_rail;
    const fitComparison = ASSEMBLIES.model_comparisons[0];
    const fitLabels = {NEWTONIAN_BARYONS_ONLY: "Newtonian baryons only", GR_NFW_DARK_HALO: "GR + NFW dark halo", MANNHEIM_CONFORMAL_GRAVITY: "Mannheim conformal gravity"};
    const fitRows = fitComparison.models.map(item => { const metrics = item.metrics; const p = item.fitted_parameters; const parameters = `q* ${p.q_star.toFixed(3)}` + (p.V200_km_s ? `; V200 ${p.V200_km_s.toFixed(1)}; c200 ${p.concentration_c200.toFixed(2)}` : ""); return `<tr class="${item.random_error_gate.passed ? "fit-pass" : "fit-fail"}"><th>${esc(fitLabels[item.model_id])}</th><td>${esc(parameters)}</td><td>${metrics.unweighted_rms_residual_km_s.toFixed(3)}</td><td>${metrics.reduced_chi_squared.toFixed(3)}</td><td>${metrics.AICc.toFixed(2)}</td><td><b>${item.random_error_gate.passed ? "PASS" : "FAIL"}</b></td></tr>`; }).join("");
    const controlRails = control.rail_summary.map((rail, index) => `<article class="assembly-gate ${ASSEMBLY_GATE_STYLE[rail.status] || "control"}"><span>${index + 1}</span><div><small>${esc(rail.status.replaceAll("_", " "))}</small><h3>${esc(title(rail.id))}</h3><p>${esc(rail.basis)}</p></div></article>`).join("");
    const controlByBenchmark = new Map(control.benchmark_coverage.map(item => [item.benchmark, item]));
    const controlBenchmarks = ASSEMBLIES.empirical_ledger.benchmarks.map(item => {
      const coverage = controlByBenchmark.get(item.id);
      const records = control.records.filter(record => coverage.record_ids.includes(record.id));
      const details = records.map(record => `<details><summary>${esc(record.id.replaceAll("_", " "))}</summary><p><b>Finding:</b> ${esc(record.finding)}</p><p><b>Observable:</b> ${esc(record.observable_map)}</p><p><b>Boundary:</b> ${esc(record.boundary)}</p><p><a href="${esc(record.stable_url)}" target="_blank" rel="noopener">Primary source</a> · ${esc(record.artifact.status.replaceAll("_", " "))}</p></details>`).join("");
      return `<article class="control-benchmark ${coverage.status === "SUPPORTED_CONTROL" ? "supported" : "unregistered"}"><span class="quality">${esc(coverage.status.replaceAll("_", " "))}</span><h3>${esc(item.label)}</h3><p>${coverage.status === "SUPPORTED_CONTROL" ? `${records.length} registered comparison${records.length === 1 ? "" : "s"}.` : "This control has no registered record in this release."}</p>${details}</article>`;
    }).join("");
    const completeCoverage = assembly.coverage.complete_direct ? "Coverage complete" : "Coverage still open";
    const certifiedCount = assembly.interfaces.filter(item => item.certification_status === "CERTIFIED").length;
    document.getElementById("assemblyExplorer").innerHTML = `
      <nav class="assembly-subtabs" aria-label="Assembly explorer sections"><button data-assembly-panel="models" class="${state.assemblyPanel === "models" ? "active" : ""}"><b>Bounded model tests</b><span>Two single-model chains and their observational gates</span></button><button data-assembly-panel="programmes" class="${state.assemblyPanel === "programmes" ? "active" : ""}"><b>Research programmes</b><span>Nine coverage prototypes and the selected source map</span></button><button data-assembly-panel="ledgers" class="${state.assemblyPanel === "ledgers" ? "active" : ""}"><b>Interfaces & calibration</b><span>Typed joins, benchmark records, and positive controls</span></button></nav>
      <div id="assemblyPanelModels" class="assembly-panel ${state.assemblyPanel === "models" ? "active" : ""}" data-assembly-panel-body="models"><section class="model-assembly"><div class="model-assembly-head"><div><p class="eyebrow">First model-scoped end-to-end result</p><h2>Field equations to Cassini</h2><p>${esc(model.title)}</p></div><div class="model-disposition"><b>Bounded assembly complete</b><span>Empirically supported in its declared scope</span><small>Complete theory: NO</small></div></div>
      <div class="model-scope"><p><b>One model:</b> ${esc(model.model_identity.theory)} — ${esc(model.model_identity.sector)}.</p><p><b>Declared coupling:</b> ${esc(model.model_identity.matter_coupling)}.</p></div>
      <div class="section-head compact-head"><div><p class="eyebrow">One object chain, not a coverage maximum</p><h3>Six composed stages</h3></div><p>Three joins are certified exactly; two operational and empirical joins are registered with literature-scoped boundaries.</p></div><div class="model-stages">${modelStages}</div>
      <div class="model-comparison"><div><p class="eyebrow">Exact prediction</p><b>PPN γ = ${assemblyFraction(model.exact_prediction_rail.ppn_identification.gamma)}</b><span>Null-delay coefficient 1 + γ = ${assemblyFraction(model.exact_prediction_rail.null_delay.first_order_delay_coefficient)}</span></div><div><p class="eyebrow">Published Cassini estimate</p><b>${esc(empirical.publisher_reported_expression)}</b><span>Exact prediction lies inside the displayed band; normalized distance ${assemblyFraction(empirical.absolute_standardized_distance)}.</span></div><div><p class="eyebrow">Evidence type</p><b>Literature-scoped comparison</b><span>Arithmetic rechecked; raw spacecraft reduction and likelihood not reproduced.</span></div></div>
      <div class="section-head compact-head"><div><p class="eyebrow">Bounded success</p><h3>Model maturity rails</h3></div><p>Green applies only inside the declared solar-exterior prediction scope. Robustness remains unassessed.</p></div><div class="model-rails">${modelRails}</div>
      <details class="applicability-details"><summary>Applicability mask: ${model.applicability_summary.required_satisfied}/${model.applicability_summary.required} required obligations satisfied</summary><p>Out-of-scope obligations are not failed tests. “Touched, not required” records a nearby concept without claiming its full atlas theorem.</p><div class="assembly-table-wrap"><table class="assembly-table applicability-table"><thead><tr><th>Atlas obligation</th><th>Role in this assembly</th><th>Reason</th></tr></thead><tbody>${applicability}</tbody></table></div></details>
      <p class="model-boundary"><b>Boundary:</b> ${esc(model.empirical_comparison_rail.boundary)} <a href="sources/foundations/results/FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1.json">Open certificate</a>.</p></section>
      <section class="model-assembly mannheim-assembly"><div class="model-assembly-head"><div><p class="eyebrow">Second model-scoped assembly — mixed result</p><h2>Weyl action to NGC 3198</h2><p>${esc(mannheim.title)}</p></div><div class="model-disposition mixed"><b>Partial — random-error gate failed</b><span>Endpoint and coarse curve shape reproduced</span><small>Empirical support: NO · complete theory: NO</small></div></div>
      <div class="model-scope"><p><b>One model:</b> ${esc(mannheim.model_identity.theory)} — ${esc(mannheim.model_identity.sector)}.</p><p><b>Declared coupling:</b> ${esc(mannheim.model_identity.matter_coupling)}.</p></div>
      <div class="section-head compact-head"><div><p class="eyebrow">A checkable chain with an explicit failed gate</p><h3>Seven composed stages</h3></div><p>Exact local predecessors, published disk equations, a content-pinned parameter row, independent numerics, and a later cross-dataset check remain distinct objects.</p></div><div class="model-stages mannheim-stages">${mannheimStages}</div>
      ${mannheimResidualSvg(mannheim)}
      <div class="model-comparison mannheim-metrics"><div><p class="eyebrow">Published endpoint</p><b>${mannheimNumeric.predicted_endpoint.velocity_km_s.toFixed(1)} vs ${mannheimNumeric.observed_endpoint_velocity_reconstructed_km_s.toFixed(1)} km/s</b><span>${(100 * mannheimNumeric.endpoint_relative_velocity_residual).toFixed(2)}% relative residual; passes the declared 5% coarse audit gate.</span></div><div><p class="eyebrow">Later SPARC curve</p><b>RMS ${mannheimEmpirical.unweighted_rms_residual_km_s.toFixed(3)} km/s</b><span>Passes the declared 5 km/s coarse shape gate across ${mannheimEmpirical.points_inside_published_radius} points.</span></div><div class="failed-metric"><p class="eyebrow">Random-error gate</p><b>Reduced χ² ${mannheimEmpirical.reduced_chi_squared_no_refit.toFixed(3)}</b><span>Fails the declared ≤2 gate using SPARC random errors alone. This blocks empirical promotion.</span></div></div>
      <div class="section-head compact-head"><div><p class="eyebrow">No averaged verdict</p><h3>Eight independent maturity rails</h3></div><p>The green, orange, grey, and red states are not collapsed into a score. A close-looking curve does not erase a failed uncertainty-sensitive comparison.</p></div><div class="model-rails mannheim-rails">${mannheimRails}</div>
      <p class="model-boundary"><b>Boundary:</b> No parameter is refitted. SPARC is a later 3.6 μm reduction, not the paper's original heterogeneous blue-band dataset; the comparison is therefore an external stress test, not an original likelihood reproduction. ${esc(mannheimEmpirical.boundary)} <a href="sources/foundations/results/FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1.json">Open certificate</a>.</p></section>
      <section class="model-assembly fit-comparison-assembly"><div class="model-assembly-head"><div><p class="eyebrow">Same data · same luminous geometry · explicit parameter penalty</p><h2>NGC 3198 head-to-head control</h2><p>Three families are fitted to the same 39 velocities. This tests whether the Mannheim result is informative relative to indispensable Newtonian/GR controls.</p></div><div class="model-disposition comparative"><b>Scoped winner: GR + NFW</b><span>Only family passing reduced χ² ≤ 2</span><small>One galaxy · complete theory: NO</small></div></div>
      ${commonFitCurveSvg(fitComparison)}
      <div class="assembly-table-wrap"><table class="assembly-table fit-table"><thead><tr><th>Model family</th><th>Fitted parameters</th><th>RMS km/s</th><th>reduced χ²</th><th>AICc</th><th>gate</th></tr></thead><tbody>${fitRows}</tbody></table></div>
      <div class="metric-reading"><article><b>Why RMS and χ² disagree</b><p>Mannheim has the smallest unweighted RMS, but misses some precisely measured points. NFW therefore has the much lower uncertainty-weighted χ².</p></article><article><b>Why AICc matters</b><p>NFW uses two extra parameters. AICc penalizes them and still ranks NFW first, Mannheim second, and baryons-only third.</p></article><article><b>What this actually says</b><p>NFW wins this bounded protocol. It does not validate all of GR/ΛCDM or refute conformal gravity across galaxies.</p></article></div>
      <p class="model-boundary"><b>Boundary:</b> Random errors only; no distance, inclination, photometric, gas-profile, or other systematic marginalization. The common analytic disk is not the full SPARC numerical mass model, and no concentration–mass prior is imposed. <a href="sources/foundations/results/FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1.json">Open certificate</a>.</p></section></div>
      <div id="assemblyPanelProgrammes" class="assembly-panel ${state.assemblyPanel === "programmes" ? "active" : ""}" data-assembly-panel-body="programmes"><div class="section-head"><div><p class="eyebrow">Coverage envelopes</p><h2>Prototype assemblies are still not composed theories</h2></div><p>The two bounded chains keep their model identities and gate outcomes intact. The selectors here instead maximize atlas coverage and remain navigational prototypes.</p></div>
      <div class="section-head compact-head"><div><p class="eyebrow">People organize around questions, not axis codes</p><h2>Meet the research programmes</h2></div><p>Each card is a fair explanatory lens over the evidence cube: what the programme is trying to do, which ideas distinguish it, what this atlas currently samples, and where the analogy stops.</p></div>
      <div class="camp-gallery">${campCards}</div>
      <section class="camp-profile"><header><div><p class="eyebrow">${esc(CAMP_KIND_LABEL[assembly.camp_kind] || assembly.camp_kind)}</p><h2>${esc(assembly.label)}</h2><p>${esc(assembly.camp_summary)}</p></div><label><b>Choose another programme</b><select id="assemblySelect">${options}</select></label></header><div class="camp-question"><small>Central question</small><b>${esc(assembly.central_question)}</b></div><div class="camp-profile-grid"><article><h3>Lineage and conversation</h3><ul>${campLineage}</ul></article><article><h3>Signature ideas</h3><ul>${campIdeas}</ul></article><article><h3>What this atlas samples</h3><p>${esc(assembly.atlas_window)}</p></article></div><p class="camp-scope"><b>Important boundary:</b> ${esc(assembly.scope_note)}</p></section>
      <article class="assembly-boundary calibrated"><p class="eyebrow">How to read this programme's envelope</p><h3>${esc(completeCoverage)}: ${assembly.coverage.direct}/${assembly.coverage.total} obligations have direct results; composition is ${certifiedCount}/${assembly.interfaces.length} certified.</h3><p>${esc(assembly.aim)} These are separate maturity statements. Grey means unregistered or not yet evaluable, not failure. Orange means partial/open. Red is reserved for an explicit incompatibility, obstruction, or failed comparison.</p></article>
      <div class="section-head compact-head"><div><p class="eyebrow">Do not collapse distinct questions</p><h2>Seven independent maturity rails</h2></div><p>The rails have dependencies, but they are reported separately. Numerical reproduction is not empirical validation. Missing records are neutral; they are not failed tests.</p></div>
      <div class="assembly-gates">${gates}</div>
      <div class="section-head compact-head"><div><p class="eyebrow">Inputs selected from the cube</p><h2>Obligation source map</h2></div><p>The deterministic selector uses the strongest recorded status inside this prototype's declared region. Open any grade to inspect its exact boundary and evidence.</p></div>
      <div class="assembly-table-wrap"><table class="assembly-table"><thead><tr><th>Physical obligation</th><th>Selected regime / carrier</th><th>Recorded grade</th><th>Reviewed direct kind</th><th>Records</th></tr></thead><tbody>${cells}</tbody></table></div></div>
      <div id="assemblyPanelLedgers" class="assembly-panel ${state.assemblyPanel === "ledgers" ? "active" : ""}" data-assembly-panel-body="ledgers"><div class="section-head compact-head"><div><p class="eyebrow">The missing middle</p><h2>Typed interface ledger</h2></div><p>Coverage becomes a theory only through explicit joins. “Not assessed” means the atlas has no registered relation; it is neither compatibility nor incompatibility.</p></div>
      <div class="interface-vocabulary">${vocabulary}</div>
      <div class="assembly-table-wrap"><table class="assembly-table interface-table"><thead><tr><th>Join</th><th>From</th><th>Relation</th><th>To</th><th>Why this state</th></tr></thead><tbody>${interfaces}</tbody></table></div>
      <div class="section-head compact-head"><div><p class="eyebrow">Scoped non-identity, not a universal no-go</p><h2>Euclidean/Krein carrier boundary</h2></div><p>The positive finite-lattice measure and the all-real two-field path integral are not the same full carrier. Conditional perturbative or analytic bridges remain open.</p></div>
      <div class="assembly-table-wrap"><table class="assembly-table interface-table"><thead><tr><th>Carrier test</th><th>From</th><th>Relation</th><th>To</th><th>Certified scope</th></tr></thead><tbody>${carrierInterfaces}</tbody></table></div>
      <div class="section-head compact-head"><div><p class="eyebrow">No benchmark name is evidence</p><h2>Empirical benchmark ledger</h2></div><p>A future record must identify observables, data, prediction, comparison method, uncertainty, fit scope, and out-of-sample status. The ledger currently contains ${ASSEMBLIES.empirical_ledger.records.length} comparison records.</p></div>
      <div class="benchmark-grid">${benchmarks}</div>
      <article class="positive-control"><p class="eyebrow">External positive control — not a candidate assembly</p><h2>${esc(control.label)}</h2><p>${esc(control.scope)}</p><div class="control-rails">${controlRails}</div><div class="section-head compact-head"><div><p class="eyebrow">Domain-specific evidence</p><h3>What a populated empirical rail looks like</h3></div><p>${control.records.length} primary-source comparison records support ${control.benchmark_coverage.filter(item => item.status === "SUPPORTED_CONTROL").length}/${control.benchmark_coverage.length} benchmark families. Unregistered domains remain grey.</p></div><div class="benchmark-grid control-grid">${controlBenchmarks}</div><p class="control-boundary"><b>Boundary:</b> ${esc(control.does_not_establish[4])}. ${esc(control.does_not_establish[0])}.</p></article>
      <article class="viability-warning boundary"><b>Fail-closed boundary.</b> ${esc(ASSEMBLIES.unit)} ${esc(ASSEMBLIES.does_not_establish[4])}.</article></div>`;
    document.querySelectorAll("[data-assembly-panel]").forEach(button => button.addEventListener("click", () => {
      state.assemblyPanel = button.dataset.assemblyPanel;
      document.querySelectorAll("[data-assembly-panel]").forEach(item => item.classList.toggle("active", item.dataset.assemblyPanel === state.assemblyPanel));
      document.querySelectorAll("[data-assembly-panel-body]").forEach(item => item.classList.toggle("active", item.dataset.assemblyPanelBody === state.assemblyPanel));
      updateHash();
      document.getElementById(`assemblyPanel${state.assemblyPanel[0].toUpperCase()}${state.assemblyPanel.slice(1)}`)?.scrollIntoView({behavior: "smooth", block: "start"});
    }));
    document.getElementById("assemblySelect").addEventListener("change", event => { state.assembly = event.target.value; renderAssemblies(); updateHash(); });
    document.querySelectorAll("[data-camp]").forEach(button => button.addEventListener("click", () => { state.assembly = button.dataset.camp; renderAssemblies(); updateHash(); document.querySelector(".camp-profile")?.scrollIntoView({behavior: "smooth", block: "start"}); }));
    document.querySelectorAll(".assembly-cell-jump").forEach(button => button.addEventListener("click", () => openCell(button.dataset.cellJump)));
  }

  function setView(view) {
    state.view = view;
    document.querySelectorAll(".tab").forEach(x => x.classList.toggle("active", x.dataset.view === view));
    document.querySelectorAll(".view").forEach(x => x.classList.toggle("active", x.id === `${view}View`));
    document.querySelector(".controls").hidden = ["viability", "assemblies", "guide", "graph", "ladder"].includes(view);
    updateHash();
  }

  function refresh() {
    renderMatrix(); renderEvidence();
    const cells = filteredCells();
    document.getElementById("filterSummary").textContent = `${cells.length} of ${DATA.cells.length} coordinates match. Every coordinate has a recorded assessment; reviewed gaps are open questions, not results or absence claims.`;
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
  function csvField(cell, field) {
    if (field === "evidence") return cell.evidence.join("; ");
    if (field === "direct_kinds") return directKinds(cell).join("; ");
    if (field === "evidence_roles") return Object.entries(cellRoles(cell)).map(([id, role]) => `${id}=${role}`).join("; ");
    return cell[field];
  }

  function exportCsv() {
    const fields = ["foundation", "carrier", "obligation", "status", "direct_kinds", "emitted", "migration_relation", "evidence", "evidence_roles", "summary", "boundary"];
    const quote = value => `"${String(value ?? "").replaceAll('"', '""')}"`;
    download("foundations-matrix-filtered.csv", [fields.join(","), ...filteredCells().map(c => fields.map(f => quote(csvField(c, f))).join(","))].join("\n") + "\n", "text/csv");
  }
  function serializedFilters() { return {query: state.q, seeded_only: state.seededOnly, selected: Object.fromEntries(Object.entries(state.selected).map(([k, v]) => [k, [...v]]))}; }
  function downloadBrief(cell) {
    const text = `# Candidate investigation: ${title(cell.obligation)}\n\n- Mathematical regime: ${title(cell.foundation)}\n- Carrier: ${title(cell.carrier)}\n- Evidence state: ${gradeLabels(cell)}\n- Migration relation: ${cell.migration_relation}\n\n## Current record\n\n${cell.summary}\n\n## Boundary\n\n${cell.boundary}\n\n## Evidence to inspect\n\n${cell.evidence.length ? cell.evidence.map(x => `- ${x} (${ROLE[cellRoles(cell)[x]]?.label || "role unrecorded"})`).join("\n") : "- No evidence assigned; run literature search without treating this as an absence result."}\n\n## Immediate research question\n\nWhat exact additional assumption, representation, or construction would move this coordinate one evidence state forward without crossing its declared boundary?\n`;
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

  parseHash(); renderStats(); renderFilters(); renderGuide(); renderTheoryProfiles(); renderAssemblies(); renderGraph(); renderLadder(); bind(); setView(state.view); refresh();
  document.getElementById("digest").textContent = `Canonical data digest: ${DATA.canonical_digest}`;
  if (state.cell) openCell(state.cell);
})();
