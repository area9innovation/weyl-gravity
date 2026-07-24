#!/usr/bin/env python3
"""Audit and assemble the transport-free outgoing-defect theorem."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import mpmath as mp
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"

SOURCES = {
    "boundary_contract": ROOT
    / "black_hole_programme/phase3/boundary_flux_contract/certificate.json",
    "radial_current": ROOT
    / (
        "black_hole_programme/phase3/"
        "axial_null_infinity_trace_preflight/certificate.json"
    ),
    "endpoint_grams": ROOT
    / "black_hole_programme/phase3/axial_null_flux_gram/certificate.json",
    "wavepacket_traces": ROOT
    / "black_hole_programme/phase3/axial_wavepacket_null_trace/certificate.json",
    "endpoint_existence": ROOT
    / (
        "black_hole_programme/phase3/"
        "axial_endpoint_remainder_enclosures/certificate.json"
    ),
    "incoming_connection": ROOT
    / (
        "black_hole_programme/phase3/"
        "axial_incoming_connection_analytic/certificate.json"
    ),
    "horizon_gram": ROOT
    / (
        "black_hole_programme/phase3/"
        "axial_horizon_grassmann_mobius_to_r4_taylor2/"
        "future_horizon_outward_gram.json"
    ),
    "old_krein_preflight": ROOT
    / (
        "black_hole_programme/phase3/"
        "axial_one_sided_krein_scattering_preflight/certificate.json"
    ),
    "numeric_preview": ROOT
    / (
        "black_hole_programme/phase3/"
        "axial_global_connection_numeric_preview/pilot-diagnostic.json"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_sources() -> dict[str, dict]:
    return {name: json.loads(path.read_text()) for name, path in SOURCES.items()}


def parse_matrix(rows: list[list[str]], omega: sp.Expr) -> sp.Matrix:
    return sp.Matrix(
        [
            [
                sp.sympify(entry, locals={"omega": omega, "I": sp.I})
                for entry in row
            ]
            for row in rows
        ]
    )


def dagger(value: sp.Matrix) -> sp.Matrix:
    return value.conjugate().T


def exact_audit(data: dict[str, dict]) -> dict:
    endpoint = data["endpoint_grams"]
    horizon = data["horizon_gram"]
    contract = data["boundary_contract"]
    current = data["radial_current"]
    traces = data["wavepacket_traces"]
    existence = data["endpoint_existence"]
    incoming = data["incoming_connection"]

    minus = endpoint["endpoint_grams"]["Iminus"]
    plus = endpoint["endpoint_grams"]["Iplus"]
    if minus["basis"] != ["XI0", "XI1", "EI0"]:
        raise ValueError("incoming basis drift")
    if plus["basis"] != ["XI2", "XI3", "EI2"]:
        raise ValueError("outgoing basis drift")
    if horizon["basis"] != ["XH0a", "XH0b", "EH0"]:
        raise ValueError("horizon basis drift")
    if incoming["declaration"]["Iminus_basis"] != minus["basis"]:
        raise ValueError("Tminus codomain basis drift")
    if incoming["declaration"]["horizon_regular_basis"] != horizon["basis"]:
        raise ValueError("Tminus domain basis drift")

    omega = sp.symbols("omega", positive=True, real=True)
    gminus = parse_matrix(minus["stokes_gram_over_pi_alpha_W"], omega)
    gplus = parse_matrix(plus["stokes_gram_over_pi_alpha_W"], omega)
    hout = parse_matrix(horizon["gram_without_pi_alpha_W"], omega)
    if any(
        sp.simplify(entry) != 0
        for matrix in (gminus - dagger(gminus), gplus - dagger(gplus), hout - dagger(hout))
        for entry in matrix
    ):
        raise ValueError("Hermitian form drift")

    expected_boundary = "J_Hplus + J_Iplus - J_Hminus - J_Iminus = 0"
    if (
        contract["action_derived_current"]["orientation"]["boundary_identity"]
        != expected_boundary
    ):
        raise ValueError("oriented boundary identity drift")
    if (
        horizon["orientation"]["future_horizon_outward"]
        != "H_out=-Hframe^dagger*K4*Hframe=-I*Hframe^dagger*Jhat*Hframe"
    ):
        raise ValueError("future-horizon orientation drift")
    if (
        minus["classification"]["determinant"]
        != "14155776*omega**3/125"
        or plus["classification"]["determinant"]
        != "3538944*omega/125"
    ):
        raise ValueError("null determinant drift")
    if sp.simplify(gminus.det() - sp.Rational(14155776, 125) * omega**3):
        raise ValueError("incoming determinant recomputation failed")
    if sp.simplify(gplus.det() - sp.Rational(3538944, 125) * omega):
        raise ValueError("outgoing determinant recomputation failed")

    exact_inputs = {
        "six_column_infinity_basis_exists": existence["claim_flags"][
            "infinity_six_column_existence_enclosure_certified"
        ],
        "six_column_horizon_initializer_exists": existence["claim_flags"][
            "horizon_six_column_initializer_certified"
        ],
        "wavepacket_null_traces_exist": traces["claim_flags"][
            "wavepacket_trace_constructed"
        ],
        "wrong_endpoint_terms_vanish": traces["claim_flags"][
            "exact_solution_wrong_endpoint_suppression"
        ],
        "radial_current_conserved": current["claim_flags"][
            "exact_six_state_radial_current"
        ],
        "null_trace_limit_interchange": endpoint["claim_flags"][
            "trace_limit_interchange_proved"
        ],
        "Tminus_exists": incoming["claim_flags"][
            "global_Tminus_exists_by_short_range_Jost_theory"
        ],
        "Tminus_invertible": incoming["claim_flags"][
            "global_Tminus_invertible_on_real_pilot_certified"
        ],
    }
    if not all(exact_inputs.values()):
        raise ValueError("abstract trace/Stokes input missing")

    return {
        "typed_raw_bases": {
            "Tminus_domain_horizon": horizon["basis"],
            "Tminus_codomain_Iminus": minus["basis"],
            "Tplus_codomain_Iplus": plus["basis"],
        },
        "normalization": "all three forms divided by pi*alpha_W",
        "oriented_forms": {
            "Gminus": (
                "past-boundary Stokes Gram "
                "=- coordinate-radial incoming Gram"
            ),
            "Gplus": (
                "future-boundary Stokes Gram "
                "= coordinate-radial outgoing Gram"
            ),
            "Hout": (
                "future inner-boundary outward Gram "
                "=- horizon coordinate-radial Gram"
            ),
            "boundary_identity": expected_boundary,
            "one_sided_identity": (
                "Hout+Tplus^dagger*Gplus*Tplus"
                "-Tminus^dagger*Gminus*Tminus=0"
            ),
        },
        "form_determinants": {
            "Gminus": str(sp.factor(gminus.det())),
            "Gplus": str(sp.factor(gplus.det())),
            "Hout": str(sp.factor(hout.det())),
        },
        "form_inertias_for_alpha_W_positive": {
            "Gminus": minus["classification"][
                "inertia_for_alpha_W_positive"
            ],
            "Gplus": plus["classification"][
                "inertia_for_alpha_W_positive"
            ],
            "Hout": horizon["inertia_for_alpha_W_positive"],
        },
        "abstract_trace_stokes_inputs": exact_inputs,
    }


def numeric_preview(data: dict[str, dict]) -> dict:
    """Reissue the old point preview in the basis required by O."""
    mp.mp.dps = 70
    preview = data["numeric_preview"]
    endpoint = data["endpoint_grams"]
    horizon = data["horizon_gram"]
    if preview["lifecycle"] != "UNVALIDATED-NUMERIC":
        raise ValueError("numeric preview lifecycle drift")
    if preview["scope"]["frequency"] != "M*omega=1/2":
        raise ValueError("numeric preview frequency drift")

    def parse_complex(text: str) -> mp.mpc:
        value = sp.sympify(text.replace("j", "*I"), locals={"I": sp.I})
        return mp.mpc(
            str(sp.N(sp.re(value), 75)),
            str(sp.N(sp.im(value), 75)),
        )

    tminus = mp.matrix(
        [
            [parse_complex(entry) for entry in row]
            for row in preview["connection"]["Cminus_3_by_3"]
        ]
    )
    omega = sp.Rational(1, 2)
    gminus_can = parse_matrix(
        endpoint["endpoint_grams"]["Iminus"][
            "stokes_gram_over_pi_alpha_W"
        ],
        omega,
    )
    # The old Cminus is expressed in the practical R=32 phase-normalized
    # infinity frame.  At omega=1/2 its incoming canonical-to-practical
    # amplitude matrix is diag(1,32,1).
    scale = sp.diag(1, 32, 1)
    gminus_norm = dagger(scale) * gminus_can * scale
    hout = parse_matrix(horizon["gram_without_pi_alpha_W"], omega)

    def to_mp(value: sp.Matrix) -> mp.matrix:
        return mp.matrix(
            [
                [
                    mp.mpc(
                        str(sp.N(sp.re(value[i, j]), 75)),
                        str(sp.N(sp.im(value[i, j]), 75)),
                    )
                    for j in range(value.cols)
                ]
                for i in range(value.rows)
            ]
        )

    gm = to_mp(gminus_norm)
    hh = to_mp(hout)
    defect = tminus.transpose_conj() * gm * tminus - hh
    determinant = mp.det(defect)
    eigenvalues = sorted(mp.re(x) for x in mp.eighe(defect, eigvals_only=True))
    hermitian_defect = max(
        abs(defect[i, j] - mp.conj(defect[j, i]))
        for i in range(3)
        for j in range(3)
    )
    return {
        "classification": "OBSERVED",
        "source_lifecycle": "UNVALIDATED-NUMERIC",
        "frequency": "1/2",
        "Tminus_source_basis": (
            "R=32 phase-normalized practical incoming frame"
        ),
        "Tminus_target_basis": ["XH0a", "XH0b", "EH0"],
        "incoming_amplitude_crosswalk": {
            "canonical_to_practical": [
                ["1", "0", "0"],
                ["0", "32", "0"],
                ["0", "0", "1"],
            ],
            "law": "Gminus_practical=S^dagger*Gminus_canonical*S",
            "applied": True,
        },
        "O_definition": "Tminus^dagger*Gminus_practical*Tminus-Hout",
        "det_O": {
            "real": mp.nstr(mp.re(determinant), 32),
            "imaginary": mp.nstr(mp.im(determinant), 8),
        },
        "eigenvalues": [mp.nstr(value, 30) for value in eigenvalues],
        "minimum_absolute_eigenvalue": mp.nstr(
            min(abs(value) for value in eigenvalues), 30
        ),
        "hermitian_defect_max": mp.nstr(hermitian_defect, 8),
        "old_preview_stokes_residual": preview["flux_diagnostic"][
            "orientation_tests"
        ]["declared_Hplus_plus_Iplus_minus_Iminus"],
        "certified_nonzero": False,
        "reason": (
            "the imported Tminus point matrix has no interval enclosure and "
            "the old Stokes residual is explicitly nonzero"
        ),
    }


def produce() -> dict:
    data = load_sources()
    exact = exact_audit(data)
    diagnostic = numeric_preview(data)
    imports = {
        name: {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256(path),
        }
        for name, path in SOURCES.items()
    }
    old = data["old_krein_preflight"]
    return {
        "schema": "phase3-axial-transport-free-outgoing-defect-preflight-v1",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_TRANSPORT_FREE_OUTGOING_DEFECT",
        "dependency_tags": ["LORENTZIAN-CAUSAL", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": "ABSTRACT_RAW_PSEUDO_ISOMETRY_ACTIVE_DET_O_INPUT_OPEN",
        "imports": imports,
        "tier_A_transport_free_determinant": {
            "exact_audit": exact,
            "definition": (
                "O=Tminus^dagger*Gminus*Tminus-Hout"
            ),
            "stokes_equivalent": (
                "O=Tplus^dagger*Gplus*Tplus"
            ),
            "determinant_equivalence": (
                "det(O)=det(Gplus)*abs(det(Tplus))^2; because Gplus is "
                "nondegenerate, det(O)!=0 iff Tplus is invertible"
            ),
            "basis_covariance": {
                "basis_law": (
                    "for Bminus'=Bminus*N and H'=H*M, "
                    "Tminus'=N^(-1)*Tminus*M, "
                    "Gminus'=N^dagger*Gminus*N, "
                    "Hout'=M^dagger*Hout*M"
                ),
                "O_law": "O'=M^dagger*O*M",
                "determinant_law": (
                    "det(O')=abs(det(M))^2*det(O)"
                ),
                "consequence": "zero/nonzero of det(O) is basis invariant",
            },
            "certified_full_typed_Tminus_matrix_available": False,
            "available_Tminus_certificate_scope": (
                "determinant formula, existence and invertibility only"
            ),
            "missing_input": (
                "one certified full 3x3 Tminus enclosure in the raw typed "
                "bases (XH0a,XH0b,EH0)->(XI0,XI1,EI0), or an explicitly "
                "conjugated equivalent with its basis map"
            ),
            "diagnostic_only": diagnostic,
            "det_O_nonzero_certified": False,
            "Tplus_rank_certified": False,
        },
        "tier_B_abstract_pseudo_isometry": {
            "packaging_gap_audited": {
                "old_status": old["status"],
                "old_activation_required_full_Tplus_entries": (
                    "the typed global 3x3 Tplus entries in the certified "
                    "endpoint frames"
                    in old["activation"]["missing"]
                ),
                "full_Tplus_entries_mathematically_necessary": False,
            },
            "abstract_Tplus_existence": {
                "certified": True,
                "argument": (
                    "the certified six-column infinity basis exists; the "
                    "future-regular horizon family defines exact global ODE "
                    "solutions; unique expansion in that infinity basis "
                    "defines both typed trace blocks Tminus and Tplus"
                ),
            },
            "abstract_stokes_identity": {
                "certified": True,
                "argument": (
                    "the exact radial current is conserved, the null "
                    "wave-packet traces exist with wrong-endpoint "
                    "suppression, the null trace/current limit interchange "
                    "passes, and the future-horizon outward sign is fixed"
                ),
                "identity": (
                    "Hout+Tplus^dagger*Gplus*Tplus"
                    "-Tminus^dagger*Gminus*Tminus=0"
                ),
            },
            "raw_embedding": {
                "incoming_variable": "x=Tminus*h",
                "Rraw": "Tplus*Tminus^(-1)",
                "Araw": "Tminus^(-1)",
                "Sraw": "vertical_stack(Rraw,Araw)",
                "source_form": "Gminus",
                "target_form": "Gplus direct_sum Hout",
                "identity": (
                    "Sraw^dagger*(Gplus direct_sum Hout)*Sraw=Gminus"
                ),
                "injective": True,
                "reason": "Araw=Tminus^(-1) is invertible",
                "certified": True,
            },
            "normalized_embedding": {
                "existence": True,
                "explicit_normalizers_computed": False,
                "reason": (
                    "Gminus, Gplus and Hout are nondegenerate Hermitian "
                    "forms with the same inertia (1,2,0), so Sylvester "
                    "congruences to a common J exist"
                ),
                "claim_scope": (
                    "abstract pseudo-isometric embedding only; no matrix "
                    "entries, outgoing rank or determinant assertion"
                ),
            },
        },
        "missing_object_ledger": [
            {
                "object": "certified_full_typed_Tminus_matrix",
                "needed_for": (
                    "forming O and certifying det(O) in the horizon basis"
                ),
                "required_basis": (
                    "(XH0a,XH0b,EH0)->(XI0,XI1,EI0), or an explicitly "
                    "conjugated equivalent with a certified basis map"
                ),
                "available_substitute": (
                    "determinant/existence/invertibility theorem plus an "
                    "UNVALIDATED-NUMERIC point preview"
                ),
                "status": "MISSING",
            },
            {
                "object": "certified_explicit_Tplus_matrix",
                "needed_for": (
                    "evaluated outgoing trace, outgoing population, "
                    "reflection matrix and numerical pseudo-isometry"
                ),
                "not_needed_for": (
                    "abstract existence of the typed trace map and the raw "
                    "one-sided Stokes identity"
                ),
                "status": "MISSING",
            },
            {
                "object": "explicit_common_J_congruence_frames",
                "needed_for": (
                    "a numerical signature-basis scattering matrix"
                ),
                "not_needed_for": (
                    "the raw-basis pseudo-isometric embedding"
                ),
                "status": "MISSING",
            },
        ],
        "claim_flags": {
            "oriented_raw_basis_crosswalk_certified": True,
            "transport_free_det_equivalence_certified": True,
            "abstract_typed_Tplus_exists": True,
            "abstract_stokes_on_horizon_regular_columns": True,
            "raw_one_sided_pseudo_isometric_embedding_certified": True,
            "abstract_common_J_normalization_exists": True,
            "full_typed_Tminus_entries_certified": False,
            "det_O_nonzero_certified": False,
            "Tplus_rank_or_outgoing_population_certified": False,
            "explicit_Tplus_matrix_certified": False,
            "physical_reflection_map_evaluated": False,
            "time_domain_or_quantum_claim": False,
        },
        "does_not_establish": [
            "a nonzero determinant enclosure for O",
            "rank or invertibility of Tplus",
            "a numerically evaluated outgoing trace or reflection map",
            "uniform direct-integral bounds or time-domain stability",
            "positivity, CPT, particles, ghosts or quantum unitarity",
        ],
        "next_gate": (
            "supply only the full typed Tminus enclosure and its basis "
            "crosswalk; form O in the horizon basis and certify a determinant "
            "enclosure excluding zero"
        ),
    }


def rendered(value: dict) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    document = produce()
    text = rendered(document)
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != text:
            raise SystemExit("certificate drift")
    else:
        OUTPUT.write_text(text)
    print(document["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
