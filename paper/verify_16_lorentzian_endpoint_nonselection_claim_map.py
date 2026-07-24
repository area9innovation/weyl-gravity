#!/usr/bin/env python3
"""Independent semantic and provenance verifier for Paper 16."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAPER = ROOT / "paper/16-lorentzian-endpoint-nonselection-pure-weyl.tex"
DEFAULT_MAP = ROOT / "paper/16-lorentzian-endpoint-nonselection-pure-weyl-claim-map.json"
DEFAULT_COVERAGE = ROOT / "planning/paper-coverage/phase4-paper16-endpoint-nonselection-overlay-2026-07-24.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"REFUSED: {message}")


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def require_flag(data: dict, key: str, value: bool, label: str) -> None:
    actual = data.get("claim_flags", {}).get(key)
    if actual is not value:
        fail(f"{label} flag drift: {key}={actual!r}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", type=Path, default=DEFAULT_PAPER)
    parser.add_argument("--claim-map", type=Path, default=DEFAULT_MAP)
    parser.add_argument("--coverage", type=Path, default=DEFAULT_COVERAGE)
    args = parser.parse_args()

    paper = resolve(args.paper)
    claim_path = resolve(args.claim_map)
    coverage_path = resolve(args.coverage)
    claims = json.loads(claim_path.read_text())
    text = paper.read_text()

    if claims.get("paper_id") != "PAPER_16_LORENTZIAN_ENDPOINT_NONSELECTION":
        fail("wrong paper identity")
    if claims.get("lifecycle_state") != "DRAFT_ALLOWED":
        fail("paper lifecycle overpromotion")
    if claims.get("paper_sha256") != digest(paper):
        fail("paper hash drift")

    for name, authority in claims.get("authorities", {}).items():
        path = ROOT / authority["path"]
        if digest(path) != authority["sha256"]:
            fail(f"authority content drift: {name}")

    required_phrases = [
        "T_-(\\omega)\\in GL(3,\\C)",
        "\\operatorname{diag}(1,-1,-1)",
        "Smith valuations \\((0,0,2)\\)",
        "connection-level intrinsic exceptional point",
        "A second-order physical",
        "Green-resolvent pole remains conditional",
        "No branch-resolving rational involution",
        "Exact scalar threshold nonresonance",
        "A two-region Volterra remainder",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            fail(f"required scoped statement missing: {phrase}")

    forbidden_phrases = [
        "T_+(\\omega)\\in GL(3,\\C) for every real \\(\\omega>0\\)",
        "the full Bach resolvent has a genuine second-order pole",
        "time-domain stability is established",
        "the theory is quantum unitary",
        "Every simple spin-two Regge--Wheeler quasinormal frequency",
    ]
    for phrase in forbidden_phrases:
        if phrase in text:
            fail(f"forbidden promotion present: {phrase}")

    authorities = claims["authorities"]
    incoming = json.loads((ROOT / authorities["incoming_global"]["path"]).read_text())
    require_flag(
        incoming,
        "Tminus_invertible_all_real_positive_omega_certified",
        True,
        "incoming",
    )
    require_flag(
        incoming,
        "Gminus_inertia_all_real_positive_omega_certified",
        True,
        "incoming",
    )
    outgoing = json.loads((ROOT / authorities["outgoing_cell"]["path"]).read_text())
    require_flag(outgoing, "Tplus_invertible_on_declared_cell", True, "outgoing")
    require_flag(
        outgoing,
        "generic_positive_real_outgoing_population_off_discrete_set",
        True,
        "outgoing",
    )
    require_flag(
        outgoing,
        "uniform_full_positive_axis_inverse_bound_certified",
        False,
        "outgoing",
    )
    growth = json.loads((ROOT / authorities["no_growth"]["path"]).read_text())
    require_flag(
        growth,
        "full_six_state_no_LHP_growing_separated_modes_certified",
        True,
        "growth",
    )
    require_flag(growth, "time_domain_linear_stability_certified", False, "growth")
    ep2 = json.loads((ROOT / authorities["qnm_spin_one_unit"]["path"]).read_text())
    require_flag(ep2, "full_connection_smith_valuations_0_0_2", True, "EP2")
    require_flag(ep2, "green_resolvent_second_order_pole_established", False, "EP2")
    threshold = json.loads((ROOT / authorities["threshold"]["path"]).read_text())
    if threshold.get("status") != "EXACT_THRESHOLD_IDENTITIES_PASS":
        fail("threshold certificate status drift")
    if (
        "a punctured positive-real interval on which T_plus is invertible"
        not in threshold.get("does_not_establish", [])
    ):
        fail("threshold scattering promotion gate missing")

    fail_closed = claims.get("fail_closed_scope", {})
    if any(value is not False for value in fail_closed.values()):
        fail("claim map contains a fail-closed promotion")

    coverage = json.loads(coverage_path.read_text())
    if coverage.get("claim_map_sha256") != digest(claim_path):
        fail("coverage-to-claim-map hash drift")
    if len(coverage.get("nodes", [])) != 5:
        fail("coverage claim count drift")
    print("PASS: Paper 16 claim map and semantic boundaries")


if __name__ == "__main__":
    main()
