# Alpha_B=3 Ostrogradsky canonical crosswalk close-out

The canonical bridge is complete for the stored balanced second-order
correction.  The selected action is exactly

```text
S_WM = integral sqrt(-g) [(3/8) C_abcd C^abcd - F_ab F^ab/4].
```

Relative to the standard `-C^2/4` canonical normalization its scale is
`-3/2`.  With the no-time-integration-by-parts ADM convention this fixes

```text
P^ij = -3 sqrt(h) C^(i n j n),
P0^ij = sqrt(h) diag(1,-1/2,-1/2)
```

in an orthonormal product frame.  The selected gravitational Hamiltonian
constraint therefore contains `+P_ij P^ij/(3 sqrt(h))`, not the rank-only
`-P_ij P^ij/(2 sqrt(h))` normalization.  The earlier one-slot ambiguity is
removed: its cubic coefficient is `-s^2/48`.

The producer derives `delta h`, `delta K`, `delta P`, `delta a` and `delta E`
directly from the four-dimensional fields.  It reconstructs `delta pi` from
the selected `P` Hamilton equation, including the exact Euler derivative of
the magnetic-Weyl term.  Both linear conformal primary constraints vanish
identically for the homogeneous, ell=2 and ell=4 templates.  The inverse map
is explicit on the stored representatives and has no physical-fibre
denominator at lambda 6 or 20.

Every actual correction is substituted.  The resulting ledger contains 27
signed rows: four nonzero-frequency pairs plus one real zero row in each of
the homogeneous, ell=2 and ell=4 blocks.  Reality, harmonic normalization,
time derivatives and the fact that every stored generic correction has
`B=0` are explicit.

The independent verifier does not import the producer.  It recomputes the
action scale and cubic coefficient, both primary constraints, the generic
inverse formula and the signed-channel census.  Eight tests reject rescaled
background momentum, zeroed `pi`, omitted channels, a nonzero omitted shift,
a boundary-term mutation and a competing action scale.

This result activates regeneration of the action-normalized `D3C` and mixed
`D2C[u,v]` tensors.  It does not evaluate the cubic Kuranishi class itself.

EVIDENCE: `bridge/certificates/EINSTEIN_WEYL_ALPHA_B3_OSTROGRADSKY_CANONICAL_CROSSWALK_V1.json`; `bridge/einstein_sector/receipts/EINSTEIN_WEYL_ALPHA_B3_OSTROGRADSKY_CANONICAL_CROSSWALK_V1_TIER_RECEIPT.json`; `residual_atlas/einstein-weyl-alpha-b3-ostrogradsky-canonical-crosswalk-fragment-v1.json`

CLOSE-OUT: DONE — the selected action now has an exact canonical convention, background momentum, invertible ell=0,2,4 correction lift and complete 27-row signed ledger.
