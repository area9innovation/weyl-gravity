# Parity-odd third-curvature carrier manifest preflight

## Disposition

The complete derivative-decorated parity-odd carrier quotient is not yet
computable from the repository's exact inputs. The first missing operation is:

```text
EXACT_SINGLE_EPSILON_LABELLED_JET_SYZYGY_QUOTIENT
```

This is an exact invariant-generation shortfall, not evidence that the odd
sector vanishes.

The existing stack proves two useful endpoints:

- one nonzero zero-derivative parity-odd \(C^3\) anchor exists;
- the parity-even nonlocal scalar-flat quotient has eleven raw and ten
  effective labelled channels.

Neither endpoint determines the derivative-decorated odd module. In
particular, inserting one Hodge dual into the five even carrier labels is not
a completeness proof because derivative placement, arbitrary analytic
functions of the labelled \(\Box_i\), integration by parts and
four-dimensional epsilon identities need not preserve the even quotient
presentation.

## Exact capability audit

The current single-epsilon contraction engine stops below the required
degree-six module. Its certificate explicitly records that degree-five/six
intrinsic orbits are factored only. The available local four-dimensional
Schouten quotient is parity even. The Schouten-zero Weyl image constructs one
odd Hodge companion but explicitly labels it `CONSTRUCTED_NOT_A_COMPLETE_BASIS`.

The missing exact operation must form the module of degree-six contractions
of three labelled Weyl or \(K\) jets and one epsilon over
\(\mathbb Q[\Box_1,\Box_2,\Box_3]\), then quotient simultaneously by:

1. algebraic and differential Bianchi identities;
2. curvature-order-three covariant-jet commutators;
3. integration by parts without commuting through labelled form factors;
4. four-dimensional five-index Schouten identities with one epsilon;
5. locally exact Pontryagin/transgression directions.

It must retain the source-label \(S_3\) action and emit canonical normal
forms, exact syzygies, stabilizers, quotient rank and dual nonmembership
witnesses.

The typed generic-math request is:

```text
sf:forge-request/single-epsilon-labelled-jet-syzygy-quotient
planning/forge-requests/single-epsilon-labelled-jet-syzygy-quotient.json
```

## Result boundary

The machine result is `OBSTRUCTED`, tagged `LOCAL-ALGEBRAIC` and
`EUCLIDEAN-SPECTRAL`. It does not emit canonical odd representatives,
stabilizers, functional relations or a quotient dimension. No sampling was
used, and no even-basis dualization was promoted.

This preflight does not compute a form-factor coefficient, identify every
nonlocal odd carrier with the local Pontryagin class, complete
\(\Gamma_1\) or \(Q_1\), restore a QME, authorize residual transfer or
establish a Lorentzian, Hadamard, positivity, particle, scattering or
unitarity result.

## Replay

```text
PYTHONPATH=quantum-weyl python3 -m transfer.parity_odd_third_curvature_preflight --check
PYTHONPATH=quantum-weyl python3 -m transfer.verify_parity_odd_third_curvature_preflight
PYTHONPATH=quantum-weyl python3 -m unittest \
  transfer.tests.test_parity_odd_third_curvature_preflight -v
```

EVIDENCE:
`quantum-weyl/transfer/certificates/PARITY_ODD_THIRD_CURVATURE_CARRIER_MANIFEST_PREFLIGHT.json`

CLOSE-OUT: OBSTRUCTED — the first exact invariant-generation operation is
named and requested; no incomplete carrier list is promoted.
