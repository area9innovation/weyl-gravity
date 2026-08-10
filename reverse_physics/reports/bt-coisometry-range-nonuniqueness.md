# BT coisometry range nonuniqueness

**Result:** `CLASSIFIED`

**Scope correction:** `SCOPE_RESTRICTED_TO_NONPERTURBATIVE_OR_DISCONNECTED_BRANCHES`

The later certificate
`REVERSE_PHYSICS_BT_PERTURBATIVE_COISOMETRY_RIGIDITY_V1` proves that the
published free cross-CCR fixes \(R_t^\dagger R_t=1\) at leading order and that
projection idempotence forbids every formal perturbative defect.  The finite
family below remains a correct theorem about arbitrary coisometries, but it is
not a model of the analytic BT branch.

The right-unit identity by itself does not determine the probability pushforward.
For (Pi=R^sharp R) and (A=RPR^sharp), exact multiplication gives

\[
A^2-A=-RP(1-\Pi)PR^\sharp,
\qquad \operatorname{tr}A=\operatorname{tr}(P\Pi).
\]

Thus both idempotence and probability depend on the unreported range/defect
overlap.  An exact Krein witness uses input metric
(G=\operatorname{diag}(1,-1,1)), output metric
(J=\operatorname{diag}(1,-1)), and fixed coisometry
(R=(I_2\;0)).  The rational rank-one projectors

\[
v_t=\frac{(1-t^2,0,2t)}{1+t^2},\qquad P_t=v_tv_t^\sharp
\]

all satisfy the same (RR^sharp=I_2), while their pushed traces at
(t=0,1/3,1/2,1) are respectively

\[
1,\quad\frac{16}{25},\quad\frac9{25},\quad0.
\]

The target (1/48) is compatible: over (mathbb Q(\sqrt{47})), take a
range-defect projector with diagonal ((1/48,0,47/48)) and off-diagonal
(\sqrt{47}/48).  But nothing in (RR^sharp=1) selects it.

Therefore the missing datum is precisely (Pi=R_t^dagger R_t), or
equivalently (P_chi(1-Pi)P_chi), on the continuum projector domain.  The
Letter's pullback formulas and negative-charge radical do not provide it.  The
`1/48` Gram, quotient trace, and complete probability remain uncomputed.

Verification:

```text
ulimit -v 500000; python3 reverse_physics/bt_coisometry_range_nonuniqueness.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_coisometry_range_nonuniqueness.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_coisometry_range_nonuniqueness
```

This exact `LOCAL-ALGEBRAIC`/`REDUCED-MODE` witness does not claim the BT
completion is inconsistent, does not lift to gravity, and makes no
`LORENTZIAN-CAUSAL` claim.  Primary source: [Bateman--Turok](https://arxiv.org/abs/2607.00096),
Eq. (19) and Appendix C.
