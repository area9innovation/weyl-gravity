"""Independent structural verifier for the endpoint-enclosure certificate."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
PHYSICS = HERE.parents[3]
CERTIFICATE = HERE / "certificate.json"


class VerifyError(RuntimeError):
    pass


def fraction(node):
    return Fraction(node["num"], node["den"])


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_data(data):
    if data.get("schema") != "phase3-black-hole-axial-endpoint-remainder-enclosures-v1":
        raise VerifyError("schema mismatch")
    if data.get("result_token") != "BH_PHASE3_AXIAL_ENDPOINT_REMAINDER_ENCLOSURES_V1":
        raise VerifyError("result token mismatch")
    for imported in data["imports"].values():
        path = Path(imported["path"])
        if not path.is_absolute():
            path = PHYSICS / path
        if not path.exists() or digest(path) != imported["sha256"]:
            raise VerifyError(f"import drift: {path}")

    horizon = data["horizon"]
    if horizon["complex_dimension"] != 6 or horizon["realified_dimension"] != 12:
        raise VerifyError("dimension mismatch")
    if horizon["kappa"] != 2 or horizon["recurrence_order"] != 3:
        raise VerifyError("recurrence contract mismatch")
    tau, epsilon = fraction(horizon["tau"]), fraction(horizon["epsilon"])
    disk = fraction(horizon["cauchy_disk_radius"])
    sb = fraction(horizon["S_B_tau"])
    majorant = fraction(horizon["cauchy_majorant"])
    if not (0 < epsilon < tau < disk and epsilon * 16 == tau):
        raise VerifyError("endpoint radii are inconsistent")
    if sb != majorant * tau / (disk - tau) or not (0 <= sb <= Fraction(1, 4)):
        raise VerifyError("Cauchy contraction bound changed")
    cells = [(fraction(a), fraction(b)) for a, b in horizon["frequency_cells"]]
    if cells[0][0] != Fraction(1, 2) or cells[-1][1] != Fraction(3, 4):
        raise VerifyError("frequency coverage endpoints changed")
    if any(a >= b for a, b in cells):
        raise VerifyError("empty frequency cell")
    if any(cells[i][1] != cells[i + 1][0] for i in range(len(cells) - 1)):
        raise VerifyError("frequency cells have a gap")
    if not data["claim_flags"]["horizon_six_column_initializer_certified"]:
        raise VerifyError("horizon flag is not certified")
    if not data["claim_flags"].get("infinity_six_column_existence_enclosure_certified"):
        raise VerifyError("infinity existence enclosure was not recorded")
    if data["claim_flags"]["infinity_six_column_initializer_certified"]:
        raise VerifyError("practical infinity initializer was promoted past the evidence")
    if data["claim_flags"]["global_matching_certified"]:
        raise VerifyError("global matching was promoted past the evidence")
    infinity = data["infinity"]
    if sorted(infinity["carrier_heads_imported"]) != ["XI0", "XI1", "XI2", "XI3"]:
        raise VerifyError("carrier head inventory changed")
    if infinity["missing_metric_normal_form_heads"]:
        raise VerifyError("verified infinity metric heads are still marked missing")
    if sorted(infinity["metric_heads_imported"]) != ["XI0", "XI1", "XI2", "XI3"]:
        raise VerifyError("metric head inventory changed")
    if not infinity["metric_heads_log_free"]:
        raise VerifyError("log-free metric-head theorem missing")
    if infinity["oscillatory_n1_obstructions"] != {"XI2": "0", "XI3": "0"}:
        raise VerifyError("oscillatory compatibility witness changed")
    if not infinity.get("q_less_than_one_quarter"):
        raise VerifyError("Volterra contraction was not certified")
    if any(p <= 1 for row in infinity["decay_p_ij"] for p in row):
        raise VerifyError("nonintegrable Volterra exponent")
    if infinity.get("normalization_radius_R") != str(2**256):
        raise VerifyError("proof-oriented infinity radius changed")
    if infinity.get("existence_enclosure_disposition") != "ENCLOSED_AT_PROOF_RADIUS":
        raise VerifyError("infinity existence disposition changed")
    if infinity.get("practical_handoff_disposition") != "NOT_STABLE_FOR_IVLINODE":
        raise VerifyError("practical handoff was promoted past the evidence")
    if infinity["disposition"] != "EXISTENCE_ONLY_NOT_DIRECTLY_CONSUMABLE":
        raise VerifyError("infinity disposition changed")
    if data["stop_condition_disposition"] != "SHORTFALL" or not data["missing_dependency"]:
        raise VerifyError("shortfall boundary missing")
    return True


def main():
    verify_data(json.loads(CERTIFICATE.read_text()))
    print("PASS independent endpoint-enclosure structure and claim boundary")


if __name__ == "__main__":
    main()
