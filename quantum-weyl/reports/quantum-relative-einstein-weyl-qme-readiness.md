# Quantum relative Einstein--Weyl QME readiness

Generality level: `G0`.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`.

## Imported evidence

The strongest current compact Einstein--Maxwell to Weyl--Maxwell input is the
complete standard-harmonic tangent inclusion before final residual quotient.
It is exact on-shell and its classical pullback form is nondegenerate, but it
is not an off-shell BV chain map and is not symplectic block by block.  A
separate quadratic-channel preflight supplies partial relative obstruction
fixtures.

The new relative linear-triangle preflight is also imported from its pinned
commit. It certifies the principal BV chain map and cone and a strict
polynomial off-shell chain map, solution cofiber, and direct pairing in the
generic axial block. The polar, exceptional, and global all-sector rows and
global mapping cofiber remain open. The classical functor preflight confirms
that this evidence does not satisfy `EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1`.
All four source certificates are checked against pinned commits and hashes.

The quantum side imports the current local anomaly-to-(D) comparison and the
partial global Berger `A104` ledger.  The former has no Cartan verdict; the
latter has no full Cauchy BRST operator, pairing, or Hadamard state.

## Shared relative row

| Setting | Map \(\iota\) | Cofiber | Relative pairing | \(\mathfrak O_2\) | Residual action | Observable map | Quantum lift |
|---|---|---|---|---|---|---|---|
| Compact Einstein--Maxwell product; complete standard harmonic tangent; fixed compact bundle; before final residual quotient | principal and generic-axial off-shell preflight imported; global V1 open | generic-axial solution cofiber certified; global cofiber open | classical reduced-mode pullback only; not renormalized | partial quadratic fixtures; arity-three disposition open | relative equivariance open | relative pullback open | `ANALYTIC_FRAMEWORK_MISSING` |

The missing classical import gate consists of exactly:

```text
EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1
EINSTEIN_WEYL_RELATIVE_LINFINITY_THROUGH_ARITY_THREE
RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1
```

The quantum consumer will import these results by hash.  It will not
reconstruct their maps or cofiber independently.

## Relative anomaly contract

Only the future target is frozen:

\[
[\mathcal A_{\mathrm{rel}}]
=
[\mathcal A_{\mathrm{Weyl}}-\iota_*\mathcal A_{\mathrm{Einstein}}].
\]

This class is not yet defined.  It requires the off-shell map, separate local
QME dispositions, renormalized observable algebras and restriction, and
explicit antifield and boundary maps.  Bulk, antifield, boundary/corner,
zero-mode, measure/Jacobian, central-extension, and (D)-Cartan ledgers remain
separate.

## Verdict and claim boundary

The classical import gate remains `NOT_SATISFIED`; the partial triangle is
positive local evidence, not the required all-sector V1 result. The sole
quantum verdict is `ANALYTIC_FRAMEWORK_MISSING`. No relative anomaly,
restored QME, renormalized pairing, state restriction, (D)-Cartan verdict,
particle interpretation, or Lorentzian quantum theorem is claimed.  Residual
quantum transfer remains unauthorized.

## Verification

The certificate has a strict Draft 2020-12 schema, hash-bound source manifest,
independent pinned-commit replay, semantic input checks, fail-closed mutations,
and focused unit tests.

Tier-1 receipts on 2026-07-17: certificate check `PASS` in 0.06 s,
independent verifier `PASS` in 0.38 s, and eight focused tests `PASS` in 0.44 s.
The shared Draft 2020-12 validation rail passed for this and the coupled-q2
certificate in 0.12 s. Tier 2 was unnecessary because this change imports
unchanged content-addressed classical evidence and changes only the readiness
consumer. Tier 3 was not run because the full triangle gate remains unsatisfied
and no theorem, freeze, release, or lifecycle promotion occurred.
