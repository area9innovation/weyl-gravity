"""Invariant lift-shear and cyclic-splitting classification for the compact bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/EINSTEIN_WEYL_SYMPLECTIC_EXTENSION_CLASSIFICATION_V1.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein-weyl-symplectic-extension-classification-v1.schema.json"
INPUTS = {
    "exact_sequence": ("bridge/certificates/EINSTEIN_WEYL_PARITY_COMPLETE_RESIDUAL_EXACT_SEQUENCE_MAXIMAL_V1.json", "EINSTEIN_WEYL_PARITY_COMPLETE_RESIDUAL_EXACT_SEQUENCE_MAXIMAL_V1", "d94140069b4972acdd2f5fcc99e8076bb773d9f2d904ce068e58548f86fbbd10"),
    "cyclic_obstruction": ("bridge/certificates/einstein_weyl_generic_identity_cyclic_obstruction.json", "EINSTEIN_WEYL_GENERIC_IDENTITY_CYCLIC_OBSTRUCTION_V1", "49c0623114c5eee478463d58fcdc9a6e89b36e57a27aa66354b5a925a77bcc77"),
    "radiative_restriction": ("bridge/certificates/einstein_maxwell_weyl_radiative_symplectic_restriction.json", "EINSTEIN_MAXWELL_WEYL_RADIATIVE_SYMPLECTIC_RESTRICTION", "560f9e96be8ee095972e745544a709fdb6a8ac7a939658a21163bc173884c2bd"),
    "axial_extra": ("bridge/certificates/einstein_maxwell_weyl_axial_extra_detector.json", "EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_DETECTOR", "dc8133d0a97c3bdf1e6fa6eb03768b3785f6415ad536ab4605bdbb52303ca17b"),
    "polar_extra": ("bridge/certificates/EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1.json", "EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1", "f411d2e62c4ffa7436966d11f7d77e4c91b85d4ffbaf220f04f816bd80ec0b71"),
    "exceptional": ("bridge/certificates/einstein_weyl_exceptional_ell1_solution_cofiber.json", "EINSTEIN_WEYL_EXCEPTIONAL_ELL1_SOLUTION_COFIBER_V1", "9197b751bf0eea4e2c2cd38c3e3cac2d42864e8cb313c263260caffef5bde25e"),
    "homogeneous": ("bridge/certificates/einstein_maxwell_weyl_homogeneous_global_symplectic_restriction.json", "EINSTEIN_MAXWELL_WEYL_HOMOGENEOUS_GLOBAL_SYMPLECTIC_RESTRICTION", "ca8f300c9b8be08b016c7d607edafaeba4fcf5112a8621ae43568599f9ca8119"),
    "twist": ("bridge/certificates/einstein_maxwell_weyl_axial_twist_symplectic_restriction.json", "EINSTEIN_MAXWELL_WEYL_AXIAL_TWIST_SYMPLECTIC_RESTRICTION", "a8234234694293a24a62a1f326441f478c090232c6e310063e774e22e25462dc"),
}


class SymplecticExtensionError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SymplecticExtensionError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.Matrix) -> list[list[str]]:
    return [[str(sp.factor(value)) for value in row] for row in matrix.tolist()]


def _inertia_2(matrix: sp.Matrix, substitutions: dict[sp.Symbol, Any]) -> list[int]:
    evaluated = matrix.subs(substitutions)
    first = sp.factor(evaluated[0, 0])
    determinant = sp.factor(evaluated.det())
    if first > 0 and determinant > 0:
        return [2, 0]
    if determinant < 0:
        return [1, 1]
    raise SymplecticExtensionError(f"undecided inertia: {evaluated}")


def _generic_blocks() -> dict[str, Any]:
    lam, k = sp.symbols("lambda k", real=True)
    source = {
        "axial": sp.diag(lam, 2),
        "polar": sp.Matrix([[1, -2], [-2, 2 * lam]]),
    }
    relative = {
        "axial": sp.Matrix([[1, 3], [sp.Rational(3, 2) * lam, 1]]),
        "polar": sp.Matrix([[1, -3 * lam], [-sp.Rational(3, 2), 1]]),
    }
    extra_fixture = {
        "axial": sp.diag(1296, sp.Rational(208, 3)),
        "polar": sp.diag(22464, 12288),
    }
    negative_vector = {
        "axial": sp.Matrix([1, -1]),
        "polar": sp.Matrix([4, 1]),
    }
    shear_scale = {"axial": 7, "polar": 22}
    output: dict[str, Any] = {}
    for parity in ("axial", "polar"):
        g_source = source[parity]
        r = relative[parity]
        g_image = (g_source * r).applyfunc(sp.factor)
        _require(g_image == g_image.T, f"{parity} image form lost Hermiticity")
        _require(sp.factor(g_source.det()) != 0, f"{parity} source form degenerate")
        _require(sp.factor(g_image.det()) != 0, f"{parity} image form degenerate")
        fixture_image = g_image.subs(lam, 6)
        vector = negative_vector[parity]
        negative_norm = sp.factor((vector.T * fixture_image * vector)[0])
        _require(negative_norm < 0, f"{parity} mutation vector is not negative")
        a = sp.zeros(2)
        a[:, 0] = shear_scale[parity] * vector
        gx = extra_fixture[parity]
        cross = fixture_image * a
        lifted_xx = (gx + a.T * fixture_image * a).applyfunc(sp.factor)
        schur = (lifted_xx - cross.T * fixture_image.inv() * cross).applyfunc(sp.factor)
        _require(schur == gx, f"{parity} Schur complement changed")
        _require(lifted_xx[0, 0] < 0, f"{parity} raw lift sign mutation did not flip")
        _require(_inertia_2(g_source, {lam: 6}) == [2, 0], f"{parity} source inertia changed")
        _require(_inertia_2(g_image, {lam: 6}) == [1, 1], f"{parity} image inertia changed")
        output[parity] = {
            "source_positive_frequency_Gram": _matrix_strings(g_source),
            "relative_operator_R": _matrix_strings(r),
            "target_image_Gram": _matrix_strings(g_image),
            "source_determinant": str(sp.factor(g_source.det())),
            "target_image_determinant": str(sp.factor(g_image.det())),
            "source_inertia_physical": [2, 0],
            "target_image_inertia_physical": [1, 1],
            "admissible_corrected_identification": "OBSTRUCTED: a time-translation- and shell-preserving complex-linear map preserves Hermitian inertia and cannot send (2,0) to (1,1)",
            "orthogonal_primary_lift": "CERTIFIED and unique because the target Einstein-image Gram is invertible",
            "fixture_lambda_k": [6, 0],
            "fixture_extra_Gram": _matrix_strings(gx),
            "sign_flip_shear_A": _matrix_strings(a),
            "sheared_cross_block": _matrix_strings(cross),
            "sheared_raw_extra_Gram": _matrix_strings(lifted_xx),
            "sheared_Schur_complement": _matrix_strings(schur),
        }
    return output


def _endpoint_table() -> list[dict[str, Any]]:
    return [
        {"scope": "exceptional ell=1 axial and polar", "extra": "one oscillator per parity", "target_internal_split": "unique orthogonal CRT split; extra Gram diag(16,3) across the two parities", "fixed_identity_cyclic": "OBSTRUCTED: R-I=3I", "corrected_solution_identification": "AVAILABLE on solution space: the target-to-source form normalizer is S=2I (equivalently the source-to-target cyclic identification is B=I/2); no strict all-row cyclic chain lift certified", "final_residual": "NO_CERTIFIED_MAP"},
        {"scope": "polar ell=0, k nonzero", "extra": "empty", "target_internal_split": "NOT_APPLICABLE", "fixed_identity_cyclic": "NOT_APPLICABLE", "corrected_solution_identification": "NOT_APPLICABLE", "final_residual": "NO_CERTIFIED_MAP"},
        {"scope": "homogeneous ell=0, k=0", "extra": "zero solution cofiber", "target_internal_split": "trivial", "fixed_identity_cyclic": "OBSTRUCTED: R-I=N has rank 2 and N^2=0", "corrected_solution_identification": "AVAILABLE on solution space: the target-to-source form normalizer is S=I+N/2 and the source-to-target identification is S^{-1}; Q_e and W_x retained", "final_residual": "NO_CERTIFIED_MAP"},
        {"scope": "twist ell=1, k=0 per real SO(3) component", "extra": "zero solution cofiber", "target_internal_split": "trivial", "fixed_identity_cyclic": "OBSTRUCTED: R-I=-3I", "corrected_solution_identification": "OBSTRUCTED under time-translation equivariance: every centralizer matrix of the A+Bt Jordan flow has nonnegative determinant a^2, but S^T Omega S=-2 Omega requires det(S)=-2", "final_residual": "NO_CERTIFIED_MAP"},
        {"scope": "finite large-U1 Wilson-line quotient", "extra": "zero tangent cofiber", "target_internal_split": "NOT_APPLICABLE", "fixed_identity_cyclic": "NOT_APPLICABLE_TO_DISCRETE_IDENTIFICATION", "corrected_solution_identification": "W_x remains a local tangent coordinate; no charged block may be hidden in a lift", "final_residual": "NO_CERTIFIED_MAP"},
    ]


def build_certificate() -> dict[str, Any]:
    records = {}
    for name, (relative, result_id, digest) in INPUTS.items():
        path = ROOT / relative
        record = json.loads(path.read_text())
        _require(record["result_id"] == result_id, f"{name} result id changed")
        _require(_sha256(path) == digest, f"{name} hash changed")
        records[name] = record
    _require(records["exact_sequence"]["maximal_preresidual_statement"]["kernel_equals_image"], "exact-sequence input changed")
    _require(records["cyclic_obstruction"]["classification"]["induced_solution_pairing_defect_nonradical"], "cyclic obstruction input changed")
    blocks = _generic_blocks()
    return {
        "schema": "einstein-weyl-symplectic-extension-classification-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_WEYL_SYMPLECTIC_EXTENSION_CLASSIFICATION_V1",
        "result_state": "ORTHOGONAL_TARGET_SPLIT_CERTIFIED_PARITY_COMPLETE_ADMISSIBLE_CYCLIC_SPLIT_OBSTRUCTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {"generator_path": str(Path(__file__).relative_to(ROOT)), "generator_sha256": _sha256(Path(__file__)), "inputs": {name: {"path": rel, "result_id": rid, "sha256": digest} for name, (rel, rid, digest) in INPUTS.items()}},
        "scope": {"theory": "Einstein-Maxwell source, Weyl-Maxwell target and extra cofiber", "background": "compactified magnetically supported Plebanski-Hacyan", "boundaries": "closed S1_L times S2 before global stabilizer reduction", "charge_sector": "fixed magnetic bundle; Q_e, W_x and twist holonomies retained", "carrier": "finite harmonic H0 exact sequence plus the necessary cohomology obstruction to cyclic chain splitting", "degree": 1, "parity": "axial and polar separately", "ell": "generic >=2, exceptional 1, homogeneous 0", "m": "all certified labels", "k": "all allowed compact momenta", "omega": "q-primary, p-primary, exceptional and generalized-zero branches"},
        "lift_shear_theorem": {
            "coordinates": "For H_W=H_E direct_sum s(H_X), replace the lift by s_A(x)=s(x)+iota(Ax).",
            "block_transform": "G_E is fixed; C_A=C+G_E A; G_X,A=G_X+A^dagger G_E A+A^dagger C+C^dagger A.",
            "invariant": "S_X=G_X-C^dagger G_E^{-1}C is unchanged by every lift shear and transforms only by congruence under a quotient-basis change.",
            "orthogonal_lift": "A_orth=-G_E^{-1}C; it is unique whenever G_E is nondegenerate.",
            "basis_invariants": ["rank and radical of the full target form", "rank, radical and inertia of G_E", "rank, radical and inertia of the Schur-complement quotient form", "nonzero cyclic defect on the fixed Einstein inclusion"],
            "not_invariant": ["a chosen lift sign", "raw extra-extra entries", "raw cross entries", "a declaration that an arbitrary algebraic split is local or cyclic"],
        },
        "generic_parity_blocks": blocks,
        "endpoint_table": _endpoint_table(),
        "extension_classification": {
            "module_extension": "ZERO/SPLIT before residual reduction: coprime p and q primaries give CRT projectors in the generic rows; distinct exceptional shells give CRT projectors at ell=1.",
            "target_internal_symplectic_extension": "ZERO/SPLIT: the nondegenerate Einstein image has a canonical orthogonal complement; in the certified primary lift its form is the direct extra Lee-Wald Gram.",
            "fixed_identity_relative_cyclic_class": "NONZERO: delta_E=iota^*Omega_WM-Omega_EM is independent of the extra lift; its generic representative D=R-I has determinant -9*lambda/2 in each parity.",
            "corrected_admissible_relative_cyclic_class": "OBSTRUCTED parity-completely: on every generic physical fibre the source positive-frequency coefficient form has inertia (2,0), while the target Einstein-image restriction has inertia (1,1). A shell/time-translation-preserving complex-linear correction cannot change inertia.",
            "strict_chain_consequence": "Any strict cyclic chain splitting would induce the forbidden cyclic solution-cohomology identification; therefore none exists under the declared locality, harmonic, time-translation, gauge and charge conditions.",
            "final_residual": "NO_CERTIFIED_MAP: no common moment-map-zero derived quotient functor exists, so this theorem does not construct an after-residual split.",
        },
        "mutations": {
            "lift_sign_called_invariant": "REJECTED by exact lambda=6,k=0 axial and polar shears: each makes the first raw lifted-extra diagonal negative while the Schur complement remains the original positive extra Gram.",
            "exact_implies_cyclic": "REJECTED by det(R-I)=-9*lambda/2 and the generic inertia mismatch.",
            "hide_charge_or_twist_in_lift": "REJECTED by harmonic, frequency, bundle-charge and holonomy grading.",
            "quotient_connected_stabilizer_as_gauge": "REJECTED: final residual carrier remains NO_CERTIFIED_MAP.",
        },
        "classification": {"algebraic_primary_split": True, "target_internal_orthogonal_split": True, "orthogonal_lift_unique": True, "raw_lift_XX_sign_invariant": False, "schur_complement_invariant": True, "fixed_identity_cyclic_split": False, "admissible_corrected_parity_complete_cyclic_split": False, "strict_chain_cyclic_split": False, "after_residual_split": False, "causal_particle_or_quantum_claim": False},
        "claim_boundary": "This certificate classifies the pre-residual finite-harmonic lift-shear invariants and supplies a cohomology-level obstruction to every declared admissible strict cyclic chain split. It distinguishes the canonical target-internal orthogonal complement from a cyclic identification with the Einstein-Maxwell source form. It does not construct the missing global moment-map-zero quotient functor, a cyclic chain homotopy outside the declared strict category, a causal Green carrier, particles, positivity, unitarity or a quantum state space.",
        "next_gate": "construct the common moment-map-zero derived quotient carrier; separately classify non-strict cyclic homotopies only after the cyclic homological substrate exists",
        "verification_commands": ["python3 -m bridge.einstein_sector.einstein_weyl_symplectic_extension_classification --verify bridge/certificates/EINSTEIN_WEYL_SYMPLECTIC_EXTENSION_CLASSIFICATION_V1.json", "python3 bridge/einstein_sector/verify_einstein_weyl_symplectic_extension_classification.py", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_symplectic_extension_classification", "python3 -m bridge.einstein_sector.generate_symplectic_extension_classification_atlas --check"],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(json.loads(path.read_text()) == build_certificate(), f"stale certificate: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and args.verify is None:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
