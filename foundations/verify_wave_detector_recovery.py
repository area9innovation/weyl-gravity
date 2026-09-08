#!/usr/bin/env python3
"""Independent rational polynomial and extremizer audit; imports no producer."""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT/'foundations/results/FOUNDATIONAL_WAVE_DETECTOR_RECOVERY_BENCHMARK_V1.json'
SOURCE = 'foundations/results/FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1.json'
REPORT = 'foundations/reports/wave-detector-recovery-benchmark-v1.md'


def digest(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def q(pair):
    if not isinstance(pair, list) or len(pair) != 2 or any(type(v) is not int for v in pair):
        raise ValueError('rational type')
    value = Q(*pair)
    if [value.numerator, value.denominator] != pair:
        raise ValueError('noncanonical rational')
    return value


def primitive_sum(cs, a, b):
    return sum((c*(b**(i+1)-a**(i+1))/Q(i+1) for i, c in enumerate(cs)), Q(0))


def tent_line(offset, midpoint):
    floor = (midpoint+offset).__floor__()
    phase = midpoint+offset-floor
    slope, intercept = (Q(2), Q(0)) if phase < Q(1, 2) else (Q(-2), Q(2))
    return [intercept+slope*(offset-floor), slope]


def initial_value(t, tau):
    points = sorted({t, t+tau, *(Q(i, 2) for i in range(5) if t < Q(i, 2) < t+tau)})
    return sum((primitive_sum(tent_line(0, (a+b)/2), a, b) for a, b in zip(points, points[1:])), Q(0))/tau-Q(1, 2)


def derivative_kernel(t, tau):
    cuts = sorted({Q(0), Q(1), *((c-t-d) % 1 for c in (Q(0), Q(1, 2)) for d in (Q(0), tau))})
    value = initial_value(t, tau)
    pieces = []
    for a, b in zip(cuts, cuts[1:]):
        plus, minus = tent_line(t+tau, (a+b)/2), tent_line(t, (a+b)/2)
        c1 = (plus[0]-minus[0])/tau
        c2 = (plus[1]-minus[1])/(2*tau)
        c0 = value-c1*a-c2*a*a
        cs = [c0, c1, c2]
        pieces.append((a, b, cs))
        value = c0+c1*b+c2*b*b
    if value != initial_value(t, tau):
        raise ValueError('periodicity')
    return pieces


def moments(pieces, n):
    integrals, norm, mean = [], Q(0), Q(0)
    for j in range(n):
        total = Q(0)
        for a, b, cs in pieces:
            a, b = max(a, Q(j, n)), min(b, Q(j+1, n))
            if a >= b:
                continue
            total += primitive_sum(cs, a, b)
        integrals.append(total)
    for a, b, cs in pieces:
        mean += primitive_sum(cs, a, b)
        # Independent direct double sum, not coefficient convolution.
        norm += sum((c*d*(b**(i+j+1)-a**(i+j+1))/Q(i+j+1)
                     for i, c in enumerate(cs) for j, d in enumerate(cs)), Q(0))
    return integrals, norm, mean


def check_case(row):
    errors = []
    n, t, tau = row['cells'], q(row['delay']), q(row['exposure'])
    if n not in (2, 4, 8, 16) or t not in (Q(0), Q(1, 8), Q(1, 4)) or tau != Q(1, 8):
        return ['case domain']
    pieces = derivative_kernel(t, tau)
    actual = [(q(r['interval'][0]), q(r['interval'][1]), list(map(q, r['coefficients']))) for r in row['kernel']]
    if actual != pieces:
        errors.append('independent adjoint kernel polynomial')
    ints, K, mean = moments(pieces, n)
    means = [n*x for x in ints]
    A = sum((n*x*x for x in ints), Q(0))
    B = K-A
    if mean != 0 or B <= 0 or A < 0:
        errors.append('mean-zero orthogonal decomposition')
    if list(map(q, row['kernel_cell_means'])) != means:
        errors.append('cell projection')
    if [q(row[k]) for k in ('kernel_norm_squared', 'projection_norm_squared', 'residual_norm_squared')] != [K, A, B]:
        errors.append('squared norm identity')
    exact = row['exact_nonzero_data']
    m = list(map(q, exact['cell_means']))
    if m != [Q((-1)**i, 2) for i in range(n)]:
        errors.append('exact observation fixture')
    E = sum((z*z/n for z in m), Q(0))
    center = sum((x*y for x, y in zip(m, ints)), Q(0))
    c2 = q(exact['extremizer_residual_coefficient_squared'])
    radius2 = q(exact['radius_squared'])
    if q(exact['source_energy_squared']) != E or q(exact['prediction_center']) != center:
        errors.append('exact-data center/energy')
    if c2 < 0 or E+c2*B != 1 or radius2 != c2*B*B or radius2 != (1-E)*B:
        errors.append('exact-data matching endpoint norm/response')
    if [q(r['eta']) for r in row['zero_reading_noisy_data']] != [Q(0), Q(1, 16), Q(1, 4), Q(1)]:
        errors.append('noise coverage')
    for noisy in row['zero_reading_noisy_data']:
        eta = q(noisy['eta'])
        cp2 = q(noisy['extremizer_projection_coefficient_squared'])
        cv2 = q(noisy['extremizer_residual_coefficient_squared'])
        terms = list(map(q, noisy['radius_sqrt_terms']))
        # Positive square roots of these coefficients specify the endpoint source.
        if min(cp2, cv2) < 0 or cp2*A+cv2*B != 1 or cp2*A > eta*eta:
            errors.append('noisy endpoint feasibility')
        u, w = terms
        gap = Q(1, 256)-u-w
        achievable = gap >= 0 and gap*gap >= 4*u*w
        if type(noisy['tolerance_one_sixteenth_achievable']) is not bool or noisy['tolerance_one_sixteenth_achievable'] != achievable:
            errors.append('finite accuracy decision')
        if terms != [cp2*A*A, cv2*B*B]:
            errors.append('noisy endpoint detector response')
        # Check upper-bound equality and maximizing region independently of producer formula.
        if eta*eta*K >= A:
            if noisy['branch'] != 'INACTIVE_NOISE_CONSTRAINT' or cp2 != cv2 or cv2*K != 1:
                errors.append('inactive constraint / full Cauchy-Schwarz equality')
        else:
            # r(s)=sqrt(A)*s+sqrt(B)*sqrt(1-s^2) increases up to s^2=A/K.
            if noisy['branch'] != 'ACTIVE_NOISE_CONSTRAINT' or cp2*A != eta*eta or not eta*eta*K < A:
                errors.append('active constraint / maximizing boundary')
    return errors


def verify(value=None):
    v = json.loads(RESULT.read_text()) if value is None else value
    errors = []
    expected_keys = {'schema_version','result_id','dependency_tags','evidence_status','created','source_commit','contract','cases',
                     'novelty_disposition','claim_flags','missing_objects','literature','provenance','human_report','content_sha256'}
    if set(v) != expected_keys:
        return ['strict top-level schema']
    if v['schema_version'] != 'wave-detector-recovery-benchmark-v1' or v['result_id'] != 'FOUNDATIONAL_WAVE_DETECTOR_RECOVERY_BENCHMARK_V1':
        errors.append('result schema/id')
    if v['dependency_tags'] != ['LOCAL-ALGEBRAIC','REDUCED-MODE'] or v['evidence_status'] != 'EXACT_BENCHMARK_WITH_HUMAN_OPTIMALITY_PROOF':
        errors.append('dependency/evidence boundary')
    if v['novelty_disposition'] != 'STANDARD_OPTIMAL_RECOVERY_SPECIALIZATION_RETAIN_AS_BENCHMARK':
        errors.append('novelty boundary')
    flags = {key: False for key in ('new_general_recovery_theorem','new_reverse_mathematics_equivalence','arbitrary_nonzero_noisy_data_solved',
             'laboratory_calibration_established','infinite_proof_kernel_checked','atlas_or_paper_promoted','new_lorentzian_claim','quantum_lifecycle_promoted')}
    flags.update(sharp_intervals_for_declared_cases=True, matching_sources_supplied=True)
    if v['claim_flags'] != flags:
        errors.append('claim boundary')
    if v['missing_objects'] != [
            'Physical calibration of source observations and detector.',
            'A nonstandard physical constraint or dynamics producing a new recovery result.',
            'Independent formal verification of the human infinite-dimensional proof.']:
        errors.append('missing-object ledger')
    if v['source_commit'] != '94d12eb369c8c2549bf0407a2d2f4feb6d2a49e3':
        errors.append('fixed source commit')
    literature = v['literature']
    if (literature['url'] != 'https://arxiv.org/abs/2111.02601'
            or literature['retrieved_pdf_sha256'] != 'c4d8cdf9b2da8eb31ea3e957ded8a070d1c8a24ffd84b3dfb6fe6f031e99c775'
            or literature['pdf_local_replay'] is not False):
        errors.append('literature provenance boundary')
    if v['content_sha256'] != digest({k:x for k,x in v.items() if k != 'content_sha256'}):
        errors.append('content digest')
    assets = [SOURCE, REPORT, 'foundations/build_wave_detector_recovery.py', 'foundations/verify_wave_detector_recovery.py', 'foundations/tests/test_wave_detector_recovery.py']
    if [a['path'] for a in v['provenance']] != assets or v['human_report'] != REPORT:
        errors.append('complete provenance')
    for asset in v['provenance']:
        if asset['path'] not in assets:
            continue
        if hashlib.sha256((ROOT/asset['path']).read_bytes()).hexdigest() != asset['sha256']:
            errors.append('source hash: '+asset['path'])
        if asset['source_commit'] != (v['source_commit'] if asset['path'] == SOURCE else None):
            errors.append('source commit provenance')
    source = json.loads((ROOT/SOURCE).read_text())['declared_observable']
    if source['test_breaks'] != [[0,1],[1,2],[1,1]] or source['test_values'] != [[0,1],[1,1],[0,1]]:
        errors.append('imported tent identity')
    expected_contract = {
        'state': 'Real mean-zero L2 right-moving chiral source a on the unit circle; b=0.',
        'energy_bound_squared': [1,1], 'spatial_detector': 'Imported periodic tent h; not a point detector.',
        'output': 'J(a) = exposure^(-1) integral_delay^(delay+exposure) integral_0^1 h(x) a(x-t) dx dt.',
        'exact_input': 'Exact means on equal cells, interpreted as observations of the actual source.',
        'noisy_input': 'Observed cell means all zero; (1/N) sum_j true_mean_j^2 <= eta^2.',
        'noise_type': 'Deterministic aggregate L2 bound; no stochastic or per-cell-independent noise claim.',
        'endpoint_domain': 'Algebraically named piecewise quadratic L2 sources; not restricted to rational step data.'}
    if v['contract'] != expected_contract:
        errors.append('observation contract')
    try:
        if [(r['cells'],q(r['delay'])) for r in v['cases']] != [(n,t) for n in (2,4,8,16) for t in (Q(0),Q(1,8),Q(1,4))]:
            errors.append('complete case inventory')
        for row in v['cases']:
            errors.extend(check_case(row))
    except (KeyError, TypeError, ValueError, ZeroDivisionError, IndexError) as exc:
        errors.append('malformed exact payload: '+str(exc))
    return errors


if __name__ == '__main__':
    errors = verify()
    print('FOUNDATIONAL_WAVE_DETECTOR_RECOVERY_BENCHMARK_V1: '+('FAIL' if errors else 'PASS'))
    for e in errors:
        print('  - '+e)
    raise SystemExit(bool(errors))
