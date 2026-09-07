#!/usr/bin/env python3
"""Independent finite reduction audit; does not check the infinite RCA_0 proof."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT/'foundations/results/FOUNDATIONAL_CODED_WAVE_MODULUS_REVERSAL_V1.json'
SCHEMA = ROOT/'foundations/schema/foundational-coded-wave-modulus-reversal-v1.schema.json'
REPORT = ROOT/'foundations/reports/coded-wave-modulus-reversal-v1.md'


def rat(pair):
    value = Q(*pair)
    if pair != [value.numerator, value.denominator]:
        raise ValueError('noncanonical rational')
    return value


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def tent_integral(a, b):
    # Primitive polynomial integration, separately on the two fixed tent halves.
    total = Q(0)
    for lo, hi, slope, intercept in [(Q(0), Q(1, 2), 2, 0), (Q(1, 2), Q(1), -2, 2)]:
        left, right = max(a, lo), min(b, hi)
        if left < right:
            total += slope*(right**2-left**2)/2+intercept*(right-left)
    return total


def step_moments(profile):
    breaks = list(map(rat, profile['breaks']))
    values = list(map(rat, profile['values']))
    assert len(breaks) == len(values)+1 and breaks[0] == 0 and breaks[-1] == 1
    assert all(a < b for a, b in zip(breaks, breaks[1:]))
    mean = sum(((b-a)*v for a, b, v in zip(breaks, breaks[1:], values)), Q(0))
    square = sum(((b-a)*v*v for a, b, v in zip(breaks, breaks[1:], values)), Q(0))
    gain = sum((v*tent_integral(a, b) for a, b, v in zip(breaks, breaks[1:], values)), Q(0))
    return mean, square, gain


def shifted_tent_polynomial(shift, midpoint):
    integer = (midpoint+shift).__floor__()
    phase = midpoint+shift-integer
    slope, intercept = (Q(2), Q(0)) if phase < Q(1, 2) else (Q(-2), Q(2))
    return slope*(shift-integer)+intercept, slope


def response_from_derivative():
    value = Q(1, 4)
    result = []
    for a, b in [(Q(0), Q(1, 4)), (Q(1, 4), Q(3, 4)), (Q(3, 4), Q(1))]:
        midpoint = (a+b)/2
        upper = shifted_tent_polynomial(Q(3, 4), midpoint)
        lower = shifted_tent_polynomial(Q(1, 4), midpoint)
        constant_derivative = 2*(upper[0]-lower[0])
        quadratic = upper[1]-lower[1]
        constant = value-constant_derivative*a-quadratic*a*a
        coefficients = [constant, constant_derivative, quadratic]
        result.append((a, b, coefficients))
        value = sum(c*b**j for j, c in enumerate(coefficients))
    assert value == Q(1, 4)
    return result


def check_fixture(fixture):
    errors = []
    prefix = fixture['prefix']
    tail = fixture['tail_start']
    if tail != max(prefix)+1:
        return ['continuation tail start']
    # Derive the infinite tail from (1-1/4)*tail_sum=4^(-tail-1).
    unit = Q(1, 4)
    tail_sum = unit**(tail+1)/(1-unit)
    actual_range_prefix = set(prefix)
    limit = sum((unit**(e+1) for e in actual_range_prefix), Q(0))+tail_sum
    if rat(fixture['limit']) != limit:
        errors.append('infinite continuation limit (not a finite prefix)')
    stages = fixture['stages']
    if [s['stage'] for s in stages] != list(range(len(prefix)+4)):
        return errors+['complete stage inventory']
    for record in stages:
        s = record['stage']
        seen = {prefix[j] if j < len(prefix) else tail+j-len(prefix) for j in range(s)}
        q = sum((unit**(e+1) for e in seen), Q(0))
        if record['seen'] != sorted(seen) or rat(record['amplitude']) != q:
            errors.append('finite discovery set / duplicate removal')
        if not 0 <= q < Q(1, 3) or rat(record['energy_squared']) != q*q:
            errors.append('unit-ball isometric embedding')
        if rat(record['observation_at_zero']) != q/4:
            errors.append('observable evaluation')
    rows = fixture['range_witnesses']
    if [r['value'] for r in rows] != list(range(tail+2)):
        return errors+['range-witness inventory']
    for row in rows:
        e = row['value']
        member = e in actual_range_prefix or e >= tail
        w = unit**(e+1)
        if row['in_range'] != member:
            errors.append('range membership')
        witness = row['absence_witness']
        if member:
            if witness is not None:
                errors.append('false absence witness for present value')
        elif witness is None:
            errors.append('missing absence witness')
        else:
            s, k = witness['stage'], witness['precision']
            if not 0 <= s < len(stages):
                errors.append('absence stage out of range')
                continue
            qs = rat(stages[s]['amplitude'])
            approximation = rat(witness['limit_approximant'])
            remainder = approximation+Q(1, 2**k)-qs
            if e in stages[s]['seen'] or abs(approximation-limit) > Q(1, 2**k):
                errors.append('invalid name or discovery premise')
            if rat(witness['upper_remainder']) != remainder or not remainder < w:
                errors.append('strict Sigma1 absence witness')
        # Late discoveries must never be classified absent, even at early stages.
        for stage in stages:
            if member and e not in stage['seen']:
                if limit-rat(stage['amplitude']) < w:
                    errors.append('late-discovery lower bound')
    return errors


def verify(value=None, report=None):
    value = json.loads(RESULT.read_text()) if value is None else value
    errors = ['schema: '+e.message for e in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value)]
    if errors:
        return errors
    payload = {k: v for k, v in value.items() if k != 'content_sha256'}
    if value['content_sha256'] != digest(payload):
        errors.append('content digest')
    obligations = value['infinite_proof_obligations']
    expected_obligations = [
        ('MODULUS_SELECTION', 'ACA_0', 'Upper bound and the supplied-rate construction'),
        ('RATE_SUPPLIED_AVOIDANCE', 'RCA_0', 'Upper bound and the supplied-rate construction'),
        ('ORDINARY_CAUCHY_WITHOUT_MODULUS', 'RCA_0', 'Why the Cauchy promise is available in RCA_0'),
        ('SIGMA1_COMPLEMENT_AND_DELTA1_RANGE', 'RCA_0 + WR', 'The output decides the range')]
    if [(o['id'], o['base'], o['report_section']) for o in obligations] != expected_obligations:
        errors.append('complete human-proof obligation ledger')
    if [f['prefix'] for f in value['fixtures']] != [[4, 1, 4, 7, 0], [7, 8, 9, 10, 0, 2], [0, 0, 0], [3, 1, 3, 1]]:
        errors.append('duplicate and delayed-discovery fixture coverage')
    expected_assets = {
        'foundations/results/FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1.json': 'existing_observable_certificate',
        'foundations/results/FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1.json': 'existing_energy_representation',
        'foundations/reports/coded-wave-modulus-reversal-v1.md': 'human_proof',
        'foundations/build_coded_wave_modulus_reversal.py': 'producer',
        'foundations/verify_coded_wave_modulus_reversal.py': 'independent_finite_audit',
        'foundations/schema/foundational-coded-wave-modulus-reversal-v1.schema.json': 'schema',
        'foundations/tests/test_coded_wave_modulus_reversal.py': 'mutation_tests'}
    assets = value['provenance']
    if len(assets) != len(expected_assets) or {a['path']: a['role'] for a in assets} != expected_assets:
        errors.append('complete source/proof/audit provenance')
    for asset in assets:
        if asset['path'] not in expected_assets:
            continue
        path = ROOT/asset['path']
        data = report.encode() if report is not None and path == REPORT else path.read_bytes()
        if hashlib.sha256(data).hexdigest() != asset['sha256']:
            errors.append('asset hash: '+asset['path'])
        expected_commit = value['repository_base_commit'] if asset['role'].startswith('existing_') else None
        if asset['source_commit'] != expected_commit:
            errors.append('imported versus new source provenance')
    source = json.loads((ROOT/'foundations/results/FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1.json').read_text())
    detector = value['detector']
    if detector != {k: source['declared_observable'][k] for k in detector}:
        errors.append('same imported detector')
    if detector['test_breaks'] != [[0, 1], [1, 2], [1, 1]] or detector['test_values'] != [[0, 1], [1, 1], [0, 1]]:
        errors.append('fixed tent detector')
    try:
        p = value['profile']
        if p['breaks'] != [[0, 1], [1, 4], [3, 4], [1, 1]] or p['values'] != [[-1, 1], [1, 1], [-1, 1]]:
            errors.append('fixed visible profile')
        mean, norm, gain = step_moments(p)
        if (rat(p['mean']), rat(p['l2_squared']), rat(p['gain_at_zero'])) != (mean, norm, gain) or (mean, norm, gain) != (0, 1, Q(1, 4)):
            errors.append('independent mean/norm/detector gain')
        if rat(p['metric_scaling_squared']) != norm:
            errors.append('metric scaling')
        expected_pieces = response_from_derivative()
        pieces = p['response_pieces']
        if len(pieces) != len(expected_pieces):
            errors.append('response piece inventory')
        else:
            for row, (a, b, coeffs) in zip(pieces, expected_pieces):
                if list(map(rat, row['interval'])) != [a, b] or list(map(rat, row['coefficients'])) != coeffs:
                    errors.append('response derivative polynomial identity')
        control = value['blind_control']
        cm, cn, cg = step_moments(control)
        if (cm, cn, cg) != (0, 1, 0) or rat(control['gain_at_zero']) != cg:
            errors.append('blind evaluation control')
        upper = value['upper_bound']
        # Integral h^2=1/3, finite Cauchy--Schwarz, Lip(h)=2.
        h2 = 2*Q(4, 3)*Q(1, 2)**3
        c = rat(upper['observable_distance_squared_constant'])
        lip = rat(upper['unit_ball_time_lipschitz_bound'])
        if rat(detector['test_l2_squared']) != h2 or c != 2*h2 or lip != 4:
            errors.append('uniform observable bounds')
        j, mesh = upper['modulus_index_shift'], upper['dyadic_mesh_index_shift']
        budget = Q(1, 2**j)+2*lip/Q(2**mesh)
        if (j, mesh) != (3, 5) or budget != rat(upper['pair_error_coefficient']) or not budget < 1:
            errors.append('upper-bound diagonal error budget')
        shift = upper['output_convergence_modulus_shift']
        if shift != j+2 or (1+Q(1, 2**j)+lip/Q(2**mesh))/4 > 1:
            errors.append('input-to-output uniform convergence budget')
        e = value['encoding']
        ratio = Q(1, e['radix'])
        if e['radix'] != 4 or e['weight_exponent_shift'] != 1:
            errors.append('encoding radix/exponent')
        if rat(e['total_weight']) != ratio/(1-ratio) or rat(e['tail_after_e_over_weight_e']) != ratio/(1-ratio):
            errors.append('geometric tail identity')
        if rat(e['output_evaluation_scale'])*gain != 1 or rat(e['output_evaluation_scale'])/2**e['output_evaluation_index_shift'] > 1:
            errors.append('output evaluation gain/index shift')
        for fixture in value['fixtures']:
            errors.extend(check_fixture(fixture))
    except (KeyError, ValueError, TypeError, ZeroDivisionError, AssertionError, OverflowError) as exc:
        errors.append('invalid exact witness: '+str(exc))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result', type=Path, default=RESULT)
    args = parser.parse_args()
    errors = verify(json.loads(args.result.read_text()))
    print('FOUNDATIONAL_CODED_WAVE_MODULUS_REVERSAL_V1: '+('FAIL' if errors else 'PASS'))
    if errors:
        for error in errors:
            print('  - '+error)
    else:
        print('  Independent rational response, encoding, error-budget, mutation-input and provenance audit.')
        print('  Infinite proof: HUMAN_PROOF, not kernel checked; no atlas/paper/quantum promotion.')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
