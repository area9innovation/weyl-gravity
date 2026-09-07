# The logical cost of removing a wave-data convergence modulus

Result: `FOUNDATIONAL_CODED_WAVE_MODULUS_REVERSAL_V1`.
Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.
Evidence status: **human proof with an independently checked exact reduction**.
The infinite reverse-mathematical proof is not proof-assistant checked.

## Result and its scope

Over `RCA_0`, the rate-free observable reconstruction principle **WR** defined
below is equivalent to `ACA_0`. The necessity already holds for one fixed
spatial profile, one fixed detector, and evaluation at time zero. Supplying a
Cauchy modulus instead makes the same reconstruction provable in `RCA_0`.

This is a representation/completion result. The dynamics and detector are
unchanged from `FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1`.
It does not say that wave propagation, laboratory measurements, or physics
requires arithmetic comprehension. The lower bound comes from recovering an
arbitrary limiting amplitude, not from propagation or infinitely many modes.
The underlying scalar completeness reversal is standard; the contribution
here is its explicit realization inside the repository's fixed observable,
including the rate-supplied comparison and exact reduction witnesses.

## Precise input and output representations

Work on the unit spatial circle. Let `D` be the rational periodic step pairs
`p=(a,b)` with each component of mean zero. Their metric is

\[
 d(p,p')^2=\int_0^1((a-a')^2+(b-b')^2)\,dx.
\]

Partitions, values, and this squared distance are finite rational codes.
These are the dense chiral energy data already used by the source theorem;
they have periodic polygonal primitives. Fix the same periodic tent detector

\[
 h(x)=\begin{cases}2x&0\le x\le1/2,\\2-2x&1/2\le x\le1,\end{cases}
 \qquad O_p(t)=\int_0^1h(x)[a(x-t)+b(x+t)]\,dx.
\]

An input is a set coding a sequence `p_n` in `D`, with `d(p_n,0)^2<=1`
for every `n`, and the **ordinary Cauchy promise**

\[
 \forall k\ \exists N\ \forall m,n\ge N\quad
 d(p_m,p_n)^2\le 2^{-2k}.\tag{C}
\]

There is no function selecting the `N`'s in the input, no named limit state,
and no convergence oracle. A completed energy-state name would already
supply the missing information and would change this problem.

An output is a sequence of rational periodic polygonal functions `A_k` with

\[
 \forall l\ge k\quad \|A_l-A_k\|_\infty\le2^{-k}.\tag{F}
\]

It represents a continuous limit `O`. Require ordinary uniform convergence
`O_{p_n}->O`, without requiring a rate from the input sequence to this limit.
This is expressible in second-order arithmetic: evaluate the fast polygonal
name at rational times, express real inequalities using its prescribed error,
and quantify over rational `t` in `[0,1]`. No supremum real or function space
as a set of all points is an input. For two rational polygons their uniform
distance is the maximum at their combined breakpoints. The name supplies its
own continuity modulus by approximation with an explicitly Lipschitz polygon.

**WR** says that every input satisfying (C) and the unit bound has such an
output. It has the form `forall input exists output`; it does not assert the
existence of a higher-type functional choosing outputs for all inputs.
Periodicity makes convergence uniform on every bounded time interval as well.

**WR_mu** is the identical assertion with a supplied function `mu(k)`
witnessing (C). The theorem is

\[
 \mathsf{RCA}_0\vdash\mathrm{WR}_{\mu},\qquad
 \mathsf{RCA}_0\vdash(\mathrm{WR}\leftrightarrow\mathsf{ACA}_0).
\]

## Upper bound and the supplied-rate construction

Finite integration and Cauchy--Schwarz give, uniformly in rational time,

\[
 |O_p(t)-O_{p'}(t)|^2\le {2\over3}d(p,p')^2\le d(p,p')^2.
\]

For unit-ball data, `||a||_1+||b||_1<=2`, so the time Lipschitz constant is
at most `4`, using `Lip(h)=2`. These rational inequalities extend to the
individual named real-time observables by the existing construction.

In `ACA_0` the arithmetic predicate
`S(j,N) := forall m,n>=N d(p_m,p_n)^2<=2^(-2j)` defines a set.
Use (C) to take its least witness for each `j`, and let `N(j)` be the maximum
of these witnesses through `j`. This is a nondecreasing modulus. In `WR_mu`,
take `N(j)=max_{i<=j} mu(i)` directly in `RCA_0`; no comprehension beyond the
base is used.

Let `I_m` denote interpolation at dyadic times of mesh `2^-m`. Set

\[
 A_k=I_{k+5}\,O_{p_{N(k+3)}}.
\]

Every sample is a rational integral of the existing step data against the
tent. The interpolation error is at most
`4*2^(-k-5)=2^(-k-3)`. For `l>=k`, monotonicity of `N` gives

\[
 \|A_l-A_k\|_\infty
 \le 2^{-l-3}+2^{-k-3}+2^{-k-3}
 \le {3\over8}2^{-k}<2^{-k}.
\]

Thus (F) holds, and evaluation produces fast real names in `RCA_0`.
For `n>=N(k+3)`, the distance from `O_{p_n}` to `A_k` is at most
`2^(-k-2)`. Since `||O-A_k||_infty<=2^-k`, using index `k+2` proves
`||O_{p_n}-O||_infty<=2^-k` for `n>=N(k+5)`. This proves the required
ordinary uniform convergence with room in the constants. Uniqueness follows
from the triangle inequality. Only selecting the input modulus used `ACA_0`.

## Lower bound: a visible one-dimensional amplitude

Use the fixed mean-zero step profile

\[
 g(x)=\begin{cases}1&1/4\le x<3/4,\\-1&\text{otherwise},\end{cases}
 \qquad p(q)=(qg,0).
\]

Its squared norm and detector pairing are exactly

\[
 \|g\|_2^2=1,\quad \int g=0,\quad
 \int hg={1\over4},\quad
 d(p(q),p(q'))^2=(q-q')^2.\tag{R}
\]

In particular `O_{p(q)}(0)=q/4`: the detector does not annihilate the
encoded amplitude. No inverse PDE problem is being assumed. At all times
`O_{p(q)}(t)=q F(t)`, where the exact periodic response is

\[
 F(t)=\begin{cases}
 1/4-4t^2&0\le t\le1/4,\\
 4t^2-4t+3/4&1/4\le t\le3/4,\\
 1/4-4(t-1)^2&3/4\le t\le1.
 \end{cases}
\]

Let `f:N->N` be arbitrary, with any allowed set parameters. Duplicates are
counted only once. Define finite rational data

\[
 E_s=\{f(j):j<s\},\quad w_e=4^{-(e+1)},\quad
 q_s=\sum_{e\in E_s}w_e,\quad p_s=p(q_s).\tag{E}
\]

Each `E_s` is a finite list with duplicate removal, not the infinite range
set. These codes exist by recursive comprehension. Finite geometric sums
give `0<=q_s<1/3`; the sequence is nondecreasing. Thus all `p_s` lie in the
specified unit ball and keep exactly the same spatial profile and detector.

### Why the Cauchy promise is available in RCA_0

It would be circular to obtain a modulus by first collecting the range of
`f`. Instead use bounded monotonicity. If (C) failed for the scalar `q_s`,
some fixed `k` would permit, beyond every index, a pair with difference
greater than `2^-k`. Monotonicity then permits a later term more than
`2^-k` above the term at the current index. Repeated finite search constructs
an increasing index chain with `2^k` such increments. Its last value exceeds
`1`, contradicting `q_s<1/3`.

Existence of a finite chain of length `r` is a Sigma-0-1 formula relative to
`f`; Sigma-0-1 induction suffices for this argument. It proves
`forall k exists N`, not the existence of a sequence of witnesses `N(k)`.
By (R) it is exactly the required energy Cauchy promise. There is no use of
monotone convergence to a real in this step.

### The output decides the range

Apply WR and evaluate its output at zero. After the fixed index shift for
multiplication by four, `r_k=4 A_{k+2}(0)` is a fast rational name for
`r=4O(0)`, with `|r-r_k|<=2^-k`. The scalar sequence `q_s` converges to `r`.
Monotonicity implies `r>=q_s` for every `s`. The following complementary
predicates are Sigma-0-1 relative to the output name and `f`:

\[
 \begin{aligned}
 e\in\operatorname{ran}(f)
 &\iff \exists j\ f(j)=e,\\
 e\notin\operatorname{ran}(f)
 &\iff \exists s,k\ [e\notin E_s\ \wedge\
                r_k+2^{-k}-q_s<w_e].\tag{D}
 \end{aligned}
\]

For the second implication from right to left, if `e` appeared after `s`,
the eventual increase would be at least `w_e`, contradicting the displayed
strict upper bound on `r-q_s`. It has not appeared before `s` either.
Conversely, when `e` never appears, convergence gives an `s` with
`r-q_s<w_e/2`. Choosing `k` with `2*2^-k<w_e/2` yields the strict rational
inequality in (D). Only the existence of these witnesses for each `e` is
used; no convergence rate of `q_s` is extracted or assumed.

Delta-0-1 comprehension therefore produces the range of every `f`.
The standard range-existence characterization gives `ACA_0` over `RCA_0`.
Equivalently one can replace `E_s` by bounded discovery sets for an arbitrary
Sigma-0-1 predicate and obtain Sigma-0-1 comprehension directly, with set
parameters retained. This completes the reverse implication.

## Attribution and what is new here

The scalar coding/comprehension argument follows the established reversal
method in Stephen G. Simpson, *Subsystems of Second Order Arithmetic*,
second edition, Chapter I, Theorem I.9.1 and the summary of Section III.1
on printed page 47. The author's [Chapter I](https://sgslogic.net/t20/sosoa/chapter1.pdf)
was checked on 2026-09-07; its complete downloaded bytes have SHA-256
`c3ec4d883a2346deb3780f14791df237f90b78ca3610596fb21ac622d4ca23ce`.
The new certificate records this bibliographic verification separately from
locally replayable inputs; the PDF is not vendored or required at test time.

The wave reduction, fixed detector visibility, two input contracts, explicit
upper-bound interpolation, and scoped consequence are supplied here.
This does not claim a new scalar completeness theorem or a literature-first
reverse-mathematical classification of waves.

## Independent audit and adversarial controls

The producer integrates the original tent against translated step data and
fits the response pieces using exact rational samples. The independent
verifier imports neither producer nor source wave implementation. It derives
the response polynomials from
`F'(t)=2[h(t+3/4)-h(t+1/4)]`, the computed pairing at zero, and exact
continuity. Equality of their rational coefficients checks whole pieces,
not just a numerical time grid.

The verifier also checks the geometric-series identity, unit norm, gain,
metric scaling, upper-bound error budget, delayed-discovery range witnesses,
source hashes, proof-report hash, schema, and fail-closed flags. Tests mutate
the detector gain, response coefficient, error budget, tail bound, evidence
boundary, duplicate handling, and delayed-discovery case. Digest-valid
mutations must still fail the independent mathematical checks.

An additional avoidance control uses the mean-zero profile `+1` on the first
half circle and `-1` on the second. Its pairing with `h` at zero vanishes, so
time-zero data on that profile alone cannot support this reduction. This is
a control on the evaluation map, not an all-time observability no-go.

The exact audits establish these finite identities and reduction witnesses.
They do **not** mechanically verify the quantified comprehension argument,
the Cauchy-chain induction, or the infinite uniform-limit proof. Those are
the human proof above. No atlas cell, theory passport, paper theorem, or
quantum lifecycle state is promoted by this package.

## Reproduction

```text
python3 foundations/build_coded_wave_modulus_reversal.py --check
python3 foundations/verify_coded_wave_modulus_reversal.py
python3 -m unittest foundations.tests.test_coded_wave_modulus_reversal
```

The dated tier receipt is
`foundations/receipts/coded-wave-modulus-reversal-v1-validation.json`.
It records exact commands, elapsed times, and test-tier dispositions.

## Boundaries and remaining work

- No proof-assistant formalization or independently checked infinite proof.
- No promotion of the earlier finite-input theorem to an unrestricted one.
- No claim that the encoded limit is a physical preparation or probability.
- No causal support, Green operator, Weyl BV, QME, or continuum-limit result.
- No equivalence for arbitrary alternative representations or all detectors.
- No impossibility claim for finite, prescribed-rate, or finite-precision
  calculations; their information contracts differ.
- No new atlas, passport, paper, or quantum lifecycle promotion.

The result answers the requested necessity question for one precise weaker
input representation. The next mathematical review target is the quantified
RCA_0 proof, especially the induction and Delta-0-1 definitions; the exact
fixture rail must not substitute for that review.

CLOSE-OUT: DONE — both directions for WR and the supplied-modulus comparison are proved in the stated human-proof scope, with an exact independent reduction audit.
EVIDENCE: foundations/results/FOUNDATIONAL_CODED_WAVE_MODULUS_REVERSAL_V1.json
