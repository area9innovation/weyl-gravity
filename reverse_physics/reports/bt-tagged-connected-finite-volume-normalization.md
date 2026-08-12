# BT tagged-connected finite-volume normalization

Certificate:
`REVERSE_PHYSICS_BT_TAGGED_CONNECTED_FINITE_VOLUME_NORMALIZATION_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

The resonant tagged-connected tree cross kernel becomes a finite,
dimensionless contribution on a declared normalized spectator box mode. It is
suppressed by one inverse spectator mode norm:

\[
 N_s=2E_sV,
 \qquad
 I_{\rm box}^{(6)}(T)
 =\frac{16\sqrt2\lambda^6W_\kappa(T)}{N_s}.
\]

For the certified tagged fixture

\[
 E_s=\frac{6\kappa}{5},qquad
 N_s=\frac{12\kappa V}{5},qquad V=L_xL_yL_z.
\]

Multiplying by the already certified active detector factors gives the exact
tree-cross probability contribution

\[
 \boxed{
 q_{\rm cross}^{(6)}(T)=
 \frac{125\sqrt2\lambda^6W_\kappa(T)\Delta\Omega}
 {12288\pi^2\kappa^3\mathrm{Area}\,V}}
\]

with

\[
 W_\kappa(T)=\frac{w(\kappa T)}{\kappa^2},
\]

\[
 w(z)=12z+\frac{125}{256}\sin\frac{16z}{5}
 +\frac{125}{128}\sin\frac{8z}{5}
 +\frac{125}{8}\sin\frac{2(\sqrt{17}-3)z}{5}.
\]

This result resolves the missing point-box normalization of the tree cross
term. It also changes its interpretation:

- at fixed finite `T`, it vanishes as `1/V` in the thermodynamic limit;
- at fixed finite `V`, it remains secular and grows linearly with `T`;
- the joint limit depends on the dimensionless ratio
  `T/(kappa^2 V)`.

Thus fixed-time infinite-volume suppression is real, but it is not an
all-time decoupling theorem.

## The spectator norm

The public BT cross commutator is

\[
 [b_\Omega(\mathbf p),b_\Upsilon^\dagger(\mathbf q)]
 =2E_{\mathbf p}\,\delta_3(\mathbf p-\mathbf q),
\]

with the same formula after exchanging Omega and Upsilon. In the public
finite-volume convention,

\[
 \delta_3(0)=V=L_xL_yL_z.
\]

For the positive ghost-even one-particle combination

\[
 u_{\mathbf p}=\frac{|\Omega,\mathbf p\rangle
                         +|\Upsilon,\mathbf p\rangle}{\sqrt2},
\]

the cross Gram gives

\[
 \langle u_{\mathbf p},u_{\mathbf p}\rangle_K
 =2E_{\mathbf p}V=N_s.
\]

Hence the normalized spectator mode is `u_p/sqrt(N_s)`.

## Why the connected amplitude gets `1/N_s`

Both the incoming and outgoing normalized spectator legs contribute
`N_s^(-1/2)`.

The disconnected four-point tree has an actual spectator identity
contraction between those legs. Its raw value is `N_s`, so

\[
 N_s^{-1/2}N_sN_s^{-1/2}=1.
\]

This is the unit spectator overlap used in the leading tagged probability.

The connected six-point tree has no spectator identity contraction. The same
external normalizers therefore leave

\[
 N_s^{-1/2}\,1\,N_s^{-1/2}=\frac1{N_s}.
\]

This factor was absent from the pointwise external-mass/species carrier, where
the identity distribution had been stripped. It is precisely the missing
finite-volume bridge. No active phase-space, label-orbit, angular-acceptance,
or beam factor is changed: those are common to the two terms on the declared
tagged cell and cancel in their ratio.

## Relative correction

The leading tagged external-jet norm is

\[
 24\lambda^4.
\]

The normalized cross coefficient divided by it is

\[
 \frac{I_{\rm box}^{(6)}}{24\lambda^4}
 =\frac{2\sqrt2\lambda^2W_\kappa(T)}{3N_s}.
\]

The leading tagged probability at the scaled fixture is

\[
 q_{\rm tag}^{(4)}
 =\frac{75\lambda^4\Delta\Omega}
 {2048\pi^2\kappa^2\mathrm{Area}}.
\]

Their product gives the boxed coefficient. The dimensions close:
`W_kappa` has mass dimension `-2`, while
`kappa^3 Area V` also has dimension `-2`.

This is a relative normalization theorem. It assumes the same declared active
cell and therefore does not claim a detector-independent three-body flux or
cross section.

## The order of limits

The exact positivity theorem for `W` gives

\[
 q_{\rm cross}^{(6)}(T)>0
\]

for finite positive `kappa,T,V,Area`. At fixed `T`, all other quantities fixed,

\[
 \lim_{V\to\infty}q_{\rm cross}^{(6)}(T)=0.
\]

At fixed `V`, however,

\[
 \lim_{T\to\infty}\frac{W_\kappa(T)}T=\frac{12}{\kappa},
\]

so

\[
 \lim_{T\to\infty}\frac{q_{\rm cross}^{(6)}(T)}T
 =\frac{125\sqrt2\lambda^6\Delta\Omega}
 {1024\pi^2\kappa^4\mathrm{Area}\,V}.
\]

Relative to the leading tagged probability,

\[
 \lim_{T\to\infty}\frac1T
 \frac{q_{\rm cross}^{(6)}}{q_{\rm tag}^{(4)}}
 =\frac{10\sqrt2\lambda^2}{3\kappa^2V}.
\]

If `T,V` grow with

\[
 \tau=\frac{T}{\kappa^2V}
\]

fixed, then

\[
 \frac{q_{\rm cross}^{(6)}}{q_{\rm tag}^{(4)}}
 \longrightarrow\frac{10\sqrt2}{3}\lambda^2\tau.
\]

The two limits therefore do not select a universal value without a physical
preparation/detector scaling. At large fixed-volume times the perturbative
expansion also becomes nonuniform; the displayed secular term is not an
all-time prediction.

## What this changes physically

The preceding theorem found a genuine resonance. This theorem shows that the
resonance is diluted by normalization of the unchanged spectator mode. It
does not contaminate the ordinary fixed-time thermodynamic limit: the
connected amplitude has to overlap one particular normalized spectator mode,
and that overlap costs `1/(2E_sV)`.

This is encouraging for the physical route, but it does not remove the whole
order-`lambda^6` problem. Long observation times can compensate the volume
suppression. A compact wave packet replaces the literal box volume by a packet
overlap functional that has not yet been derived. The active loop, source
dressing, and survival terms also occur at the same probability order.

## Claim boundary

The result is the finite-volume tree-cross contribution only. It does not
establish the complete order-`lambda^6` probability, a box-independent compact
packet coefficient, an active one-loop term, source or survival completion,
forward/collinear or KLN completion, an all-time operator, general Eq. (19),
gravity or metric BV--BRST transfer, or anything `LORENTZIAN-CAUSAL`. No
literature-priority claim is made.

## Verification receipt

- Tier 0: the changed Python and JSON files parse; the scoped diff passes
  `git diff --check`; Papers 05 and 06 compile twice.
- Tier 1: the exact producer passes 32/32 checks, the independent cross-Gram
  and ten-channel verifier passes 30/30 checks, and 21 tests including 20
  adversarial mutations pass. Every scientific rail runs under a 500 MB
  virtual-memory cap.
- Tier 2: all imported mathematical inputs are unchanged and content
  addressed. Both rails verify their hashes and passing states; no predecessor
  producer was rerun.
- Tier 3 was not run because no shared algebra, freeze, release, QME state, or
  Lorentzian claim changes.
- The Science Forge fold accepts the work item and append-only DONE event with
  no invalid item or malformed event.

Commands:

```text
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_tagged_connected_finite_volume_normalization.py --write --check
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_tagged_connected_finite_volume_normalization.py
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_tagged_connected_finite_volume_normalization
```
