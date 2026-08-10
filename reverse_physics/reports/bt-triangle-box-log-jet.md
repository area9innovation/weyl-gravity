# Bateman--Turok triangle and box logarithmic jets

**Result:** `COEFFICIENT_COMPUTED`

**Dependency:** `REDUCED-MODE`

**Certificate:**
[`REVERSE_PHYSICS_BT_TRIANGLE_BOX_LOG_JET_V1`](../certificates/REVERSE_PHYSICS_BT_TRIANGLE_BOX_LOG_JET_V1.json)

## Result

The complete two-cubic/one-quartic triangle family and four-cubic box family
have now been computed through the cut-constructible logarithmic
four-external-mass interference jet required by the Bateman--Turok projector.

Their separate collinear expansions contain the same `r^-2` and `r^-1`
enhancements found in the bubble sector.  In the sum of all three topology
families, however, both inverse powers cancel exactly:

\[
 J_B+J_T+J_X=15(L_s+L_t+L_u),
\]

and therefore

\[
 J_{\rm log}=15(3L-\ell)+O(r),
 \qquad r=t/s,\quad L=\log(\mu^2/s),\quad
 \ell=\log(-t/s).
\]

This closes the triangle/box **logarithmic** gate.  A ratio logarithm remains.
The external phase-space projector has not been applied to it, so no
real--virtual cancellation or beyond-tree probability is claimed.  Cut-free
finite rational pieces are also not determined by this calculation.

## Why the tensor integrals collapse

Let the reduced perfect-square tree amplitude be

\[
 A=E-Q,
\]

where `E` is the sum of the three cubic-exchange graphs and `Q` is the
quartic contact graph.  Direct exact reduction in

\[
 \mathbb Q(s,t)[x_1,x_2,x_3,x_4]/(x_i^2)
\]

gives

\[
 A^{(0)}=A^{(1)}=0,
 \qquad
 A^{(2)}=\frac12\sum_{i<j}x_i x_j.
\]

The external tree in the one-loop interference also begins at degree two.
Consequently only loop-amplitude terms through degree two can reach the
fourfold projector.  At those degrees, the two-body cut can use the universal
`A^(2)` rather than the unreduced exchange denominators.

For the left and right sides of a channel cut,

\[
 B=Q_LQ_R,
 \qquad
 T=-Q_LE_R-E_LQ_R,
 \qquad
 X=E_LE_R.
\]

Since `E=A+Q`, these become

\[
 T=-Q_LA_R-A_LQ_R-2Q_LQ_R,
\]

\[
 X=A_LA_R+A_LQ_R+Q_LA_R+Q_LQ_R,
\]

and hence

\[
 B+T+X=A_LA_R.
\]

This identity performs the dangerous exchange-denominator cancellation before
any large tensor reduction.  It is also the central mutation control: changing
the relative topology sign destroys the collapse.

## Arbitrary-mass channel polynomials

For channel `(a,b)|(c,d)`, write

\[
 S=(a+b)^2=(c+d)^2,\qquad T=(a+c)^2,
 \qquad x_j=p_j^2,
\]

and

\[
 \Sigma_x=x_a+x_b+x_c+x_d,
 \qquad
 \Sigma_\times=x_ax_c+x_ax_d+x_bx_c+x_bx_d.
\]

After giving the two cut lines independent masses `y,z`, including the
ordinary two-body density, and applying
`partial_y partial_z` at `y=z=0`, every topology has normalization

\[
 \partial_y\partial_z\operatorname{Cut}_{y,z}\big|_0
 =\frac1{12}P_{\rm topology}.
\]

The previously computed bubble polynomial is

\[
 P_B=7S^2+ST+T^2-(7S+T)\Sigma_x
 +x_ax_b+x_cx_d+7\Sigma_\times.
\]

The new triangle polynomial is

\[
 P_T=-\left[
 19S^2+2ST+2T^2-(25S+2T)\Sigma_x
 +3x_ax_b+3x_cx_d+32\Sigma_\times
 \right].
\]

The new box polynomial is

\[
 P_X=12S^2+ST+T^2-(18S+T)\Sigma_x
 +5x_ax_b+5x_cx_d+31\Sigma_\times.
\]

Their sum is much smaller:

\[
 P_B+P_T+P_X
 =3x_ax_b+3x_cx_d+6\Sigma_\times.
\]

It vanishes on shell in every channel, rather than only after summing crossed
channels.  At the forward on-shell point `T=0`, the generic-coupling weights

\[
 2P_B=14S^2,\qquad -P_T=19S^2,\qquad P_X/2=6S^2
\]

reproduce the three coefficients in Holdom's published expansion

\[
 (6\lambda_3^2+7\lambda_4)(\lambda_3^2+2\lambda_4)
 =6\lambda_3^4+19\lambda_3^2\lambda_4+14\lambda_4^2.
\]

This is an external normalization and topology control, not an input used to
derive the arbitrary-mass polynomials.

## Four-mass interference jets

For each topology define

\[
 J_{\rm top}=[x_1x_2x_3x_4]\,
 A\sum_{S=s,t,u}P_{{\rm top},S}L_S.
\]

Each separate answer is represented over
`s^2 t^2 (s+t)^2`.  The rows below multiply `s^(6-k)t^k`, `k=0,...,6`.
The `R_log` row comes only from Taylor expanding the kinematic argument
`L_u(x)`; it is not a cut-free finite rational loop term.

### Triangle

| part | coefficients |
|---|---|
| `L_s` | `(-19,60,154,42,28,2,-2)` |
| `L_t` | `(-2,2,28,42,154,60,-19)` |
| `L_u` | `(-19,-22,53,106,53,-22,-19)` |
| `R_log` | `(0,76,199,248,199,76,0)` |

### Box

| part | coefficients |
|---|---|
| `L_s` | `(12,-47,-90,7,0,-1,1)` |
| `L_t` | `(1,-1,0,7,-90,-47,12)` |
| `L_u` | `(12,23,5,-9,5,23,12)` |
| `R_log` | `(0,-48,-140,-185,-140,-48,0)` |

The `L_s,L_t` reversal and the palindromic `L_u,R_log` rows are exact crossing
checks.  Adding the bubble rows gives

| part | complete coefficients |
|---|---|
| `L_s` | `(0,0,15,30,15,0,0)` |
| `L_t` | `(0,0,15,30,15,0,0)` |
| `L_u` | `(0,0,15,30,15,0,0)` |
| `R_log` | `(0,0,0,0,0,0,0)` |

The apparent denominator cancels, leaving exactly
`15*(L_s+L_t+L_u)`.

Restoring normalization, each topology contributes

\[
 [x_1x_2x_3x_4]\,2\operatorname{Re}
 (M_{\rm tree}^*M_{{\rm loop,top,log}})
 =\frac{\lambda^6}{(4\pi)^2}\frac{16}{3}J_{\rm top}.
\]

## Collinear cancellation

The three expansions are

\[
 J_B=\frac{15L-\ell}{r^2}
 +\frac{-45L+3\ell-35}{r}
 -30L+8\ell+\frac{31}{2}+O(r),
\]

\[
 J_T=\frac{-40L+2\ell}{r^2}
 +\frac{120L-6\ell+95}{r}
 +35L-18\ell+\frac{43}{2}+O(r),
\]

\[
 J_X=\frac{25L-\ell}{r^2}
 +\frac{-75L+3\ell-60}{r}
 +40L-5\ell-37+O(r).
\]

Both inverse-power coefficients sum to zero.  The constants also cancel,
leaving

\[
 J_B+J_T+J_X=45L-15\ell+O(r).
\]

Thus the bubble's power-enhanced singularity was an artifact of separating a
topology family.  The surviving ratio logarithm is precisely the kind of term
that can interact with the normalization-dependent real threshold.  It has
not yet been passed through the external phase-space density or expressed in
the real calculation's normalization.

## Independent verification

The producer derives the quartic/tree cross moment using a covariant
center-of-mass decomposition and obtains the four-mass jet by sequential exact
differentiation.

The independent verifier does not import the producer.  It:

1. builds the complete tree in a 16-slot subset jet algebra;
2. derives the quartic/tree cross cut from the transverse tensor projector
   `q_mu q_nu`;
3. reconstructs all triangle and box interference rows in the subset algebra;
4. checks the published forward coefficient combination; and
5. enforces the finite-part and physical-claim boundary through a strict
   schema.

All canonical coefficients are exact integers or rational functions.  No
floating-point arithmetic is used.

## Claim boundary

This certificate computes the complete cut-constructible logarithmic
triangle and box jets on the declared reduced carrier.  It does **not**
compute or establish:

- cut-free finite rational triangle or box terms;
- the renormalized finite bubble and counterterm jet;
- lower-point and wave-function insertion contributions;
- the external four-leg phase-space projector and its moving boundaries;
- a common real--virtual infrared prescription;
- cancellation of the real reduced `-3/8` coefficient;
- a physical NLO probability, KLN theorem, or dressed-state construction;
- positivity or unitarity beyond tree level; or
- any tensor/BRST gravitational lift or anything `LORENTZIAN-CAUSAL`.

## Sources

- [Bateman and Turok, *Escape from Ostrogradsky via Hidden Ghost Parity*](https://arxiv.org/abs/2607.00096v1), Eq. (2) and Appendix B.
- [Holdom, *Running couplings and unitarity in a 4-derivative scalar field theory*](https://arxiv.org/abs/2303.06723v2), Eqs. (20)--(22).
- [Holdom, *UV-complete 4-derivative scalar field theory*](https://arxiv.org/abs/2402.09223v1), Eqs. (11)--(13).

The universal tree virtuality identity, arbitrary-mass triangle/box cut
polynomials, and four-mass interference rows are repository results.  No
literature-priority claim is made.

## Verification

```text
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 \
  reverse_physics/bt_triangle_box_log_jet.py --check
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 \
  reverse_physics/verify_bt_triangle_box_log_jet.py
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 \
  -m unittest -v reverse_physics.tests.test_bt_triangle_box_log_jet
```

All symbolic commands were run sequentially under a 500,000 KB virtual-memory
limit.  Final scoped receipt (2026-08-10):

| Tier | Command | Time | Peak RSS | Result |
|---|---|---:|---:|---|
| 0 | `py_compile` producer, verifier, and test | 0.03 s | 15,172 KB | PASS |
| 0 | `json.tool` certificate | 0.02 s | 14,124 KB | PASS |
| 0 | `json.tool` schema | 0.02 s | 14,084 KB | PASS |
| 1 producer | exact covariant cut and sequential jet reproduction | 2.96 s | 75,312 KB | PASS, 21/21 |
| 1 independent | subset tree/jet and transverse-projector verifier | 1.20 s | 74,292 KB | PASS, 15/15 |
| 1 new tests | triangle/box logarithmic jet tests | 6.51 s | 75,384 KB | PASS, 12/12 |
| affected predecessor | bubble logarithmic jet tests | 9.44 s | 78,768 KB | PASS, 10/10 |

The advisory `env -u SF_PROGRAM ci/science-forge-shadow.sh` was attempted
under the same cap and is **not** a pass.  Its `cbp` caller/where helpers
aborted at the memory ceiling and the advisory stopped making progress; it was
terminated after 114.22 s rather than lifting the cap.  The advisory wrapper's
non-failing exit convention does not promote this interrupted run.

Tier 2 used the exact SHA-256 hashes of the unchanged bubble and independent-
mass threshold inputs recorded in the certificate; their producers were not
regenerated.  Tier 3 was not run because this is not a freeze, shared-core
change, release, or explicit full-suite request.  Neither the incomplete
advisory nor skipped Tier 3 rail is reported as a pass.

CLOSE-OUT: SHORTFALL -- triangle and box logarithmic jets are complete and
their power-enhanced collinear terms cancel, but the external phase-space
projector and cut-free finite parts remain open.

EVIDENCE: `reverse_physics/certificates/REVERSE_PHYSICS_BT_TRIANGLE_BOX_LOG_JET_V1.json`

MISSING-DEP: common-prescription external four-mass phase-space projection of
the surviving `15*(Ls+Lt+Lu)` ratio logarithm
