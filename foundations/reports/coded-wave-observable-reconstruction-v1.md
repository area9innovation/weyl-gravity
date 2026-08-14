# Coded wave observable reconstruction v1

**Result:** `FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1`

## Theorem

RCA_0 proves that, for each declared mean-zero rational step-pair p and the declared rational periodic polygonal detector h, the finite dyadic rational polygonal approximants A_N(k) converge uniformly to the smeared chiral observable O_h on every rational bounded time interval. The explicit cutoff is N(k)=k+ell(K)+1, where K=Lip(h)(norm_1(a)+norm_1(b)) and ell(K) is the least natural ell with K<=2^ell; the certified error is at most K 2^-N(k)<=2^-(k+1)<2^-k.

This is the first foundations certificate that carries declared rational wave data through a finite approximation sequence to a named observable with a uniform-in-time error bound. It reconstructs one observable, not the full field.

## Declared observable

`O_h(t;p)=integral_0^1 h(x)[T_t a(x)+T_-t b(x)] dx`

A bounded spatially smeared amplitude of the two chiral wave components; h is a declared detector profile, not a probability rule.

## Finite approximants and cutoff

A_m is the periodic piecewise-linear interpolation in time through the exact rational samples (j/2^m,O_h(j/2^m;p)) for 0<=j<=2^m.

The cutoff is `N(k)=k+ell(K)+1` and the certificate proves

`sup_{|t|<=T}|A_N(k)(t)-O_h(t;p)|<=K*2^-N(k)<=2^-(k+1)<2^-k for every positive rational T`.

The cutoff is independent of the displayed bounded interval because the cylinder observable is one-periodic. All samples and cutoff arithmetic are finite and primitive recursive; RCA₀ is used for the coded real-time extension and uniform-limit assertion.

## Proof ledger

| Stage | Base | Establishes |
|---|---|---|
| `EXACT_RATIONAL_SAMPLES` | `PRA` | For a rational step-pair p, rational periodic polygonal detector h, and dyadic q, the translated partition and O_h(q;p) are finite rational data computable by bounded exact arithmetic. |
| `BOUNDED_LINEAR_OBSERVABLE` | `RCA_0` | Cauchy-Schwarz gives |O_h(t;p)-O_h(t;p')|^2<=2 norm_2(h)^2 d(p,p')^2. Thus the rational smeared functional is linear and extends uniquely and boundedly to the coded energy completion. |
| `OBSERVABLE_LIPSCHITZ_BOUND` | `PRA` | With K=Lip(h)(norm_1(a)+norm_1(b)), change of variables and the polygonal Lipschitz inequality give |O_h(t;p)-O_h(s;p)|<=K d_circle(t,s) first for rational s,t. |
| `FINITE_DYADIC_INTERPOLANT` | `PRA` | A_m is the periodic rational polygonal interpolation of the 2^m+1 exact samples O_h(j/2^m;p); it is a finite code. |
| `UNIFORM_INTERPOLATION_BOUND` | `RCA_0` | The rational Lipschitz map has a unique real-time extension, and every t between adjacent dyadic nodes satisfies |A_m(t)-O_h(t;p)|<=K 2^-m; hence the same bound holds uniformly on every coded bounded interval. |
| `EXPLICIT_CUTOFF` | `PRA` | Let ell(K) be the least natural ell with K<=2^ell, taking ell(0)=0. The primitive-recursive cutoff N(k)=k+ell(K)+1 gives K 2^-N(k)<=2^-(k+1)<2^-k. |
| `UNIFORM_RECONSTRUCTION` | `RCA_0` | The subsequence A_N(k) is a prescribed-rate uniform Cauchy name for O_h on the coded circle and therefore converges uniformly on every rational bounded time interval with the displayed cutoff. |

## Exact fixtures

| Initial datum | K | Cutoff | Exact approximation checks |
|---|---:|---|---:|
| `TRIANGLE_RIGHT` | `[2, 1]` | `N(k)=k+2` | 6 |
| `QUARTER_MIXED` | `[4, 1]` | `N(k)=k+3` | 6 |
| `NONUNIFORM_MIXED` | `[6, 1]` | `N(k)=k+4` | 6 |

Each approximation row records the exact grid size, rational uniform bound, requested tolerance, and SHA-256 digest of every exact rational sample. The independent checker regenerates those samples and also tests the interpolants on a strictly finer rational grid.

## Reproduction

```text
python3 foundations/build_coded_wave_observable_reconstruction.py --check
python3 foundations/check_coded_wave_observable_reconstruction.py
python3 foundations/verify_coded_wave_observable_reconstruction.py
python3 -m unittest foundations.tests.test_coded_wave_observable_reconstruction
```

## Boundaries

- This does not establish that RCA_0 is necessary or the weakest base.
- This does not establish uniform reconstruction for unnamed convergent data without a supplied rate or finite rational code.
- This does not establish reconstruction of the full wave state from this one smeared observable.
- This does not establish a point-local field observable or probability rule.
- This does not establish a localized spacetime-distributional weak equation.
- This does not establish finite propagation, causal support, or an advanced/retarded Green operator.
- This does not establish a variable-coefficient, curved-spacetime, biwave, or metric-BV theorem.
- This does not establish empirical calibration of the detector profile.
- This does not establish a new LORENTZIAN-CAUSAL result.
