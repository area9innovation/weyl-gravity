#!/usr/bin/env python3
"""Extract the actual order-zero metric observable lift; preserve old receipts."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = 'quantum-weyl/classical_import/certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json'
PAIRING = 'quantum-weyl/classical_import/certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json'
REFERENCE = 'quantum-weyl/lorentzian/certificates/VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD.json'
RECONCILED = 'foundations/inputs/tt-reduced-reference-reconciled-v1.json'
OUTPUT = ROOT / 'foundations/results/TT_OBSERVABLE_EXTENSION_V1.json'


def build():
    graph = json.loads((ROOT / GRAPH).read_text())
    p = graph['graph_sdr_component_maps']['p_end_graph']
    entries = []
    for c in p['coefficients']:
        selected = [e for e in c['entries'] if 5 <= e[0] < 15]
        if selected and any(c['multiindex']):
            raise ValueError('metric projection is no longer order zero')
        entries.extend(selected)
    sources = [GRAPH, PAIRING, REFERENCE, RECONCILED,
               'covariant_completion/certificates/curved_direct_causal_pairing_transport.json',
               'covariant_completion/certificates/curved_prolonged_current_comparison.json',
               'foundations/results/TT_HADAMARD_CUTOFF_OBSTRUCTION_V1.json']
    return {
        'result_id': 'TT_OBSERVABLE_EXTENSION_V1', 'schema_version': 1,
        'lifecycle': 'CONDITIONAL_RESEARCH_NOTE',
        'dependency_tags': ['LOCAL-ALGEBRAIC', 'REDUCED-MODE'],
        'source_commit': 'd79b0d04e460eaeec6e0b730da386699b16f1a7b',
        'inputs': [{'path': p, 'sha256': hashlib.sha256((ROOT / p).read_bytes()).hexdigest()} for p in sources],
        'metric_projection': {'shape': [10, 386], 'order': 0,
                              'row_convention': 'global metric indices 5..14; source indices 0..385',
                              'entries': entries},
        'advertised_projection_chain_witness': [[0, 1, 0, 0], 10, 233, '-1/2'],
        'gauge_factorization': {
            'zero_order_ghost_changes': [[0, 238, '-1/4'], [1, 232, '-1/4'], [2, 233, '-1/4'], [3, 234, '-1/4']],
            'Weyl_derivative_coefficients': [[axis, source, '1/16'] for axis, source in enumerate((238, 232, 233, 234))],
            'identity': 'p0 R386 = Rmetric Gamma', 'advertised_pghost_identity_defects': 28,
        },
        'observable_lift': 'F=p_0^T f in ordinary field/source dual coordinates; no Green operator or inverse frequency occurs',
        'reconciliation': {'legacy_reference': 'FAIL_STALE_HASH_PRESERVED',
                           'new_reference': RECONCILED,
                           'allowed_change': 'dependencies.causal_pairing_transport.sha256 only',
                           'scope': 'reduced reference import and oscillator replay; not a full classical freeze'},
        'claims': {'order_zero_compact_source_lift': True,
                   'coefficientwise_gauge_factorization': True,
                   'advertised_projection_gauge_chain_identity': False,
                   'conditional_positivity_transport_argument': True,
                   'full_strict_physical_positivity_decided': False,
                   'all_energy_TT_commutator_normalization_identified': False,
                   'quantum_lifecycle_promoted': False},
        'remaining_obligation': 'Identify p_0 Delta_386 p_0^T on every TT harmonic with the action-normalized E/L commutator, in ordinary field/source coordinates, including pairing/suspension signs.',
        'report': 'foundations/reports/tt-observable-extension-v1.md',
    }


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--check', action='store_true'); a = p.parse_args()
    text = json.dumps(build(), indent=2, sort_keys=True) + '\n'
    if a.check:
        if OUTPUT.read_text() != text: raise SystemExit('extension artifact drift')
        print('TT observable extension reproduction: PASS')
    else:
        OUTPUT.write_text(text)
