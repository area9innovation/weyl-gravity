# How much source information suffices for a detector prediction?

Result: `FOUNDATIONAL_WAVE_DETECTOR_RECOVERY_BENCHMARK_V1`.
Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.
Disposition: **standard optimal-recovery specialization; retain as a benchmark**.

## Outcome in plain language

A finite set of source measurements can certify a future wave-detector
reading without specifying the entire initial wave. The interval is sharp:
we explicitly construct two sources compatible with the same measurements
that attain its opposite endpoints. No method using only those measurements
and the declared energy bound can give a smaller worst-case error.

For the particular normalization and detector tested here, 16 equal source
cells suffice for error at most `1/16` when the reported averages are zero
and their aggregate error is at most `1/16`. Eight cells do not suffice.
This comparison holds at the three tested delays, not for all delays or
arbitrary data. The certificate makes the comparisons using exact squared
rational inequalities, without rounding square roots.

This is an answer to the feasibility study, not a new general recovery
principle. Its proof uses familiar orthogonal projection and Cauchy--Schwarz.
The research decision is to stop expanding this simple example as a novelty
claim. It is useful as a regression benchmark for a future problem with a
specific physical constraint or more substantive dynamics.

## The measurement contract

Use the unit circle and a real, right-moving mean-zero source `a` in `L2`,
with `integral a^2 <= 1`. Set the other chiral component `b=0`. This is an
explicit restriction of the existing scalar chiral carrier, not the full
Weyl or gravitational field space. The observable is the previously defined
chiral amplitude, not an assertion about a calibrated physical instrument.

Retain the source certificate's periodic tent detector `h`, with values
`0,1,0` at `0,1/2,1`. Average its reading over a nonzero exposure `tau=1/8`:

\[
 J_T(a)=\frac1\tau\int_T^{T+\tau}\int_0^1h(x)a(x-t)\,dx\,dt.
\]

The detector is spatially smeared over the circle and temporally averaged;
it is not point evaluation or a strictly band-limited instrument. Change of
variables gives `J_T(a)=<k_T,a>` with

\[
 k_T(y)=\frac1\tau\int_T^{T+\tau}h(y+t)\,dt-\frac12.
\]

The constant subtraction is legitimate because `a` has mean zero. Every
`k_T` is a mean-zero periodic piecewise quadratic polynomial. The tested
source measurements are averages on `N` equal cells. Let `C_N` be the
orthogonal projection onto cellwise constants. The constant direction is
removed automatically for mean-zero sources; this `C_N` is a measurement
projection, distinct from the classical BV homological projection `pi_cl`.

Two distinct input contracts are tested:

1. **Exact nonzero data:** the true cell averages are specified exactly.
2. **Noisy zero readings:** every reported average is zero, and the true
   averages `m_j` obey `(1/N) sum_j m_j^2 <= eta^2`.

The latter is an aggregate deterministic error bound on the normalized
measurement vector. It is neither independent noise on every cell nor a
probability distribution. Arbitrary nonzero noisy readings are not solved
by this benchmark. These are observations of the actual source, not merely
entries in an approximation sequence with an unknown relation to its limit.

## Exact observations: interval and matching sources

Write `u=C_N k_T`, `v=k_T-u`, `A=||u||^2`, `B=||v||^2`, and `K=A+B`.
Let `m=C_N a` be the known cellwise-constant source. Feasibility requires
`m` mean zero and `||m||^2<=1`. Then

\[
 J_T(a)\in[c-r,c+r],\qquad
 c=\langle k_T,m\rangle,\qquad
 r^2=(1-\|m\|^2)B.
\]

Indeed, `a=m+z` with `C_N z=0`, so
`J_T(a)=c+<v,z>` and `||z||^2<=1-||m||^2`. Cauchy--Schwarz gives the
bound, with equality at

\[
 a_\pm=m\pm\sqrt{\frac{1-\|m\|^2}{B}}\,v.
\]

All tested cases have `B>0`. The two sources have exactly the same observed
averages, mean zero, unit energy, and readings `c+-r`. Thus `c` is the minimax
prediction even among nonlinear algorithms: any output has error at least
`r` on one of these two sources. The tested nonzero data are the alternating
cell means `m_j=(-1)^j/2`, whose squared norm is `1/4`.

The endpoints are algebraically named piecewise quadratic sources in the
completed `L2` carrier. They need not be rational step functions. No unnamed
limit or oracle is required to specify them. Their finite polynomial
integrals and algebraic normalization are checked exactly.

## Noisy zero readings: sharp error radius

The possible sources satisfy `||a||<=1` and `||C_N a||<=eta`. The set is
symmetric, so zero is the minimax prediction. Its exact worst-case radius is

\[
 R(\eta)=
 \begin{cases}
 \sqrt K,&\eta^2K\ge A,\\
 \eta\sqrt A+\sqrt{(1-\eta^2)B},&\eta^2K<A.
 \end{cases}
\]

For a proof put `s=||C_N a||`. Orthogonality and Cauchy--Schwarz bound the
reading by `sqrt(A)*s+sqrt(B)*sqrt(1-s^2)`, with `0<=s<=min(eta,1)`.
This expression increases up to `s^2=A/K` and then decreases; its maximum
is the displayed formula. This is an elementary scalar optimization, not a
new spectral or existence theorem.

In the first branch an endpoint source is `a_+=k_T/sqrt(K)`. In the second,

\[
 a_+=\frac\eta{\sqrt A}u+
       \sqrt{\frac{1-\eta^2}{B}}v.
\]

Take `a_-=-a_+`. Both are compatible with the same zero report by choosing
observation error `-C_N a_+` or `-C_N a_-`. They are not claimed to have
identical true cell averages when `eta>0`. They have unit source energy and
attain `+-R`. If `A=0`, the first branch applies and no division by `A` is
needed. All certified `B` are positive.

This resolves existence, construction, and certification for these finite
input contracts. It does not assert a new `RCA_0`/`ACA_0` equivalence.
The exact finite computations use rational arithmetic and positive square
roots; the general Hilbert-space argument above is a human proof, not an
infinite proof checked by a proof-assistant kernel.

## Exact results and a finite-accuracy decision

For all tested delays, `K=151/1920`. Here is the unseen detector energy `B`:

| Source cells | Delay 0 | Delay 1/8 | Delay 1/4 |
|---|---:|---:|---:|
| 2 | 781/11520 | 301/11520 | 301/11520 |
| 4 | 11/720 | 11/720 | 11/720 |
| 8 | 23/5760 | 23/5760 | 23/5760 |
| 16 | 49/46080 | 49/46080 | 49/46080 |

For exact zero readings the squared uncertainty is `B`. For the declared
nonzero alternating readings it is `3B/4`. Delay can change what the
measurements reveal: the two-cell case illustrates this explicitly. The
identical values at finer grids reflect the tested alignment symmetries,
not a universal statement of time independence.

At zero reported averages and `eta=1/16`, the radii for 8 and 16 cells are

\[
 R_8=\sqrt{43/147456}+\sqrt{391/98304}>1/16,
\]
\[
 R_{16}=\sqrt{715/2359296}+\sqrt{833/786432}<1/16.
\]

The comparison uses the following exact test for nonnegative `p,q,e`:
`sqrt(p)+sqrt(q)<=e` iff `e^2-p-q>=0` and `(e^2-p-q)^2>=4pq`.
No floating-point evaluation enters the decision. There are 12 detector/grid
cases, 12 nonzero exact-data endpoint pairs and 48 noisy endpoint pairs,
including zero noise and inactive-noise-constraint cases.

## Relation to the previous modulus obstruction

There is no contradiction with
`FOUNDATIONAL_CODED_WAVE_MODULUS_REVERSAL_V1`. That result starts with an
arbitrary Cauchy sequence of source approximations without a rate. The
current result starts with finite measurements guaranteed to constrain the
actual source. That guarantee is additional information.

More source measurements can reduce the unseen component `v`, while noise
can leave a nonzero error floor. Finite detector resolution alone does not
supply either an observation-error bound or an approximation modulus.
The present result identifies a concrete alternative information contract;
it does not claim to solve the rate-free input problem.

## Novelty assessment and stop decision

Optimal recovery already formulates prediction from a model set and linear
observations as a worst-case problem, including inaccurate Hilbert-space
data. See Simon Foucart and Chunyang Liao,
[*Optimal Recovery from Inaccurate Data in Hilbert Spaces: Regularize, but
what of the Parameter?*](https://arxiv.org/abs/2111.02601).
The [author-hosted full text](https://foucart.github.io/publi/ORHilbert_Reg2.pdf)
was read for its framework and input conventions; the retrieved PDF hash is
pinned in the certificate, but the PDF is not vendored or replayed locally.

The projection/endpoint proof here is a direct specialization of standard
Hilbert geometry. The rational wave kernel, exact noise branches, and
matched source fixtures make that specialization executable. They do not
support a claim of a new general optimal-recovery theorem. The literature
review is targeted, not exhaustive; it is sufficient to avoid presenting
this elementary mechanism as new.

**Stop decision:** retain this small benchmark and do not grow it into a
standalone novelty claim merely by adding grids, delays, or certificates.
A successor would need a specified physical constraint, observation geometry,
or nontrivial dynamics for which an existing recovery theorem does not
already supply the desired result. Candidate selection belongs in the roadmap.

## Reproduction and receipt

```text
python3 foundations/build_wave_detector_recovery.py --check
python3 foundations/verify_wave_detector_recovery.py
python3 -m unittest foundations.tests.test_wave_detector_recovery
```

The producer constructs the kernel using the integrated tent primitive and
exact polynomial interpolation. The independent verifier reconstructs it
from `k_T'(x)=[h(x+T+tau)-h(x+T)]/tau`, an independently integrated initial
value, and continuity. It checks every polynomial coefficient, cell integral,
norm split, endpoint feasibility, equality case and finite-accuracy decision.
Neither computation imports the other. Mutation tests reseal the payload
digest, so a changed mathematical witness must fail for mathematical reasons.

`foundations/receipts/wave-detector-recovery-benchmark-v1-validation.json`
records commands, elapsed times, imported hashes and test-tier dispositions.

## Assumptions and non-claims

- Unit-circle scalar right-moving chiral model, unit energy bound, fixed
  periodic tent, exposure `1/8`, declared cells, delays and noise convention.
- A mathematically specified source-observation contract, not a laboratory
  calibration, random-error model, probability law or empirical prediction.
- Explicit algebraic endpoint sources in `L2`; no rational-only endpoint claim.
- No arbitrary nonzero noisy-data solution, continuum reconstruction, causal
  Green theorem, Weyl BV, Lorentzian QME, or quantum lifecycle promotion.
- No new general recovery theorem, weakest-foundation classification,
  proof-assistant-checked infinite proof, or atlas/paper promotion.

CLOSE-OUT: DONE — sharp finite-data detector intervals and matching sources are obtained; the mechanism is standard and retained as a benchmark.
EVIDENCE: foundations/results/FOUNDATIONAL_WAVE_DETECTOR_RECOVERY_BENCHMARK_V1.json
