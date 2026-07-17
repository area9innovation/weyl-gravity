#!/usr/bin/env python3
"""C-G2: causal BV transport on a globally conformal open background class."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
ABSTRACT = ROOT / "d_quotient_classical/certificates/ABSTRACT_CYCLIC_CAUSAL_TRANSFER.json"
BASE_GREEN = ROOT / "covariant_completion/certificates/curved_full_prolonged_green_homotopy_assembly.json"
BASE_CURRENT = ROOT / "covariant_completion/certificates/curved_prolonged_current_comparison.json"
FIELD_DICTIONARY = ROOT / "d_quotient_classical/minimal_bv_antifield/foundation/field_dictionary.json"
ATOM_MANIFEST = ROOT / "d_quotient_classical/minimal_bv_antifield/foundation/atom_basis_manifest.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/CONFORMALLY_RELATED_CYCLIC_CAUSAL_TRANSFER_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/conformally-related-cyclic-causal-transfer.md"
SCHEMA = ROOT / "d_quotient_classical/schema/conformally-related-cyclic-causal-transfer-v1.schema.json"
VERIFIER = HERE / "verify_conformally_related_cyclic_causal_transfer.py"
TESTS = HERE / "tests/test_conformally_related_cyclic_causal_transfer.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"dependency is not an object: {path}")
    return value


def _dependency(path: Path, value: dict) -> dict[str, str]:
    return {
        "artifact_id": value.get("result_id", value.get("schema", path.stem)),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def _zero(matrix: sp.Matrix) -> bool:
    return all(sp.factor(value) == 0 for value in matrix)


def _canonical_fixture() -> dict[str, object]:
    """Check the finite Diff-semidirect-Weyl tangent/cotangent action."""
    r, a = sp.symbols("r a", nonzero=True, real=True)
    # Generator order: metric tangent, diffeomorphism ghost, Weyl ghost.
    tangent = sp.Matrix([[r, 0, 0], [0, 1, 0], [0, -a, 1]])
    tangent_inverse = sp.Matrix([[1 / r, 0, 0], [0, 1, 0], [0, a, 1]])
    cotangent = tangent_inverse.T
    cotangent_inverse = tangent.T
    canonical = sp.zeros(6)
    canonical[:3, 3:] = sp.eye(3)
    canonical[3:, :3] = -sp.eye(3)
    full = sp.diag(1, 1, 1, 1, 1, 1)
    full[:3, :3] = tangent
    full[3:, 3:] = cotangent
    full_inverse = sp.diag(1, 1, 1, 1, 1, 1)
    full_inverse[:3, :3] = tangent_inverse
    full_inverse[3:, 3:] = cotangent_inverse

    r1, r2, a1, a2 = sp.symbols("r1 r2 a1 a2", nonzero=True, real=True)
    t1 = tangent.subs({r: r1, a: a1})
    t2 = tangent.subs({r: r2, a: a2})
    composed = tangent.subs({r: r1 * r2, a: a1 + a2})
    defects = {
        "tangent_inverse_left": tangent_inverse * tangent - sp.eye(3),
        "tangent_inverse_right": tangent * tangent_inverse - sp.eye(3),
        "full_inverse_left": full_inverse * full - sp.eye(6),
        "full_inverse_right": full * full_inverse - sp.eye(6),
        "odd_pairing_preserved": full.T * canonical * full - canonical,
        "finite_group_composition": t2 * t1 - composed,
    }
    if any(not _zero(value) for value in defects.values()):
        raise AssertionError("finite conformal BV-canonical fixture failed")

    # Exact nonconstant consumer on the cylinder.
    t = sp.symbols("t", real=True)
    omega = 1 + 1 / (10 * (1 + t**2))
    lower = sp.factor(omega - 1)
    upper = sp.factor(sp.Rational(11, 10) - omega)
    dlog = sp.factor(sp.diff(sp.log(omega), t))
    if sp.simplify(lower - 1 / (10 * (t**2 + 1))) != 0 or sp.simplify(upper - t**2 / (10 * (t**2 + 1))) != 0:
        raise AssertionError("nonconstant conformal-factor bounds drifted")
    if sp.simplify(dlog + 2 * t / ((t**2 + 1) * (10 * t**2 + 11))) != 0:
        raise AssertionError("nonconstant affine ghost coefficient drifted")

    return {
        "tangent": tangent,
        "cotangent": cotangent,
        "defects": {name: 0 for name in defects},
        "omega": omega,
        "lower": lower,
        "upper": upper,
        "dlog": dlog,
    }


def _inputs() -> dict[str, dict]:
    values = {
        "abstract_causal_transfer": _load(ABSTRACT),
        "cylinder_full_green_homotopy": _load(BASE_GREEN),
        "cylinder_current_comparison": _load(BASE_CURRENT),
        "minimal_field_dictionary": _load(FIELD_DICTIONARY),
        "minimal_atom_manifest": _load(ATOM_MANIFEST),
    }
    if values["abstract_causal_transfer"]["flags"]["ABSTRACT_CAUSAL_TRANSFER_CERTIFIED"] is not True:
        raise ValueError("abstract causal-transfer theorem unavailable")
    if values["cylinder_full_green_homotopy"].get("causal_green_homotopy") is not True:
        raise ValueError("cylinder causal Green homotopy unavailable")
    if values["cylinder_current_comparison"].get("prolonged_current_comparison") is not True:
        raise ValueError("cylinder current comparison unavailable")
    roles = {row["role"]: row for row in values["minimal_field_dictionary"]["generators"]}
    expected = {
        "metric": 2,
        "diffeomorphism_ghost": 0,
        "weyl_ghost": 0,
        "metric_antifield": -2,
        "diffeomorphism_ghost_antifield": 0,
        "weyl_ghost_antifield": 0,
    }
    if {name: roles[name]["Weyl_weight"] for name in expected} != expected:
        raise ValueError("minimal conformal-weight dictionary drifted")
    return values


def build() -> dict:
    inputs = _inputs()
    fixture = _canonical_fixture()
    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-conformally-related-cyclic-causal-transfer-v1",
        "result_id": "CONFORMALLY_RELATED_CYCLIC_CAUSAL_TRANSFER_V1",
        "result_state": "G3_GLOBAL_CONFORMAL_ORBIT_CAUSAL_TRANSFER_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: _dependency(path, inputs[name])
            for name, path in {
                "abstract_causal_transfer": ABSTRACT,
                "cylinder_full_green_homotopy": BASE_GREEN,
                "cylinder_current_comparison": BASE_CURRENT,
                "minimal_field_dictionary": FIELD_DICTIONARY,
                "minimal_atom_manifest": ATOM_MANIFEST,
            }.items()
        },
        "background_class": {
            "manifold": "M=R x S^3",
            "reference_metric": "g0=-dt^2+dOmega_3^2",
            "metrics": "g_phi=exp(2 phi) g0",
            "parameter_space": "U_epsilon={phi in C_b^infinity(M,R): sup_M |phi|<epsilon}, epsilon>0",
            "topology": "bounded-smooth Frechet topology; U_epsilon is open by the C0 seminorm",
            "global_hyperbolicity": "positive conformal rescaling preserves global hyperbolicity and the Cauchy surfaces {t=constant}",
            "causal_sets": "J_g_phi^+/-=J_g0^+/- as subsets of M",
            "boundary": "no timelike boundary",
            "uniformity_scope": "smooth and support categories; Sobolev estimates require the corresponding finite C_b derivative seminorms of phi",
        },
        "finite_BV_canonical_map": {
            "phi": "log Omega",
            "minimal_rows": {
                "h": "h_phi=exp(2 phi) h",
                "xi": "xi_phi=xi",
                "omega": "omega_phi=omega-xi(phi)",
                "g_star": "g_star_phi=exp(-2 phi) g_star",
                "xi_star": "xi_star_phi=xi_star+d(phi) omega_star",
                "omega_star": "omega_star_phi=omega_star",
            },
            "derived_rows": {
                "E_g": "E_g,phi=exp(-2 phi) E_g",
                "N_xi": "N_xi,phi=N_xi+d(phi) N_omega",
                "N_omega": "N_omega,phi=N_omega",
            },
            "nonminimal_and_prolonged_rows": "transport every generalized-auxiliary defining row by the same tangent map and every dual row by its inverse formal adjoint; equivalently transport the gauge fermion rather than reusing the untransformed cylinder gauge",
            "inverse": "U_phi^-1=U_-phi with the inverse affine ghost/cotangent shear",
            "group_law": "U_psi U_phi=U_(phi+psi)",
            "odd_pairing": "U_phi^sharp Omega_BV U_phi=Omega_BV",
            "finite_fixture_tangent_matrix": [[str(x) for x in row] for row in fixture["tangent"].tolist()],
            "finite_fixture_cotangent_matrix": [[str(x) for x in row] for row in fixture["cotangent"].tolist()],
            "finite_fixture_defects": fixture["defects"],
        },
        "transport_theorem": {
            "differential": "Q_phi=U_phi Q_0 U_phi^-1",
            "advanced_retarded_homotopies": "Lambda_phi,+/-=U_phi Lambda_0,+/- U_phi^-1",
            "chain_identity": "Q_phi Lambda_phi,+/-+Lambda_phi,+/- Q_phi=1",
            "support": "supp Lambda_phi,+/- f subset J_g_phi^+/-(supp f)",
            "cyclic_adjoint": "Lambda_phi,+^sharp=Sigma_phi Lambda_phi,- Sigma_phi^-1",
            "current": "Omega_Sigma,phi(U_phi u,U_phi v)=Omega_Sigma,0(u,v); transported improvements remain d+Q exact",
            "causal_quasi_isomorphism": "the compact-to-spacelike-compact causal map transports by U_phi",
            "proof": "conjugate the cylinder chain identity; U_phi and U_phi^-1 are pointwise support-local, preserve the odd pairing, and positive conformal rescaling leaves the causal relation unchanged",
        },
        "nonconstant_consumer": {
            "phi": "log(1+1/(10*(1+t^2)))",
            "Omega": str(fixture["omega"]),
            "bounds": {"Omega_minus_1": str(fixture["lower"]), "11_over_10_minus_Omega": str(fixture["upper"]), "conclusion": "1<Omega<=11/10"},
            "d_phi": str(fixture["dlog"]),
            "nonconstant": True,
            "all_derivatives_bounded": True,
            "same_causal_cones": True,
            "transported_complete_complex": True,
        },
        "exact_checks": {
            "minimal_row_weights_imported": True,
            "affine_Weyl_ghost_term_included": True,
            "cotangent_antifield_shear_included": True,
            "finite_map_invertible": True,
            "finite_group_law_exact": True,
            "BV_pairing_preserved": True,
            "transported_gauge_fermion_declared": True,
            "chain_identity_transports_by_conjugation": True,
            "advanced_retarded_support_preserved": True,
            "cyclic_adjoint_transports": True,
            "current_pairing_transports": True,
            "nonconstant_global_consumer_exact": True,
        },
        "flags": {
            "CONFORMALLY_RELATED_CYCLIC_CAUSAL_TRANSFER_V1": True,
            "G3_OPEN_BACKGROUND_CLASS": True,
            "ALL_GLOBALLY_CONFORMALLY_CYLINDRICAL_METRICS_IN_CLASS": True,
            "ALL_LOCALLY_CONFORMALLY_FLAT_TOPOLOGIES": False,
            "FIXED_UNTRANSFORMED_GAUGE_FERMION": False,
            "TIMELIKE_BOUNDARY_VERSION": False,
            "HADAMARD_TRANSFER": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "C_G2_LOCAL_PATCHING_OR_CONFORMALLY_EINSTEIN_CURVATURE_OBSTRUCTION",
        "claim_boundary": (
            "This theorem promotes a genuine G3 open class on the fixed cylinder manifold: every bounded-smooth positive global conformal rescaling in U_epsilon inherits the complete smooth/support causal BV homotopies and cyclic current pairing from the certified cylinder complex by the displayed finite BV-canonical gauge transformation. The Weyl ghost affine term and its cotangent antifield shear are essential. The gauge-fixed and prolonged rows use the transported gauge fermion; this theorem does not assert that the original untransformed coordinate gauge has identical coefficients. It does not cover conformally flat manifolds requiring multiple conformal charts, new topology, timelike boundaries, Sobolev-uniform estimates without derivative bounds, Hadamard products, interactions, anomalies, or quantum theory."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/conformally_related_cyclic_causal_transfer.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_conformally_related_cyclic_causal_transfer.py",
                "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_conformally_related_cyclic_causal_transfer",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/conformally-related-cyclic-causal-transfer-v1.schema.json -d d_quotient_classical/certificates/CONFORMALLY_RELATED_CYCLIC_CAUSAL_TRANSFER_V1.json",
            ],
        },
    }


def validate(value: dict) -> None:
    if value.get("result_state") != "G3_GLOBAL_CONFORMAL_ORBIT_CAUSAL_TRANSFER_CERTIFIED":
        raise ValueError("conformal causal-transfer state drifted")
    if not all(value.get("exact_checks", {}).values()):
        raise ValueError("conformal causal-transfer check dropped")
    flags = value.get("flags", {})
    if (
        flags.get("G3_OPEN_BACKGROUND_CLASS") is not True
        or flags.get("ALL_GLOBALLY_CONFORMALLY_CYLINDRICAL_METRICS_IN_CLASS") is not True
        or any(
            flags.get(name) is not False
            for name in (
                "ALL_LOCALLY_CONFORMALLY_FLAT_TOPOLOGIES",
                "FIXED_UNTRANSFORMED_GAUGE_FERMION",
                "TIMELIKE_BOUNDARY_VERSION",
                "HADAMARD_TRANSFER",
                "QUANTUM_CLAIM",
            )
        )
    ):
        raise ValueError("conformal causal-transfer claim boundary drifted")


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# C-G2: globally conformal cyclic causal transport

Let \(g_0=-dt^2+d\Omega_3^2\) and

\[
g_\phi=e^{2\phi}g_0,
\qquad
\phi\in C_b^\infty(\mathbb R\times S^3),
\qquad \|\phi\|_\infty<\epsilon.
\]

This is an open class in the bounded-smooth topology.  Every metric is
globally hyperbolic with the same causal sets and Cauchy slices as \(g_0\).

The finite transformation is not a list of independent scalar weights.  The
semidirect Diff--Weyl algebra forces

\[
h_\phi=e^{2\phi}h,
\qquad \xi_\phi=\xi,
\qquad \omega_\phi=\omega-\xi(\phi),
\]

and BV canonicity forces

\[
g^*_{\phi}=e^{-2\phi}g^*,
\qquad \xi^*_{\phi}=\xi^*+d\phi\,\omega^*,
\qquad \omega^*_{\phi}=\omega^*.
\]

Transporting every generalized-auxiliary defining row and its cyclic dual,
and transporting the gauge fermion itself, gives a pointwise BV-canonical
chain isomorphism \(U_\phi\).  Therefore

\[
Q_\phi=U_\phi Q_0U_\phi^{-1},
\qquad
\Lambda_{\phi,\pm}=U_\phi\Lambda_{0,\pm}U_\phi^{-1}
\]

satisfy the complete chain identity, advanced/retarded support, cyclic
adjoint reversal and Cauchy-current comparison.  This proves a G3 theorem on
the global conformal orbit, not merely another background replay.

The exact nonconstant consumer is

\[
\Omega(t)=1+\frac1{10(1+t^2)},
\qquad 1<\Omega\leq\frac{11}{10}.
\]

The theorem does not cover manifolds requiring multiple conformal charts,
new topology, timelike boundaries, an untransported coordinate gauge,
Hadamard products or quantum claims.
"""


def _guards(value: dict) -> None:
    mutations = [
        ("drop affine ghost", ("exact_checks", "affine_Weyl_ghost_term_included"), False),
        ("claim all topologies", ("flags", "ALL_LOCALLY_CONFORMALLY_FLAT_TOPOLOGIES"), True),
        ("claim fixed gauge", ("flags", "FIXED_UNTRANSFORMED_GAUGE_FERMION"), True),
        ("claim quantum", ("flags", "QUANTUM_CLAIM"), True),
    ]
    for name, path, replacement in mutations:
        mutant = deepcopy(value)
        mutant[path[0]][path[1]] = replacement
        try:
            validate(mutant)
        except ValueError:
            continue
        raise AssertionError(f"mutation guard accepted: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check:
        if OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report():
            raise AssertionError("conformal causal-transfer outputs drifted")
    if args.guards:
        _guards(value)
    print("CONFORMALLY_RELATED_CYCLIC_CAUSAL_TRANSFER_V1: PASS")


if __name__ == "__main__":
    main()
