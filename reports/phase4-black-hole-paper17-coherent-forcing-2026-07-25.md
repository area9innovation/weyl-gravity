# Paper 17 finite-time coherent forcing

## Result

Paper 17 now proves the exact response of the isolated critical kernel

\[
g_{\rm W}(t)=\Theta(t)Cte^{-\gamma t}e^{-i\Omega t}
\]

to a switched-on phase-locked source

\[
F(t)=F_0\Theta(t)e^{-i\Omega_dt}.
\]

With

\[
\Delta=\Omega-\Omega_d,\qquad\lambda=\gamma+i\Delta,
\]

the causal response is

\[
x_{\rm W}(t)=
CF_0e^{-i\Omega_dt}
\frac{1-(1+\lambda t)e^{-\lambda t}}{\lambda^2}.
\]

The ordinary simple-pole response is

\[
x_{\rm E}(t)=
AF_0e^{-i\Omega_dt}
\frac{1-e^{-\lambda t}}{\lambda}.
\]

At perfect real-frequency tuning, the early-time laws are respectively

\[
x_{\rm W}(t)=\frac12CF_0t^2e^{-i\Omega t}+O(t^3),
\]

\[
x_{\rm E}(t)=AF_0te^{-i\Omega t}+O(t^2).
\]

The critical response therefore builds quadratically rather than linearly
during the coherent early-time window.  It nevertheless saturates for
\(\gamma>0\), with steady amplitude proportional to
\((\gamma^2+\Delta^2)^{-1}\).  Its half-power detuning is

\[
|\Delta|_{\rm hp}=\gamma\sqrt{\sqrt2-1},
\]

compared with \(\gamma\) for the ordinary Lorentzian.

## Phase-matched pulse train

For impulses separated by \(T=2\pi/\Omega\), put
\(q=e^{-\gamma T}\).  The critical arithmetic--geometric sum is

\[
T\sum_{j=1}^Njq^j
=
T\frac{q[1-(N+1)q^N+Nq^{N+1}]}{(1-q)^2}.
\]

When \(NT\ll1/\gamma\), it has \(N^2\) scaling, while the ordinary
geometric sum has \(N\) scaling.  Damping truncates both laws.

For the certified mode,

\[
\tau_{\rm damp}\simeq11.24M,\qquad
T_{\rm osc}\simeq16.81M,
\]

\[
e^{-\gamma T_{\rm osc}}\simeq0.224,\qquad
Q_{\rm mode}\simeq2.10.
\]

The mode is strongly damped.  Its useful coherent preparation window is
one or a few damping times, not a long high-\(Q\) pulse train.

## Optimal finite-window drive

For the declared source-coefficient budget

\[
\int_0^T|F(s)|^2\,ds\le E,
\]

Cauchy--Schwarz gives the sharp bound

\[
|x(T)|_{\max}
=
\frac{|C|\sqrt E}{2\gamma^{3/2}}
\sqrt{
1-e^{-2\gamma T}
(1+2\gamma T+2\gamma^2T^2)
}.
\]

The optimizer is the time-reversed conjugate kernel,

\[
F_{\rm opt}(s)\propto
\overline{g_{\rm W}(T-s)}
\propto
(T-s)e^{-\gamma(T-s)}e^{+i\Omega(T-s)}.
\]

The long-window bound is

\[
\frac{|C|\sqrt E}{2\gamma^{3/2}}.
\]

This is exact in the projected coefficient-space \(L^2\) norm.  The
budget is not identified with invariant gravitational energy, and a
physical spacetime source with the required adjoint radial, parity, and
angular profile has not been constructed.

## Independent verification

The verifier independently checks:

- both convolution formulas through their differential and initial-value
  identities;
- the quadratic and linear Taylor coefficients;
- the critical half-power width;
- the finite arithmetic--geometric pulse sum;
- the finite-window kernel norm and its long-window limit;
- the certified damping time, period, one-cycle retention, and quality
  factor;
- the fail-closed declaration schema.

Ten new mutation tests reject changes to the convolution numerator,
quadratic factor, linewidth, pulse-sum terminal power, \(N^2\) scaling,
one-cycle retention, matched-drive damping exponent, conjugation, and two
forbidden physical promotions.  The scoped suite passed 77 tests in
100.852 seconds.  The full repository suite passed 149 tests in 1.34
seconds.

## Claim boundary

Established:

- exact isolated-kernel coherent-drive response;
- exact quadratic early-time buildup and damped saturation;
- exact critical half-power width;
- exact phase-matched finite-pulse sum and coherent \(N^2\) regime;
- exact certified-mode damping scales;
- exact finite-window coefficient-space optimizer and sharp bound.

Not established:

- the complete global causal Schwarzschild response;
- a physical matched spacetime source;
- equality of the coefficient-space budget with invariant gravitational
  energy;
- nonlinear saturation or backreaction;
- detector feasibility;
- arbitrarily large response or instability;
- any quantum statement.

CLOSE-OUT: DONE — the isolated Weyl EP2 is now an exactly solvable damped
critical resonator: coherent forcing builds quadratically, saturates, and
is optimized by the time-reversed conjugate kernel.

EVIDENCE: `reports/PAPER17_COHERENT_FORCING_TIER_RECEIPT.json`
