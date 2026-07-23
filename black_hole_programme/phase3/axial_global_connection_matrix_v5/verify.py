"""Independent claim-boundary and generated-Forge replay for v5."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
PHYSICS = HERE.parents[3]
FORGE = Path("/home/alstrup/area9/tango/forge")
CERTIFICATE = HERE / "certificate.json"
ADAPTER = HERE / "validated_global_connection.forge"


class VerifyError(RuntimeError):
    pass


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _import_path(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else PHYSICS / path


def verify_data(data: dict, adapter_text: str | None = None) -> bool:
    if data.get("schema") != "phase3-black-hole-axial-global-connection-matrix-v5-v1":
        raise VerifyError("schema mismatch")
    if data.get("result_token") != "BH_PHASE3_AXIAL_GLOBAL_CONNECTION_MATRIX_V5":
        raise VerifyError("result token mismatch")
    if data.get("stop_condition_disposition") != "SHORTFALL":
        raise VerifyError("terminal disposition was silently promoted")
    if "parameter-dependent affine frames" not in data.get("missing_dependency", ""):
        raise VerifyError("missing dependency is not explicit")
    if data.get("missing_dependency_request") != "planning/forge-requests/phase3-ivlinode-parametric-affine-rectangular.json":
        raise VerifyError("parametric affine request is not linked")
    declaration = data["declaration"]
    if list(map(Fraction, declaration["target_frequency_cover"])) != [Fraction(1, 2), Fraction(3, 4)]:
        raise VerifyError("target frequency cover changed")
    if list(map(Fraction, declaration["tested_required_cell"])) != [Fraction(1, 2), Fraction(129, 256)]:
        raise VerifyError("tested base cell changed")
    for item in data["imports"].values():
        path = _import_path(item["path"])
        if not path.exists() or digest(path) != item["sha256"]:
            raise VerifyError(f"import drift: {path}")

    growth = data["flattened_width_growth"]
    radii = [x["radius"] for x in growth]
    widths = [x["carrier_max_width"] for x in growth]
    if radii != [31, 30, 28, 24, 16, 4]:
        raise VerifyError("width checkpoints changed")
    if not all(a < b for a, b in zip(widths, widths[1:])) or widths[-1] < 1e15:
        raise VerifyError("wrapping-growth witness missing")

    affine = data["affine_moving_frame_result"]
    if not affine["carrier_rank_certified"] or not affine["kernel_rank_certified"]:
        raise VerifyError("landed affine diagonal theorem was demoted")
    if affine["carrier_max_local_correction_width"] >= .02 or affine["kernel_max_local_correction_width"] >= .01:
        raise VerifyError("affine diagonal width gate changed")
    naive = affine["naive_full_frame"]
    if naive != {"certified": False, "meaning": "the unstructured 12-real interval factor loses the exact zero upper-right block; this is a representation refusal, not singularity", "refusal_code": 10, "refusal_name": "IVLIN_AFFINE_FACTOR_RANK_UNCERTIFIED", "refusal_reset": 0}:
        raise VerifyError("naive full-frame refusal changed")
    lower = data["structured_lower_lift_result"]
    if not lower["all_1792_local_krawczyk_solves_closed"]:
        raise VerifyError("structured lower solves did not all close")
    if lower["maximum_width_reset"] != 65 or lower["maximum_interval_width"] < 1e7:
        raise VerifyError("parameter decorrelation witness changed")
    if lower["midpoint_correction_max_abs_at_reset_65"] >= 1e-8:
        raise VerifyError("midpoint lower correction is no longer near zero")

    flags = data["claim_flags"]
    if not flags["required_first_cell_attempted"] or not flags["all_local_checkpoint_solves_certified"]:
        raise VerifyError("attempt evidence missing")
    promoted = [
        "full_frequency_cover_certified",
        "lower_lift_certified",
        "global_connection_certified",
        "radial_current_conservation_certified",
        "endpoint_flux_or_scattering_claim",
    ]
    if any(flags[name] for name in promoted):
        raise VerifyError("claim promoted beyond SHORTFALL")
    if not flags["required_first_cell_diagonal_rank_certified"]:
        raise VerifyError("affine diagonal rank theorem missing")

    text = ADAPTER.read_text() if adapter_text is None else adapter_text
    forbidden = ["ivm_inverse", "ivm_inv", "null flux", "scattering_matrix",
                 "ivlin_fundamental(gc_full_0,12,0.0,28.0"]
    if any(token in text for token in forbidden):
        raise VerifyError("forbidden monolithic/inverse/flux surface entered adapter")
    if "pub fn axial_global_connection_parametric_frame_obstruction()" not in text:
        raise VerifyError("public obstruction consumer missing")
    return True


def verify_forge() -> None:
    binary = Path(os.environ.get("FORGE_BIN", "/tmp/forgebin"))
    if not binary.exists():
        subprocess.run(["go", "build", "-o", str(binary), "./cmd/forge"], cwd=FORGE, check=True)
    result = subprocess.run(
        [str(binary), "-incremental", "-run", str(ADAPTER)],
        cwd=FORGE,
        env={**os.environ, "FORGE_LIB": str(FORGE / "lib")},
        text=True,
        capture_output=True,
    )
    if result.returncode != 42:
        raise VerifyError(f"Forge shortfall rail failed rc={result.returncode}\n{result.stdout}\n{result.stderr}")
    required = ["carrier-rank=true", "kernel-rank=true",
                "structured-lower-solves=true", "max-reset=65"]
    if any(token not in result.stdout for token in required):
        raise VerifyError(f"Forge output lost obstruction witness\n{result.stdout}")


def main() -> None:
    verify_data(json.loads(CERTIFICATE.read_text()))
    verify_forge()
    print("PASS independent v5 parametric-frame SHORTFALL replay")


if __name__ == "__main__":
    main()
