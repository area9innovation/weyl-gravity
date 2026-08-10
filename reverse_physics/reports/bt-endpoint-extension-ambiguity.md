# BT endpoint-extension ambiguity

**Result:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

**Certificate:**
[`REVERSE_PHYSICS_BT_ENDPOINT_EXTENSION_AMBIGUITY_V1`](../certificates/REVERSE_PHYSICS_BT_ENDPOINT_EXTENSION_AMBIGUITY_V1.json)

## Result

The endpoint problem is not merely a divergent integral.  The exact
dimensionless shape of the ordered-slot cross Gram derived from (R_t) is

\[
 h(z)=-\frac{1-3z+3z^2}{2z^3(1-z)^3}
     =-\frac12\left(\frac1{z^3}+\frac1{(1-z)^3}\right).
\]

A distribution of scaling degree three at either endpoint is not unique.
At (z=0) its extension may be changed by

\[
 c_0\delta_0+c_1\delta'_0+c_2\delta''_0.
\]

Reflection symmetry relates the two endpoints but does not remove the three
constants.  The complete reflection-even ambiguity is

\[
 \sum_{n=0}^2c_n\left(\delta_0^{(n)}+(-1)^n\delta_1^{(n)}\right).
\]

The independent verifier checks its rank on the three even endpoint probes
(1), (z(1-z)), and (z^2(1-z)^2).

Two exact, reflection-even extensions already prove nonuniqueness.  The
triple-plus extension gives

\[
 \langle h_{+++},1\rangle=0,
\]

whereas the symmetric sharp-cutoff Hadamard finite part gives

\[
 \operatorname{FP}\langle h,1\rangle=\frac12.
\]

Their difference is an allowed endpoint distribution.  More generally,
adding (c_0(\delta_0+\delta_1)) changes the inclusive constant response by
(2c_0).  Starting from the plus extension, choosing
(c_0=1/96) yields (1/48).  That demonstrates tunability; it is forbidden
as a derivation because it simply fits the known target.

## Meaning for the probability

The interior nonlinear (R_t) kernel, reflection symmetry, and finite scaling
degree do **not** predict the needed `1/48`.  The coefficient can only become
physical if the omitted oscillatory creation terms, the (Q_t) squeezed
vacuum, projector idempotence, and a common incoming/outgoing resolution flow
provide a dynamical matching condition that fixes all three endpoint
constants.

This is an exact obstruction to a unique ordinary endpoint extension, not a
proof that BT's full construction cannot produce `1/48`.  It leaves the full
NLO quotient trace and physical probability `NOT_ESTABLISHED`.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_endpoint_extension_ambiguity.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_endpoint_extension_ambiguity.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_endpoint_extension_ambiguity
```

The producer uses exact rational polynomial jets.  The verifier independently
checks the partial fraction, two inequivalent extensions, rank-three symmetric
ambiguity, input hashes, and claim boundary.  The scoped rail passes 13/13,
7/7, and 4/4 respectively under the 500000 KB cap; peak RSS remains below
31 MB.  Tier 2 and Tier 3 were not run because this classification changes no
shared input or promoted theorem.  Those skipped tiers are not passes.

Primary source boundary: [Bateman--Turok, arXiv:2607.00096v1](https://arxiv.org/abs/2607.00096),
Eq. (16), Eq. (19), and Appendix C.  The distribution classification is a
repository result and makes no `LORENTZIAN-CAUSAL` claim.
