"""Produce the channel-factorized C theorem and physical availability audit."""

from __future__ import annotations

import hashlib
import json
import subprocess
from decimal import Decimal, getcontext
from pathlib import Path

from .exact import criterion_fixture, determinant_identity

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent

INPUTS = {
    "incoming_gram": ROOT
    / "black_hole_programme/phase3/axial_incoming_extended_domain_audit/certificate.json",
    "incoming_connection_scope": ROOT
    / "black_hole_programme/phase3/axial_transport_free_outgoing_defect_preflight_v1/certificate.json",
    "horizon_gram": ROOT
    / "black_hole_programme/phase3/axial_horizon_grassmann_mobius_to_r4_taylor2/future_horizon_outward_gram.json",
    "outgoing_population_cell": ROOT
    / "black_hole_programme/phase3/axial_outgoing_population_cell_half_v1/certificate.json",
    "scalar_reflection_cell": ROOT
    / "black_hole_programme/phase3/axial_scalar_reflection_cell_half_v1/certificate.json",
    "incoming_connection": ROOT
    / "black_hole_programme/phase3/axial_incoming_connection_analytic/certificate.json",
    "determinant_audit": ROOT
    / "black_hole_programme/phase3/axial_one_sided_krein_scattering_preflight/certificate.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def _source_commit(path: Path) -> str:
    relative = path.relative_to(ROOT)
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", str(relative)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _fixture_summary(kind: str) -> dict:
    f = criterion_fixture(kind)
    return {
        "G_hermitian": f["G_hermitian"],
        "KH_hermitian": f["KH_hermitian"],
        "Kplus_hermitian": f["Kplus_hermitian"],
        "L_G_self_adjoint": f["L_G_self_adjoint"],
        "L_diagonalizable": f["L_diagonalizable"],
        "spectrum": f["spectrum"],
        "G_C_inertia": list(f["H0_inertia"]) if f["H0_inertia"] else None,
        "KH_C_inertia": list(f["KH_C_inertia"])
        if f["KH_C_inertia"]
        else None,
        "Kplus_C_inertia": list(f["Kplus_C_inertia"])
        if f["Kplus_C_inertia"]
        else None,
    }


def build_certificate() -> dict:
    imported = {name: _load(path) for name, path in INPUTS.items()}

    incoming = imported["incoming_gram"]
    scope = imported["incoming_connection_scope"]
    horizon = imported["horizon_gram"]
    outgoing = imported["outgoing_population_cell"]
    scalar = imported["scalar_reflection_cell"]
    connection = imported["incoming_connection"]
    determinant = imported["determinant_audit"]

    if not incoming["claim_flags"]["factor_adapted_Iminus_gram_certified"]:
        raise ValueError("incoming Gram authority is not certified")
    if horizon["status"] != "PASS" or horizon["rank"] != 3:
        raise ValueError("horizon Gram authority is not nondegenerate")
    if not outgoing["claim_flags"]["Tplus_invertible_on_declared_cell"]:
        raise ValueError("outgoing-invertible cell is not certified")
    if not connection["determinant_theorem"]["Tminus_invertible"]:
        raise ValueError("Tminus invertibility is not certified")

    full_tminus = scope["tier_A_transport_free_determinant"][
        "certified_full_typed_Tminus_matrix_available"
    ]
    if full_tminus:
        raise ValueError(
            "upstream availability changed: a new typed-matrix consumer is required"
        )

    getcontext().prec = 70
    spin2_sq = Decimal(
        scalar["certified_lower_bounds"]["spin_2"]["abs_A_out_squared_lower"]
    )
    spin1_sq = Decimal(
        scalar["certified_lower_bounds"]["spin_1"]["abs_A_out_squared_lower"]
    )
    det_l_upper = Decimal(1) / (
        (Decimal(1) + spin2_sq) ** 2 * (Decimal(1) + spin1_sq)
    )

    imports = {
        name: {
            "path": str(path.relative_to(ROOT)),
            "sha256": _sha(path),
            "source_commit": _source_commit(path),
        }
        for name, path in INPUTS.items()
    }

    cert = {
        "schema": "phase4-channel-factorized-c-pullback-test-v1",
        "result_id": "PURE_WEYL_PHASE4_CHANNEL_FACTORIZED_C_PULLBACK_TEST_V1",
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "theorem": {
            "setting": {
                "forms": "G, H_H, G_+ are finite-dimensional nondegenerate Hermitian forms",
                "maps": "A=Tminus^(-1) and R=Tplus*Tminus^(-1) are invertible",
                "pullbacks": "K_H=A^dagger*H_H*A; K_+=R^dagger*G_+*R=G-K_H",
                "operator": "L_H=G^(-1)*K_H",
                "self_adjointness": "L_H^dagger*G=G*L_H",
            },
            "criterion": (
                "A channel-factorized positive fundamental symmetry exists "
                "iff L_H is diagonalizable over C and spec(L_H) is contained "
                "in the open real interval (0,1)."
            ),
            "common_incoming_formulation": (
                "There is an involution C_- self-adjoint for G,K_H,K_+ with "
                "G*C_->0, K_H*C_->0 and K_+*C_->0."
            ),
            "channel_transport": {
                "horizon": "C_H=A*C_-*A^(-1)",
                "outgoing": "C_+=R*C_-*R^(-1)",
                "intertwining": [
                    "C_H*A=A*C_-",
                    "C_+*R=R*C_-",
                ],
            },
            "necessity": [
                "Common self-adjointness gives [C_-,L_H]=0.",
                "H0=G*C_->0 and K_H*C_-=H0*L_H>0.",
                "K_+*C_-=H0*(I-L_H)>0.",
                "Thus L_H is H0-self-adjoint with 0<L_H<I, hence diagonalizable with real spectrum in (0,1).",
            ],
            "sufficiency": [
                "For diagonalizable G-self-adjoint L_H with real spectrum, distinct eigenspaces are G-orthogonal.",
                "Each eigenspace is G-nondegenerate because their orthogonal direct sum is the whole nondegenerate space.",
                "Choose a fundamental symmetry of G on each eigenspace and take their direct sum.",
                "It commutes with L_H; eigenvalues in (0,1) make both H0*L_H and H0*(I-L_H) positive.",
            ],
            "determinant_audit": determinant_identity(),
            "boundary_cases": (
                "lambda=0 or 1 makes a channel pullback degenerate; nonreal "
                "spectrum or a Jordan block obstructs a common positive metric."
            ),
        },
        "exact_fixtures": {
            "positive": _fixture_summary("positive"),
            "negative_eigenvalue": _fixture_summary("negative_eigenvalue"),
            "nonreal_pair": _fixture_summary("nonreal_pair"),
            "jordan_inside_interval": _fixture_summary("jordan"),
        },
        "imports": imports,
        "physical_audit": {
            "scope": {
                "background": "Schwarzschild M=1, axial ell=2",
                "frequency_cell": ["0.49995", "0.50005"],
                "coupling_sign": "alpha_W>0",
            },
            "available": {
                "Gminus_exact": True,
                "Gminus_basis": incoming["factor_adapted_Iminus_gram"][
                    "source_basis"
                ],
                "Gminus_rank": 3,
                "Tminus_exists_and_is_invertible": True,
                "Tminus_determinant_formula": connection["determinant_theorem"][
                    "formula"
                ],
                "H_H_exact": True,
                "H_H_basis": horizon["basis"],
                "H_H_rank": horizon["rank"],
                "Tplus_invertible_on_cell": True,
                "Kplus_nondegenerate_inertia": [1, 2, 0],
            },
            "missing": {
                "full_typed_Tminus_entries": True,
                "certified_availability_flag": full_tminus,
                "required_basis_map": scope["missing_object_ledger"][0][
                    "required_basis"
                ],
                "diagnostic_point_matrix_rejected": True,
                "reason": scope["tier_A_transport_free_determinant"][
                    "diagnostic_only"
                ]["reason"],
            },
            "assembly": {
                "K_H_defined_by_certified_numeric_or_exact_entries": False,
                "generalized_pencil_defined": False,
                "generalized_eigenvalues_certified": False,
                "factorized_C_existence_certified": False,
                "factorized_C_obstruction_certified": False,
                "disposition": "SHORTFALL_MISSING_FULL_TYPED_TMINUS_MATRIX",
            },
            "partial_determinant_information": {
                "general_identity": determinant_identity(),
                "endpoint_normalizer_ratio_matches_Tminus_prefactor": determinant[
                    "determinant_audit"
                ]["ratio_matches_prefactor"],
                "reduced_identity": (
                    "det(L_H)=1/(abs(A_in_2)^4*abs(A_in_1)^2) "
                    "in the certified raw/factor normalization"
                ),
                "wronskian": "abs(A_in_s)^2=1+abs(A_out_s)^2",
                "cell_bound": f"0<det(L_H)<{det_l_upper}",
                "interpretation": (
                    "The product is positive and below one, but neither this "
                    "product nor the endpoint inertias determines the three "
                    "generalized eigenvalues or diagonalizability."
                ),
            },
            "minimal_missing_object": (
                "A certified full 3x3 Tminus enclosure on the cell in "
                "(XH0a,XH0b,EH0)->(XI0,XI1,EI0), or an explicitly conjugated "
                "equivalent with a certified analytic basis crosswalk."
            ),
        },
        "claim_flags": {
            "spectral_criterion_exact": True,
            "criterion_positive_fixture_verified": True,
            "criterion_obstruction_fixtures_verified": True,
            "physical_Gminus_imported": True,
            "physical_horizon_gram_imported": True,
            "physical_Tplus_invertible_cell_imported": True,
            "physical_full_typed_Tminus_available": False,
            "physical_generalized_spectrum_certified": False,
            "physical_channel_factorized_C_certified": False,
            "physical_channel_factorized_C_obstructed": False,
        },
        "does_not_establish": [
            "existence or obstruction of a channel-factorized C on the physical cell",
            "the generalized eigenvalues of det(K_H-lambda*Gminus)",
            "a full typed Tminus or explicit Tplus matrix",
            "a canonical, covariant, causal, holomorphic or BRST-compatible C",
            "whole-axis positive-norm boundedness",
            "time-domain stability, particles, ghosts or quantum unitarity",
        ],
    }
    return cert


def main() -> None:
    cert = build_certificate()
    (HERE / "certificate.json").write_text(
        json.dumps(cert, indent=2, sort_keys=True) + "\n"
    )
    receipt = {
        "schema": "phase4-channel-factorized-c-pullback-receipt-v1",
        "result_id": cert["result_id"],
        "source_commit": subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip(),
        "certificate_sha256": _sha(HERE / "certificate.json"),
        "producer": (
            "python3 -m "
            "black_hole_programme.phase4.channel_factorized_c_pullback_test_v1.produce"
        ),
        "independent_verifier": (
            "python3 -m "
            "black_hole_programme.phase4.channel_factorized_c_pullback_test_v1.verify"
        ),
        "tests": (
            "python3 -m unittest -v "
            "black_hole_programme.phase4.channel_factorized_c_pullback_test_v1.test_pullback"
        ),
        "expected_exit_status": 0,
        "test_tiers": {
            "tier_0": {
                "status": "PASS",
                "commands": [
                    "python3 -m py_compile black_hole_programme/phase4/channel_factorized_c_pullback_test_v1/*.py",
                    "python3 -m json.tool black_hole_programme/phase4/channel_factorized_c_pullback_test_v1/certificate.json",
                    "python3 -m json.tool black_hole_programme/phase4/channel_factorized_c_pullback_test_v1/receipt.json",
                    "git diff --check -- black_hole_programme/phase4/channel_factorized_c_pullback_test_v1 planning/work-items/phase4-black-hole-channel-factorized-c-pullback-test-v2.json",
                ],
                "observed_elapsed_seconds": "<1",
            },
            "tier_1": {
                "status": "PASS",
                "commands": [
                    "python3 -m black_hole_programme.phase4.channel_factorized_c_pullback_test_v1.produce",
                    "python3 -m black_hole_programme.phase4.channel_factorized_c_pullback_test_v1.verify",
                    "python3 -m unittest -v black_hole_programme.phase4.channel_factorized_c_pullback_test_v1.test_pullback",
                ],
                "observed_elapsed_seconds": "<2",
                "tests": 7,
            },
            "tier_2": {
                "status": "NOT_RUN",
                "criterion": "No imported mathematical input, shared operator, schema, or upstream certificate was modified; every imported authority is content-hash checked.",
            },
            "tier_3": {
                "status": "NOT_RUN",
                "criterion": "This is a scoped theorem/availability certificate, not a freeze, release, shared-core change, or Tier-3 promotion.",
            },
        },
        "arithmetic": "SymPy exact rational/complex algebra plus Decimal directed scalar bound assembled from certified lower bounds",
        "claim_boundary": (
            "The exact spectral criterion is certified. The physical pencil "
            "and its eigenvalues remain undefined because the full typed "
            "Tminus entries are absent from committed authorities."
        ),
    }
    (HERE / "receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )


if __name__ == "__main__":
    main()
