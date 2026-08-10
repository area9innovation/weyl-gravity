# Bateman--Turok ultraviolet hard-scattering law

**Result:** `COEFFICIENT_COMPUTED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

**Certificate:**
[`REVERSE_PHYSICS_BT_UV_HARD_SCATTERING_LAW_V1`](../certificates/REVERSE_PHYSICS_BT_UV_HARD_SCATTERING_LAW_V1.json)

## Physical result

The certified Bateman--Turok Born rate, one-loop running coupling, and complete
projected hard logarithm fit one Callan--Symanzik equation exactly.  This gives
a positive leading-log prediction for the short-distance two-to-two event
rate at every fixed angle away from the forward and backward collinear
directions.

Let

\[
 \lambda_0=\lambda(\sqrt{s_0}),\qquad
 D(s)=\frac1{\lambda_0^2}
      +\frac5{16\pi^2}\log\frac{s}{s_0}.
\]

Then

\[
 \boxed{
 \frac{d\sigma_{\mathrm{hard}}^{\mathrm{LL}}}{d\Omega}
 =\frac{3}{32\pi^2s\,D(s)^2}}
\]

and the rate is positive wherever `D(s)>0`, in particular on the
asymptotically-free ultraviolet branch.  Defining

\[
 \Lambda^2=s_0\exp\left[-\frac{16\pi^2}{5\lambda_0^2}\right]
\]

puts the prediction in the universal form

\[
 \boxed{
 \frac{d\sigma_{\mathrm{hard}}^{\mathrm{LL}}}{d\Omega}
 =\frac{24\pi^2}
 {25s\log^2(s/\Lambda^2)}}.
\]

Thus

\[
 \lim_{s\to\infty}
 s\log^2(s/\Lambda^2)
 \frac{d\sigma_{\mathrm{hard}}^{\mathrm{LL}}}{d\Omega}
 =\frac{24\pi^2}{25}.
\]

In ordinary language: at very high energy the interaction becomes weaker.
The geometrical `1/s` falloff of a four-dimensional cross section acquires an
additional, precisely determined `1/log(s)^2` suppression.

## Why this is not merely “put the running coupling into tree level”

The three inputs were obtained in separate calculations:

\[
 \frac{d\sigma_{\rm Born}}{d\Omega}
 =\frac{3\lambda^4}{32\pi^2s},
 \qquad
 \beta_\lambda=-\frac{5\lambda^3}{16\pi^2},
\]

and

\[
 \frac{d\sigma_{\rm virt,log}}{d\Omega}
 =\frac{5\lambda^6}{256\pi^4s}(L_s+L_t+L_u).
\]

At fixed scattering angle all three hard invariants scale with `s`.  Each
`L_X=log(mu^2/|X|)` differentiates to `2` with respect to `log(mu)`.  After
powers of `pi` are suppressed, the explicit scale derivative is

\[
 2\times3\times\frac5{256}=\frac{15}{128}.
\]

The running of the Born term gives independently

\[
 -4\times\frac5{16}\times\frac3{32}=-\frac{15}{128}.
\]

They cancel exactly.  Two channel logarithms leave residual `-5/128`; reversing
the virtual sign leaves `-15/64`.  The agreement is therefore a live
coefficient test, not dimensional analysis.

Expanding the resummed answer gives the first ultraviolet loop logarithm

\[
 \frac{d\sigma_{\mathrm{hard}}^{\mathrm{LL}}}{d\Omega}
 =\frac{3\lambda_0^4}{32\pi^2s}
 \left[1-\frac{5\lambda_0^2}{8\pi^2}
 \log\frac{s}{s_0}+\cdots\right].
\]

Its absolute coefficient is
`-15*lambda0^6/(256*pi^4*s)`, exactly the fixed-angle dilation of the
independently projected three-channel hard logarithm.  The certificate retains
the first seven coefficients of the full leading-log series and the verifier
checks them by multiplying the series by the square of the running
denominator.

## A finite detector window

To keep the statement away from the unresolved beam-collinear endpoints,
choose a fixed acceptance

\[
 \theta_0\leq\theta\leq\pi-\theta_0,
 \qquad 0<\theta_0<\frac\pi2.
\]

Its solid angle is `4*pi*cos(theta0)`.  The leading-log hard rate in that
window is

\[
 \boxed{
 \sigma_{\rm window}^{\rm LL}
 =\frac{3\cos\theta_0}{8\pi s\,D(s)^2}}
\]

and

\[
 \lim_{s\to\infty}s\log^2(s/\Lambda^2)
 \sigma_{\rm window}^{\rm LL}
 =\frac{96\pi^3}{25}\cos\theta_0.
\]

Writing `z=-t/s=(1-cos(theta))/2`, the residual angular logarithm is
`-log(z*(1-z))`.  It is bounded for every fixed `theta0>0`; this is why the
declared window is a controlled hard observable rather than a claim about the
collinear endpoints.

## Universality and physical boundary

The coefficient `24*pi^2/25` is universal at leading logarithmic order.
Under an analytic scheme change `lambda'=lambda+c*lambda^3+...`, the one-loop
cubic beta coefficient remains `5/(16*pi^2)` and the leading Born coefficient
remains `3/(32*pi^2)`.  The definition of `Lambda` shifts, but that affects only
subleading inverse-log terms.

This is a physical **hard/acceptance-window leading-log result**, not the final
inclusive answer.  Exact particle-number two-to-two scattering in a massless
theory is not by itself infrared safe.  The result supplies the short-distance
baseline that a completed collinear-inclusive or dressed-state construction
must approach for every fixed nonzero `theta0`.  The following remain open:

- real--virtual endpoint cancellation and the inclusive quotient trace;
- the order-`lambda` Jordan/`R_t` asymptotic generator;
- incoming degenerate sectors;
- cut-free finite terms and next-to-leading-log accuracy;
- positivity beyond this leading-log hard contribution; and
- every tensor/BRST gravitational or `LORENTZIAN-CAUSAL` claim.

Accordingly the certificate says `PHYSICAL_HARD_RESULT` and simultaneously
keeps `full_inclusive_nlo_probability=NOT_ESTABLISHED`.  Neither statement may
be dropped.

## Sources and originality boundary

Bateman and Turok provide the Born normalization in
[arXiv:2607.00096v1](https://arxiv.org/abs/2607.00096).  Holdom provides the
general one-loop beta functions in
[arXiv:2303.06723v2](https://arxiv.org/abs/2303.06723).  This repository had
already certified their restriction to the perfect-square locus and had
independently computed the projected three-channel hard logarithm.

The new result is the exact closure of those independently obtained
coefficients in one physical Callan--Symanzik equation, the resummed
nonforward-window law, and its universal coefficient.  No priority claim is
made for running-coupling improvement as a general method.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_uv_hard_scattering_law.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_uv_hard_scattering_law.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_uv_hard_scattering_law
```

The producer uses exact rational arithmetic.  The independent verifier does
not import it: it parses the three predecessor certificates, rebuilds the RG
identity, verifies the leading-log series by a different polynomial method,
checks scheme invariance and positive rational UV fixtures, validates all
content hashes, and rejects coefficient and claim-boundary mutations.  Final
timed receipt, 2026-08-10:

| Tier | Command | Time | Peak RSS | Result |
|---|---|---:|---:|---|
| 0 | `py_compile` on producer, verifier, test | 0.04 s | 15,888 KB | PASS |
| 0 | `json.tool` on certificate and schema | 0.06 s | 14,572 KB | PASS |
| 1 producer | exact reproduction | 0.03 s | 20,108 KB | PASS, 21/21 |
| 1 independent | verifier | 0.10 s | 30,032 KB | PASS, 14/14 |
| 1 focused | new tests | 0.46 s | 30,396 KB | PASS, 10/10 |
| 1 consumer | RG-separatrix tests | 1.31 s | 70,052 KB | PASS, 11/11 |
| 1 consumer | projected-hard-log tests | 0.28 s | 30,540 KB | PASS, 10/10 |
| 1 consumer | Born/preflight tests | 0.47 s | 30,608 KB | PASS, 10/10 |
| papers | Paper 05 final pass | 0.40 s | 50,332 KB | PASS |
| papers | Paper 06 final pass | 0.45 s | 50,496 KB | PASS |

All jobs ran sequentially under `ulimit -v 500000`; none exceeded 71 MB.
PDF text extraction confirms the physical formula, Callan--Symanzik language,
and inclusive-NLO disclaimer.  Paper 06 has no overfull boxes.  Paper 05 has
only its three small pre-existing boxes, at most 4.21 pt.

The three mathematical inputs are unchanged and content-addressed, and all
three direct consumers passed.  No Tier 2 producer regeneration was needed.
Tier 3 was not run because this is not a freeze, release, shared-core change,
or theorem promotion beyond the stated `COEFFICIENT_COMPUTED` lifecycle.  A
skipped higher tier is not a pass.
