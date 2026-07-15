# Berger clock reduced charge seed

The positive Berger background carries a nonzero conserved matter clock
momentum.  If \(R(T_1,T_2)=(-T_2,T_1)\), then

\[
\mathcal L_D(T_1,T_2)=\omega R(T_1,T_2),
\]

and the standard-sign scalar \(O(2)\) current has future charge density

\[
j_R=T_1\dot T_2-T_2\dot T_1=\rho^2\omega>0.
\]

The Maurer--Cartan normalization fixes the Berger volume to

\[
\operatorname{Vol}(S^3_{\rm Berger})=16\pi^2a^3\sqrt q,
\]

and the exact background relations give

\[
Q_R=16\pi^2\alpha_Bq\sqrt{1-4q}>0.
\]

Thus the phase is canonically paired with genuine conserved matter momentum;
it is not a cost-free scalar gauge marker.  This makes it a plausible
physical clock.

## Fixed-coupling warning

The background relation at fixed theory couplings is

\[
q^2-5q+1+6(\alpha_B\lambda)(1-4q)^2=0.
\]

Its on-shell derivative is

\[
\frac{3(6q-1)}{4q-1}\ne0
\]

throughout the certified interval. Hence \(\delta q=0\) inside the
stationary fixed-coupling family. The open \(q\)-interval classifies a family
of theories/backgrounds; it is not a tangent direction of one fixed theory.

## Covariant current and helical identity

Direct variation of the conformal-scalar action gives

\[
\Omega_{\rm m}(\delta,R)=\delta Q_R.
\]

The curvature-improvement cross term vanishes because
\(\delta_Rg=0\) and \(\delta_R(T_1^2+T_2^2)=0\). Since the Berger metric is
stationary while \(\mathcal L_DT=\omega RT\), the full current obeys

\[
\boxed{\Omega_{\rm total}(\delta,\mathcal L_D)=\omega\,\delta Q_R.}
\]

The remaining question is therefore precise: does the allowed fixed-coupling
linearized solution space contain a tangent with \(\delta Q_R\ne0\)?

The result is not yet the total \(D\)-charge theorem.  The next gate,

```text
TOTAL_BERGER_D_PRESYMPLECTIC_AUDIT
```

must combine the pure-Weyl and improved scalar presymplectic currents on the
complete fixed-coupling linearized solution space.  Only that calculation can
classify total \(D\) as gauge, charged, sector-dependent, or non-Hamiltonian.
