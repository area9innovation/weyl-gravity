"""Basis-independent projector onto the certified generic axial extra module."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_axial_extra_detector import _shell_reduce


ROOT = Path(__file__).resolve().parents[2]
DETECTOR = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_extra_detector.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_extra_projector.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_extra_projector.schema.json"


class AxialExtraProjectorError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AxialExtraProjectorError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[i, j])) for j in range(matrix.cols)] for i in range(matrix.rows)]


def _projector() -> dict[str, Any]:
    record = json.loads(DETECTOR.read_text(encoding="utf-8"))
    eigenvalue, momentum, frequency = sp.symbols("lambda k omega", real=True)
    local = {"lam": eigenvalue, "k": momentum, "omega": frequency}
    parse = lambda value: sp.sympify(value.replace("lambda", "lam"), locals=local)
    representatives = sp.Matrix(
        [[parse(value) for value in row] for row in record["detector"]["extra_representative_columns"]]
    )
    detector = sp.Matrix(
        [[parse(value) for value in row] for row in record["detector"]["detector_rows"]]
    )
    reduce = lambda value: _shell_reduce(value, frequency, momentum, eigenvalue)
    identity = (detector * representatives).applyfunc(reduce)
    projector = (representatives * detector).applyfunc(reduce)
    idempotence = (projector * projector - projector).applyfunc(reduce)
    image = (projector * representatives - representatives).applyfunc(reduce)
    detector_descent = (detector * projector - detector).applyfunc(reduce)
    _require(identity == sp.eye(2), "detector/reconstruction identity changed")
    _require(idempotence == sp.zeros(4), "extra projector is not idempotent")
    _require(image == sp.zeros(4, 2), "projector does not fix the extra image")
    _require(detector_descent == sp.zeros(2, 4), "detector does not descend through projector")

    a, b, c, d = sp.symbols("a b c d")
    change = sp.Matrix([[a, b], [c, d]])
    changed_projector = representatives * change * change.inv() * detector
    basis_remainder = (changed_projector - representatives * detector).applyfunc(sp.cancel)
    _require(basis_remainder == sp.zeros(4), "projector changed under an invertible basis change")
    return {
        "coefficient_order": record["detector"]["coefficient_order"],
        "definition": "Pi_X=E_X D_X, where D_X E_X=I_2 on p=omega^2-k^2-lambda+2/3=0",
        "matrix": _strings(projector),
        "rank": 2,
        "idempotence_remainder": _strings(idempotence),
        "image_remainder": _strings(image),
        "detector_descent_remainder": _strings(detector_descent),
        "generic_basis_change": "E_X -> E_X S, D_X -> S^(-1)D_X for det(S)!=0",
        "basis_change_remainder": _strings(basis_remainder),
        "basis_independent": True,
        "identity_on_extra_module": True,
        "annihilates_certified_Einstein_image": record["detector"]["annihilates_Einstein_image"],
        "shell": record["detector"]["extra_shell"],
    }


def build_certificate() -> dict[str, Any]:
    record = json.loads(DETECTOR.read_text(encoding="utf-8"))
    _require(record["result_id"] == "EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_DETECTOR", "detector input changed")
    return {
        "schema": "einstein-maxwell-weyl-axial-extra-projector-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_PROJECTOR",
        "result_state": "BASIS_INDEPENDENT_GENERIC_AXIAL_EXTRA_SHELL_PROJECTOR_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_GENERIC_AXIAL_EXTRA_SHELL_PROJECTOR",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {str(DETECTOR.relative_to(ROOT)): _sha256(DETECTOR)},
        },
        "domain": "generic axial ell>=2 Weyl-Maxwell solution coefficients on the extra shell, after local Diff x U(1) reduction and before residual quotient",
        "projector": _projector(),
        "classification": {
            "canonical_after_certified_symplectic_splitting": True,
            "basis_independent": True,
            "off_shell_projector": False,
            "nonlinear_projector": False,
            "final_residual_descent": False,
        },
        "interpretation": "The detector and reconstruction map define an idempotent rank-two shell projector independent of the chosen extra basis. It separates the certified axial extra normal-mode component from the Einstein image, but it is not an off-shell or nonlinear projection.",
        "next_gate": "apply Pi_X only to shell-supported normal-source data; for nonresonant quadratic sources first invert the target Hessian and keep the induced correction distinct from a homogeneous extra normal mode",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE projector exists only on the generic axial extra shell. It does not define a spacetime-local, causal, asymptotic, residual-invariant, or nonlinear projector.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_extra_projector --verify bridge/certificates/einstein_maxwell_weyl_axial_extra_projector.json",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_extra_projector",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(json.loads(path.read_text(encoding="utf-8")) == build_certificate(), f"stale axial extra projector: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and args.verify is None:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
