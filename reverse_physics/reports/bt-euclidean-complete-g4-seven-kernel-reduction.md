# BT complete-g4 seven-kernel reduction and signed power carrier

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SEVEN_KERNEL_REDUCTION_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

Lifecycle:
`SEVEN_KERNEL_REDUCTION_AND_ISOLATED_POWER_CARRIER_PROVED_COMBINED_BOUND_OPEN`

## Result

The fourteen unfactorized entries in the generic-\(L\) two-loop atlas are not
fourteen independent estimates.  Replacing \(p\) by \(-p\), followed by the
loop-variable change \(q\mapsto-q,\ r\mapsto-r\), pairs them exactly as


```text
(1,4), (2,5), (3,6), (7,10), (8,11), (9,12), (13,14).
```

The large-volume problem therefore has seven, not fourteen, signed kernels.
The coefficients of the seven representatives are


```text
324, 324, -432, -216, -108, 180, 48.
```

The last pair is a positive quartic-score square.  The fourth pair is the
dangerous negative one-soft carrier isolated below.

## Exact paired-quartic identity

Put


\[
 w=\omega_k,\quad v=\omega_r,\quad
 u=\omega_{k+r},\quad t=\omega_{k-r},
\]

and define


\[
 x=w+v-u=B(k,r),\qquad y=w+v-t=B(k,-r),
 \qquad C=\sum_{j=1}^4\omega_{k,j}\omega_{r,j}.
\]

The one-axis lattice identity


\[
 \omega_j(k+r)+\omega_j(k-r)
 =2\omega_j(k)+2\omega_j(r)-\omega_j(k)\omega_j(r)
\]

gives \(x+y=C\).  Direct reduction of the certified quartic kernel gives


\[
 \boxed{24K_4(k,-k,r,-r)
 =x^2+y^2+2(w+v)C+4wv.}
\]

Every term on the right is nonnegative.  Since
\(0\le C\le wv\), \(w+v\le32\), and
\(|x|,|y|\le2\sqrt{wv}\), one obtains the uniform two-sided estimate


\[
 \boxed{\frac{wv}{6}\le K_4(k,-k,r,-r)
 \le\frac{19}{6}wv.}
\]

This is stronger than a generic soft-leg estimate: it fixes the sign and the
correct product scale for every pair of lattice momenta.

## Momentum-dependent tadpole

Define


\[
 G_1(L)=\sum_{r\ne0}\frac1{\omega_r},\qquad
 Y_L(k)=\sum_{r\ne0}\frac{K_4(k,-k,r,-r)}{\omega_r^2}.
\]

The dispersion bound \(\omega_r\le16\) gives
\((N-1)/16\le G_1(L)\).  The centered max-norm shell count used in the
preceding certificate gives


\[
 G_1(L)\le L^2\{2R(R+1)+H_R\}\le2N,
 \qquad R=\lfloor L/2\rfloor.
\]

Consequently


\[
 \frac{\omega_kG_1(L)}6
 \le Y_L(k)
 \le\frac{19\omega_kG_1(L)}6
 \le\frac{19}{3}N\omega_k.
\]

In particular, \(Y_L(k)\) is positive; it cannot be discarded by a sign
argument.

## A rigorous negative \(L^2\) carrier

The inversion pair formed by atlas rows 7 and 10 factorizes exactly as


\[
 T_L=-\frac{216}{N}\sum_{q\ne0,-p}
 \frac{K_3(p,q,-p-q)^2Y_L(q)}
 {\omega_q^4\omega_{p+q}^2}.
\]

Thus \(T_L<0\).  To obtain a volume lower bound on its magnitude, no
asymptotic integral is needed.  Retain only the transverse lowest mode
\(q=e_2\).  If \(w=\omega_p\), then


\[
 \omega_q=w,\qquad \omega_{p+q}=2w,\qquad
 K_3(p,q,-p-q)=-\frac23w^2.
\]

The lower tadpole bound therefore yields


\[
 T_L\le-\frac{4G_1(L)}{N\omega_p}
 \le-\frac{N-1}{4N\omega_p}.
\]

Using \(\sin(\pi/L)\le\pi/L\) and \(N=L^4\),


\[
 \boxed{T_L\le
 -\frac{624}{625}\frac{L^2}{16\pi^2},\qquad L\ge5.}
\]

This proves that the negative one-soft term has at least quadratic magnitude.
On the previously certified tuned branch,
\(g_L^2\log L\to8\pi^2/5\), so \(g_L^4|T_L|\) diverges.  A termwise
order-\(g^4\) uniform estimate is therefore impossible.  This is a method
obstruction, not divergence of the sum: the other six kernels can still
cancel \(T_L\) at the same \(N\omega_p\) scale.

## Supporting generic-volume scan

The low-memory binary64 evaluator streams the seven exact formulas with
\(O(L^4)\) memory.  It gives


| \(L\) | seven-kernel sum | sum/\(N\omega_p\) |
|---:|---:|---:|
| 5 | -16.5260210439 | -0.0191333459 |
| 6 | -23.1188861467 | -0.0178386467 |
| 7 | -30.4783503985 | -0.0168574763 |
| 8 | -38.6111483193 | -0.0160921272 |

The persistent negative ratio supplies the target for the analytic
hard/one-soft/all-soft calculation.  It is supporting evidence only: four
volumes do not prove an asymptotic sign or coefficient.

## What changed in the barrier

The previous gate asked for bounds on fourteen opaque affine integrands.  The
new exact structure says instead:


1. only seven inversion-paired kernels are independent;
2. the paired quartic tadpole has a fixed positive sign and exact product
   bounds;
3. one nested term is rigorously negative and of order at least \(L^2\);
4. running coupling cannot control the pieces separately;
5. any successful perturbative estimate must compute a cancellation among
   all seven \(N\omega_p\) carriers before restoring the already bounded
   factorized sector and the lower-loop terms.

The active calculation is now the common power coefficient of these seven
kernels.  If it is nonzero, the tuned fixed-order route is obstructed.  If it
cancels, the remainder needs a polylogarithmic bound before returning to the
whole-composite nonperturbative score.

## Claim boundary

This result does **not** establish the sign or scaling of the seven-kernel
sum, complete \(M_4\), divergence of the perturbative series, divergence or
boundedness of the actual Gibbs score, the interacting \(H^{-1}\) moment,
tightness, or a continuum limit.  It supplies no Born rule, Krein
reconstruction, or `LORENTZIAN-CAUSAL` statement.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_seven_kernel_reduction.py --check
ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_seven_kernel_decision.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_seven_kernel_reduction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_seven_kernel_reduction
ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_seven_kernel_preflight.py --smoke
```

## Verification receipt

Tier 0: changed Python sources compiled in 0.05 s (21,476 KB maximum RSS), and
the C evaluator compiled with `-Wall -Wextra -Werror` in 0.94 s (103,812 KB).
Every changed JSON and schema parsed with `jq`; two bounded LaTeX passes
completed in 0.80 s and 0.78 s (53,552 KB maximum RSS).  The exact staged diff
passed `git diff --check`.

Tier 1: the deterministic reduction builder, certificate builder, independent
verifier, 11 unit/adversarial-mutation tests, and bounded \(L=5\) C smoke
preflight passed in 0.04 s, 0.03 s, 0.31 s, 0.37 s, and 1.65 s (20,644 KB,
20,208 KB, 29,796 KB, 30,928 KB, and 103,800 KB maximum RSS).  Mutations cover
the inversion partition, representative flow, paired-quartic bound, carrier
bound, combined-kernel and complete-\(M_4\) promotions, the interacting
\(H^{-1}\) boundary, dependency tags, and schema closure.  The Paper 21
claim-map generator check and independent verifier passed in 0.07 s each
(31,668 KB and 28,380 KB maximum RSS).

Tier 2: the independent verifier reconstructs the seven inversion pairs from
the upstream 14-row atlas, expands the paired-quartic identity by an
independent coefficient ledger, checks the one-axis dispersion polynomial,
rederives the shell constants, transverse cubic fixture, coefficient \(-4\),
hashes, schema, and fail-closed claim boundary.  The full supporting
\(L=5,6,7,8\) scan completed in 50.19 s with 104,008 KB maximum RSS; it is
typed as binary64 supporting evidence and is not used in the proof.  The
append-only planning import accepted 1,620 nodes with no invalid item or
malformed event in 6.71 s (211,768 KB maximum RSS under
`GOMEMLIMIT=300MiB`).

Tier 3 was not run: this is a bounded
`LOCAL-ALGEBRAIC`/`EUCLIDEAN-SPECTRAL` checkpoint, Paper 21 remains a
`WORKING_DRAFT`, the seven-kernel and complete-\(M_4\) decisions remain open,
and no freeze, release, shared-core, quantum lifecycle, continuum, or paper-
theorem lifecycle was promoted.
