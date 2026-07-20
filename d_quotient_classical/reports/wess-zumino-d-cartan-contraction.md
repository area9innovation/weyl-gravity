# Wess--Zumino compensator raw-\(D\) Cartan contraction

## Result

On the unit vacuum conformal cylinder, in the closed-universe derived sector
`P_der`, raw \(D_{\rm compact}=\partial_t\) has zero Weyl component.  The
formal Wess--Zumino compensator quartet therefore admits the exact
same-background contraction

\[
Q_0S+SQ_0=1-\iota\pi,\qquad
[Q_0,\iota_{D,0}]_+=\mathcal L_{D,0}.
\]

The projection sets
`tau=omega=omega_star=tau_hat_star=0`.  The homotopy is the normalized
quartet Euler homotopy

\[
s(\omega)=\tau,\qquad s(\widehat\tau^*)=\omega^*,\qquad
S=N^{-1}s\quad(N>0).
\]

All Cartan, side-condition, support-locality, \(D\)-equivariance and cyclic
pairing identities pass exactly.  The finite replay covers weights
`-2, 0, 3`, and the opposite-weight cyclic fixtures cover `0` and `+/-2`.
The all-monomial statement follows by the declared filtration-continuous
graded-derivation extension.

## Sharp generator boundary

This is raw `D_compact`, not `K_Berger`; the Wess--Zumino `tau` is not the
Berger clock.  The construction does not extend by name matching to
Minkowski dilation.  For a generator with Weyl component `sigma_D`,

\[
\pi(\mathcal L_D\tau)-\mathcal L_D(\pi\tau)=\sigma_D.
\]

Thus the tau-adic augmentation ideal is \(D\)-stable on the cylinder
(`sigma_D=0`) and fails already on `tau` for Minkowski `D_M`
(`sigma_D=-1`).

## Consumer boundary

The classical input requested by the one-loop quantum \(D\)-Ward calculation
is complete for the vacuum-cylinder raw-`D_compact` row.  The complete
renormalized `Q1`, `iota_D1`, `L_D1`, renormalized products and the
local-insertion-to-Cartan Ward map remain absent.  Consequently no quantum
Cartan class or residual quantum transfer follows.

## Reproduction

```bash
python3 d_quotient_classical/compensator/wess_zumino_d_cartan_contraction.py --check
python3 d_quotient_classical/compensator/verify_wess_zumino_d_cartan_contraction.py
python3 -m unittest d_quotient_classical.compensator.tests.test_wess_zumino_d_cartan_contraction
```

Operator hash: `1aff0fc5c1baa0286b9aefd96615a29396333b9c6407f4f45b666231bdc8232b`

Formal-algebra hash: `cdac0d2803a1c2e9e56e192533d26e69f1c138725c9a9793d35012d9383c2e97`

CLOSE-OUT: DONE — the complete stop condition is met
EVIDENCE: d_quotient_classical/certificates/WESS_ZUMINO_D_CARTAN_CONTRACTION_V1.json
