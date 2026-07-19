# Compact-product residual atlas v1

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The generated ledger at
`bridge/einstein_sector/atlas/einstein-compact-product-atlas-fragment.json`
seeds the common residual-atlas schema with stable entries for the
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
- the completed `d`-cross axial-plus-polar matrix has certified cancellable
  resonant projections in both parities but remains `OPEN` as a full
  nonlinear extension;
- the complete declared one-fibre shared-axis global--extra orbit is
  `OBSTRUCTED` for bounded/finite-quasiperiodic corrections but `CERTIFIED`
  for smooth exponential-polynomial corrections, with coefficient-explicit
  global/global, all sixteen twist--extra, and all twenty `C^4` extra/extra
  bilinear generators;
- the complete finite generic `ell>=2` carrier, including arbitrary finite
  momentum fibres and relative phases, has smooth-secular tangent cone
  `mu_H=mu_Px=mu_J1=mu_J2=mu_J3=0`; its bounded resonant-functional formula
  is certified but its coefficientwise zero locus remains `OPEN`;
- every compact-product causal/retarded verdict remains `OPEN`;
- the crosswalk to asymptotic or vacuum-cylinder modes is
  `NO_CERTIFIED_MAP`.

The shared schema is
`residual_atlas/schema/residual-atlas-fragment-v1.schema.json`.  It requires
the exact field name `ell`, not a carrier-specific alias, and the five-value
fail-closed vocabulary.  Other teams can validate generated fragments with
`residual_atlas/validate_fragment.py`.
