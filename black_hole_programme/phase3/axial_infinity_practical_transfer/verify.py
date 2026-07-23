"""Independent structural and Forge replay for the practical infinity basis."""
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
ADAPTER = HERE / "validated_infinity_transfer.forge"


class VerifyError(RuntimeError):
    pass


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_data(data: dict) -> bool:
    if data.get("schema") != "phase3-axial-infinity-practical-transfer-v1":
        raise VerifyError("schema mismatch")
    if data.get("result_token") != "BH_PHASE3_AXIAL_INFINITY_PRACTICAL_TRANSFER_V1":
        raise VerifyError("result token mismatch")
    for item in data["imports"]["files"].values():
        path = Path(item["path"])
        if not path.is_absolute():
            path = PHYSICS / path
        if not path.exists() or digest(path) != item["sha256"]:
            raise VerifyError(f"import drift: {path}")
    cells = data["interval_cells"]
    if len(cells) != 64 * 32:
        raise VerifyError("omega/z subdivision count changed")
    omega = sorted({tuple(map(Fraction, c["omega_cell"])) for c in cells})
    zcells = sorted({tuple(map(Fraction, c["z_cell"])) for c in cells})
    if omega[0][0] != Fraction(1, 2) or omega[-1][1] != Fraction(3, 4):
        raise VerifyError("omega cover changed")
    if zcells[0][0] != 0 or zcells[-1][1] != Fraction(1, 32):
        raise VerifyError("z cover changed")
    if any(omega[i][1] != omega[i + 1][0] for i in range(len(omega) - 1)):
        raise VerifyError("omega cover gap")
    if any(zcells[i][1] != zcells[i + 1][0] for i in range(len(zcells) - 1)):
        raise VerifyError("z cover gap")
    rates = (0, 0, -2, -2, 0, -2)
    for cell in cells:
        p = cell["powers"]
        constants = [[Fraction(x) for x in row] for row in cell["constants"]]
        if max(Fraction(cell["neumann"]["carrier_q"]),
               Fraction(cell["neumann"]["kernel_q_max"])) >= 1:
            raise VerifyError("Neumann inverse is not certified")
        for i in range(6):
            for j in range(6):
                if p[i][j] >= 99:
                    continue
                if p[i][j] < 3 or constants[i][j] < 0:
                    raise VerifyError("z-flow lost its exact zero extension")
                if rates[i] != rates[j] and p[i][j] < 3:
                    raise VerifyError("cross-rate amplitude is not O(z)")
    structural = data["structural_proof"]
    if structural["XI2_XI3_derivative_consistency"] != "F4=(hpower-3)*H1_3":
        raise VerifyError("F4 derivative consistency missing")
    if structural["z_zero_extension"] != (
        "all entries are zero; same-rate and cross-rate p are at least 3"
    ):
        raise VerifyError("z=0 limit statement changed")
    flags = data["claim_flags"]
    if not (flags["continuous_z_zero_extension_certified"]
            and flags["full_rank_R32_initializer_certified"]
            and flags["direct_ivlinode_compatible"]):
        raise VerifyError("practical initializer not certified")
    if flags["global_matching_certified"] or flags["flux_certified"]:
        raise VerifyError("claim promoted beyond the endpoint handoff")
    return True


def verify_forge() -> None:
    binary = Path(os.environ.get("FORGE_BIN", "/tmp/forgebin"))
    if not binary.exists():
        subprocess.run(["go", "build", "-o", str(binary), "./cmd/forge"],
                       cwd=FORGE, check=True)
    result = subprocess.run(
        [str(binary), "-incremental", "-run", str(ADAPTER)],
        cwd=FORGE,
        env={**os.environ, "FORGE_LIB": str(FORGE / "lib")},
        text=True,
        capture_output=True,
    )
    if result.returncode != 42:
        raise VerifyError(
            f"Forge practical-transfer rail failed rc={result.returncode}\n"
            f"{result.stdout}\n{result.stderr}"
        )


def main() -> None:
    verify_data(json.loads(CERTIFICATE.read_text()))
    verify_forge()
    print("PASS independent practical R=32 infinity transfer and Forge replay")


if __name__ == "__main__":
    main()
