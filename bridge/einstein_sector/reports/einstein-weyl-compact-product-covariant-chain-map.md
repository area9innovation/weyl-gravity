# Compact-product covariant Einstein--Weyl chain map

The formerly separate harmonic coefficient maps are the reductions of one
natural support-local four-dimensional chain morphism.  Its equation row is
the universal Bach-from-Einstein operator plus a parallel algebraic product
correction and a first-order Maxwell commutator.  The induced identity map is
unique in the declared invariant class.  No inverse Laplacian, curl,
frequency, momentum or harmonic projector is used.

Writing (L,S) for the two parallel factor projectors, (J_L,J_S) for their
oriented mixed-index volume forms, (B(A,B;X)) for their symmetrized action
on a symmetric tensor, and (P(E)) for the universal principal
Bach-from-Einstein operator, the equation map is

\[
\begin{split}
W={}&3P(E)+\operatorname{TF}\bigl[
\tfrac32B(L,L;E)-B(L,S;E)-\tfrac52B(S,S;E)\\
&\quad-\tfrac12B(J_L,J_L;E)+\tfrac52B(J_S,J_S;E)
+3B(I,J_S;\nabla M)-3B(J_S,I;\nabla M)\bigr].
\end{split}
\]

The Maxwell equation maps identically.  If
(I_b=\nabla^aE_{ab}+\bar F_{bc}M^c) and (J=\nabla_aM^a), the unique identity
row in the declared invariant class is

\[
I'_b=\tfrac32\Box I_b+(L_b{}^c-\tfrac12S_b{}^c)I_c
-\tfrac32(J_S)_b{}^c\nabla_cJ,
\qquad J'=J,
\]

with zero image in the new Weyl trace identity.

The exact symbolic replay covers both parities at three independent spherical
eigenvalues, retains arbitrary off-shell frequency and compact momentum, and
globalizes by the degree-two natural-operator bound and SO(3) equivariance.

This closes the local covariant-glue gate, not the entire relative triangle.
The standard action pairings remain noncyclic by the separately certified
inertia obstruction.  Finite residual and large-gauge endpoint rows and the
three distinct Einstein/pulled-back-Weyl/relative forms remain the next gate.

The strict certificate is
`bridge/certificates/EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1.json`.
Its heavy proof records the complete 41-parameter oriented invariant solve,
the unique nine-parameter identity solve, and six exact action-row replays
(both parities at three independent spherical eigenvalues).  The independent
consumer does not import the producer and rechecks the schema, content hashes,
coefficient vectors, replay coverage, support claim and fail-closed boundary.
The timed test-tier receipt is
`bridge/einstein_sector/receipts/einstein-weyl-compact-product-covariant-chain-map-v1.json`.

Reproduction commands:

```text
PYTHONPATH=. python3 -m bridge.einstein_sector.einstein_weyl_compact_product_covariant_chain_map --verify-proof
PYTHONPATH=. python3 -m bridge.einstein_sector.einstein_weyl_compact_product_covariant_chain_map --verify bridge/certificates/EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1.json
PYTHONPATH=. python3 bridge/einstein_sector/verify_einstein_weyl_compact_product_covariant_chain_map.py
PYTHONPATH=. python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_compact_product_covariant_chain_map -v
```
