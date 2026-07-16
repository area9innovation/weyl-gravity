# Cross-programme \(D\)-quotient validation dossier

This directory consolidates the four investigations of whether cylinder time
translation/dilatation may be quotiented as gauge.  It is a validation dossier,
not yet Paper IX.

The dossier never assigns one universal Boolean to \(D\).  Every claim is
keyed by

```text
(generator, phase space, boundary conditions, lifecycle layer)
```

because the existing results concern different objects:

- the classical compact-cylinder charge and Taub-zero reduction;
- the real asymptotic generator dictionary and boundary-preservation gate;
- nonlinear homological transfer and interacting Cartan stability;
- the renormalized quantum Ward/QME obstruction.

The cross-team dependency order from these certificates to clocks/redshift,
waves, particles, black holes, galaxy phenomenology, and cosmology is recorded
in [`../notes/universe-building-roadmap.md`](../notes/universe-building-roadmap.md).
It also defines the triggers for moving capacity between teams; it does not
change the verdict or lifecycle rules in this dossier.

## Authoritative artifacts

- [`certificates/D_QUOTIENT_PROGRAMME_STATUS.json`](certificates/D_QUOTIENT_PROGRAMME_STATUS.json)
- [`reports/consolidated-status.md`](reports/consolidated-status.md)
- [`registry/generators.json`](registry/generators.json)
- [`registry/phase_spaces.json`](registry/phase_spaces.json)
- [`schema/programme-status-v1.schema.json`](schema/programme-status-v1.schema.json)
- [`schema/team-contribution-v1.schema.json`](schema/team-contribution-v1.schema.json)
- [`contributions/`](contributions/)
- [`reports/classical-scalar-clock-registration-receipt.md`](reports/classical-scalar-clock-registration-receipt.md)
- [`reports/classical-neutral-clock-registration-receipt.md`](reports/classical-neutral-clock-registration-receipt.md)
- [`reports/classical-neutral-clock-health-registration-receipt.md`](reports/classical-neutral-clock-health-registration-receipt.md)
- [`reports/classical-homogeneous-stealth-registration-receipt.md`](reports/classical-homogeneous-stealth-registration-receipt.md)
- [`reports/classical-standard-stealth-no-go-registration-receipt.md`](reports/classical-standard-stealth-no-go-registration-receipt.md)
- [`contributions/classical-positive-berger-clock-background.json`](contributions/classical-positive-berger-clock-background.json)
- [`contributions/classical-berger-clock-charge-seed.json`](contributions/classical-berger-clock-charge-seed.json)
- [`contributions/classical-berger-fixed-coupling-delta-charge.json`](contributions/classical-berger-fixed-coupling-delta-charge.json)
- [`contributions/classical-berger-minimal-bv-clock-sdr.json`](contributions/classical-berger-minimal-bv-clock-sdr.json)
- [`contributions/classical-berger-retained-minimal-layout.json`](contributions/classical-berger-retained-minimal-layout.json)
- [`reports/classical-positive-berger-clock-registration-receipt.md`](reports/classical-positive-berger-clock-registration-receipt.md)
- [`reports/classical-berger-clock-charge-seed-registration-receipt.md`](reports/classical-berger-clock-charge-seed-registration-receipt.md)
- [`reports/classical-berger-fixed-coupling-registration-receipt.md`](reports/classical-berger-fixed-coupling-registration-receipt.md)
- [`reports/classical-berger-minimal-bv-sdr-registration-receipt.md`](reports/classical-berger-minimal-bv-sdr-registration-receipt.md)
- [`reports/classical-berger-retained-layout-registration-receipt.md`](reports/classical-berger-retained-layout-registration-receipt.md)
- [`reports/einstein-ed1a-registration-receipt.md`](reports/einstein-ed1a-registration-receipt.md)
- [`contributions/einstein-berger-incidence.json`](contributions/einstein-berger-incidence.json)
- [`reports/einstein-berger-incidence-registration-receipt.md`](reports/einstein-berger-incidence-registration-receipt.md)
- [`contributions/einstein-maxwell-product-incidence.json`](contributions/einstein-maxwell-product-incidence.json)
- [`reports/einstein-maxwell-product-registration-receipt.md`](reports/einstein-maxwell-product-registration-receipt.md)
- [`contributions/einstein-maxwell-product-tangent-preflight.json`](contributions/einstein-maxwell-product-tangent-preflight.json)
- [`reports/einstein-maxwell-product-tangent-registration-receipt.md`](reports/einstein-maxwell-product-tangent-registration-receipt.md)
- [`contributions/einstein-maxwell-chevreton-tangent.json`](contributions/einstein-maxwell-chevreton-tangent.json)
- [`reports/einstein-maxwell-chevreton-tangent-registration-receipt.md`](reports/einstein-maxwell-chevreton-tangent-registration-receipt.md)
- [`contributions/einstein-maxwell-second-order-fixed-flux.json`](contributions/einstein-maxwell-second-order-fixed-flux.json)
- [`contributions/einstein-maxwell-second-order-null-extension.json`](contributions/einstein-maxwell-second-order-null-extension.json)
- [`reports/einstein-maxwell-second-order-registration-receipt.md`](reports/einstein-maxwell-second-order-registration-receipt.md)
- [`contributions/einstein-maxwell-periodic-photon-second-order.json`](contributions/einstein-maxwell-periodic-photon-second-order.json)
- [`reports/einstein-maxwell-periodic-photon-registration-receipt.md`](reports/einstein-maxwell-periodic-photon-registration-receipt.md)
- [`contributions/einstein-maxwell-periodic-graviton-second-order.json`](contributions/einstein-maxwell-periodic-graviton-second-order.json)
- [`reports/einstein-maxwell-periodic-graviton-registration-receipt.md`](reports/einstein-maxwell-periodic-graviton-registration-receipt.md)
- [`contributions/einstein-maxwell-obstruction-bilinear-g1.json`](contributions/einstein-maxwell-obstruction-bilinear-g1.json)
- [`reports/einstein-maxwell-obstruction-bilinear-registration-receipt.md`](reports/einstein-maxwell-obstruction-bilinear-registration-receipt.md)
- [`contributions/einstein-maxwell-compact-domain-taub-descent.json`](contributions/einstein-maxwell-compact-domain-taub-descent.json)
- [`reports/einstein-maxwell-compact-domain-taub-registration-receipt.md`](reports/einstein-maxwell-compact-domain-taub-registration-receipt.md)
- [`contributions/einstein-maxwell-harmonic-adjoint-block-preflight.json`](contributions/einstein-maxwell-harmonic-adjoint-block-preflight.json)
- [`reports/einstein-maxwell-harmonic-adjoint-block-registration-receipt.md`](reports/einstein-maxwell-harmonic-adjoint-block-registration-receipt.md)
- [`contributions/einstein-maxwell-axial-master-complex.json`](contributions/einstein-maxwell-axial-master-complex.json)
- [`reports/einstein-maxwell-axial-master-registration-receipt.md`](reports/einstein-maxwell-axial-master-registration-receipt.md)
- [`contributions/einstein-maxwell-polar-master-preflight.json`](contributions/einstein-maxwell-polar-master-preflight.json)
- [`reports/einstein-maxwell-polar-master-preflight-registration-receipt.md`](reports/einstein-maxwell-polar-master-preflight-registration-receipt.md)
- [`contributions/einstein-maxwell-polar-master-complex.json`](contributions/einstein-maxwell-polar-master-complex.json)
- [`reports/einstein-maxwell-polar-master-registration-receipt.md`](reports/einstein-maxwell-polar-master-registration-receipt.md)
- [`contributions/einstein-maxwell-polar-exceptional-complex.json`](contributions/einstein-maxwell-polar-exceptional-complex.json)
- [`reports/einstein-maxwell-polar-exceptional-registration-receipt.md`](reports/einstein-maxwell-polar-exceptional-registration-receipt.md)
- [`reports/nonlinear-nd1-registration-receipt.md`](reports/nonlinear-nd1-registration-receipt.md)
- [`reports/quantum-cartan-registration-receipt.md`](reports/quantum-cartan-registration-receipt.md)
- [`verify_programme_status.py`](verify_programme_status.py)

## Verification

From `physics/symplectic-reconstruction/`:

```bash
python3 d_quotient_programme/verify_programme_status.py --check --guards
```

The verifier checks the exact Git commit and SHA-256 digest of every imported
team certificate.  A team updates its own certificate first; the programme
certificate is regenerated only after the new claim has passed its team-level
verification.

## Publication policy

Papers VII--VIII retain their completed theorem, now with an explicit compact
phase-space split. The certified one-real-scalar no-go and the scoped neutral
two-field replacement supply the scalar-clock scope half of the Paper-IX gate;
Paper IX remains reserved until at least one complete boundary or interaction
theorem also lands.
A possible Paper X is reserved for interaction and quantum stability after the
applicable classical export and QME gates pass.

The neutral pair remains a valid homogeneous reference clock, but its local
positive-health promotion is obstructed. The complete standard one-field
stealth family is exhausted as well. The replacement is now concrete: an exact
Berger-cylinder family carries two standard-sign rotating conformal scalars
with positive quartic potential, dominant-energy stress, timelike phase, and
full raw clock incidence. This is a healthy background theorem, not yet a
complete all-row clock theorem. Downstream teams must import all scoped clock
results by content hash.
The first sub-gate is now exact: the phase carries nonzero conserved global
\(O(2)\) momentum and the full helical contraction satisfies
\(\Omega_{\rm total}(\delta,\mathcal L_D)=\omega\delta Q_R\). The fixed-coupling
audit closes the tangent question exactly:

\[
\delta E_N=-\frac{\alpha_Bq^{3/2}}2\frac{\delta Q_R}{Q_R}.
\]

Compact spatial averaging excludes an inhomogeneous escape, so `D_GAUGE`
holds on the declared smooth fixed-coupling linearized Berger phase space.
The temporal/Weyl clock doublets and all minimal dual rows admit an exact
first-order support-local cyclic SDR.  The retained 26-row minimal `q1` is now
coefficientwise exact and cyclic, its endpoint factors are Green-hyperbolic,
and reattaching the clock rows gives a scalar-biwave principal witness on all
metric and ghost directions.  The next classical gate is the curved
clock-reattached witness and total causal homotopy.

The Einstein team has separately proved that this Berger background is a
genuine non-Einstein Weyl--matter branch.  It is neither Einstein,
conformally Einstein, nor Einstein with the same clock stress for any
constant `kappa,Lambda`; therefore its same-base-point Einstein tangent gate
is `NOT_APPLICABLE`.  This does not replace the nonlinear team's separate
`CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT` gate.

At the separate common Einstein--Maxwell/Weyl--Maxwell product background,
the principal chain map is now complemented by a complete on-shell linear
theorem. The parallel flux kills the first variation of the quadratic
Chevreton defect, so every Einstein--Maxwell solution tangent survives in
Weyl--Maxwell before residual quotient. This does not yet supply the curved
off-shell BV map, quotient injection, nonlinear closure, or causal scattering
sector.

The second-order product test is also phase-space split. On the compact
periodic product at fixed magnetic flux, the constant radion and Maxwell
duality directions have certified adjoint-cokernel obstructions. On the
universal cover, a polynomial null tangent with nonzero Chevreton defect has
an explicit correction. Neither result is a general nonlinear verdict; the
next Einstein-sector gate is the fixed-charge test for periodic
nonzero-frequency graviton and photon harmonics.

The first physical-mode gate is now closed for one declared photon harmonic.
The smooth axisymmetric `l=1`, `omega=2` photon--metric mode has zero
first-order electric and magnetic charge variations, but its quadratic
Weyl--Maxwell `tt` source has normalized constant-lapse pairing `-16/3`.
Consequently it has no smooth periodic second-order correction at fixed
charges. This is not a no-go for every photon harmonic; the next compact gate
is one periodic helicity-two harmonic.

That gravitational-mode gate is now closed for one declared branch. The
smooth odd-parity `l=2` metric harmonic mixes with a Maxwell harmonic through
the background magnetic flux and has exact frequencies
`omega^2=6+/-2sqrt(3)`. For the certified plus branch, the normalized `t=0`
quadratic source pairing is `-(12/5)(6+5sqrt(3))`, so no smooth periodic
second-order correction exists at fixed electric and magnetic charges. The
minus branch and other harmonics remain open; the next deliverable is the
focused paper theorem.

The adjacency programme's first reusable obstruction object is now registered
at `G1` on the declared four-dimensional fixture span. Its constant-lapse
bilinear is diagonal on `(radion,duality,photon,gravitational-plus)` with exact
entries `(-2,-1/2,-16/3,-12sqrt(3)-72/5)`. The fixed magnetic-charge fibre
retains this relative Taub component; admitting the second-order magnetic
coefficient removes it from the augmented cokernel. The full harmonic domain
and complete adjoint cokernel remain the next promotion gate.

The compact domain has now been sharpened globally.  For the rational fixture,
compact `U(1)` quantization gives `N(epsilon)=2+2 epsilon^2 p`; a smooth family
on the same `N=2` bundle therefore has `p=0`.  The variable-magnetic-row repair
belongs to an enlarged continuous de Rham-flux theory, not the fixed-bundle
phase space.  Differentiated coupled Noether identities make the imported
constant-lapse form gauge-descended and slice independent, so it is registered
as a relative Taub bilinear on the fixed-bundle domain.  The complete harmonic
cohomology, other adjoint classes, and surviving block coefficients remain
open.

The harmonic calculation now has its first exact infinite block.  On the
declared homogeneous axial `H_x/a_x` tower,
`K_ell=[[lambda,2],[lambda,lambda]]` with
`omega^2=lambda+/-sqrt(2 lambda)` for every `(ell,m)`.  The missing `ell=1`
zero branch is locally gauge but globally retained because its generator is
not periodic around `S1`.  The reduced Wronskian and universal energy,
momentum, rotation, and electric-flux projection interface are frozen.  This
is a block preflight: axial gauge-quotient completeness, nonzero momentum,
polar sectors, covariant symplectic matching, and extra fourth-order adjoint
classes remain open.

The axial preflight is now promoted to every periodic `S1` momentum.  After
complete standard axial gauge fixing, two transverse masters obey
`omega^2=k_n^2+lambda+/-sqrt(2lambda)` for every `ell>=2,m`.  At `ell=1`, the
null vector is periodic gauge for nonzero Fourier modes, while the constant
twist remains globally.  A local reduced current is exact; polar modes,
covariant symplectic matching, extra fourth-order adjoint classes, and the
quadratic coefficient theorem remain open.

The complete polar tower and its exceptional blocks are now classified, and
the radiative symplectic gate is closed on the fixed bundle.  The exact
Einstein--Maxwell second variation gives positive action-normalized axial and
polar forms for every `ell>=2`; at `ell=1` their kernels are exactly the
declared residual gauge branches, with positive physical quotients.  On the
closed `S1 x S2` Cauchy surface these reduced Wronskians equal the integrated
Einstein--Maxwell Lee--Wald form.  The remaining compact gates are the
homogeneous `ell=0` and axial-twist global pairs, the independent
Weyl--Maxwell pullback, and the extra fourth-order adjoint classes.
