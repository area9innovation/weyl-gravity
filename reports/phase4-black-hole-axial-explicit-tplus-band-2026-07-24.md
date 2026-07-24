# Phase-4 explicit \(T_+\) band — interaction-picture restart checkpoint

Dependency tags: `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Result

The earlier experiment resumed the certified common-moving \(R/S\) outgoing
partial-jet checkpoint at \(r=979/32\). A bounded order-120 panel of width
\(5/32\) reached \(r=487/16\).

The accepted boundary satisfies:

- common frequency generator: `7315`;
- validated exponential pre-tail:
  `4.4421679558528834e-05`;
- joint base/tangent hull width: `5.12490045532877`;
- exact equality of retained partial-jet and direct sixteen-state Taylor
  coefficients;
- interval containment of the independent boundary comparison;
- content-addressed successor payload:
  `b1240852cb5f60848ab7d6fb6a165f394bafb803472003fada34f6816373c04a`.

This closes the specific Phase-3 runtime refusal: the order-120 fallback that
was never reached after the larger-panel timeout is admissible when executed
directly.

## Exact interaction-picture reconstruction

The restarted experiment now proves in exact rational arithmetic:

\[
J'=P^{-1}EP,\qquad
K'=P^{-1}DR,\qquad
\dot K'=P^{-1}CR-JP^{-1}DR,
\]

for

\[
J=P^{-1}\dot P,\qquad
K=P^{-1}Q,\qquad
\dot K=\partial_\tau(P^{-1}Q)|_0.
\]

It independently verifies

\[
\Phi_6=
\operatorname{diag}(P,P,R)
\begin{pmatrix}
I&J&JK+\dot K\\
0&I&K\\
0&0&I
\end{pmatrix}
=
\begin{pmatrix}
P&\dot P&\dot Q\\
0&P&Q\\
0&0&R
\end{pmatrix}.
\]

The projective charts carry \(q,\lambda,q_\tau,\lambda_\tau\), with the
exact reciprocal transition

\[
p=q^{-1},\quad
\mu=\lambda+\log q,\quad
p_\tau=-q_\tau/q^2,\quad
\mu_\tau=\lambda_\tau+q_\tau/q.
\]

The independent verifier re-derives these identities with a separate exact
`Fraction` matrix implementation rather than rerunning the SymPy producer.

## First physical restart gate

A physical center-frequency fixture at

\[
\omega=\frac{8193}{16384}
\]

continues from \(r=487/16\) to \(r=3895/128\). It forces reciprocal-chart
switches in both the spin-two and spin-one blocks. The largest comparison
residual is

\[
1.43\times10^{-14}
\]

for the direct versus interaction-picture tangent. The Wronskian residuals
are below \(2.3\times10^{-16}\). This is a numerical consistency fixture,
not an enclosure.

Separately, the pinned Forge Taylor/affine rail validates the same micro-panel:

```text
radial start       487/16
radial end         3895/128
frequency generator 7315
tail               4.215517341618608e-27
joint hull width   5.214992266499738
jet/direct coefficients equal  true
interval difference contains 0 true
```

Thus the certified radial frontier has moved strictly beyond \(487/16\).

## Remaining gate

The frame is still at \(r=3895/128\), not \(r=4\). The exact
interaction-picture representation is now closed, but its full
Taylor/affine interval implementation is not. The next producer must enclose
the projective/logarithmic lines and the \(J,K,\dot K\) quadratures
correlatively, using the direct sixteen-state rail only at coarse
checkpoints.

No \(T_+\), reflection amplitude, Stokes identity, or frequency-band theorem
is claimed.

## Verification

```text
python3 -m black_hole_programme.phase4.axial_explicit_tplus_band_v1.produce --check
python3 -m black_hole_programme.phase4.axial_explicit_tplus_band_v1.verify
python3 -m unittest -v black_hole_programme.phase4.axial_explicit_tplus_band_v1.test_checkpoint
python3 -m black_hole_programme.phase4.axial_explicit_tplus_band_v1.produce_interaction --check
python3 -m black_hole_programme.phase4.axial_explicit_tplus_band_v1.verify_interaction
python3 -m unittest -v black_hole_programme.phase4.axial_explicit_tplus_band_v1.test_interaction_picture
```

Both independent verifiers and all nine scoped tests passed. Tier 2 and
Tier 3 were not run because no shared operator changed, the common frame has
not reached the matching section, and no paper theorem is promoted.

CLOSE-OUT: SHORTFALL — the exact interaction picture and a new validated micro-successor are closed, but explicit \(T_+\) remains open at the full projective-interval transport gate.
EVIDENCE: black_hole_programme/phase4/axial_explicit_tplus_band_v1/interaction_receipt.json
