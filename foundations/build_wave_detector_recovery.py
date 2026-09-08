#!/usr/bin/env python3
"""Exact finite-source recovery benchmark; an application of optimal recovery."""
from fractions import Fraction as Q
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'foundations/results/FOUNDATIONAL_WAVE_DETECTOR_RECOVERY_BENCHMARK_V1.json'
REPORT = 'foundations/reports/wave-detector-recovery-benchmark-v1.md'
SOURCE = 'foundations/results/FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1.json'
BASE = '94d12eb3'  # Resolved full source commit in the emitted provenance.
TAU = Q(1, 8)


def enc(x):
    x = Q(x)
    return [x.numerator, x.denominator]


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def tent_primitive(x):
    n = x.__floor__()
    z = x-n
    return Q(n, 2)+(z*z if z <= Q(1, 2) else 2*z-z*z-Q(1, 2))


def kernel_value(x, delay):
    return (tent_primitive(x+delay+TAU)-tent_primitive(x+delay))/TAU-Q(1, 2)


def kernel(delay):
    breaks = sorted({Q(0), Q(1), *((v-delay-shift) % 1 for v in (Q(0), Q(1, 2)) for shift in (Q(0), TAU))})
    rows = []
    for a, b in zip(breaks, breaks[1:]):
        m = (a+b)/2
        ya, ym, yb = [kernel_value(x, delay) for x in (a, m, b)]
        c2 = ((yb-ym)/(b-m)-(ym-ya)/(m-a))/(b-a)
        c1 = (ym-ya)/(m-a)-c2*(a+m)
        c0 = ya-c1*a-c2*a*a
        rows.append((a, b, [c0, c1, c2]))
    return rows


def integrate(rows, left=Q(0), right=Q(1), square=False):
    total = Q(0)
    for a, b, cs in rows:
        a, b = max(a, left), min(b, right)
        if b <= a:
            continue
        if square:
            squared = [Q(0)]*(2*len(cs)-1)
            for i, c in enumerate(cs):
                for j, d in enumerate(cs):
                    squared[i+j] += c*d
            cs = squared
        total += sum((c*(b**(i+1)-a**(i+1))/(i+1) for i, c in enumerate(cs)), Q(0))
    return total


def case(delay, cells):
    rows = kernel(delay)
    K = integrate(rows, square=True)
    means = [cells*integrate(rows, Q(i, cells), Q(i+1, cells)) for i in range(cells)]
    A = sum((x*x/cells for x in means), Q(0))
    B = K-A
    noisy = []
    for eta in (Q(0), Q(1, 16), Q(1, 4), Q(1)):
        if eta*eta*K >= A:
            branch = 'INACTIVE_NOISE_CONSTRAINT'
            cp2 = cv2 = 1/K
        else:
            branch = 'ACTIVE_NOISE_CONSTRAINT'
            cp2 = eta*eta/A
            cv2 = (1-eta*eta)/B
        u, v = cp2*A*A, cv2*B*B
        margin = Q(1, 256)-u-v
        noisy.append({'eta': enc(eta), 'branch': branch,
                      'tolerance_one_sixteenth_achievable': margin >= 0 and margin*margin >= 4*u*v,
                      'extremizer_projection_coefficient_squared': enc(cp2),
                      'extremizer_residual_coefficient_squared': enc(cv2),
                      'radius_sqrt_terms': [enc(cp2*A*A), enc(cv2*B*B)]})
    # A nonzero exactly measured source, piecewise constant with mean zero.
    m = [Q((-1)**i, 2) for i in range(cells)]
    energy = sum((x*x/cells for x in m), Q(0))
    center = sum((x*y/cells for x, y in zip(m, means)), Q(0))
    return {'cells': cells, 'delay': enc(delay), 'exposure': enc(TAU),
            'kernel': [{'interval': [enc(a), enc(b)], 'coefficients': [enc(c) for c in cs]} for a, b, cs in rows],
            'kernel_cell_means': [enc(x) for x in means],
            'kernel_norm_squared': enc(K), 'projection_norm_squared': enc(A), 'residual_norm_squared': enc(B),
            'exact_nonzero_data': {'cell_means': [enc(x) for x in m], 'source_energy_squared': enc(energy),
                                   'prediction_center': enc(center), 'radius_squared': enc((1-energy)*B),
                                   'extremizer_residual_coefficient_squared': enc((1-energy)/B)},
            'zero_reading_noisy_data': noisy}


def build():
    # Pin source tree, proof and both independent computational rails.
    import subprocess
    base = subprocess.check_output(['git', 'rev-parse', BASE], cwd=ROOT, text=True).strip()
    paths = [SOURCE, REPORT, 'foundations/build_wave_detector_recovery.py',
             'foundations/verify_wave_detector_recovery.py', 'foundations/tests/test_wave_detector_recovery.py']
    value = {
        'schema_version': 'wave-detector-recovery-benchmark-v1',
        'result_id': 'FOUNDATIONAL_WAVE_DETECTOR_RECOVERY_BENCHMARK_V1',
        'dependency_tags': ['LOCAL-ALGEBRAIC', 'REDUCED-MODE'],
        'evidence_status': 'EXACT_BENCHMARK_WITH_HUMAN_OPTIMALITY_PROOF',
        'created': '2026-09-08', 'source_commit': base,
        'contract': {'state': 'Real mean-zero L2 right-moving chiral source a on the unit circle; b=0.',
                     'energy_bound_squared': [1, 1], 'spatial_detector': 'Imported periodic tent h; not a point detector.',
                     'output': 'J(a) = exposure^(-1) integral_delay^(delay+exposure) integral_0^1 h(x) a(x-t) dx dt.',
                     'exact_input': 'Exact means on equal cells, interpreted as observations of the actual source.',
                     'noisy_input': 'Observed cell means all zero; (1/N) sum_j true_mean_j^2 <= eta^2.',
                     'noise_type': 'Deterministic aggregate L2 bound; no stochastic or per-cell-independent noise claim.',
                     'endpoint_domain': 'Algebraically named piecewise quadratic L2 sources; not restricted to rational step data.'},
        'cases': [case(t, n) for n in (2, 4, 8, 16) for t in (Q(0), Q(1, 8), Q(1, 4))],
        'novelty_disposition': 'STANDARD_OPTIMAL_RECOVERY_SPECIALIZATION_RETAIN_AS_BENCHMARK',
        'claim_flags': {'sharp_intervals_for_declared_cases': True, 'matching_sources_supplied': True,
                        'new_general_recovery_theorem': False, 'new_reverse_mathematics_equivalence': False,
                        'arbitrary_nonzero_noisy_data_solved': False, 'laboratory_calibration_established': False,
                        'infinite_proof_kernel_checked': False, 'atlas_or_paper_promoted': False,
                        'new_lorentzian_claim': False, 'quantum_lifecycle_promoted': False},
        'missing_objects': ['Physical calibration of source observations and detector.',
                            'A nonstandard physical constraint or dynamics producing a new recovery result.',
                            'Independent formal verification of the human infinite-dimensional proof.'],
        'literature': {'url': 'https://arxiv.org/abs/2111.02601',
                       'citation': 'Simon Foucart and Chunyang Liao, Optimal Recovery from Inaccurate Data in Hilbert Spaces: Regularize, but what of the Parameter? (2021).',
                       'scope': 'Existing optimal-recovery framework; the benchmark uses elementary Hilbert projection and Cauchy-Schwarz.',
                       'retrieved_pdf_sha256': 'c4d8cdf9b2da8eb31ea3e957ded8a070d1c8a24ffd84b3dfb6fe6f031e99c775', 'pdf_local_replay': False},
        'provenance': [{'path': p, 'sha256': sha(p), 'source_commit': base if p == SOURCE else None} for p in paths],
        'human_report': REPORT}
    value['content_sha256'] = digest(value)
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    data = json.dumps(build(), indent=2)+'\n'
    if args.check:
        ok = OUT.exists() and OUT.read_text() == data
        print('Wave detector recovery deterministic artifact: '+('PASS' if ok else 'FAIL'))
        return 0 if ok else 1
    OUT.write_text(data)
    print(OUT.relative_to(ROOT))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
