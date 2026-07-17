"""Independent verifier for the ungauged polar equation/Noether lift."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

from bridge.einstein_sector.einstein_maxwell_polar_master_complex import _matrix as _source_matrix
from bridge.einstein_sector.einstein_maxwell_weyl_axial_green_current import _green_terms
from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import _equation_map


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ungauged_noether_lift.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_polar_ungauged_noether_lift.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expr(value: str, local: dict[str, sp.Expr]) -> sp.Expr:
    return sp.sympify(value.replace("lambda", "lam"), locals=local)


def _matrix(values: list[list[str]], local: dict[str, sp.Expr]) -> sp.Matrix:
    return sp.Matrix([[_expr(value, local) for value in row] for row in values])


def _zero(matrix: sp.MatrixBase) -> bool:
    return matrix.applyfunc(lambda value: sp.factor(sp.expand(value))) == sp.zeros(matrix.rows, matrix.cols)


def _adjoint(matrix: sp.MatrixBase, w: sp.Symbol, k: sp.Symbol) -> sp.Matrix:
    return matrix.subs({w: -w, k: -k}, simultaneous=True).T


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    generator = ROOT / payload["provenance"]["generator_path"]
    assert payload["provenance"]["generator_sha256"] == _sha256(generator)
    for record in payload["provenance"]["inputs"].values():
        assert record["sha256"] == _sha256(ROOT / record["path"])

    l, k, w = sp.symbols("lambda k omega", real=True)
    local = {"lam": l, "k": k, "omega": w, "I": sp.I}
    contractions = payload["contractions"]
    complexes = payload["complexes"]
    chain = payload["chain_map"]
    Gs = _matrix(contractions["source_gauge_map"], local)
    Gt = _matrix(contractions["target_gauge_map"], local)
    Ps = _matrix(contractions["source_invariant_projection"], local)
    Pt = _matrix(contractions["target_invariant_projection"], local)
    Js = _matrix(contractions["source_section"], local)
    Jt = _matrix(contractions["target_section"], local)
    Hs = _matrix(contractions["source_homotopy"], local)
    Ht = _matrix(contractions["target_homotopy"], local)
    ghost = _matrix(chain["ghost_map_source_to_target"], local)
    assert _zero(Ps * Gs) and _zero(Pt * Gt)
    assert Ps * Js == sp.eye(5) and Pt * Jt == sp.eye(4)
    assert _zero(Js * Ps - sp.eye(8) - Gs * Hs)
    assert _zero(Jt * Pt - sp.eye(8) - Gt * Ht)
    assert _zero(Gt * ghost - Gs)

    source, source_symbols = _source_matrix()
    target, field_map, equation_map, target_symbols = _equation_map()
    assert source_symbols == target_symbols == (l, k, w)
    assert _zero(Pt - field_map * Ps)
    Es = _matrix(complexes["source_ungauged_Euler_operator"], local)
    Lt = _matrix(complexes["target_ungauged_Hessian_operator"], local)
    Ns = _matrix(complexes["source_Bianchi_map"], local)
    Nt = _matrix(complexes["target_Noether_map"], local)
    Je = _matrix(chain["equation_map_source_to_target"], local)
    Ki = _matrix(chain["identity_map_source_to_target"], local)
    assert _zero(Es - source * Ps)
    assert _zero(Lt - _adjoint(Pt, w, k) * target * Pt)
    assert _zero(Je - _adjoint(Pt, w, k) * equation_map)
    assert _zero(Nt - _adjoint(Gt, w, k))
    assert _zero(Es * Gs) and _zero(Ns * Es)
    assert _zero(Lt * Gt) and _zero(Nt * Lt)
    assert _zero(Lt - Je * Es)
    assert _zero(Nt * Je - Ki * Ns)
    assert _zero(Lt - _adjoint(Lt, w, k))

    T, X = sp.symbols("T X", commutative=True)
    subs = {w: sp.I * T, k: -sp.I * X}
    ungauged = _green_terms(Lt.subs(subs, simultaneous=True).applyfunc(lambda value: sp.factor(sp.expand(value))), T, X)
    reduced = _green_terms(target.subs(subs, simultaneous=True).applyfunc(lambda value: sp.factor(sp.expand(value))), T, X)
    current_payload = {"time_current_terms": ungauged["time_current_terms"], "space_current_terms": ungauged["space_current_terms"]}
    digest = hashlib.sha256(json.dumps(current_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    audit = payload["local_Green_current"]
    assert digest == audit["current_terms_sha256"]
    assert ungauged["jet_identity_remainder"] == []
    assert ungauged["time_current_term_count"] == audit["time_current_term_count"]
    assert ungauged["space_current_term_count"] == audit["space_current_term_count"]
    selected = {0: 0, 1: 1, 2: 2, 7: 3}
    for component in ("time_current_terms", "space_current_terms"):
        restricted = []
        for term in ungauged[component]:
            if term["u_component"] in selected and term["v_component"] in selected:
                record = dict(term)
                record["u_component"] = selected[record["u_component"]]
                record["v_component"] = selected[record["v_component"]]
                restricted.append(record)
        assert restricted == reduced[component]

    assert payload["classification"]["cyclic_BV_chain_map_certified"] is False
    assert payload["classification"]["final_residual_descent_certified"] is False
    assert payload["classification"]["quantum_classical_import_gate_satisfied"] is False
    assert payload["verification_receipt"]["tier_0"]["status"] == "PASS"
    assert payload["verification_receipt"]["tier_1"]["status"] == "PASS"
    assert payload["verification_receipt"]["tier_2"]["status"] == "NOT_RUN_NOT_REQUIRED"
    assert payload["verification_receipt"]["tier_3"]["status"] == "NOT_RUN"


if __name__ == "__main__":
    verify_certificate()
