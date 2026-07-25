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

## 25 July amplitude-preserving terminal audit

The complete certified Phase-3 infinity-plane cover was replayed while
retaining the exact amplitude cocycle
\[
Y=G_{\rm chart}(Z)A
\]
instead of resetting \(A\) after propagation or chart changes.  The
frequency variable was restricted exactly to
\[
I_*=[1/2,10001/20000],\qquad
\epsilon_{\rm parent}
=-\frac{497}{625}+\frac{128}{625}\epsilon_{I_*}.
\]

Stages 0--4 preserved the endpoint normalization and certified ranks
\((6,6,12)\).  At the dense fixed-frame crosswalk, the Grassmann pivot
retained a remainder floor.  The producer therefore reconstructed the
physical frame, applied the crosswalk without inversion, and continued the
remaining factors as a raw Taylor frame.

Both physical frame enclosures reached \(r=4\), but neither terminal inverse
was certifiable:

| frame | maximum coefficient scale | maximum remainder | remainder/scale |
|---|---:|---:|---:|
| incoming | \(9.8573\times10^2\) | \(6.0570\times10^9\) | \(6.1446\times10^6\) |
| outgoing | \(5.3832\times10^5\) | \(6.8707\times10^{11}\) | \(1.2763\times10^6\) |

The certificate stores exact rational values decoded from the rational
Taylor coefficients and binary64 interval endpoints.  This establishes a
representation-specific shortfall:

> The amplitude-preserving Grassmann continuation followed by a rectangular
> raw-frame tail cannot certify the terminal inverse or explicit \(T_+\) on
> \(I_*\).

It does not establish singularity of \(T_+\), nor failure of a
better-conditioned representation.  The separately certified scalar
diagonal factors continue to prove invertibility on \(I_*\); the unresolved
data are the normalized extension shears and complete matrix inverse.

Future attempts should retain normalized interaction variables
\(J,K,\dot K\), projective/logarithmic amplitudes, or an affine equivalent
through the dense crosswalk.  Repeating the rectangular raw tail is not
recommended.

Verification:

```text
python3 -m black_hole_programme.phase4.axial_explicit_tplus_band_v1.produce_amplitude_summary
python3 -m black_hole_programme.phase4.axial_explicit_tplus_band_v1.verify_amplitude_taylor
python3 -m unittest -v black_hole_programme.phase4.axial_explicit_tplus_band_v1.test_amplitude_taylor
```

CLOSE-OUT: SHORTFALL — the physical amplitude enclosure reaches \(r=4\), but
rectangular wrapping prevents terminal rank and explicit-\(T_+\)
certification.
EVIDENCE: black_hole_programme/phase4/axial_explicit_tplus_band_v1/amplitude_certificate.json
