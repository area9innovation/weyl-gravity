# Compact-product residual atlas v1

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The generated ledger at
`bridge/einstein_sector/atlas/einstein-compact-product-atlas-fragment.json`
seeds the common residual-atlas schema with eight stable entries for the
compactified magnetically supported Plebański--Hacyan fixture.  Each entry
carries the complete scope

```text
(theory, background, boundaries, charge sector, carrier,
 degree, parity, ell, m, k, omega)
```

and separate causal, symplectic, nonlinear, observational and quantum
statuses.  Dispersion, Lee--Wald, Taub, resonance and second-order fields are
content-addressed to their source certificates.

The second-order equation is uniformly typed as

\[
L_{\bar\Phi}v=-\frac12D^2E_{\bar\Phi}[u,u].
\]

Its verdict is never shared silently between bounded/finite-quasiperiodic,
smooth-secular and causal/retarded correction classes.  In particular:

- generic pure-extra modes are linearly nonradical but fixed-bundle
  Taub-obstructed;
- one balanced Einstein--extra `ell=2,k=0` tangent has a complete bounded
  second-order correction;
- the twist-balanced exceptional fixture is the independence witness
  `mu_X(u)=0` with `R_bounded(u)!=0`;
- the new `d`-cross axial matrix has a certified cancellable resonant
  projection but remains `OPEN` as a full nonlinear extension;
- every compact-product causal/retarded verdict remains `OPEN`;
- the crosswalk to asymptotic or vacuum-cylinder modes is
  `NO_CERTIFIED_MAP`.

The shared schema is
`residual_atlas/schema/residual-atlas-fragment-v1.schema.json`.  It requires
the exact field name `ell`, not a carrier-specific alias, and the five-value
fail-closed vocabulary.  Other teams can validate generated fragments with
`residual_atlas/validate_fragment.py`.
