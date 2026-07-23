# Axial horizon Grassmann/Möbius transport toward \(r=4\): q0 shortfall

## Disposition

`METHOD_SHORTFALL`, not a failed physical theorem.

The exact lower pilot child

\[
\omega\in[1/2,2049/4096]
\]

was propagated from \(\rho=2^{-22}\) using:

- the committed action-derived axial horizon initializer and radial system;
- 256 exact radial panels per dyadic shell;
- all 20 complex \(3\)-plane Grassmann charts;
- a separate \(6\times6\) amplitude transport;
- exact rational right-action covariance;
- a 64-cell uniform frequency rank audit.

The graph remains controlled through shell 2. The first-order
shared-affine enclosure of the amplitude ceases to certify full column rank
at the shell-2 boundary. No finer 512/1024 radial-panel chase was performed.

## Frozen terminal trace

The terminal run records:

```text
SHELL q=0 shell=0 chart=11 rank=6 norm=1.0054955957723855 zwidth=0.0637599810738783 awidth=0.03550619494176685 direct=true overlap=true switches=0
SHELL q=0 shell=1 chart=11 rank=6 norm=1.0304296997354865 zwidth=0.39751653564104067 awidth=0.3142447264451248 direct=true overlap=true switches=0
HEARTBEAT q=0 shell=2 panel=256 chart=11 norm=1.5016200852686385 zwidth=3.003240069284962
REFUSE amplitude-rank q=0 shell=2
```

The program exits with code 3. The complete log additionally prints the
exact rational centre of the terminal amplitude. Its exact centre rank and
ordinary floating SVD are diagnostics only.

That centre has exact rank 6. Its ordinary double-precision singular values
are

\[
(1.92655924,1.92655924,1.00000100,1.00000100,
  0.73415170,0.73415170),
\]

so \(\sigma_{\min}\simeq0.73415\) and
\(\kappa_2\simeq2.6242\). This strongly identifies wrapping/correlation loss
as the proximate numerical-proof failure rather than a near-singular centre,
but it is deliberately not a uniform interval-rank certificate.

## Interpretation

This refusal does not show that the horizon-regular plane becomes singular.
It shows that repeated multiplication in the degree-one `ivaffine` model
loses too much shared \(\omega\)-correlation to certify the separate
amplitude rank. In that kernel, every \(A_1B_1e^2\) term is folded into an
interval remainder after each multiplication.

The next justified method is a validated shared Taylor matrix model retaining
exact coefficients through degree at least two. A reusable Forge request is
recorded as:

`sf:forge-request/phase3-validated-shared-taylor-grassmann-transport`.

## What this does not establish

This package does not establish:

- a horizon-to-\(r=4\) handoff;
- a horizon-to-infinity connection matrix;
- absence or existence of a global regular additional channel;
- scattering, a flux sign, stability, a physical ghost, positivity, CPT, or
  unitarity;
- any frequency outside this lower child cell;
- polar parity or \(\ell\ne2\).

## Verification

```bash
python3 -m unittest \
  black_hole_programme.phase3.axial_horizon_grassmann_mobius_to_r4.test_verify
python3 \
  black_hole_programme/phase3/axial_horizon_grassmann_mobius_to_r4/verify.py
python3 \
  black_hole_programme/phase3/axial_horizon_grassmann_mobius_to_r4/analyze_center.py \
  black_hole_programme/phase3/axial_horizon_grassmann_mobius_to_r4/sentinel_q00.log
```

The expensive producer command is recorded in `receipt.json`; the verifier
does not disguise a reproduction as an independent proof rail.
