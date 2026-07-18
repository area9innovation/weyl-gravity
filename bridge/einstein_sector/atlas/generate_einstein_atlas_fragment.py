#!/usr/bin/env python3
"""Generate the compact Plebański-Hacyan Einstein residual-atlas fragment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = Path(__file__).with_name("einstein-compact-product-atlas-fragment.json")
SCHEMA = ROOT / "residual_atlas/schema/residual-atlas-fragment-v1.schema.json"
STATUSES = ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"]
AXES = ["causal", "symplectic", "nonlinear", "observational", "quantum"]
CERTIFICATES = {
    "standard": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
    "axial_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json",
    "polar_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "axial_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "taub": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "balanced": ROOT / "bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json",
    "exceptional_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json",
    "exceptional_resonance": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_all_m_resonance.json",
    "twist_independence": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_twist_resonance.json",
    "twist_extension": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_balanced_second_order.json",
    "d_resonance": ROOT / "bridge/certificates/einstein_maxwell_weyl_d_axial_ell2_extra_resonance.json",
    "abstract_cone": ROOT / "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(name: str) -> dict:
    return json.loads(CERTIFICATES[name].read_text(encoding="utf-8"))


def _evidence(*names: str) -> list[dict[str, str]]:
    rows = []
    for name in names:
        path = CERTIFICATES[name]
        payload = _load(name)
        rows.append({"path": str(path.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": _sha256(path)})
    return rows


BASE = {
    "theory": "Einstein-Maxwell source included in Weyl-Maxwell target",
    "background": "compactified magnetically supported Plebanski-Hacyan R_t x S1_L x S2 fixture",
    "boundaries": "closed Cauchy slice S1_L x S2; no asymptotic boundary; before final residual SO(4,2) quotient",
    "charge_sector": "fixed magnetic U(1) bundle P_N with N=2; electric tangent allowed unless narrowed",
}


def _scope(**updates: object) -> dict[str, object]:
    value: dict[str, object] = dict(BASE)
    value.update(updates)
    return value


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def _second_order(bounded: tuple[str, str], secular: tuple[str, str], causal: tuple[str, str]) -> dict[str, object]:
    return {
        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
        "bounded_or_finite_quasiperiodic": _claim(*bounded),
        "smooth_secular": _claim(*secular),
        "causal_retarded": _claim(*causal),
    }


def _entry(
    identifier: str,
    scope: dict[str, object],
    descriptions: dict[str, str],
    dispersion: tuple[str, str],
    lee_wald: tuple[str, str],
    taub_maps: tuple[str, str],
    resonance: tuple[str, str],
    second_order: dict[str, object],
    evidence: list[dict[str, str]],
    boundary: str,
) -> dict[str, object]:
    return {
        "id": identifier,
        "scope": scope,
        "descriptions": descriptions,
        "mode_data": {
            "dispersion": _claim(*dispersion),
            "lee_wald": _claim(*lee_wald),
            "taub_maps": _claim(*taub_maps),
            "resonance": _claim(*resonance),
            "second_order": second_order,
        },
        "evidence": evidence,
        "claim_boundary": boundary,
    }


def entries() -> list[dict[str, object]]:
    open_causal = ("OPEN", "No compact-product causal/retarded Green theorem has been certified.")
    return [
        _entry(
            "einstein.ph.em_wm.standard.generic_radiative",
            _scope(carrier="Einstein q-primary image in the Weyl-Maxwell axial and polar coefficient complexes", degree=1, parity="axial and polar", ell=">=2", m="all", k="2*pi*n/L, n in Z", omega="omega^2=k^2+lambda +/- sqrt(2*lambda), lambda=ell(ell+1)"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "Two Einstein-Maxwell q-primary shells: omega^2=k^2+lambda +/- sqrt(2*lambda)."),
            ("CERTIFIED", "The identity inclusion is nonnull and nondegenerate but has branch-dependent relative endomorphism R; axial and polar branches are covered."),
            ("CERTIFIED", "The five compact stabilizer moment maps and their harmonic selection rules are explicit, but the pure-Einstein common zero locus is not classified."),
            ("OPEN", "The complete finite-harmonic q-primary resonance functionals are not classified."),
            _second_order(("OPEN", "No general bounded finite-harmonic Einstein-sector extension theorem."), ("OPEN", "No general smooth-secular Einstein-sector extension theorem."), open_causal),
            _evidence("standard", "axial_current", "polar_current", "taub", "abstract_cone"),
            "This is a compact pre-final-residual linear phase-space entry, not an asymptotic graviton, scattering, or all-orders Einstein-sector theorem.",
        ),
        _entry(
            "einstein.ph.wm.extra.generic_p_primary",
            _scope(theory="Weyl-Maxwell target", carrier="two p-primary extra polarizations in each axial and polar generic block", degree=1, parity="axial and polar", ell=">=2", m="all", k="2*pi*n/L, n in Z", omega="omega_e^2=k^2+lambda-2/3"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OBSTRUCTED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The extra shell is omega_e^2=k^2+lambda-2/3 and has two cyclic p-primary summands per parity."),
            ("CERTIFIED", "The direct Lee-Wald extra block is nonradical with positive-frequency current inertia (2,0) per parity and is orthogonal to the Einstein image."),
            ("CERTIFIED", "mu_H is negative definite on every nonzero real pure-extra finite-energy tangent at fixed magnetic bundle."),
            ("OPEN", "Additional bounded resonance functionals are not needed for the pure-extra Taub no-go and are not globally classified."),
            _second_order(("OBSTRUCTED", "Every nonzero real pure-extra tangent violates the fixed-bundle time-translation Taub constraint."), ("OBSTRUCTED", "Allowing secular propagation corrections does not remove the certified stabilizer moment-map obstruction."), open_causal),
            _evidence("axial_operator", "polar_operator", "axial_current", "polar_current", "taub", "abstract_cone"),
            "The obstruction is classical and fixed-bundle. It does not erase the linear mode, prove a quantum ghost, or supply a Lorentzian-causal no-go.",
        ),
        _entry(
            "einstein.ph.wm.mixed.ell2_k0_balanced_jet",
            _scope(theory="Weyl-Maxwell target with Einstein q-primary and extra p-primary inputs", carrier="one real axial ell=2,m=0,k=0 Einstein-minus mode plus one extra mode at the certified balancing amplitude", degree=2, parity="axial input with polar and homogeneous quadratic outputs", ell="input ell=2; outputs ell=0,2,4", m=0, k=0, omega="omega_-^2=6-2*sqrt(3), omega_e^2=16/3"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The two incommensurable input shells are omega_-^2=6-2*sqrt(3) and omega_e^2=16/3."),
            ("CERTIFIED", "The Einstein and extra inputs are orthogonal nonnull Lee-Wald directions with opposite Taub signs."),
            ("CERTIFIED", "The exact positive balancing amplitude makes all five stabilizer moment maps vanish."),
            ("CERTIFIED", "Every finite output channel is nonresonant or has its zero-frequency source canceled; all action rows are Noether-completed."),
            _second_order(("CERTIFIED", "A complete real finite-quasiperiodic second-order correction is constructed channel by channel."), ("CERTIFIED", "The bounded correction is also an admissible smooth exponential-polynomial correction."), open_causal),
            _evidence("balanced", "taub", "abstract_cone"),
            "This is one explicit second-order jet, not the full mixed cone, an exact nonlinear family, or an all-orders closure theorem.",
        ),
        _entry(
            "einstein.ph.wm.extra.exceptional_ell1_k0",
            _scope(theory="Weyl-Maxwell target", carrier="complete axial-plus-polar exceptional extra dipole block", degree=1, parity="axial and polar", ell=1, m="-1,0,1", k=0, omega="omega_e^2=4/3"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OBSTRUCTED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The exceptional extra dipole shell has omega_e^2=4/3."),
            ("CERTIFIED", "The exceptional axial and polar current blocks are nonradical and positive definite before the final residual quotient."),
            ("CERTIFIED", "The pure exceptional block has a definite fixed-bundle Taub obstruction."),
            ("CERTIFIED", "The all-m positive-positive source has a nonzero polar ell=2 p-shell projection; its exact STF zero locus is only the origin."),
            _second_order(("OBSTRUCTED", "Every nonzero exceptional dipole is obstructed by the certified Taub and resonant functionals."), ("OBSTRUCTED", "The stabilizer Taub obstruction persists even if a resonant propagation correction is allowed to be secular."), open_causal),
            _evidence("exceptional_current", "exceptional_resonance", "abstract_cone"),
            "This all-m compact no-go is pre-final-residual and does not identify an asymptotic state or a quantum particle.",
        ),
        _entry(
            "einstein.ph.wm.mixed.twist_exceptional_independence",
            _scope(theory="Weyl-Maxwell target", carrier="one real m=0 exceptional axial dipole plus a collinear standard twist velocity", degree=2, parity="axial input; polar ell=2 resonant output", ell="input ell=1; output ell=2", m=0, k=0, omega="omega_e^2=4/3 plus generalized-zero twist velocity"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OBSTRUCTED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The input combines the exceptional omega_e^2=4/3 shell with a generalized-zero twist velocity."),
            ("CERTIFIED", "Both inputs belong to certified nonnull compact current blocks before the final residual quotient."),
            ("CERTIFIED", "The twist amplitude is chosen so every stabilizer moment map mu_X vanishes."),
            ("CERTIFIED", "A polar ell=2 p-shell adjoint functional remains nonzero: mu_X(u)=0 but R_bounded(u)!=0."),
            _second_order(("OBSTRUCTED", "The nonzero resonant functional forbids a bounded/finite-quasiperiodic correction despite vanishing moment maps."), ("OPEN", "A complete smooth-secular correction has not been constructed or obstructed."), open_causal),
            _evidence("twist_independence", "exceptional_current", "abstract_cone"),
            "This is the independence witness separating stabilizer moment maps from dynamical resonance functionals; it is not a full exceptional mixed-cone classification.",
        ),
        _entry(
            "einstein.ph.wm.mixed.homogeneous_twist_velocity_jet",
            _scope(theory="Weyl-Maxwell target", carrier="standard homogeneous a-coordinate balanced with an arbitrary SO(3)-rotated twist-velocity vector at A=0", degree=2, parity="homogeneous scalar plus axial ell=1", ell="0 plus 1; quadratic outputs 0,1,2", m="all by SO(3) orbit", k=0, omega="generalized zero frequency"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The homogeneous/twist input is a generalized-zero Jordan block rather than an oscillatory shell."),
            ("CERTIFIED", "The homogeneous and twist pairs are nondegenerate blocks of the standard compact phase space."),
            ("CERTIFIED", "The harmonic-normalized balance 3*a^2=4*|B|^2 satisfies the compact stabilizer constraints."),
            ("CERTIFIED", "All homogeneous, axial ell=1 and polar ell=2 output rows are solved on the A=0 SO(3) orbit."),
            _second_order(("OPEN", "No bounded-correction theorem is asserted for this generalized-zero velocity input."), ("CERTIFIED", "A complete smooth exponential-polynomial second-order correction is constructed."), open_causal),
            _evidence("standard", "twist_extension", "abstract_cone"),
            "This certifies the A=0 twist-velocity orbit only; twist position and the full global cone remain open.",
        ),
        _entry(
            "einstein.ph.wm.interaction.d_times_axial_ell2_extra",
            _scope(theory="Weyl-Maxwell target", carrier="homogeneous circumference velocity d crossed with the two axial ell=2 extra-primary amplitudes", degree=2, parity="axial", ell=2, m="all", k=0, omega="output omega_e^2=16/3"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The resonant output is the axial p-shell at omega_e^2=16/3."),
            ("CERTIFIED", "The extra input multiplicity is the certified nonradical axial Lee-Wald block."),
            ("OPEN", "The simultaneous five stabilizer moment maps for this enlarged input have not been solved."),
            ("CERTIFIED", "The d-cross source-to-adjoint pairing is an isomorphism with determinant 832, so any axial p-shell defect is algebraically cancellable for d!=0."),
            _second_order(("OPEN", "The axial resonant projection is cancellable, but polar, nonresonant and stabilizer conditions remain."), ("OPEN", "No complete smooth-secular extension has been assembled."), open_causal),
            _evidence("d_resonance", "axial_current", "abstract_cone"),
            "This is a resonant compatibility matrix, not a complete second-order extension or a full homogeneous/twist source matrix.",
        ),
        _entry(
            "einstein.crosswalk.compact_product_to_asymptotic_or_vacuum_cylinder",
            _scope(theory="crosswalk", background="compact Plebanski-Hacyan <-> asymptotically flat/dS/AdS or vacuum conformal cylinder", boundaries="cross-background boundary/carrier identification", charge_sector="crosswalk", carrier="mode identification map", degree="crosswalk", parity="n/a", ell="n/a", m="n/a", k="n/a", omega="n/a"),
            {axis: "NO_CERTIFIED_MAP" for axis in AXES},
            ("NO_CERTIFIED_MAP", "No dispersion-preserving cross-background map is certified."),
            ("NO_CERTIFIED_MAP", "No Lee-Wald crosswalk is certified."),
            ("NO_CERTIFIED_MAP", "No stabilizer/Taub crosswalk is certified."),
            ("NO_CERTIFIED_MAP", "No resonance crosswalk is certified."),
            _second_order(("NO_CERTIFIED_MAP", "No bounded correction-class crosswalk."), ("NO_CERTIFIED_MAP", "No secular correction-class crosswalk."), ("NO_CERTIFIED_MAP", "No causal/retarded correction-class crosswalk.")),
            [],
            "Compact-product modes must not be called asymptotic gravitons or vacuum-cylinder residual classes without an explicit certified crosswalk.",
        ),
    ]


def build() -> dict[str, object]:
    records = {name: _load(name) for name in CERTIFICATES}
    if not records["standard"]["classification"]["complete_standard_harmonic_linear_restriction"]:
        raise AssertionError("standard inclusion input lost completeness")
    if not records["taub"]["classification"]["all_nonzero_generic_pure_extra_fixed_bundle_tangents_second_order_obstructed"]:
        raise AssertionError("generic pure-extra Taub input changed")
    if not records["balanced"]["classification"]["complete_second_order_extension_constructed"]:
        raise AssertionError("balanced second-order extension input changed")
    if not records["exceptional_resonance"]["classification"]["complete_all_m_exceptional_ell1_two_polarization_cone_second_order_obstructed"]:
        raise AssertionError("exceptional all-m input changed")
    if not records["twist_independence"]["classification"]["nonzero_adjoint_cokernel_witness_certified"]:
        raise AssertionError("twist independence witness changed")
    if not records["d_resonance"]["classification"]["d_cross_adjoint_map_invertible"]:
        raise AssertionError("d-cross resonance input changed")
    if not records["abstract_cone"]["flags"]["FINITE_HARMONIC_TANGENT_CONE_FORMULA"]:
        raise AssertionError("abstract tangent-cone theorem changed")
    value = {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "einstein_boundary",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": _sha256(Path(__file__)),
        "status_vocabulary": STATUSES,
        "description_axes": AXES,
        "entries": entries(),
        "verification_commands": [
            "python3 -m bridge.einstein_sector.atlas.generate_einstein_atlas_fragment --check",
            "python3 residual_atlas/validate_fragment.py bridge/einstein_sector/atlas/einstein-compact-product-atlas-fragment.json",
            "python3 bridge/einstein_sector/atlas/verify_einstein_atlas_fragment.py",
            "python3 -m unittest bridge.einstein_sector.atlas.tests.test_einstein_atlas_fragment",
        ],
    }
    Draft202012Validator.check_schema(json.loads(SCHEMA.read_text(encoding="utf-8")))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(value)
    identifiers = [entry["id"] for entry in value["entries"]]
    if len(identifiers) != len(set(identifiers)):
        raise AssertionError("atlas mode identifiers are not unique")
    for entry in value["entries"]:
        if not entry["evidence"] and "crosswalk" not in entry["id"]:
            raise AssertionError(f"unsupported atlas entry: {entry['id']}")
    return value


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise AssertionError("Einstein atlas fragment is stale")
    print("EINSTEIN_COMPACT_PRODUCT_RESIDUAL_ATLAS_FRAGMENT_V1: PASS")


if __name__ == "__main__":
    main()
