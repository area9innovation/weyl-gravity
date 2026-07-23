#!/usr/bin/env python3
"""Independent fail-closed verifier for the normalized-plane join contract."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "preactivation-certificate.json"
HANDOFF_SCHEMA = HERE / "normalized-r4-plane-handoff.schema.json"

EXPECTED_STATE = ["P", "Pprime", "Q", "Qprime", "H1", "F"]
EXPECTED_REAL_STATE = [
    "Re(P)", "Re(Pprime)", "Re(Q)", "Re(Qprime)", "Re(H1)", "Re(F)",
    "Im(P)", "Im(Pprime)", "Im(Q)", "Im(Qprime)", "Im(H1)", "Im(F)",
]
FORBIDDEN_FLAGS = {
    "normalized_plane_handoff_available",
    "normalized_plane_connection_certified",
    "negative_endpoint_wavepacket_certified",
    "normalized_one_sided_J_isometry_certified",
    "canonical_endpoint_amplitudes_certified",
    "Einstein_additional_origin_labels_certified",
    "frozen_endpoint_L2_equivalence_certified",
    "full_scattering_matrix_certified",
    "stability_or_CPT_certified",
    "physical_quantum_ghost_or_unitarity_certified",
}
REQUIRED_GATES = {
    "all realified frames obey the standard complex-structure equivariance",
    "H, Bminus and Bplus have complex rank three on the whole cell",
    "[Bminus Bplus] has complex rank six on the whole cell",
    "the validated solve encloses [Bminus Bplus]*C-H as exact zero",
    "the full pulled current includes and certifies the endpoint cross block as zero",
    "K4 uses +i*Jhat and matches the exact endpoint Gram by congruence",
    "the future-horizon outward sign is minus the increasing-r orientation",
    "the Stokes defect encloses exact zero entrywise",
    "the endpoint Gplus Gram has inertia (1,2,0) for alpha_W positive",
    "the endpoint Gram and normalized connection vary continuously on an open frequency cell",
    "nonunitary GL(3,C) basis changes obey the connection and Gram covariance laws",
    "every rank, inertia, inverse and multiplier statement is certified on the complete frequency cell",
}
REQUIRED_MUTATIONS = {
    "replace +i*Jhat by -i*Jhat",
    "flip only the future-horizon outward sign",
    "swap Iminus and Iplus",
    "corrupt one imaginary realification partner while preserving real rank",
    "duplicate one frame column",
    "replace one frame by an arbitrary full-rank plane",
    "transpose, invert or block-swap the connection",
    "narrow a solve or Stokes remainder so that the true residual is excluded",
    "drop or zero the endpoint cross block without recomputation",
    "apply an invertible nonunitary right basis change and demand raw matrix equality",
    "apply a singular right basis change",
    "mutate the child cell, shared generator, state order or phase convention",
    "lower rank_Cplus from two to one while retaining the negative-wavepacket claim",
    "change endpoint Gplus inertia while retaining the rank-index conclusion",
    "drop the infinite-dimensional disjoint-frequency-support refinement while retaining rank_Cplus at least two",
    "promote negative endpoint flux to negative total energy or a quantum ghost",
    "promote canonical amplitudes, origin labels, endpoint L2 equivalence, full scattering, stability, CPT, ghost or unitarity",
}
REQUIRED_LIMITS = {
    "canonical endpoint or scattering amplitudes",
    "Einstein/additional origin restrictions after plane mixing",
    "equivalence with the frozen endpoint L2 normalization",
    "a full two-ended scattering matrix",
    "negative total conserved energy or a horizon-completed energy sign",
    "a physical quantum ghost, particles, or unitarity",
}


class ContractError(ValueError):
    """Raised when the preactivation or future handoff violates the contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_path(text: str) -> Path:
    path = Path(text)
    _require(not path.is_absolute() and ".." not in path.parts, "unsafe import path")
    resolved = (ROOT / path).resolve()
    _require(ROOT.resolve() in resolved.parents, "import path escapes repository")
    return resolved


def _realify(matrix: sp.Matrix) -> sp.Matrix:
    re = matrix.applyfunc(lambda value: sp.re(sp.expand_complex(value)))
    im = matrix.applyfunc(lambda value: sp.im(sp.expand_complex(value)))
    return re.row_join(-im).col_join(im.row_join(re))


def negative_index_lower_bound(rank: int, positive_index: int = 1) -> int:
    """Return the dimension-theoretic lower bound for a pulled-back negative index."""

    _require(isinstance(rank, int) and 0 <= rank <= 3, "invalid image rank")
    _require(
        isinstance(positive_index, int) and 0 <= positive_index <= 3,
        "invalid positive index",
    )
    return max(0, rank - positive_index)


def verify_reference_algebra() -> None:
    """Check the exact normalization, Stokes and covariance formulae."""

    eye = sp.eye(3)
    zero = sp.zeros(3)
    bminus = eye.col_join(zero)
    bplus = zero.col_join(eye)
    horizon = (2 * eye).col_join(eye)
    whole = bminus.row_join(bplus)
    # The endpoint plus block has inertia (1,2,0), matching the exact axial
    # endpoint theorem for alpha_W>0.  The first block is chosen only to make
    # the reference Stokes calculation transparent.
    current = sp.diag(-1, -1, -1, 1, -1, -1)
    _require(current.H == current, "reference K4 is not Hermitian")

    connection = whole.inv() * horizon
    cminus, cplus = connection[:3, :], connection[3:, :]
    _require(whole * connection == horizon, "reference connection solve failed")
    _require(bminus.H * current * bplus == zero, "reference cross block is nonzero")

    gminus = -(bminus.H * current * bminus)
    gplus = bplus.H * current * bplus
    ghorizon = -(horizon.H * current * horizon)
    pull_minus = cminus.H * gminus * cminus
    pull_plus = cplus.H * gplus * cplus
    _require(
        ghorizon + pull_plus - pull_minus == zero,
        "reference Stokes identity failed",
    )

    # Standard complex-structure and realification identities.
    j6 = sp.zeros(12)
    j6[:6, 6:] = -sp.eye(6)
    j6[6:, :6] = sp.eye(6)
    j3 = sp.zeros(6)
    j3[:3, 3:] = -eye
    j3[3:, :3] = eye
    for name, frame in (
        ("H", horizon), ("Bminus", bminus), ("Bplus", bplus)
    ):
        real_frame = _realify(frame)
        _require(
            j6 * real_frame == real_frame * j3,
            f"reference {name} violates complex-structure equivariance",
        )
        _require(
            real_frame.T * _realify(current) * real_frame
            == _realify(frame.H * current * frame),
            f"reference {name} pullback realification failed",
        )

    # A genuinely nonunitary exact change of all three frames.
    ah = sp.diag(2, 3, 5)
    aminus = sp.Matrix([[1, 1, 0], [0, 2, 1], [0, 0, 3]])
    aplus = sp.Matrix([[2, 0, 0], [1, 1, 0], [0, 1, 2]])
    changed_whole = (bminus * aminus).row_join(bplus * aplus)
    changed_horizon = horizon * ah
    changed_connection = changed_whole.inv() * changed_horizon
    expected_connection = sp.diag(aminus.inv(), aplus.inv()) * connection * ah
    _require(
        changed_connection == expected_connection,
        "reference connection covariance failed",
    )
    changed_cminus = changed_connection[:3, :]
    changed_cplus = changed_connection[3:, :]
    changed_gminus = aminus.H * gminus * aminus
    changed_gplus = aplus.H * gplus * aplus
    changed_ghorizon = ah.H * ghorizon * ah
    _require(
        changed_ghorizon
        + changed_cplus.H * changed_gplus * changed_cplus
        - changed_cminus.H * changed_gminus * changed_cminus
        == zero,
        "reference basis-covariant Stokes identity failed",
    )

    # Exact index-pullback witnesses.  A rank-r image inside a Hermitian
    # space of inertia (1,2,0) has negative index at least r-1.
    endpoint = sp.diag(1, -1, -1)
    rank_one = sp.Matrix([[1], [0], [0]])
    rank_two = sp.Matrix([[1, 0], [0, 1], [0, 0]])
    rank_three = sp.eye(3)
    _require(
        rank_one.H * endpoint * rank_one == sp.diag(1)
        and negative_index_lower_bound(1) == 0,
        "rank-one index-pullback witness failed",
    )
    _require(
        rank_two.H * endpoint * rank_two == sp.diag(1, -1)
        and negative_index_lower_bound(2) == 1,
        "rank-two index-pullback witness failed",
    )
    _require(
        rank_three.H * endpoint * rank_three == endpoint
        and negative_index_lower_bound(3) == 2,
        "rank-three index-pullback witness failed",
    )


def validate_handoff_shape(document: dict[str, Any]) -> None:
    """Validate the future handoff vocabulary without promoting current work."""

    schema = json.loads(HANDOFF_SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(document),
        key=lambda error: list(error.path),
    )
    if errors:
        path = ".".join(str(part) for part in errors[0].path) or "root"
        raise ContractError(f"{path}: {errors[0].message}")

    all_certified = True
    any_certified = False
    any_negative_wavepacket = False
    for cell in document["cells"]:
        omega_lo, omega_hi = (
            Fraction(cell["omega_interval"][0]),
            Fraction(cell["omega_interval"][1]),
        )
        _require(omega_lo < omega_hi, "frequency cell is not a nonempty open interval")
        certified = cell["disposition"] == "CERTIFIED"
        all_certified = all_certified and certified
        any_certified = any_certified or certified
        if certified:
            _require(cell["shortfall"] is None, "certified cell has a shortfall")
            _require(
                isinstance(cell["evidence"], dict)
                and isinstance(cell["gates"], dict)
                and isinstance(cell["results"], dict),
                "certified cell lacks complete evidence",
            )
            for inertia in (
                cell["results"]["endpoint_Gplus_inertia"],
                cell["results"]["GHplus_inertia"],
                cell["results"]["gminus_inertia"],
                cell["results"]["gplus_inertia"],
            ):
                _require(sum(inertia) == 3, "complex inertia does not sum to three")
            results = cell["results"]
            _require(
                results["endpoint_Gplus_inertia"] == [1, 2, 0],
                "endpoint Gplus inertia does not match the exact pilot theorem",
            )
            rank_plus = results["rank_Cplus"]
            lower_bound = negative_index_lower_bound(rank_plus)
            _require(
                results["negative_index_lower_bound"] == lower_bound,
                "negative-index lower bound does not follow from image rank",
            )
            _require(
                results["gplus_inertia"][1] >= lower_bound,
                "pulled endpoint form violates the index-pullback theorem",
            )
            negative_wavepacket = rank_plus >= 2
            _require(
                results["compact_frequency_negative_endpoint_flux_wavepacket"]
                == negative_wavepacket,
                "negative endpoint wave-packet activation does not match rank_Cplus",
            )
            _require(
                results["infinite_dimensional_negative_endpoint_flux_subspace"]
                == negative_wavepacket,
                "disjoint-frequency-support refinement does not match activation",
            )
            any_negative_wavepacket = (
                any_negative_wavepacket or negative_wavepacket
            )
            expected_isometry = results["rank_Cminus"] == 3
            _require(
                results["normalized_one_sided_J_isometry"] == expected_isometry,
                "one-sided J-isometry does not match uniform Cminus invertibility",
            )
            if not negative_wavepacket:
                expected_branch = "no-negative-endpoint-activation"
            elif (
                results["rank_Cminus"] == 3
                and results["rank_Cplus"] == 3
                and results["normalized_one_sided_J_isometry"]
            ):
                expected_branch = "full-rank-normalized-one-sided-J-isometry"
            else:
                expected_branch = "rank-two-endpoint-negative-flux"
            _require(
                results["activation_branch"] == expected_branch,
                "activation branch does not match certified ranks",
            )
        else:
            _require(
                isinstance(cell["shortfall"], dict) and cell["shortfall"],
                "shortfall cell lacks a typed disposition",
            )
            _require(
                cell["evidence"] is None
                and cell["gates"] is None
                and cell["results"] is None,
                "shortfall cell carries uncertified result payloads",
            )
    _require(
        document["status"] == ("CERTIFIED" if all_certified else "SCOPED_SHORTFALL"),
        "root status does not match cell dispositions",
    )
    _require(
        document["claim_flags"]["normalized_plane_connection_certified"]
        == any_certified,
        "normalized connection flag does not match certified cell evidence",
    )
    _require(
        document["claim_flags"]["negative_endpoint_wavepacket_certified"]
        == any_negative_wavepacket,
        "negative endpoint wave-packet flag does not match certified ranks",
    )
    limits = set(document["does_not_establish"])
    _require(REQUIRED_LIMITS <= limits, "future handoff weakens the claim boundary")


def verify_certificate(data: dict[str, Any]) -> None:
    _require(
        data.get("schema")
        == "phase3-axial-normalized-plane-classification-preactivation-v1",
        "wrong preactivation schema",
    )
    _require(data.get("status") == "NOT_ACTIVATED", "preactivation was promoted")
    _require(data.get("lifecycle") == "CLASSIFIED", "wrong lifecycle")
    _require(
        data.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency tags drift",
    )

    contract = data.get("normalization_contract", {})
    _require(
        contract.get("kind") == "chart-identity-normalized-r4-planes"
        and contract.get("accumulated_endpoint_amplitudes_available") is False,
        "normalization boundary drift",
    )
    _require(
        contract.get("complex_state_order") == EXPECTED_STATE
        and contract.get("real_state_order") == EXPECTED_REAL_STATE,
        "state order drift",
    )
    current = contract.get("current", {})
    _require(
        current.get("hermitian") == "K4 = +i*Jhat(r=4,omega)",
        "the mandatory +i current convention is absent",
    )
    _require(
        current.get("realification")
        == "R(K4) = [[Re(K4),-Im(K4)],[Im(K4),Re(K4)]]",
        "current realification drift",
    )
    _require(
        "conservation alone is insufficient"
        in current.get("required_endpoint_crosscheck", ""),
        "sign crosscheck is not fail closed",
    )

    connection = contract.get("connection", {})
    _require(
        connection.get("frame_equation")
        == "[Bminus Bplus]*[Cminus;Cplus] = H",
        "connection equation drift",
    )
    _require(
        connection.get("basis_covariance") == "Cpm' = Apm^-1*Cpm*AH",
        "basis covariance drift",
    )
    pullbacks = contract.get("pullbacks", {})
    expected_pullbacks = {
        "cross": "Bminus^dagger*K4*Bplus = 0",
        "Gminus": "-Bminus^dagger*K4*Bminus",
        "Gplus": "Bplus^dagger*K4*Bplus",
        "GHplus": "-H^dagger*K4*H",
        "gminus": "Cminus^dagger*Gminus*Cminus",
        "gplus": "Cplus^dagger*Gplus*Cplus",
        "stokes": "GHplus+gplus-gminus=0",
    }
    _require(pullbacks == expected_pullbacks, "pullback or orientation formula drift")

    index_pullback = contract.get("index_pullback", {})
    _require(
        index_pullback.get("endpoint_inertia") == "(1,2,0) for alpha_W>0"
        and index_pullback.get("lower_bound") == "n_minus >= max(0,rank_Cplus-1)",
        "index-pullback theorem drift",
    )
    _require(
        "compactly supported frequency profile"
        in index_pullback.get("wavepacket_corollary", "")
        and "disjoint frequency supports"
        in index_pullback.get("infinite_dimensional_refinement", "")
        and "endpoint flux only"
        in index_pullback.get("claim_boundary", ""),
        "wave-packet corollary or claim boundary drift",
    )

    _require(set(data.get("required_gates", [])) == REQUIRED_GATES, "gate set drift")
    _require(
        set(data.get("mandatory_mutations", [])) == REQUIRED_MUTATIONS,
        "mutation set drift",
    )
    flags = data.get("claim_flags", {})
    _require(set(flags) == FORBIDDEN_FLAGS, "claim flag inventory drift")
    _require(not any(flags.values()), "preactivation contains a promoted claim")
    _require(
        REQUIRED_LIMITS <= set(data.get("does_not_establish", [])),
        "preactivation weakens the claim boundary",
    )
    _require(len(data.get("missing_inputs", [])) == 6, "missing-input ledger drift")

    for reference in data.get("imports", {}).values():
        path = _safe_path(reference["path"])
        _require(path.is_file(), f"missing imported object: {reference['path']}")
        _require(_sha256(path) == reference["sha256"], "import content hash drift")
        _require(
            len(reference["commit"]) == 40
            and all(character in "0123456789abcdef" for character in reference["commit"]),
            "import commit is not a full SHA-1",
        )

    schema = json.loads(HANDOFF_SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    verify_reference_algebra()


def verify(path: Path = CERTIFICATE) -> None:
    verify_certificate(json.loads(path.read_text()))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, default=CERTIFICATE)
    args = parser.parse_args()
    verify(args.certificate)
    print("PASS normalized-r4 plane preactivation contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
