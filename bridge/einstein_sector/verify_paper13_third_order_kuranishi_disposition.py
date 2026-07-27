#!/usr/bin/env python3
"""Independent fail-closed audit of the Paper 13 third-order disposition."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ci.standalone_provenance import read_attached_blob


MAP = ROOT / "paper/13-compact-weyl-maxwell-second-order-tangent-cone-claim-map.json"
TEX = ROOT / "paper/13-compact-weyl-maxwell-second-order-tangent-cone.tex"
ATLAS = ROOT / "residual_atlas/einstein-weyl-compact-cauchy-third-order-kuranishi-evaluation-fragment-v1.json"
BASELINE = "aa7f7ff984e930f71e208538deac6e22b9cc22cf"

PINNED_SHA256 = {
    "bridge/certificates/EINSTEIN_WEYL_COMPACT_CAUCHY_THIRD_ORDER_KURANISHI_EVALUATION_V1.json":
        "fcd47578b0409c2196ed07e83a8e400e7d8c45540abd899f0ce663e6fa74a87c",
    "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json":
        "d3770043041c94e52daa253c5dab1cf3730ea47f078e1b1553e42f00625496cd",
    "bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_ADJOINT_KERNEL_CLASSIFICATION_V1.json":
        "b0012a5ff0f1653523b90076e88a94212d16660a390128022b59598e20cc8ce0",
    "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json":
        "047594a9019eb68a000ecce1799063789714db632c41e67e48d37bdf0fc3657a",
    "bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_AMM_SEMIFREDHOLM_SLICE_V1.json":
        "d49e367008aa9b6e123db49bb4ebf244913ec98c02e84a20f82305c7a7f630aa",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def audit_claim_map(value: dict) -> None:
    assert value["lifecycle_state"] == "THEOREM_FROZEN"
    assert value["structural_theorem_lifecycle_state"] == "THEOREM_FROZEN"
    assert value["bounded_common_zero_lifecycle_state"] == "OPEN"
    assert value["source_baseline"] == BASELINE
    scope = value["certified_scope"]
    assert scope["complete_finite_support_exponential_polynomial_cone"] is True
    assert scope["complete_finite_support_bounded_obstruction_ledger"] is True
    assert scope["compact_cauchy_global_adjoint_kernel"] == "EXACTLY_FIVE_LIFTED_STABILIZERS"
    assert scope["balanced_third_order_global_K3_class"] == "ZERO_IN_CORRECTION_INDEPENDENT_TWO_DIMENSIONAL_QUOTIENT"
    assert scope["balanced_third_order_l2_image"] == "SPAN_H_J1_J2_RANK_3"
    assert scope["balanced_third_order_bounded_shells_for_certified_v"] == "OBSTRUCTED_ON_ALL_FOUR_OCCUPIED_ORIGINAL_SHELLS"
    assert scope["balanced_third_order_finite_exponential_polynomial_for_certified_v"] == "CERTIFIED_WITH_SECULAR_DEGREE_Q_LE_1_P_LE_2"
    assert scope["balanced_third_order_bounded_shell_quotient_over_all_v"] == "OPEN"
    assert scope["balanced_third_order_causal_retarded"] == "NO_CERTIFIED_MAP"
    disposition = value["third_order_disposition"]
    assert disposition["lifecycle_state"] == "THEOREM_FROZEN"
    assert "correction-independent" in disposition["correction_independent_claim"]
    assert "certified second-order representative" in disposition["representative_scoped_claim"]
    assert "remain open" in disposition["open_boundary"]


def main() -> None:
    claim_map = json.loads(MAP.read_text(encoding="utf-8"))
    audit_claim_map(claim_map)

    map_sources = {row["path"]: row["git_blob"] for row in claim_map["sources"]}
    for rel, expected_sha in PINNED_SHA256.items():
        ref, baseline_bytes = read_attached_blob(
            BASELINE,
            rel,
            expected_sha,
        )
        expected_blob = git("rev-parse", ref.object_spec)
        assert map_sources[rel] == expected_blob, rel

    cert = json.loads((ROOT / next(iter(PINNED_SHA256))).read_text(encoding="utf-8"))
    assert cert["global_constraint_projection"]["intrinsic_global_K3_class"] == "0"
    assert cert["global_constraint_projection"]["l2_image"] == "span{H,J_1,J_2}"
    assert cert["global_constraint_projection"]["quotient_basis"] == ["P_x", "J_3"]
    assert cert["classification"]["bounded_third_order_extension"] is False
    assert cert["classification"]["smooth_secular_third_order_extension"] is True
    assert cert["classification"]["causal_retarded_third_order_extension"] is False
    assert len(cert["resonant_shells"]) == 4
    assert all(any(not witness["exact_zero"] for witness in shell["pairing_witnesses"])
               for shell in cert["resonant_shells"])

    tex = TEX.read_text(encoding="utf-8")
    required_tex = (
        "Correction-independent global cubic class versus a",
        "finite exponential-polynomial third-order correction exists",
        "homogeneous second-order-correction freedom.  Items~2 and~3 retain the",
        "bounded third-order verdict after quotienting the shell functionals",
        "\\textsc{theorem-frozen} for external specialist review",
    )
    for phrase in required_tex:
        assert phrase in tex, phrase
    assert tex.index("\\section{Third-order Kuranishi input gate}") < tex.index("\\begin{thebibliography}")

    atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in atlas["entries"]}
    assert rows["einstein.ph.wm.balanced_ell2.third_order.global_kuranishi_quotient"]["descriptions"]["nonlinear"] == "CERTIFIED"
    bounded = rows["einstein.ph.wm.balanced_ell2.third_order.bounded_shells"]
    assert bounded["descriptions"]["nonlinear"] == "OBSTRUCTED"
    assert "quotient over all second-order corrections is open" in bounded["mode_data"]["resonance"]["statement"]
    assert rows["einstein.ph.wm.balanced_ell2.third_order.smooth_secular"]["descriptions"]["causal"] == "NO_CERTIFIED_MAP"

    mutations = []
    promoted_shell_quotient = copy.deepcopy(claim_map)
    promoted_shell_quotient["certified_scope"]["balanced_third_order_bounded_shell_quotient_over_all_v"] = "CERTIFIED"
    mutations.append(promoted_shell_quotient)
    promoted_causal = copy.deepcopy(claim_map)
    promoted_causal["certified_scope"]["balanced_third_order_causal_retarded"] = "CERTIFIED"
    mutations.append(promoted_causal)
    lost_global_class = copy.deepcopy(claim_map)
    lost_global_class["certified_scope"]["balanced_third_order_global_K3_class"] = "ZERO_FOR_ONE_REPRESENTATIVE_ONLY"
    mutations.append(lost_global_class)
    for mutation in mutations:
        try:
            audit_claim_map(mutation)
        except AssertionError:
            continue
        raise AssertionError("claim-promotion mutation was not rejected")

    print("PAPER13_THIRD_ORDER_KURANISHI_DISPOSITION: PASS")


if __name__ == "__main__":
    main()
