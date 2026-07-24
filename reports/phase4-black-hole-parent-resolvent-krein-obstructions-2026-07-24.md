# Parent resolvent and Krein obstructions

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

## Exact results

On a gauge-fixed space where the linearized Einstein operator is invertible,
the auxiliary-tensor Hessian has the exact inverse

```text
H^-1 = (1/(4 alpha)) [
  [E^-1 A E^-1, E^-1],
  [E^-1,          0   ]
].
```

The rank-one Laurent algebra gives the candidate double coefficient
`(beta_parent/alpha_n^2) u_n tensor u_tilde_n`.  This becomes a physical QNM
pole theorem only after the analytic Fredholm and bounded-insertion
hypotheses are established.

The categorical involution result is exact for a nonsplit self-extension of
a simple object in characteristic zero.  Its unconditional application to
the Bach spin-two module still requires generic simplicity of the
Regge--Wheeler differential module or an equivalent endomorphism-ring
certificate.  The earlier branch-resolving no-go remains unconditional.

The endpoint hyperbolic plane gives:

- no uniformly positive closed subspace containing the Einstein channel;
- the canonical quotient duality `B_2/E ≅ E*`;
- a clear separation between endpoint Krein diagonalization and local
  dynamical splitting.

## New experiment rails

1. Compute the regularized parent overlap `<f_tilde,A f>` at the certified
   physical QNM and compare it with the normalized radial extension overlap,
   including endpoint and commutator terms.
2. Compare direct six-state evolution with sequential Einstein evolution
   implementing `G_E^ret A G_E^ret`; use the Minkowski biwave kernel as the
   first control.

## Verification

```bash
python3 black_hole_programme/phase4/parent_resolvent_krein_obstructions_v1/produce.py
python3 black_hole_programme/phase4/parent_resolvent_krein_obstructions_v1/verify.py
python3 -m unittest -v \
  black_hole_programme/phase4/parent_resolvent_krein_obstructions_v1/test_resolvent.py
```

Higher tiers are not triggered: this package adds isolated exact algebra and
experiment specifications while importing content-addressed operator and
QNM certificates.

CLOSE-OUT: DONE — exact parent-resolvent algebra, the simple-extension
involution lemma, endpoint Krein obstructions, and both experiment
specifications are certified; physical Fredholm, generic Regge--Wheeler
simplicity, and Schwarzschild time-domain promotions remain fail-closed.

EVIDENCE: black_hole_programme/phase4/parent_resolvent_krein_obstructions_v1/certificate.json
