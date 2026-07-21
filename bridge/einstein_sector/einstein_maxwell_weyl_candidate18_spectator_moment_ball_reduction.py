"""Eliminate candidate-18 spectators exactly to a spin-two moment ball."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_CANDIDATE18_SPECTATOR_MOMENT_BALL_REDUCTION_V1.json"
ATLAS = ROOT / "residual_atlas/einstein-candidate18-spectator-moment-ball-reduction-fragment-v1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-candidate18-spectator-moment-ball-reduction-v1.schema.json"
INPUT_COMMIT = "252df7272"
INPUTS = {
    "parent_gate": ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_GLOBAL_BOUNDED_CONE_REAL_LOCUS_GATE_V1.json",
    "active_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_active_restricted_current_degeneracy.json",
    "phase_reduction": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_phase_reduced_presymplectic_divisors.json",
    "complex_carrier": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_complex_singular_resolution.json",
    "central_bridge": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_singular_smooth_bridge.json",
    "stabilizer": ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
}
EXPECTED_HASHES = {
    "parent_gate": "8a6565668d1add5214d11eaf6c5ef0f2645f596953b1c9aed3af6ad4fa5b1b37",
    "active_current": "af541fe8332dd1769bf23dfc12c207c9b3df46670d6f60bd7e02bcf8cc24bedc",
    "phase_reduction": "d4e6091c079a75a82f16db01e3478d6e6b971df020c48557ffd471137fb80786",
    "complex_carrier": "16390b76191d608e3fd6b81db10c0fd9bd34817866033aa9ca26ae8c6d10b971",
    "central_bridge": "dbe2504b9ae1bcbdfda09f410ccb7beda5cfc70f9486fe300b73e1a3cc5d6806",
    "stabilizer": "7d2840bc88b3fb157345badb7ae2683adceb7401b611ba5b90dca4b8868993b8",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def spin_two_matrices() -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    j = sp.Integer(2)
    ms = tuple(range(-2, 3))
    raising = sp.zeros(5)
    for column, m in enumerate(ms[:-1]):
        raising[column + 1, column] = sp.sqrt(j * (j + 1) - m * (m + 1))
    lowering = raising.T
    return (
        (raising + lowering) / 2,
        (raising - lowering) / (2 * sp.I),
        sp.diag(*ms),
    )


def spin_two_exact_checks() -> dict[str, Any]:
    jx, jy, jz = spin_two_matrices()
    if jx.H != jx or jy.H != jy or jz.H != jz:
        raise AssertionError("spin-two generators are not Hermitian")
    if sp.simplify(jx * jy - jy * jx - sp.I * jz) != sp.zeros(5):
        raise AssertionError("spin-two commutator changed")
    if list(jz.eigenvals()) != [-2, -1, 0, 1, 2]:
        raise AssertionError("spin-two weights changed")

    x, y = sp.symbols("x y", nonnegative=True, real=True)
    vector = sp.zeros(5, 1)
    vector[2] = x
    vector[4] = y
    norm = sp.simplify((vector.H * vector)[0])
    moment = [sp.simplify((vector.H * generator * vector)[0]) for generator in (jx, jy, jz)]
    if norm != x**2 + y**2 or moment != [0, 0, 2 * y**2]:
        raise AssertionError("spin-two ball witness changed")
    return {
        "basis_order": ["m=-2", "m=-1", "m=0", "m=1", "m=2"],
        "T3_eigenvalues": [-2, -1, 0, 1, 2],
        "operator_norm_bound": "For every unit n, n_a*T_a is SO(3)-conjugate to T3, hence |s^dagger n_a*T_a s|<=2*s^dagger*s.",
        "axis_witness": "s_1=x*e_0+y*e_2, s_2=0, S=x^2+y^2 and r=2*y^2; equivalently x^2=S-r/2, y^2=r/2 for 0<=r<=2S",
        "axis_witness_norm": str(norm),
        "axis_witness_moment": [str(value) for value in moment],
        "rotated_witness": "Apply the exact spin-two representation of an SO(3) rotation taking e_z to nu/|nu|.",
    }


def _input_records() -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for name, path in INPUTS.items():
        digest = _sha256(path)
        if digest != EXPECTED_HASHES[name]:
            raise AssertionError(f"{name} content hash changed")
        value = _load(path)
        records[name] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": digest,
            "result_id": value["result_id"],
            "lifecycle_state": value["lifecycle_state"],
        }
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", INPUT_COMMIT, "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if ancestor.returncode:
        raise AssertionError("required input commit is not an ancestor of HEAD")
    return records


def build_certificate() -> dict[str, Any]:
    inputs = {name: _load(path) for name, path in INPUTS.items()}
    parent = inputs["parent_gate"]
    phase = inputs["phase_reduction"]["candidate18"]
    complex_carrier = inputs["complex_carrier"]["complete_carrier"]
    if parent["selected_invariant_gate"]["ambient_real_dimension"] != 60:
        raise AssertionError("parent real carrier changed")
    if "ten positive current-orthogonal spectators" not in phase["ambient_coordinate_order"]:
        raise AssertionError("spectator carrier changed")
    if complex_carrier["isomorphism"] != "C^10_spectator x R_plus x R_minus":
        raise AssertionError("candidate-18 complex carrier changed")
    if inputs["stabilizer"]["background_stabilizer"]["connected_lie_algebra"] != "R*H direct-sum R*P_x direct-sum so(3)":
        raise AssertionError("lifted rotation stabilizer changed")

    producer = Path(__file__).resolve()
    certificate = {
        "schema": "einstein-maxwell-weyl-candidate18-spectator-moment-ball-reduction-v1",
        "result_id": "EINSTEIN_MAXWELL_WEYL_CANDIDATE18_SPECTATOR_MOMENT_BALL_REDUCTION_V1",
        "result_state": "TEN_SPECTATORS_EXACTLY_REDUCED_TO_CONNECTED_SPIN2_MOMENT_BALL_FIBRES",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": parent["scope"],
        "input_gate": {
            "required_commit": INPUT_COMMIT,
            "exact_hashes": EXPECTED_HASHES,
            "parent_state": parent["result_state"],
        },
        "spectator_representation": {
            "carrier": "C^10_spectator=V_2 tensor C^2, two complete spin-two multiplets",
            "real_dimension": 20,
            "Hermitian_current": "positive identity block in the imported candidate-18 current normalization",
            "node_phase": "the common positive-node U(1) acts diagonally on spectators and active f amplitudes; it is retained in the associated-fibre reconstruction",
            "lifted_rotation": "SO(3) acts in V_2 on both spectator copies",
            "exact_generator_check": spin_two_exact_checks(),
        },
        "spectator_moment_ball_theorem": {
            "normalized_norm": "H_s=|s_1|^2+|s_2|^2",
            "normalized_moment": "M_s,a=sum_{r=1}^2 s_r^dagger*T_a*s_r",
            "image_at_fixed_norm": "{nu in R^3: |nu|<=2*H_s}",
            "necessity": "The spin-two operator norm bound gives |M_s|<=2*H_s.",
            "sufficiency": "The displayed m=0/m=2 witness realizes every radius 0<=r<=2*H_s on the z axis; SO(3) covariance realizes every direction.",
            "connected_fibres": "For H_s>0, divide the norm sphere by its connected Hopf U(1) to CP^9. Kirwan connectedness for the compact connected Hamiltonian SO(3)-space CP^9 makes every moment fibre connected; its Hopf preimage is connected. At H_s=0 the fibre is the origin.",
            "all_ten_spectators_retained": True,
        },
        "active_coordinate_gate": {
            "coordinate_order": "(f_plus,f_minus,g_plus,g_minus), each in C^5",
            "ambient_real_dimension": 40,
            "resonance_equations": [
                "f_plus wedge g_plus=0 (ten complex 2x2 minors)",
                "f_minus wedge g_minus=0 (ten complex 2x2 minors)",
            ],
            "positive_active_norm": "H_f=<f,(A tensor I_5)f>, A=[[a,c],[c,a]] with a=w_x/12+w_y/4 and c=-w_x/12+w_y/4",
            "negative_norm_level": "b*(|g_plus|^2+|g_minus|^2)=6*N_minus, b=6*h_minus>0",
            "spectator_slack": "H_s=6*N_plus-H_f",
            "active_rotation_moment": "M_f,a=<f,(A tensor T_a)f>-b*<g,(I_2 tensor T_a)g>",
            "exact_spectator_existence_conditions": [
                "H_s>=0",
                "|M_f|^2<=4*H_s^2",
            ],
            "strict_reduction": "60 real amplitude coordinates -> 40 real active coordinates plus one exact quadratic inequality; spectator fibres and their stabilizer action are attached, not discarded",
        },
        "necessity_and_sufficiency": {
            "forward": "Any full rotation-zero point has M_s=-M_f and therefore satisfies H_s>=0 and |M_f|<=2*H_s.",
            "reverse": "For any active resonance point satisfying the negative level and the two displayed inequalities, the spin-two moment-ball witness supplies all ten spectator amplitudes with norm H_s and moment -M_f, giving a full fixed-occupation rotation-zero point.",
            "equivalence": "The projection of the complete 60-real-coordinate physical fibre onto active coordinates is exactly the displayed 40-real-coordinate semialgebraic set.",
        },
        "phase_and_orbit_reconstruction": {
            "group": "U(1)_plus x U(1)_minus x lifted SO(3)",
            "fibre_functor": "Over an active point a, attach F_a={s in C^10: |s|^2=H_s(a), M_s=-M_f(a)}; every F_a is nonempty exactly on the reduced gate and is connected.",
            "equivariance": "F_{R*a}=R*F_a and the positive-node phase acts diagonally on (f,s), so stabilizers and relative phases are retained.",
            "full_quotient_formula": "{(a,s): a in B_40, s in F_a}/(U(1)_plus x U(1)_minus x SO(3))",
            "full_orbit_type_classification": "OPEN",
        },
        "remaining_strict_gate": {
            "name": "candidate18-active-40-real-moment-ball-gate",
            "problem": "Compute the real radical/component decomposition of B_40, its active stabilizer strata, and the associated connected spectator-fibre quotients; decide whether every resulting component meets the central bridge.",
            "strictly_smaller_than_parent": True,
            "parent_real_dimension": 60,
            "active_real_dimension": 40,
            "Forge_component_singularity_layer_state": "PROPOSED_NOT_CERTIFIED_FOR_USE",
        },
        "classification": {
            "spectator_moment_image_exact_ball": True,
            "spectator_moment_fibres_connected": True,
            "ten_spectators_retained_by_exact_fibre_reconstruction": True,
            "parent_gate_reduced_strictly": True,
            "active_40_real_semialgebraic_gate_exact": True,
            "active_real_radical_classified": False,
            "full_U1_squared_SO3_orbit_quotient_classified": False,
            "every_component_meets_central_bridge": False,
            "complex_irreducibility_substituted_for_real_connectedness": False,
            "global_finite_support_causal_all_orders_observational_or_quantum_claim": False,
        },
        "provenance": {
            "input_commit": INPUT_COMMIT,
            "inputs": _input_records(),
            "producer_path": str(producer.relative_to(ROOT)),
            "producer_sha256": _sha256(producer),
            "schema_path": str(SCHEMA.relative_to(ROOT)),
            "schema_sha256": _sha256(SCHEMA),
        },
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.einstein_sector.einstein_maxwell_weyl_candidate18_spectator_moment_ball_reduction --check",
            "PYTHONPATH=. python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_candidate18_spectator_moment_ball_reduction",
            "PYTHONPATH=. python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_candidate18_spectator_moment_ball_reduction",
            "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-candidate18-spectator-moment-ball-reduction-fragment-v1.json",
        ],
        "next_gate": "classify the exact 40-real-coordinate active determinantal moment-ball set and its stabilizer/orbit strata, then attach the certified connected spectator fibres",
        "claim_boundary": "This exactly eliminates, but does not drop, all ten spectators and gives a necessary-and-sufficient 40-real-coordinate active gate. It does not compute that active real radical, classify the full compact-group orbit quotient, prove every component meets the bridge, glue occupations, or establish global finite-support, causal, all-orders, observational or quantum claims.",
    }
    Draft202012Validator(_load(SCHEMA)).validate(certificate)
    return certificate


def build_atlas(certificate: dict[str, Any]) -> dict[str, Any]:
    scope = {
        key: value
        for key, value in certificate["scope"].items()
        if key != "correction_class"
    }
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "einstein_nonlinear",
        "generated_by": str(Path(__file__).resolve().relative_to(ROOT)),
        "generated_by_sha256": _sha256(Path(__file__).resolve()),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [{
            "id": "einstein.ph.wm.candidate18.spectator_moment_ball_reduction",
            "scope": scope,
            "descriptions": {
                "causal": "NO_CERTIFIED_MAP",
                "symplectic": "CERTIFIED",
                "nonlinear": "OPEN",
                "observational": "NO_CERTIFIED_MAP",
                "quantum": "NO_CERTIFIED_MAP",
            },
            "mode_data": {
                "dispersion": {"status": "CERTIFIED", "statement": "The candidate-18 active collision data are unchanged."},
                "lee_wald": {"status": "CERTIFIED", "statement": "The spectator block is two positive spin-two multiplets."},
                "taub_maps": {"status": "CERTIFIED", "statement": "Spectator norm/moment elimination is the exact ball |M_f|<=2H_s."},
                "resonance": {"status": "CERTIFIED", "statement": "Both rank-at-most-one 5x2 factors remain explicit."},
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "bounded_or_finite_quasiperiodic": {"status": "OPEN", "statement": "The exact gate is reduced from 60 to 40 real coordinates; its active real components and orbit strata remain open."},
                    "smooth_secular": {"status": "NOT_APPLICABLE", "statement": "This reduction is scoped to the bounded correction class."},
                    "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No retarded complex is imported."},
                },
            },
            "evidence": [{
                "path": str(OUTPUT.relative_to(ROOT)),
                "sha256": _sha256(OUTPUT),
                "result_id": certificate["result_id"],
            }],
            "claim_boundary": certificate["claim_boundary"],
        }],
        "verification_commands": certificate["verification_commands"],
    }


def write_outputs() -> None:
    certificate = build_certificate()
    OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ATLAS.write_text(json.dumps(build_atlas(certificate), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_output() -> None:
    expected = build_certificate()
    if _load(OUTPUT) != expected:
        raise AssertionError("certificate is stale")
    if _load(ATLAS) != build_atlas(expected):
        raise AssertionError("atlas is stale")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write_outputs()
    if args.check:
        verify_output()
    if not (args.write or args.check):
        parser.error("choose --write or --check")


if __name__ == "__main__":
    main()
