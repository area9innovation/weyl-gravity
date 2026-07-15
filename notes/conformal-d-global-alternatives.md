# Exact reduced-mode alternatives with (D) global

## Scope and verdict

This report addresses only the alternative-complex kernel of
`d-quotient-classical-team-brief.md`.  It imports the certified local
Diff\(\times\)Weyl reduction and the exact all-level (E/A/L) oscillator
module.  It does **not** compute the covariant Hamiltonian charge of (D).

Dependency tags:

```text
REDUCED-MODE
LOCAL-ALGEBRAIC
```

The main exact comparison is:

> If cylinder (SO(4,2)) is retained as a global symmetry after local gauge
> reduction, there are no residual CE ghosts and the residual differential is
> zero.  The complete (E/A/L) one-particle module therefore survives, with
> canonical Krein signs (+,-,-).

This is an algebraic answer to “what is the state complex if residual
transformations are not gauged?”  Whether it is the correct physical answer is
`OPEN_PENDING_COVARIANT_D_CHARGE`.

## Why deleting only the (D) ghost is invalid

The fourteen-dimensional span obtained by removing (D) from the certified
fifteen-generator conformal basis is not closed under brackets.  In the exact
magnetic basis,

\[
 \frac14\sum_{a=1}^4[K^-_a,K^+_a]=2D.
\]

Individual brackets also contain compact rotations, but their invariant sum
cancels those rotation terms and retains (2D).  Hence there is no CE complex
called “(\mathfrak{so}(4,2)) with only the (D) ghost deleted.”  Any such
matrix would fail nilpotency rather than define an alternative quotient.

## No residual gauging

Let

\[
 \mathcal H_{\rm loc}
 =\mathcal F(\mathcal W_+\oplus\mathcal W_-)
\]

be the state space after certified local Diff\(\times\)Weyl reduction.  When
the cylinder conformal group acts globally, the residual complex is simply

\[
 (\mathcal H_{\rm loc},0).
\]

Thus every state is a degree-zero cohomology class.  At one particle the exact
all-level inventory is

| tower | range | dimension at (D=n) | Krein block |
|---|---:|---:|---:|
| (E_n) | (n\ge2) | (2(n-1)(n+3)) | (+I) |
| (A_n) | (n\ge3) | (2(n-1)(n+1)) | (-I) |
| (L_n) | (n\ge4) | (2(n-3)(n+1)) | (-I) |

The first exact weights are therefore

| particle number | (D)-weight | dimension | Gram signature |
|---:|---:|---:|---:|
| 0 | 0 | 1 | ((1,0)) |
| 1 | 2 | 10 | ((10,0)) |
| 1 | 3 | 40 | ((24,16)) |
| 1 | 4 | 82 | ((42,40)) |
| 2 | 4 | 55 | ((55,0)) |

In particular:

* the helicity-(\pm2) (E_2) states return as ten positive one-particle
  classes;
* the positive Einstein (E) branch and negative (A/L) branches survive as
  separate summands;
* the complete weight-four Gram matrix, in the certified occupation basis, is
  \[
    \operatorname{diag}(I_{42},-I_{30},-I_{10},I_{55}),
  \]
  with signature ((97,40));
* (W_+^2,W_-^2\in\operatorname{Sym}^2(E_2^+\oplus E_2^-)) remain
  orthonormal with Gram (I_2), but they are now ordinary degree-zero vectors
  inside a 55-dimensional two-particle space.  Without residual gauging,
  cohomology does not single them out.

This is the sharp contrast with the selected closed-universe absolute complex:
there the Cartan differential removes the one-particle module and leaves only
the two centered Weyl-square classes at the relevant degree.

## An illustrative legal subalgebra

For a second, mathematically defined comparison, take the closed abelian
lowering algebra

\[
 \mathfrak n_-:=\operatorname{span}\{K^-_a\}_{a=1}^4.
\]

It excludes (D), while (D) remains a global grading because

\[
 [D,K^-_a]=-K^-_a.
\]

This choice is **illustrative, not uniquely physical**.  It exists to show how
a valid (D)-global CE comparison differs from deleting one generator from a
nonclosed set.

The exact Koszul differential on the one-particle module was assembled in each
cutoff-complete total-(D)-weight block through weight four.  Its cochain
dimensions, exact ranks, and cohomology dimensions in ghost degrees (0,ldots,4)
are:

| total (D)-weight | cochain dimensions | differential ranks | cohomology dimensions |
|---:|---:|---:|---:|
| 2 | (10,0,0,0,0) | (0,0,0,0) | (10,0,0,0,0) |
| 3 | (40,40,0,0,0) | (40,0,0,0) | (0,0,0,0,0) |
| 4 | (82,160,60,0,0) | (82,60,0,0) | (0,18,0,0,0) |

All displayed ranks are exact: the good-prime minors reach the elementary row
or column upper bounds, and the differentials compose to zero symbolically.
The lowest (H^0) is precisely the ten-dimensional (E_2^+\oplus E_2^-)
space with Gram (I_{10}).

At centered weight four, the zero-action vacuum and lowest two-particle blocks
add one class in ghost degree four and 55 classes in ghost degree zero.  The
two Weyl-square vectors again span a positive (I_2) subspace of the latter.
The complementary-degree pairing for the new 18-dimensional ghost-degree-one
group has **not** been computed and remains fail-closed.

The cutoff statement stops at total weight four.  Cohomology at larger total
weight needs higher one-particle shells because the incoming lowering
differential can originate above the present cutoff.

## What is and is not established

Machine flags:

```text
delete_D_only_is_valid_Lie_algebra       = false
no_residual_gauging_complex_exact        = true
full_EAL_one_particle_module_survives    = true
negative_norm_one_particle_branches_survive = true
lowering_subalgebra_closed               = true
lowering_subalgebra_physical             = false
D_charge_computed_here                   = false
```

The result establishes a conditional warning with direct physical relevance:
if the residual conformal transformations are global rather than gauge, the
negative (A/L) one-particle branches are not removed by residual cohomology.
It does not decide whether compact-cylinder (D) is proper gauge, charged, or
sector-dependent.  That decision belongs to the independent covariant
presymplectic-charge audit.

## Reproduction

```bash
python3 symbolic/verify_conformal_d_global_alternatives.py --write-result
python3 symbolic/verify_conformal_d_global_alternatives.py --check-result
```

Machine-readable result:

```text
symbolic/conformal-d-global-alternatives.json
```

The certificate stores SHA-256 provenance for the imported all-level
generator, absolute-CE, and relative-weight-four implementations.
