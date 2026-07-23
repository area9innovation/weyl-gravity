#!/usr/bin/env python3
"""Independent fail-closed verifier for the horizon transport shortfall."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    cert = json.loads((HERE / "certificate.json").read_text())
    controls = json.loads((HERE / "controls.json").read_text())
    render = json.loads((HERE / "render-metadata.json").read_text())
    graph = json.loads((HERE / "grassmann-preflight-metadata.json").read_text())

    require(cert["lifecycle"] == "SHORTFALL", "shortfall lifecycle changed")
    require(
        cert["terminal_disposition"] == "VALIDATED_METHOD_SHORTFALL_NOT_PHYSICS",
        "terminal disposition widened",
    )
    require(
        cert["missing_dependency"]["id"]
        == "PARAMETER_CORRELATED_VALIDATED_GRASSMANN_RICCATI_FLOW",
        "missing dependency changed",
    )
    require(
        "No parameter-correlated real 12x6 horizon-to-r4 map is emitted."
        in cert["not_established"],
        "fail-closed r4 boundary missing",
    )
    orient = cert["orientation_contract"]
    require(orient["increasing_r_radial_current"] == "+", "radial orientation")
    require(orient["future_horizon_exterior_stokes_orientation"] == "-", "horizon orientation")

    artifacts = cert["artifacts"]
    paths = {
        "producer_sha256": "produce.py",
        "full_column_source_sha256": "validated_horizon_to_r4.forge",
        "grassmann_producer_sha256": "produce_grassmann_preflight.py",
        "grassmann_source_sha256": "validated_regular_subspace_first_shell.forge",
    }
    for key, rel in paths.items():
        require(sha256(HERE / rel) == artifacts[key], f"hash mismatch: {rel}")
    require(
        render["imports"][
            "symplectic-reconstruction/black_hole_programme/phase3/"
            "axial_endpoint_remainder_enclosures/validated_horizon_initializer.forge"
        ]
        == artifacts["initializer_source_sha256"],
        "initializer provenance mismatch",
    )

    require(render["generator"] == graph["generator"] == 7315, "generator mismatch")
    require(render["omega_cell"] == graph["omega_cell"] == ["1/2", "129/256"], "cell mismatch")
    require(render["raw_future_regular_selector"] == [0, 1, 2], "raw selector")
    require(render["public_future_regular_selector"] == [0, 1, 4], "public selector")
    require(render["rebase_bits"] == graph["dyadic_rebase_bits"] == 128, "rebase bits")

    ids = [row["id"] for row in controls["controls"]]
    require(
        ids
        == [
            "wide-cell-full-column",
            "narrow-cell-n3-full-column",
            "auxiliary-rho-2^-40-full-column",
            "one-shell-graph-reset-cadence-four",
        ],
        "control ledger changed",
    )
    for row in controls["controls"][:3]:
        widths = row["shell_widths"]
        require(all(b > a for a, b in zip(widths, widths[1:])), f"non-growing control {row['id']}")
        require("trap" in row["terminal"], f"untyped terminal {row['id']}")
    graph_control = controls["controls"][3]
    require(graph_control["computed_rank"] == [6, 6], "computed graph rank")
    require(graph_control["rank_certified"] is False, "uncertified graph promoted")
    require(
        graph_control["reconstruction_width"] > graph_control["direct_width"],
        "failed width control erased",
    )
    require(
        controls["required_successor"]["initial_real_pivot_rows"] == [1, 2, 8, 5, 6, 10],
        "reviewed pivot map changed",
    )

    full_src = (HERE / "validated_horizon_to_r4.forge").read_text()
    graph_src = (HERE / "validated_regular_subspace_first_shell.forge").read_text()
    require("fn sl_local_transition" in full_src, "local structured kernel absent")
    require("fn sl_compose" not in full_src, "withdrawn multi-panel composer imported")
    require("7315" in full_src and "7315" in graph_src, "shared generator absent")
    require("ivam_solve_rect" in graph_src, "certified graph solve absent")

    print(
        "PASS phase3 axial horizon transport: exact method shortfall; "
        "no r4 or scattering promotion"
    )


if __name__ == "__main__":
    main()
