# Product \(S^2\times S^2\) minimal-vector determinant precertificate

**Dependency tag:** `EUCLIDEAN-SPECTRAL`.

The two active scalar product-zeta carriers have now been evaluated with the
exceptional exact rows removed and the coexact Killing zeros primed. Their
one-polarization weighted modified determinants satisfy

```text
4.6464224421... < first-factor block  < 4.6464226170...
9.6379155127... < second-factor block < 9.6379169068...
```

Including exact and coexact polarizations gives

```text
28.5686759097... < minimal-vector weighted log < 28.5686790475...
18.5686759097... < minimal-vector zeta log     < 18.5686790475...
```

The difference is exactly `-10`, the previously certified local
zeta-to-weighted defect. Combining the selected weighted prescription with
the matched Schur factor yields

```text
19.0791598956... < full vector-plus-Schur weighted log
                    < 19.0791630891...
```

The proof uses the order-18 product-heat Euler--Maclaurin enclosure for the
finite parts at `s=1,2`. The active restrictions reduce to the full product
zeta minus elementary sphere rows:

```text
FP zeta_S2(1) = 2 EulerGamma - 1
zeta_S2(2)    = 1
zeta_(2 Delta)(s) = 2^-s zeta_Delta(s).
```

Each `det3` is split at `|J|=1/100`: finitely many large modes use exact
order-120 rational Taylor intervals, while 5.76 million small modes use a
positive order-eight sum with explicit `gamma_N` bounds. A rational exterior
lattice estimate controls the infinite rectangle. That exterior estimate,
not heat or floating-point error, dominates the final `3.2e-6` width.
Every interval endpoint is converted from its exact binary MPF rational with
decimal floor/ceiling rounding, so serialization cannot shrink the directed
enclosure.

This remains a precertificate because the inherited 830-test Tier-3
promotion run failed on stale receipts outside this package. It is also a
special-background determinant, not the remaining full BV ledger or a
generic-background form factor. All QME, Lorentzian and Hadamard promotions
remain false.

Receipts:

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.product_s2_s2_ghost_minimal_vector_determinant_precertificate --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_product_s2_s2_ghost_minimal_vector_determinant_precertificate
PYTHONPATH=quantum-weyl python3 -m unittest \
  quantum-weyl/spectral/euclidean/tests/test_product_s2_s2_ghost_minimal_vector_determinant_precertificate.py
```

Tier 3 is not rerun by this fail-closed dependent calculation. The focused
producer check passed in `30.0 s`, the independent verifier in `0.2 s`, and
the six scoped tests in about `29.7 s`. The strict nested schema, exact dependency
hashes and directed-interval identities are part of the affected chain.
