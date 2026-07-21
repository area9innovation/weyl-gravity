# Balanced third-order Kuranishi evaluation after the canonical crosswalk

The selected-action gate closes with a sharp split verdict:

```text
global compact-stabilizer Kuranishi class: zero in O/im(l2)
bounded / finite-quasiperiodic third-order correction: obstructed
smooth exponential-polynomial correction with secular terms: exists
causal / retarded correction: NO_CERTIFIED_MAP
```

The calculation uses the exact `alpha_B=3` Ostrogradsky crosswalk and all 27
signed rows of the certified second-order correction. The restricted
action-derived tensor contains 832 mixed `q2=D2E` terms and 579 cubic
`q3=D3E` terms. It retains equatorial coefficient derivatives through order
five; order five is required to separate the axial `ell=2` coefficient from
the `ell=4,6` closure. A mutation suppressing that derivative changes the
certified source and is rejected.

The global constraint source is axial with even `ell=2,4,6`, `m=0`, `k=0`.
It pairs trivially with scalar `ell=0` stabilizers `H,P_x` and with the lifted
axial `ell=1` rotations. Thus both `D2C[u,v]` and `D3C[u,u,u]/6` have zero
five-component projection. On the complete same-frequency spin-two
correction space,

```text
im l2(u,-) = span{H,J1,J2}, rank 3,
O/im l2 = span{P_x,J3},
[K3] = 0.
```

This supersedes the earlier rank-one statement, which was restricted to two
real amplitude variations.

The four original `ell=2` shells nevertheless have nonzero bounded adjoint
functionals. In the declared action-row normalization the positive-frequency
values are

```text
q-minus: -2323.7892958977675152... != 0
p-extra: (0, -723.3976090292099712...) != (0,0)
```

The negative-frequency rows are their exact reality conjugates. The
certificate stores algebraic expressions and minimal polynomials with
nonzero constant terms; the decimals are only readable summaries. The
Fredholm alternative therefore excludes a bounded or finite-quasiperiodic
third-order correction for the certified no-homogeneous-addition
second-order representative.

This does not contradict the zero global Kuranishi class. The bounded shell
cokernel is a different obstruction. If secular terms are permitted, the
square constant-coefficient axial pencil has nonzero determinant `p^2 q`;
adjugate reduction gives a smooth exponential-polynomial preimage, with
degree at most one on the `q` shell and at most two on the `p` shell.

## Verification

- Exact producer from the order-ten action checkpoint: PASS, 70.61 s,
  351656 KiB peak RSS.
- Method-distinct replay from the committed rational slice: PASS, 279.09 s,
  103220 KiB peak RSS.
- Independent quadratic row-normalization calibration against the direct
  four-dimensional axial--polar fixture: PASS, exact zero remainder, 7.8 s.
- Fifth-coefficient-derivative deletion mutation: REJECTED.
- Schema/status mutations for bounded promotion, nonzero global class,
  omitted shell and causal promotion: REJECTED.
- Scoped unit tests: PASS.
- Strict residual-atlas validation: PASS.
- Paper 13 `pdflatex -halt-on-error`: PASS.
- Tier 3 full repository suite: not run; no shared core algebra or programme
  release was changed.

Primary evidence:

- `bridge/certificates/EINSTEIN_WEYL_COMPACT_CAUCHY_THIRD_ORDER_KURANISHI_EVALUATION_V1.json`
  (`fcd47578b0409c2196ed07e83a8e400e7d8c45540abd899f0ce663e6fa74a87c`)
- `bridge/einstein_sector/generated/einstein_weyl_compact_cauchy_balanced_q2_q3_resonant_slice_v1.json`
  (`0a94ffea6d872c0cd2d2d8c45ccd93d89c048c5650be775398db9394016900de`)
- `residual_atlas/einstein-weyl-compact-cauchy-third-order-kuranishi-evaluation-fragment-v1.json`
  (`7fff245f5ee7337f28c81f711d7af4d12ba1691859584ff36898b4bfc5702065`)

The result is third order for one balanced fixture. It does not classify
arbitrary homogeneous second-order additions, the full mixed cone, causal
retarded propagation, all-orders integration, particles, positivity,
unitarity or quantum theory.

EVIDENCE: exact q2/q3 slice, action-normalized certificate, independent replay, rejecting mutations, atlas fragment and Paper 13 theorem.
CLOSE-OUT: DONE — the first action-normalized third-order verdict is zero globally but bounded-shell obstructed, with a certified smooth secular preimage.
