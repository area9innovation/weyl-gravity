# Lorentzian Weyl BV completion atlas V7

## Outcome

Yes. Atlas V7 imports an explicit hybrid Gate basis with 386 unique component rows: thirty Gate-canonical endpoint rows, thirty-six ordered generalized-auxiliary doublet rows and all 320 split curvature mapping-cylinder cone/cotangent rows. The algebraic complement is therefore concretely 356=36+320 rather than only a projector rank. The odd pairing is a complete exact rational table with 410 ordered nonzero entries and rank 386: 30 endpoint, 60 auxiliary-complement and 320 cone-complement entries. Every entry has total degree one and the reverse coefficient is its negative. The full T, T^sharp_G and R diagonals are serialized on those same row indices; T^T Omega=Omega T^sharp_G and R=T^sharp_G T replay componentwise with the certified 381/5, 381/5 and 376/10 sign counts. V7 also corrects a coordinate label: the earlier count 54 describes the endpoint DeWitt/ghost pairing before Gate pullback, whereas the Gate-coordinate endpoint pairing has 30 entries; the suspension algebra is unchanged. Gate A remains fail closed because the full prolonged q1, H_alg, endpoint inclusion/projection and advanced/retarded Green operator coefficient tables are still represented by formal block identities and hashes rather than one portable component snapshot. Thus not every component operator adjoint or homotopy identity has been independently replayed. Local D, q2, Hadamard, Ward, positivity, renormalized products, QME and residual transfer remain open.

## Component carrier result

- Rows: **386 = 30 + 356=36+320**.
- Odd pairing: **410 ordered rational entries**, exact rank **386**.
- Endpoint pairing counts: **30** in Gate coordinates; **54** before pullback.
- Componentwise `T` pairing adjoint: **replayed**; every q1/projector/Green operator adjoint: **open**.

## Updated route selection

| rank | route | leverage | tractability | dependency depth |
|---:|---|---|---|---|
| 1 | `STRICT_386_OPERATOR_COMPONENT_SERIALIZATION` | VERY_HIGH | MEDIUM | LOW |
| 2 | `STRICT_386_LOCAL_D` | VERY_HIGH | LOW | MEDIUM |
| 3 | `STRICT_386_Q2_GREEN_COMPATIBILITY` | HIGH | LOW | HIGH |
| 4 | `DIRECT_SPACETIME_Q26_HADAMARD` | VERY_HIGH | LOW | MEDIUM |
| 5 | `BACH_FLAT_NONLINEAR_CARTAN` | HIGH | MEDIUM | MEDIUM |

## Reproduction

```text
python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v7.py --check
python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v7.py
python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v7.py
python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v7.py
```

## Boundaries

- This does not establish a passed strict pure-Weyl classical import gate.
- This does not establish a no-go theorem for every nonstationary Krein Hadamard representative.
- This does not establish a no-go theorem for the complete general non-cone 104-row completion class.
- This does not establish a no-finite-carrier theorem or a global lower bound above 104 added free rows.
- This does not establish that non-free or projective carrier extensions obey the free-module lower bound.
- This does not establish a normalized Berger H26_plus or serialized C26.
- This does not establish a BRST-compatible Hadamard state on a complete off-shell carrier.
- This does not establish physical positivity, particles, scattering or unitarity.
- This does not establish renormalized Lorentzian time-ordered products.
- This does not establish a Lorentzian QME theorem or residual quantum transfer.
- This does not establish equivalence between strict pure Weyl and the positive-clock Berger theory.
- This does not establish that a numerical route rank is a theorem or proof of eventual success.
- This does not establish that the finite D x SO(4) residual contraction is an arbitrary-support or causal Green homotopy.
- This does not establish that zero missing serialized objects means the common full-carrier Gate A has passed.
- This does not establish that the PRA classification of the finite sign wrapper calibrates the imported analytic causal theorem.
- This does not establish compatibility of strict q2 or D with the transported 386-row Green homotopy.
- This does not establish that convention stability is a passed Gate A, Hadamard state or Lorentzian quantum completion.
- This does not establish q2 or local D compatibility on the common causal bytes.
- This does not establish a passed Gate A, Hadamard state, Ward theorem, QME restoration, residual transfer or Lorentzian quantum theory.
- This does not establish local D or q2 compatibility on the common causal carrier.
- This does not establish portable full prolonged q1, H_alg, endpoint inclusion/projection or Green operator component tables.
- This does not establish an independent component-by-component replay of every operator adjoint and homotopy identity.
- This does not establish one accepted common Gate-A operator hash, local D, q2, Hadamard, QME or Lorentzian quantum theory.
