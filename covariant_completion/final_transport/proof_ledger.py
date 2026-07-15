"""Deterministic proof ledger for the completed covariant H4 theorem.

The ledger is deliberately generated from the persisted final-claim DAG.  It
does not create a second theorem gate.  Direct evidence is used when a
terminal requirement has it; derived requirements inherit the complete leaf
evidence of their dependency subgraph.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from covariant_completion.certificate_provenance import (
    DigestMode,
    digest_file,
    load_json_object,
)


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE_DIR = ROOT / "covariant_completion" / "certificates"
DAG_PATH = CERTIFICATE_DIR / "final_claim_dependencies.json"
JSON_PATH = ROOT / "covariant_completion" / "generated" / "covariant_H4_proof_ledger.json"
MARKDOWN_PATH = ROOT / "covariant_completion" / "generated" / "covariant_H4_proof_ledger.md"

TERMINAL_REQUIREMENT_COUNT = 23

REPRODUCTION_COMMANDS: dict[str, tuple[str, ...]] = {
    "curved_operator_identity": (
        "python3 symbolic/verify_conformal_curved_operator_workstream.py --guards --claim-curved-operator-identity",
    ),
    "curved_deformation_retract": (
        "python3 symbolic/verify_conformal_curved_retract.py --guards --claim-curved-deformation-retract",
    ),
    "curved_current_comparison": (
        "python3 symbolic/verify_conformal_curved_current.py --guards --claim-curved-current --claim-curved-potentials --claim-green-current-equality",
    ),
    "scalar_wave_witness_no_go": (
        "python3 symbolic/verify_conformal_curved_operator_workstream.py --guards",
    ),
    "weyl_symbol_helicity_isomorphism": (
        "python3 symbolic/verify_conformal_curvature_evolution.py --guards",
    ),
    "curved_EB_equations": (
        "python3 symbolic/verify_conformal_curvature_evolution.py --guards",
    ),
    "curved_EB_first_order_closure": (
        "python3 symbolic/verify_conformal_curvature_evolution.py --guards",
    ),
    "curved_EB_symmetric_hyperbolicity": (
        "python3 symbolic/verify_conformal_curvature_evolution.py --guards",
    ),
    "curved_sourced_constraint_identity": (
        "python3 symbolic/verify_conformal_curvature_evolution.py --guards",
    ),
    "curved_constraint_propagation": (
        "python3 symbolic/verify_conformal_curvature_evolution.py --guards",
    ),
    "EAL_curvature_spectrum_match": (
        "python3 symbolic/verify_conformal_curvature_eal_spectrum.py --guards",
    ),
    "support_local_prolongation_retract": (
        "python3 symbolic/verify_conformal_curvature_evolution.py --guards",
    ),
    "prolonged_BV_operator_identity": (
        "python3 symbolic/verify_conformal_curvature_evolution.py --guards",
    ),
    "direct_tractor_causal_homotopy": (
        "python3 symbolic/verify_conformal_full_prolonged_green_homotopy_assembly.py --guards",
    ),
    "causal_green_homotopy": (
        "python3 symbolic/verify_conformal_full_prolonged_green_homotopy_assembly.py --guards",
    ),
    "causal_quasi_isomorphism": (
        "python3 symbolic/verify_conformal_causal_transport_recognition.py --guards",
    ),
    "residual_endpoint_recovery": (
        "python3 symbolic/verify_conformal_causal_transport_recognition.py --guards",
    ),
    "SO42_equivariant_transport": (
        "python3 symbolic/verify_conformal_so42_causal_transport.py --guards",
    ),
    "prolonged_current_comparison": (
        "python3 symbolic/verify_conformal_prolonged_current_comparison.py",
    ),
    "direct_causal_pairing_transport": (
        "python3 symbolic/verify_conformal_direct_causal_pairing_transport.py --guards",
    ),
    "pairing_compatibility": (
        "python3 symbolic/verify_conformal_direct_causal_pairing_transport.py --guards",
        "python3 symbolic/verify_conformal_curved_current.py --guards --claim-green-current-equality",
    ),
    "residual_H4_is_C2": (
        "python3 symbolic/verify_conformal_completed_residual.py",
    ),
    "residual_gram_is_I2": (
        "python3 symbolic/verify_conformal_completed_residual.py",
    ),
}

SCOPED_CAVEATS: dict[str, str] = {
    "curved_operator_identity": "Exact operator identities; it does not reinstate the ruled-out scalar-symbol witness.",
    "curved_deformation_retract": "Support-local classical BV equivalence, not a Green operator construction.",
    "curved_current_comparison": "Off-shell d+Q/current comparison; causal Green pairing is a separate gate.",
    "scalar_wave_witness_no_go": "Scoped to the 24-field pointwise-pairing, first-order-companion scalar witness.",
    "weyl_symbol_helicity_isomorphism": "A reduced null-symbol statement, not by itself global Green hyperbolicity.",
    "curved_EB_equations": "Exact free linearized cylinder equations only.",
    "curved_EB_first_order_closure": "Closure of the certified Weyl--Cotton state/constraint presentation.",
    "curved_EB_symmetric_hyperbolicity": "The positive PDE symmetrizer is not the BV/Krein pairing.",
    "curved_sourced_constraint_identity": "Applies to the explicitly certified compatible-source rows.",
    "curved_constraint_propagation": "Constraint propagation is used with, not instead of, sourced compatibility.",
    "EAL_curvature_spectrum_match": "All-level free spectrum audit; no finite-cutoff extrapolation is used.",
    "support_local_prolongation_retract": "Finite-order graph/mapping-cylinder maps; no inverse curvature reconstruction.",
    "prolonged_BV_operator_identity": "All-row free BV identity for the certified prolonged presentation.",
    "direct_tractor_causal_homotopy": "Direct hybrid homotopy; it does not claim a canonical endpoint inverse.",
    "causal_green_homotopy": "Free Lorentzian causal contraction, not an interacting/Hadamard/QME theorem.",
    "causal_quasi_isomorphism": "Uses compactness of S3 to identify spacelike-compact and smooth global solutions.",
    "residual_endpoint_recovery": "Recovers the fifteen classical reducibilities and dual endpoints only once.",
    "SO42_equivariant_transport": "Equivariance is on cohomology via the certified cutoff chain homotopy.",
    "prolonged_current_comparison": "Cyclic current equivalence; the hyperbolic symmetrizer remains distinct.",
    "direct_causal_pairing_transport": "Implementation-neutral pairing transport; no canonical D_TF inverse is asserted.",
    "pairing_compatibility": "Derived from current, causal, and E/A/L inputs rather than an independent Gram computation.",
    "residual_H4_is_C2": "Centered residual deformation/vertex cohomology, not a one-particle state count.",
    "residual_gram_is_I2": "Cohomological Gram I2, not a positive particle Hilbert metric.",
}

EXTERNAL_REVIEW_CHECKLIST = (
    {
        "id": "R1",
        "question": "Do the action, curvature, BV-degree, adjoint, and orientation conventions agree before any comparison?",
        "independent_action": "Re-derive a convention table from the action and recompute at least one sign-sensitive adjoint and current boundary term by hand.",
        "reject_if": "The review merely imports the generated convention constants.",
    },
    {
        "id": "R2",
        "question": "Are Q^2=0 and QW+WQ=P consequences of the curved coefficients on every row?",
        "independent_action": "Reconstruct representative field, ghost, antifield, and nonminimal rows from the action/gauge data and compare after independent derivative normalization.",
        "reject_if": "Only principal symbols or the persisted zero-defect fields are inspected.",
    },
    {
        "id": "R3",
        "question": "Is the scalar-wave no-go basis-independent and scoped correctly?",
        "independent_action": "Recompute rank(E2)=11 and rank(K1)=9 at a generic null covector and identify the helicity +2/-2 quotient representation.",
        "reject_if": "The conclusion is broadened to a no-go for Green hyperbolicity or the BV complex.",
    },
    {
        "id": "R4",
        "question": "Do the curved finite-HPL transfer and Weyl--Cotton first-order system reproduce the covariant Bianchi--Bach operator?",
        "independent_action": "Re-derive the finite homological-perturbation transfer, perform an independent 3+1 Bach decomposition, and test an independently generated complete Weyl two-jet basis.",
        "reject_if": "Agreement is checked only against fitted frequencies or principal symbols.",
    },
    {
        "id": "R5",
        "question": "Are symmetric hyperbolicity and sourced constraint propagation both established?",
        "independent_action": "Recompute the symmetrized principal matrices and derive the inhomogeneous subsidiary identity for arbitrary compatible sources.",
        "reject_if": "Homogeneous constraint propagation is substituted for source compatibility.",
    },
    {
        "id": "R6",
        "question": "Does curvature propagation retain all E, A, and L towers at every level?",
        "independent_action": "Derive the SO(4) character/rank identities symbolically and check low-level exceptional ranges separately.",
        "reject_if": "A finite harmonic sample or only the Einstein tower is used.",
    },
    {
        "id": "R7",
        "question": "Is the prolongation equivalence local, all-row, and support preserving?",
        "independent_action": "Trace the mapping-cylinder maps through fields, equations, identities, antifields, and nonminimal rows; search explicitly for inverse curl/Laplacian/projectors.",
        "reject_if": "Only field rows or a curvature-to-metric inverse are checked.",
    },
    {
        "id": "R8",
        "question": "Does the hybrid causal homotopy satisfy the two-sided all-row identity and support bound?",
        "independent_action": "Re-derive the 356+30 projector decomposition and recursively verify the advanced/retarded endpoint blocks and graded adjoint relation.",
        "reject_if": "Strong hyperbolicity of a monolithic first-order symbol is assumed or support is inferred from mode projectors.",
    },
    {
        "id": "R9",
        "question": "Does the causal support exact sequence really induce the compact-to-spacelike-compact quasi-isomorphism?",
        "independent_action": "Reconstruct the exact sequence for compact and retarded/advanced supports, prove exactness directly, and check that Lambda_+-Lambda_- realizes the connecting morphism.",
        "reject_if": "The quasi-isomorphism is inferred only from existence of Cauchy evolution or from compactness of S3.",
    },
    {
        "id": "R10",
        "question": "Are all fifteen residual endpoints recovered without duplication?",
        "independent_action": "Construct temporal-cutoff representatives independently and verify their causal images, grading 4+7+4, duals, and suspension sign.",
        "reject_if": "Global CKVs are inserted by a nonlocal projector.",
    },
    {
        "id": "R11",
        "question": "Is the causal bridge SO(4,2)-equivariant rather than only a vector-space isomorphism?",
        "independent_action": "Recompute the cutoff-equivariance identity [kappa,rho]=[Q,[chi,rho]] and representative proper-conformal brackets on cohomology.",
        "reject_if": "Only R x SO(4) covariance of the Cauchy split is shown.",
    },
    {
        "id": "R12",
        "question": "Do Green, prolonged, auxiliary, metric, Cauchy, and E/A/L pairings coincide?",
        "independent_action": "Derive the Green/current Stokes identity independently, recompute the graded-adjoint sign, and recover the E/A/L signs +1,-1,-1 from the action current.",
        "reject_if": "The positive PDE symmetrizer or a few normalized modes replace the action current.",
    },
    {
        "id": "R13",
        "question": "Is residual H4=C2 with Gram I2 independently certified?",
        "independent_action": "Repeat the exact-arithmetic cocycle, boundary, and Gram reduction from a generated ansatz without hard-coding W_+^2,W_-^2 as the answer.",
        "reject_if": "The covariant theorem is treated as a fresh finite-cutoff CE computation.",
    },
    {
        "id": "R14",
        "question": "What do the hashes and verifier reruns actually establish?",
        "independent_action": "Confirm hashes bind the reviewed inputs, then perform at least R1--R13 selectively from definitions rather than trusting matching receipts.",
        "reject_if": "Re-running repository scripts is presented as independent mathematical review.",
    },
)


class ProofLedgerError(AssertionError):
    """Fail-closed ledger construction error."""


def _sha256(path: Path) -> str:
    return digest_file(path, mode=DigestMode.RAW_FILE, root=ROOT)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = load_json_object(path, root=ROOT)
    except (OSError, TypeError, ValueError) as exc:
        raise ProofLedgerError(f"cannot read certificate {path}: {exc}") from exc
    return value


def _resolve_evidence_path(name: str) -> Path:
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts:
        raise ProofLedgerError(f"unsafe evidence path: {name}")
    if "/" in name:
        path = ROOT / relative
    else:
        path = CERTIFICATE_DIR / relative
    if not path.is_file():
        raise ProofLedgerError(f"missing authoritative evidence: {path}")
    _load_json(path)
    return path


def _leaf_evidence(
    claim: str, claims: Mapping[str, Mapping[str, Any]], trail: tuple[str, ...] = ()
) -> list[tuple[str, str]]:
    if claim in trail:
        raise ProofLedgerError("claim dependency cycle: " + " -> ".join((*trail, claim)))
    if claim not in claims:
        raise ProofLedgerError(f"unknown dependency claim: {claim}")
    node = claims[claim]
    evidence = node.get("evidence")
    requires = node.get("requires")
    if not isinstance(evidence, list) or not all(isinstance(x, str) for x in evidence):
        raise ProofLedgerError(f"malformed evidence list for {claim}")
    if not isinstance(requires, list) or not all(isinstance(x, str) for x in requires):
        raise ProofLedgerError(f"malformed requirement list for {claim}")
    result = [(claim, name) for name in evidence]
    for dependency in requires:
        result.extend(_leaf_evidence(dependency, claims, (*trail, claim)))
    return result


def _validate_command(command: str) -> None:
    fields = command.split()
    if len(fields) < 2 or fields[0] != "python3":
        raise ProofLedgerError(f"unsupported reproduction command: {command}")
    script = ROOT / fields[1]
    if not script.is_file():
        raise ProofLedgerError(f"missing verifier named by command: {fields[1]}")


def build_ledger(dag: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build and validate the deterministic proof ledger payload."""

    snapshot = deepcopy(dict(dag)) if dag is not None else _load_json(DAG_PATH)
    claims = snapshot.get("claims")
    if not isinstance(claims, Mapping):
        raise ProofLedgerError("final DAG has no claims mapping")
    terminal = claims.get("final_covariant_H4")
    if not isinstance(terminal, Mapping):
        raise ProofLedgerError("final DAG has no terminal theorem claim")
    requirements = terminal.get("requires")
    if not isinstance(requirements, list) or not all(
        isinstance(name, str) for name in requirements
    ):
        raise ProofLedgerError("terminal requirements are malformed")
    if len(requirements) != TERMINAL_REQUIREMENT_COUNT or len(set(requirements)) != len(
        requirements
    ):
        raise ProofLedgerError(
            f"expected {TERMINAL_REQUIREMENT_COUNT} distinct terminal requirements"
        )
    if set(requirements) != set(REPRODUCTION_COMMANDS):
        raise ProofLedgerError("reproduction-command coverage drifted from terminal DAG")
    if set(requirements) != set(SCOPED_CAVEATS):
        raise ProofLedgerError("scoped-caveat coverage drifted from terminal DAG")
    if terminal.get("status") is not True:
        raise ProofLedgerError("the completed-theorem ledger cannot promote a false terminal")

    inventory: dict[str, dict[str, Any]] = {}
    entries: list[dict[str, Any]] = []
    for ordinal, name in enumerate(requirements, start=1):
        node = claims.get(name)
        if not isinstance(node, Mapping):
            raise ProofLedgerError(f"missing terminal requirement node: {name}")
        if node.get("status") is not True:
            raise ProofLedgerError(f"false terminal requirement: {name}")
        note = node.get("note")
        classification = node.get("classification")
        if not isinstance(note, str) or not note.strip():
            raise ProofLedgerError(f"missing mathematical statement for {name}")
        if not isinstance(classification, str) or not classification:
            raise ProofLedgerError(f"missing classification for {name}")
        evidence_pairs = _leaf_evidence(name, claims)
        if not evidence_pairs:
            raise ProofLedgerError(f"terminal requirement has no transitive evidence: {name}")
        evidence_names: list[str] = []
        source_claims: dict[str, list[str]] = {}
        for source_claim, evidence_name in evidence_pairs:
            if evidence_name not in evidence_names:
                evidence_names.append(evidence_name)
            source_claims.setdefault(evidence_name, [])
            if source_claim not in source_claims[evidence_name]:
                source_claims[evidence_name].append(source_claim)
            path = _resolve_evidence_path(evidence_name)
            relative = path.relative_to(ROOT).as_posix()
            digest = _sha256(path)
            certificate = _load_json(path)
            schema_label = certificate.get("schema")
            if not schema_label and "schema_version" in certificate:
                schema_label = f"schema_version={certificate['schema_version']}"
            prior = inventory.get(relative)
            if prior is not None and prior["sha256"] != digest:
                raise ProofLedgerError(f"inconsistent evidence digest: {relative}")
            inventory[relative] = {
                "sha256": digest,
                "schema": schema_label or "UNDECLARED",
            }
        commands = list(REPRODUCTION_COMMANDS[name])
        for command in commands:
            _validate_command(command)
        entries.append(
            {
                "ordinal": ordinal,
                "requirement": name,
                "status": True,
                "classification": classification,
                "mathematical_statement": note,
                "authoritative_evidence": [
                    {
                        "path": _resolve_evidence_path(evidence_name)
                        .relative_to(ROOT)
                        .as_posix(),
                        "source_claims": source_claims[evidence_name],
                    }
                    for evidence_name in evidence_names
                ],
                "reproduction_commands": commands,
                "scoped_caveat": SCOPED_CAVEATS[name],
            }
        )

    terminal_receipts = {}
    for name in (
        "covariant_completion/certificates/final_claim_dependencies.json",
        "covariant_completion/certificates/four_flag_closure_status.json",
        "covariant_completion/certificates/covariant_H4_transport.json",
        "covariant_completion/certificates/covariant_gram_transport.json",
    ):
        path = ROOT / name
        _load_json(path)
        terminal_receipts[name] = _sha256(path)

    return {
        "schema": "pure-weyl-covariant-H4-proof-ledger-v1",
        "dependency_tag": "LORENTZIAN-CAUSAL",
        "theorem": {
            "claim": "final_covariant_H4",
            "status": True,
            "statement": "H^4_cov = span{[W_+^2],[W_-^2]} with G_cov = I_2",
            "terminal_requirement_count": TERMINAL_REQUIREMENT_COUNT,
            "source_DAG_sha256": _sha256(DAG_PATH),
            "derivation_policy": "transport through pairing-compatible causal quasi-isomorphisms; no auxiliary H4 recomputation",
        },
        "terminal_receipts": terminal_receipts,
        "requirements": entries,
        "evidence_inventory": dict(sorted(inventory.items())),
        "external_review_policy": {
            "rerunning_scripts_is_not_independent_rederivation": True,
            "checklist": list(EXTERNAL_REVIEW_CHECKLIST),
        },
    }


def render_markdown(payload: Mapping[str, Any]) -> str:
    """Render the human-readable ledger from the validated JSON payload."""

    theorem = payload["theorem"]
    lines = [
        "# Covariant H4 proof ledger",
        "",
        "This file is generated by `symbolic/verify_conformal_covariant_H4_proof_ledger.py`.",
        "It maps the live terminal DAG to exact evidence. Matching hashes establish",
        "artifact identity; they do **not** replace independent mathematical review.",
        "",
        f"- Theorem: `{theorem['statement']}`",
        f"- Status: **{'PASS' if theorem['status'] else 'FAIL'}**",
        f"- Dependency tag: `{payload['dependency_tag']}`",
        f"- Terminal requirements: `{theorem['terminal_requirement_count']}`",
        f"- Source DAG SHA-256: `{theorem['source_DAG_sha256']}`",
        f"- Policy: {theorem['derivation_policy']}",
        "",
        "## Requirement ledger",
        "",
    ]
    for entry in payload["requirements"]:
        evidence = ", ".join(
            f"`{item['path']}`" for item in entry["authoritative_evidence"]
        )
        lines.extend(
            [
                f"### {entry['ordinal']}. `{entry['requirement']}` — PASS",
                "",
                entry["mathematical_statement"],
                "",
                f"- Classification: `{entry['classification']}`",
                f"- Authoritative evidence: {evidence}",
                "- Reproduce:",
                *[f"  - `{command}`" for command in entry["reproduction_commands"]],
                f"- Scoped caveat: {entry['scoped_caveat']}",
                "",
            ]
        )
    lines.extend(["## Evidence inventory", ""])
    for path, item in payload["evidence_inventory"].items():
        lines.append(
            f"- `{path}` — SHA-256 `{item['sha256']}`; schema `{item['schema']}`"
        )
    lines.extend(["", "## Terminal receipts", ""])
    for path, digest in payload["terminal_receipts"].items():
        lines.append(f"- `{path}` — SHA-256 `{digest}`")
    lines.extend(
        [
            "",
            "## Skeptical external-review checklist",
            "",
            "A reviewer should independently rederive the sensitive mathematics, not",
            "merely rerun repository scripts.",
            "",
        ]
    )
    for item in payload["external_review_policy"]["checklist"]:
        lines.extend(
            [
                f"### {item['id']}. {item['question']}",
                "",
                f"- Independent action: {item['independent_action']}",
                f"- Reject the review if: {item['reject_if']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def outputs_are_current(payload: Mapping[str, Any] | None = None) -> bool:
    expected = payload if payload is not None else build_ledger()
    try:
        return (
            JSON_PATH.read_text(encoding="utf-8") == canonical_json(expected)
            and MARKDOWN_PATH.read_text(encoding="utf-8")
            == render_markdown(expected)
        )
    except OSError:
        return False


def write_outputs(payload: Mapping[str, Any] | None = None) -> None:
    value = payload if payload is not None else build_ledger()
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(canonical_json(value), encoding="utf-8")
    MARKDOWN_PATH.write_text(render_markdown(value), encoding="utf-8")
