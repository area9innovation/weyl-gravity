"""Produce the restriction-stable polar module/current closure."""
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path
from .module_audit import current_layer_table, literal_current_shape, master_infinity_audit, polynomial_master_ricci_residual, shallow_log_audit

ROOT = Path(__file__).resolve().parents[3]
PKG = Path(__file__).resolve().parent

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build() -> dict:
    completion = ROOT/'black_hole_programme/phase2/general_l_polar_completion/certificate.json'
    polar = ROOT/'black_hole_programme/phase2/general_l_polar/certificate.json'
    branches = sorted((completion.parent/'branch_artifacts').glob('*.json'))
    completion_data=json.loads(completion.read_text())
    polar_data = json.loads(polar.read_text())
    current = polar_data['exact_symbolic_lambda_result']['literal_lee_wald_current']['sphere_integrated_slice_current']
    prefix_files=sorted((PKG/'prefix_artifacts').glob('*depth8.json'))
    prefix_summary={}
    for pp in prefix_files:
      pd=json.loads(pp.read_text()); prefix_summary[pp.name]={
        'sha256':sha(pp),'sector':pd['sector'],'logs':pd['logs'],'depth':pd['depth'],
        'final_free_dimension':pd['final_free_dimension'],
        'last_rank':pd['per_order_affine_rank_witnesses'][-1]['rank'],
        'last_nullity':pd['per_order_affine_rank_witnesses'][-1]['nullity']}
    current_files=sorted((PKG/'current_artifacts').glob('oscillatory-*.json'))
    matrix_path=PKG/'current_artifacts/oscillatory-matrix-filtration.json'
    matrix=json.loads(matrix_path.read_text())
    wall_path=PKG/'current_artifacts/canonical-pivot-wall-certificate.json'
    wall=json.loads(wall_path.read_text())
    basis_path=PKG/'current_artifacts/basis-lift-congruence.json'
    basis=json.loads(basis_path.read_text())
    return {
      "schema_version":"phase2-polar-extendible-current-closure-v1",
      "result_id":"POLAR_RESTRICTION_STABLE_MODULE_CURRENT_FILTRATION_V1",
      "dependency_tags":["LOCAL-ALGEBRAIC","REDUCED-MODE"],
      "imports":{"input_commit":"b9d347d832492d9e39a8cfbd346b041f35f22de7",
        "completion_sha256":sha(completion),"polar_v1_sha256":sha(polar),
        "branch_sha256":{p.name:sha(p) for p in branches}},
      "master_infinity":master_infinity_audit(),
      "polynomial_master_seven_row_crosscheck":polynomial_master_ricci_residual(),
      "shallow_log":shallow_log_audit(),
      "literal_current_parser": literal_current_shape(current),
      "serialized_full_seven_prefixes": prefix_summary,
      "prefix_projection": {
        "zero": "one direction restricts nontrivially; log0/log<=1 dimensions 1/1",
        "oscillatory": "one log-free direction restricts nontrivially; a second log0 vector and the third log<=1 vector are supported only at terminal n=8",
        "terminal_only_disposition": "not promoted to an extendible quotient before one-step q9 compatibility"
      },
      "compatibility_stabilized_module_typing": {
        "E": "The nonterminal full-seven-row homogeneous direction has zero Ricci carrier by construction and is the retained Einstein-image direction.",
        "X0_X1_X2": "The three imported metric reconstructions have nonzero sourced Ricci carriers and form the chosen additional complement.",
        "residual_gauge": "No independent residual diffeomorphism or Weyl-gauge vector occurs in the generic ell>=2, omega!=0 Regge-Wheeler-gauge restriction-stable prefix image.",
        "weyl_radical": "No standalone Weyl-radical direction is promoted in the retained module; the filtered mixed radical is an asymptotic-current statement, not a gauge classification.",
        "maximality": "The lower-order restriction image of the depth-eight oscillatory log-free kernel is one-dimensional; every other displayed basis vector is terminal-only. Thus span(E) is the maximal restriction-stable homogeneous input at the certified depth."
      },
      "six_sourced_carrier_safe_tail_ledger": [{
        "sector":x['sector'],"branch_index":x['branch_index'],
        "artifact_path":x['artifact_path'],"artifact_sha256":x['artifact_sha256'],
        "all_seven_rows_through_metric_depth":x['all_seven_rows_through_metric_depth'],
        "safe_tail_ledger":x['safe_tail_ledger']
      } for x in completion_data['canonical_log_free_frontier']],
      "bounded_gj_reconnaissance": {
        "status": "SERIALIZED_PREFIX_CLASSIFICATION",
        "zero_rate_depth8_log_le_1_final_free": 1,
        "oscillatory_depth8_log_le_1_final_free": 3,
        "oscillatory_depth7_log0_final_free": 2,
        "interpretation": "One zero and one oscillatory direction are restriction-stable. The two additional oscillatory vectors are terminal-only at n=8 and are excluded pending q9 compatibility."
      },
      "invariant_current_filtration": {
        "matrix_artifact": str(matrix_path.relative_to(ROOT)),
        "matrix_sha256": sha(matrix_path),
        "entry_sha256": {p.name:sha(p) for p in current_files},
        "basis": matrix['basis'],
        "anti_hermitian": matrix['anti_hermitian'],
        "leading_power": 0,
        "subleading_power": -1,
        "generic_rank_away_from_detK_walls": matrix['leading_p0']['generic_rank_away_from_detK_walls'],
        "generic_radical_dimension_away_from_detK_walls": matrix['leading_p0']['generic_radical_dimension_away_from_detK_walls'],
        "schur_numerator_identically_zero": matrix['leading_p0']['schur_numerator_identically_zero'],
        "p_minus_1_induced_radical_form_identically_zero": matrix['subleading_p_minus_1']['induced_form_on_leading_radical_identically_zero'],
        "p_minus_2_induced_form_identically_zero": matrix['first_finite_p_minus_2']['identically_zero'],
        "disposition": wall['finite_line']['generic_disposition'],
        "exact_exceptional_locus": wall['finite_line']['exact_exceptional_locus'],
        "canonical_pivot_wall_status": wall['disposition'],
        "wall_artifact":str(wall_path.relative_to(ROOT)),"wall_sha256":sha(wall_path),
        "basis_congruence_artifact":str(basis_path.relative_to(ROOT)),"basis_congruence_sha256":sha(basis_path),
        "invariant_ledger":basis['invariant_ledger']
      },
      "zero_rate_disposition": {
        "status":"EXCLUDED_FROM_RADIATIVE_HEADLINE",
        "reason":"The zero-rate block is stationary/generalized-zero data, whereas the conjugate-frequency radiation current theorem assumes real omega!=0. Its p>=-1 cancellations are not promoted as a gauge or radical theorem.",
        "available_evidence":"The serialized zero-rate upper-triangle entries cancel every dangerous p>=-1 layer; no zero-rate scattering norm is defined here."
      },
      "status":{
        "module_reconciliation":"SCOPED PASS: one zero and one oscillatory full-seven-row direction are restriction-stable; terminal-only n=8 vectors remain unpromoted pending q9",
        "current":"SCOPED PASS: the full ordered 4x4 oscillatory current on (E,X0,X1,X2) is exact through p=-1",
        "current_convention_mutation":"reconstruction uses exp(+I*omega*v), literal current left slot exp(-I*omega*v); raw insertion gives a false Lambda=6 E|E p=4, while whole-profile conjugation restores dangerous-layer cancellation",
        "finite_radical":"A one-dimensional mixed Einstein/additional line survives p=0,-1 and has a generically nonzero first finite p=-2 pairing; its exact exceptional set is Q21(ell(ell+1),omega^2)=0",
        "bounded_frontier":"q9 compatibility of terminal-only prefixes and deeper filtration on the Q21 exceptional locus remain open."},
      "does_not_establish":["terminal-only prefix extension","deeper filtration on Q21 exceptional frequencies","all-order asymptotic solutions","horizon-to-infinity matching","asymptotic phase space","scattering","stability","positivity"]}

def main():
    PKG.mkdir(parents=True,exist_ok=True)
    (PKG/'certificate.json').write_text(json.dumps(build(),indent=2,sort_keys=True)+'\n')
if __name__=='__main__': main()
