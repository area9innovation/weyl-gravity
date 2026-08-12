# BT crossed six-point finite-hierarchy pre-trace no-go

Certificate:
`REVERSE_PHYSICS_BT_CROSSED_SIX_POINT_NONFACTORIZING_PRETRACE_NO_GO_V1`

Lifecycle: `COEFFICIENT_COMPUTED`

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The complete 220-tree leading external-mass jet does not hide a
nonfactorizing crossed six-point sign repair at finite hierarchy ratio.  On
the certified correlated square-free cylinder, all three singleton spectator
masks have one exact pre-trace row, all three complementary-pair masks have a
second exact row, and the cubic spectator mask is absent.  This is true before
the strong-order limit and before scalar square-free contraction.

The two rows reconstruct uniquely through the invertible outer profile
matrix.  Their residual outside the known two-profile carrier is identically
zero.  Crossing the inner invariant leaves one coefficient strictly negative
and the other strictly positive for every positive physical parameter, so the
fixed-sharp quotient remains rank two and negative throughout this finite
correlated cylinder.

This closes the nonfactorizing pre-trace escape anticipated by
`REVERSE_PHYSICS_BT_CROSSED_PROFILE_SELECTIVE_PARITY_OBSTRUCTION_V1` on the
declared cylinder.  It does not close the complete non-correlated six-body
phase space or a doubled/off-diagonal BT source.

## Complete finite-hierarchy rows

The producer retains the complete six-point tree census

\[
 10\,V_4^2+105\,V_3^2V_4+105\,V_3^4,
\]

with the relative tree signs and all seven square-free spectator masks.  The
common external-mass expansion begins at order \(\delta^2\).  At that order,
the three singleton masks \(1,2,4\) agree, the three pair masks \(3,5,6\)
agree, and mask \(7\) vanishes.  These componentwise equalities are checked at
three unrelated hard fixtures while retaining the hierarchy ratio \(e\)
exactly.

Writing the two rows as \((s_e,p_e)^T\), the outer parent/profile matrix is

\[
 M_{\rm out}=
 \begin{pmatrix}
 -a_2^2/(4\tau_2)&a_2/(2\tau_2)\\
 a_2(2\tau_2-a_2)/(4\tau_2^2)&(\tau_2+a_2)/(2\tau_2^2)
 \end{pmatrix},
 \qquad
 \det M_{\rm out}=-\frac{3a_2^2}{8\tau_2^2}.
\]

It therefore determines unique coefficients.  With
\(\chi=a_0^2+a_0a_1+a_1^2\), they are

\[
 u(e)=\frac{2\tau_1(a_0+a_1)-(a_0-a_1)^2}{2\tau_1^2}
      -\frac{e^2\chi}{3a_2^2},
\]
\[
 v(e)=\frac{a_2}{2}
      +\frac{e[\tau_1(a_0+a_1)-(a_0-a_1)^2]}{2\tau_1}
      +\frac{e^2\chi}{3a_2}.
\]

Direct substitution gives

\[
 M_{\rm out}(u(e),v(e))^T=(s_e,p_e)^T,
 \qquad \operatorname{residual}=(0,0)^T.
\]

Thus finite \(e\) changes the known profile coefficients but supplies no
third, nonfactorizing pre-trace row.

## Exact crossed sign

Cross with \(\tau_1=-x\), scale \(a_0=1,a_1=r\), and take
\(a_2,e,r,x>0\).  The signs follow without sampling:

\[
 -6a_2^2x^2u_\times=
 3a_2^2\bigl[(r-1)^2+2x(r+1)\bigr]
 +2e^2x^2(r^2+r+1)>0,
\]

and

\[
 6a_2xv_\times=
 3a_2^2x
 +3a_2e\bigl[(r-1)^2+x(r+1)\bigr]
 +2e^2x(r^2+r+1)>0.
\]

Hence \(u_\times<0<v_\times\).  For the certified coherent collapse
\(R_+=[I_2,I_2]\), the raised pullback has rank two and characteristic
polynomial

\[
 z^2(z-2u_\times v_\times)^2.
\]

Its nonzero eigenvalue \(2u_\times v_\times\) is strictly negative.  The
fixed Hilbertized Gram is

\[
 6u_\times v_\times I_2<0.
\]

The strict \(e\to0\) limit reproduces the preceding strongly ordered crossed
quotient, so the earlier sign was not an artifact of taking that limit.

## Interpretation and next gate

The result joins two exact statements.  Regular same-carrier and inherited
public ghost parities cannot repair the crossed sign, and the complete finite-
hierarchy leading jet on the correlated square-free cylinder generates no
additional pre-trace direction that could do so dynamically.

The physical calculation must now genuinely enlarge its data.  The direct
route is the complete non-correlated crossed \(3\to3\) external-mass phase
space, retaining independent invariants rather than the nested correlated
cylinder.  The alternative is an explicit doubled or off-diagonal source
coupling derived from the BT action or nonlinear \(R_t\), not merely an
abstract carrier that has the desired signature.

## Claim boundary

This certificate does not establish:

- the complete non-correlated crossed \(3\to3\) six-body amplitude;
- absence of subleading-\(\delta\) or finite external-mass contributions;
- absence of a doubled, off-diagonal, singular, or different-chart source;
- a positive crossed six-point probability or the twelve reversed
  intertwiners;
- a complete Moller, LSZ, or \(S\) operator;
- Bateman--Turok Eq. (19), positivity beyond tree level, or a KLN theorem;
- a metric/BRST lift to Weyl gravity or anything `LORENTZIAN-CAUSAL`;
- a new physical dimension or literature priority.

## Verification receipts

All symbolic commands were run sequentially under a 500 MB virtual-memory
limit.

| Tier | Check | Result | Elapsed / peak RSS |
|---|---|---:|---:|
| 0 | Python compile, JSON parse, schema parse, scoped `git diff --check` | PASS | under 1 s |
| 1 | producer, 25 exact checks | PASS | 8.59 s / 77,780 KB |
| 1 | independent verifier, 24 checks and explicit 220-tree finite fixtures | PASS | 2.37 s / 78,060 KB |
| 1 | 21-test mutation suite | PASS | 47.583 s |
| 1 | Paper V, two sequential `pdflatex` passes | PASS; no new overfull box | 0.51 / 0.50 s; 50,688 KB max |
| 1 | Paper VI, two sequential `pdflatex` passes | PASS; no warning or overfull box | 0.54 / 0.54 s; 50,644 KB max |
| affected planning rail | Science Forge import, 1,445 nodes, zero invalid items and zero malformed events | PASS | 17.14 s / 279,604 KB |
| 2 | predecessor hashes and direct interfaces | checked by producer and verifier | included above |
| 3 | not run: no freeze, lifecycle promotion, shared-core change, or release | NOT APPLICABLE | -- |

Exact commands:

```bash
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_crossed_six_point_nonfactorizing_pretrace_no_go.py --write --check
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_crossed_six_point_nonfactorizing_pretrace_no_go.py
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest reverse_physics.tests.test_bt_crossed_six_point_nonfactorizing_pretrace_no_go
```

The first advisory-import attempt under `ulimit -v 500000` failed before
startup because the Go runtime could not reserve its virtual page arena.  A
second attempt using `/tmp` failed during linking with `No space left on
device`.  Neither is counted as a pass.  The successful import used a fresh
disk-backed repository-local temporary directory, `GOMEMLIMIT=256MiB`, and
`GOMAXPROCS=1`; that directory was removed after the process exited.  Paper V
retains four pre-existing overfull boxes outside the inserted passage.
