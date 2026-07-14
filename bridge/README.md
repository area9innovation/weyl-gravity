# Pure-Weyl metric-to-residual bridge programme

This directory is the canonical implementation roadmap for closing the three
conditional steps in Paper VII.  The starting points already proved are:

- the smooth global Bach-to-geometric-curvature isomorphism on
  `R x S3`;
- the chiral geometric target;
- the algebraic symmetric-Fock lift, once one-particle BV cohomology is
  known;
- the intrinsic complementary-degree residual CE pairing; and
- the exact residual cohomology calculation on the hand-specified `E/A/L`
  coefficient module.

The programme must connect those endpoints.  It must not extend cutoff tables
as a substitute for an all-energy construction.

## Blocking target: an all-energy cylinder right inverse

For every allowed compact energy `n` and `SO(4) = SU(2)_L x SU(2)_R` type,
construct exact harmonic spaces and matrices

```text
K_n        gauge parameter -> trace-free metric
C_n        trace-free metric -> algebraic Weyl curvature
B_n        C_n^sharp C_n
D2_n       C_n^sharp star
```

and verify

```text
C_n K_n = 0
D2_n C_n = 0
B_n = C_n^sharp C_n.
```

For every basis vector in the `E_n`, `A_n`, and `L_n` curvature towers,
construct an exact same-block metric preimage.  The required output is a
symbolic family

```text
R_n : W_n -> H_metric,n
C_n R_n = identity_W_n
```

including all low-level exceptions.  Coefficients should be exact algebraic
functions of `n`.  A practical discovery pass may compute `n=2,...,12` and
interpolate rational/radical formulas, but completion requires a symbolic
all-`n` proof.  The dimensions

```text
10, 40, 82, 136, 202
```

remain regression tests, not the theorem.

Acceptance requires the blockwise identity

```text
ker(B_n) / im(K_n)
  = E_n+ + A_n+ + L_n+ + E_n- + A_n- + L_n-
```

for every permitted `n`.

## Workstream 2: complete one-particle BV complex

Encode, rather than silently discard:

- metric perturbations;
- Diff and Weyl ghosts;
- metric and ghost antifields;
- gauge-fixing and nonminimal pairs, where used; and
- the fifteen conformal-Killing zero modes.

Construct an exact projector `P_CKV` with compact decomposition
`4_-1 + 7_0 + 4_+1` and verify

```text
K P_CKV = 0
P_CKV^2 = P_CKV.
```

Every nonminimal doublet `(u,v)` must be accompanied by an explicit
contraction certificate `q u=v`, `q v=0`, `s v=u`.  The one-particle result is
complete only after the physical metric row, local ghost rows, antifield
rows, and nonminimal rows have all been audited.  The target is

```text
H(q)_one-particle = W_+ + W_-.
```

The many-particle Fock statement then follows from the symmetric-algebra
lemma and requires no new large rank computation.

## Workstream 3: equivariant cyclic retract

Construct exact block operators `p`, `j`, and `s` satisfying

```text
p j = identity
j p = identity - q s - s q.
```

First verify compact equivariance with `D` and both rotation factors.  Then
report, without assuming vanishing,

```text
K_q^+ j - j K_H^+
p K_q^+ - K_H^+ p
[K_q^+, s]
```

and their lowering counterparts.

There are two acceptable outcomes:

1. **Strict:** every commutator vanishes symbolically.
2. **Homotopy-equivariant:** every defect is `q`-exact and the induced HPL
   corrections are computed explicitly and shown to vanish on the centered
   weight-four window.

Using the actual BV/Krein pairing, verify `j^sharp=p`, the graded cyclic
identity for `s`, and the dressed isometry `I^sharp I=identity`.  Blockwise
`D x SO(4)` splittings are not evidence of full `SO(4,2)` equivariance.

## Workstream 4: residual BFV package

Implement the graded residual algebra independently:

```text
g = g_-1 + g_0 + g_+1
dim = 4 + 7 + 4.
```

Generate structure constants, ghosts, contractions, the CE differential,
compact degree, and the complementary-degree top-form pairing.  Verify

```text
d^2 = 0
[d, i_D]_+ = L_D
d^sharp = -d
```

for the CE pairing.

Construct determinant vectors `v_-`, `Theta_0`, and `v_+`; prove that their
wedge saturates all fifteen ghost directions; and normalize
`(v_-,v_-)_gh=1`.  This package certifies the residual CE pairing.  It must
not claim that the full pure-Weyl BV/BFV transfer induces that pairing until
Workstream 5 is complete.

## Workstream 5: local-to-residual transfer

After combining the nonzero-mode BV complex with the residual zero modes,
compute the finite HPL series

```text
Q_H = p Delta (1 + s Delta)^(-1) j
```

to the maximum order allowed by ghost number and compact degree.  Compare it
with the strict residual CE differential.  Any difference must be emitted
with local degree, residual ghost degree, compact degree, and its action on:

- the centered one-particle complex;
- the weight-four two-particle complex; and
- `[W_+^2]` and `[W_-^2]`.

Strictness is a result only if `Q_H-d_CE=0` in the actual BV implementation.

## Workstream 6: Taub/moment-map comparison

Construct the quadratic Bach source and charges

```text
T_X[h] = integral_S3 n_mu X_nu B^(2)^{mu nu}[h,h].
```

Verify conservation on linear Bach solutions, express each charge in
oscillator variables, prove equivariance, and compare it with the quadratic
oscillator moment map.  Fix the common scalar with `D`, then use one
proper-conformal component as an independent check.  Do not fit fifteen
unrelated coefficients.

## Workstream 7: end-to-end integration

Reconstruct the centered complex from transferred metric/BV data:

```text
metric BV complex
  -> transferred Weyl module
  -> residual CE complex
  -> H^4_(delta=0).
```

The integration test must recover

```text
H^4_(N=0) = 0
H^4_(N=1) = 0
H^4_(N=2) = span(W_+^2, W_-^2)
G_res = I_2.
```

## Sprint order

1. **Cylinder curvature bridge:** exact harmonic spaces, `K_n`, `C_n`,
   `B_n`, `D2_n`, same-block preimages, and all-`n` formulas.
2. **One-particle BV:** complete rows, CKV projector, contractions, and full
   one-particle cohomology.
3. **Equivariant cyclic retract:** `p,j,s`, compact checks, noncompact defect
   report, and cyclicity.
4. **Residual BFV and transfer:** canonical CE pairing, transferred
   differential, strictness comparison, and end-to-end residual test.
5. **Taub interpretation:** second-order Bach current and equivariant
   equality with oscillator moment maps.

## Repository contract

Every theorem-level deliverable must include:

- a symbolic proof script using exact arithmetic where possible;
- low-level numerical or modular regression tests;
- a generated LaTeX statement or table;
- a machine-readable certificate; and
- CI coverage.

Planned package layout:

```text
bridge/
  cylinder_harmonics/
  bgg_operators/
  metric_preimages/
  bv_complex/
  zero_modes/
  cyclic_retract/
  residual_bfv/
  transfer/
  taub_moment_map/
  integration_tests/
```

## Explicit non-goals

Until the bridge closes, do not:

- add Euclidean jet levels without an all-`n` formula target;
- enlarge residual cutoffs merely to obtain bigger rank tables;
- begin quantum anomaly calculations;
- generalize to arbitrary curved backgrounds;
- infer full conformal equivariance from `D x SO(4)` checks;
- discard ghost or antifield rows without contraction certificates; or
- treat the Hamada insertion as proof of the pure-Weyl BV/BFV transfer.

The immediate programming deliverable is the exact cylinder-harmonic right
inverse `R_n` of the linearized Weyl map on every `E/A/L` block.

## Implemented checkpoint: physical E/A/L preimages

`bridge/cylinder_harmonics/linearized_geometry.py` and
`bridge/metric_preimages/all_energy.py` now implement the normalized
highest-weight metric representatives and the full coordinate linearized
Weyl/Bach operators with symbolic energy `n`.  The certificate

```text
symbolic/verify_conformal_cylinder_preimages.py
```

proves a nonzero chiral Bach-flat Weyl image and an exact same-block right
inverse for every `E_n`, `A_n`, and `L_n`, with parity completion and the
first five level dimensions as regressions.  The machine-readable and LaTeX
artifacts are in `bridge/certificates/` and `bridge/generated/`.

This closes the immediate physical-block preimage target.  Sprint 1 remains
open until the surrounding off-shell gauge/metric/compatibility matrices
`K_n,C_n,D2_n` and their exactness certificates are also implemented.
