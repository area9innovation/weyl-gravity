#!/usr/bin/env python3
"""Emit exact witnesses for WR <-> ACA_0; not an infinite-proof checker."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / 'foundations/results/FOUNDATIONAL_CODED_WAVE_MODULUS_REVERSAL_V1.json'
REPORT = 'foundations/reports/coded-wave-modulus-reversal-v1.md'
SOURCE = 'foundations/results/FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1.json'
BASE = '548f99056ef0ef55a9edabae0252381a8c5ffa9b'


def enc(q):
    q = Q(q)
    return [q.numerator, q.denominator]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def tent(x):
    x %= 1
    return 2*x if x <= Q(1, 2) else 2-2*x


def response(t):
    # Translate the step partition; integrate the tent by trapezoids.
    cuts = sorted({Q(0), Q(1), Q(1, 2), (t+Q(1, 4)) % 1, (t+Q(3, 4)) % 1})
    value = Q(0)
    for a, b in zip(cuts, cuts[1:]):
        x = ((a+b)/2-t) % 1
        sign = 1 if Q(1, 4) <= x < Q(3, 4) else -1
        value += sign*(b-a)*(tent(a)+tent(b))/2
    return value


def fit_piece(a, b):
    m = (a+b)/2
    ya, ym, yb = response(a), response(m), response(b)
    quadratic = ((yb-ym)/(b-m)-(ym-ya)/(m-a))/(b-a)
    linear = (ym-ya)/(m-a)-quadratic*(a+m)
    constant = ya-linear*a-quadratic*a*a
    return {'interval': [enc(a), enc(b)], 'coefficients': [enc(constant), enc(linear), enc(quadratic)]}


def weight(e):
    return Q(1, 4**(e+1))


def fixture(prefix):
    tail = max(prefix)+1
    # Infinite continuation f(len(prefix)+j)=tail+j; no claimed infinite computation.
    limit = sum((weight(e) for e in set(prefix)), Q(0))+Q(1, 3*4**tail)
    stages = []
    for s in range(len(prefix)+4):
        seen = set(prefix[:s]) | set(range(tail, tail+max(0, s-len(prefix))))
        amplitude = sum((weight(e) for e in seen), Q(0))
        stages.append({'stage': s, 'seen': sorted(seen), 'amplitude': enc(amplitude),
                       'observation_at_zero': enc(amplitude/4), 'energy_squared': enc(amplitude**2)})
    witnesses = []
    s = len(prefix)
    qs = sum((weight(e) for e in set(prefix)), Q(0))
    for e in range(tail+2):
        member = e in prefix or e >= tail
        k = 2*e+6
        rname = Q((limit*2**k).__floor__(), 2**k)
        witnesses.append({'value': e, 'in_range': member,
                          'absence_witness': None if member else {
                              'stage': s, 'precision': k, 'limit_approximant': enc(rname),
                              'upper_remainder': enc(rname+Q(1, 2**k)-qs)}})
    return {'prefix': prefix, 'tail_start': tail, 'limit': enc(limit), 'stages': stages,
            'range_witnesses': witnesses}


def build():
    source = json.loads((ROOT/SOURCE).read_text())
    assets = [(SOURCE, 'existing_observable_certificate', BASE),
              ('foundations/results/FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1.json', 'existing_energy_representation', BASE),
              (REPORT, 'human_proof', None),
              ('foundations/build_coded_wave_modulus_reversal.py', 'producer', None),
              ('foundations/verify_coded_wave_modulus_reversal.py', 'independent_finite_audit', None),
              ('foundations/schema/foundational-coded-wave-modulus-reversal-v1.schema.json', 'schema', None),
              ('foundations/tests/test_coded_wave_modulus_reversal.py', 'mutation_tests', None)]
    result = {
        'schema_version': 'foundational-coded-wave-modulus-reversal-v1',
        'result_id': 'FOUNDATIONAL_CODED_WAVE_MODULUS_REVERSAL_V1',
        'result_kind': 'REPRESENTATION_SPECIFIC_REVERSE_MATHEMATICS',
        'evidence_status': 'HUMAN_PROOF_WITH_EXACT_REDUCTION_AUDIT',
        'created': '2026-09-07', 'repository_base_commit': BASE,
        'dependency_tags': ['LOCAL-ALGEBRAIC', 'REDUCED-MODE'],
        'theorem': {
            'base': 'RCA_0', 'rate_free_principle': 'WR', 'equivalent_system': 'ACA_0',
            'supplied_modulus_principle': 'WR_mu', 'supplied_modulus_base': 'RCA_0',
            'scope': 'Unit-ball Cauchy sequences of mean-zero rational chiral step pairs, with the fixed periodic tent detector.',
            'quantifiers': 'For every coded input satisfying the ordinary Cauchy promise, there exists a fast uniform polygonal output name.',
            'input_rate_supplied': False, 'input_limit_state_supplied': False,
            'output_input_convergence_rate_required': False,
            'higher_type_choice_functional_asserted': False,
            'necessity_uses': 'One fixed spatial profile and evaluation at time zero.'},
        'detector': {key: source['declared_observable'][key] for key in ('id', 'test_breaks', 'test_values', 'test_l2_squared', 'formula')},
        'profile': {'breaks': [[0, 1], [1, 4], [3, 4], [1, 1]], 'values': [[-1, 1], [1, 1], [-1, 1]],
                    'mean': [0, 1], 'l2_squared': [1, 1], 'gain_at_zero': [1, 4],
                    'metric_scaling_squared': [1, 1],
                    'response_pieces': [fit_piece(Q(0), Q(1, 4)), fit_piece(Q(1, 4), Q(3, 4)), fit_piece(Q(3, 4), Q(1))]},
        'upper_bound': {'observable_distance_squared_constant': [2, 3], 'unit_ball_time_lipschitz_bound': [4, 1],
                        'modulus_index_shift': 3, 'dyadic_mesh_index_shift': 5,
                        'pair_error_coefficient': [3, 8], 'output_convergence_modulus_shift': 5},
        'encoding': {'radix': 4, 'weight_exponent_shift': 1, 'duplicates_counted_once': True,
                     'total_weight': [1, 3], 'tail_after_e_over_weight_e': [1, 3],
                     'output_evaluation_scale': [4, 1], 'output_evaluation_index_shift': 2,
                     'absence_comparison': 'r_k + 2^(-k) - q_s < w_e',
                     'absence_requires_not_seen': True},
        'infinite_proof_obligations': [
            {'id': 'MODULUS_SELECTION', 'base': 'ACA_0', 'status': 'HUMAN_PROOF', 'report_section': 'Upper bound and the supplied-rate construction'},
            {'id': 'RATE_SUPPLIED_AVOIDANCE', 'base': 'RCA_0', 'status': 'HUMAN_PROOF', 'report_section': 'Upper bound and the supplied-rate construction'},
            {'id': 'ORDINARY_CAUCHY_WITHOUT_MODULUS', 'base': 'RCA_0', 'status': 'HUMAN_PROOF', 'report_section': 'Why the Cauchy promise is available in RCA_0'},
            {'id': 'SIGMA1_COMPLEMENT_AND_DELTA1_RANGE', 'base': 'RCA_0 + WR', 'status': 'HUMAN_PROOF', 'report_section': 'The output decides the range'}],
        'fixtures': [fixture(p) for p in ([4, 1, 4, 7, 0], [7, 8, 9, 10, 0, 2], [0, 0, 0], [3, 1, 3, 1])],
        'blind_control': {'breaks': [[0, 1], [1, 2], [1, 1]], 'values': [[1, 1], [-1, 1]], 'gain_at_zero': [0, 1],
                          'scope': 'Time-zero evaluation only; not all-time blindness.'},
        'provenance': [{'path': path, 'sha256': hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),
                        'role': role, 'source_commit': commit} for path, role, commit in assets],
        'literature': {'citation': 'Stephen G. Simpson, Subsystems of Second Order Arithmetic, second edition (2009), Chapter I, Theorem I.9.1 and the Section III.1 summary on printed page 47.',
                       'url': 'https://sgslogic.net/t20/sosoa/chapter1.pdf', 'accessed': '2026-09-07',
                       'retrieved_sha256': 'c3ec4d883a2346deb3780f14791df237f90b78ca3610596fb21ac622d4ca23ce',
                       'local_replay_status': 'NOT_VENDORED_NOT_REPLAYED_BY_VERIFIER',
                       'role': 'Standard scalar comprehension reversal and range-existence characterization; no novelty claim for that argument.'},
        'claim_flags': {'human_equivalence_proof_supplied': True, 'exact_reduction_witnesses_supplied': True,
                        'infinite_proof_kernel_checked': False, 'unrestricted_wave_foundations_classified': False,
                        'physical_preparation_or_probability_proved': False, 'causal_support_proved': False,
                        'new_lorentzian_claim': False, 'atlas_or_passport_promoted': False,
                        'paper_theorem_promoted': False, 'quantum_lifecycle_promoted': False},
        'missing_objects': ['Proof-assistant formalization of the quantified RCA_0 argument.',
                            'Independent review of the infinite proof, beyond the exact reduction audit.'],
        'human_report': REPORT,
    }
    result['content_sha256'] = digest(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    data = json.dumps(build(), indent=2, ensure_ascii=False)+'\n'
    if args.check:
        ok = RESULT.exists() and RESULT.read_text() == data
        print('Coded-wave modulus reversal deterministic receipt: '+('PASS' if ok else 'FAIL'))
        return 0 if ok else 1
    RESULT.write_text(data)
    print(RESULT.relative_to(ROOT))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
