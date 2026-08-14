# Complete BT order-g4 expected-Hessian kernel

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_EFFECTIVE_HESSIAN_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

Lifecycle: `EXPECTED_HESSIAN_KERNEL_FORMULA_PROVED_MOMENTUM_BOUND_OPEN`

## Result

The remaining signed order-$g^4$ calculation no longer requires a separate
enumeration of every Wick pairing.  For a polynomial $F$ of a centered
finite-dimensional Gaussian background with covariance $C$, define

\[
 K_F=\mathbb E_0[D^2F].
\]

On the support of $C$, Gaussian integration by parts gives

\[
 \Pi_2F=\frac12:\!\eta^T K_F\eta\!:,
 \qquad
 \|\Pi_2F\|_0^2=\frac12\operatorname{Tr}(CK_FCK_F).
\]

If $A=\frac12:\!\eta^TK_A\eta\!:$, then

\[
 \langle A,F\rangle_0
 =\frac12\operatorname{Tr}(CK_ACK_F).
\]

The actual conditioned covariance may be singular in the ambient coordinate
space.  No inverse covariance is used: the statement is applied on its
finite-dimensional support.

## One combined kernel

The predecessor reduction left

\[
 E=C_{\rm score}-\frac12W_1B+RA,
 \qquad
 R=\frac18W_1^2-\frac12W_2-\frac12z_2.
\]

The complete expected Hessian is

\[
\begin{aligned}
K_E=\mathbb E_0\big[&D^2C_{\rm score}
-\tfrac12(W_1D^2B+B D^2W_1+DW_1\mathbin{\odot}DB)\\
&+R D^2A+A D^2R+DR\mathbin{\odot}DA\big],
\end{aligned}
\]

where $u\odot v=u\otimes v+v\otimes u$ and

\[
 DR=\frac14W_1DW_1-\frac12DW_2,
 \qquad
 D^2R=\frac14(DW_1\otimes DW_1+W_1D^2W_1)-\frac12D^2W_2.
\]

The normalization constant $z_2$ has no derivative, but it remains inside
$R D^2A$.  Dropping it before expectation would therefore be an error.

An exact one-dimensional Gaussian fixture checks the direct second derivative,
the displayed product-rule assembly, the second-chaos norm, and the pairing
with $A=H_2$.  It gives

\[
 z_2=\frac{19}{2},\quad K_E=\frac{527}{4},\quad
 \|\Pi_2E\|^2=\frac{277729}{32},\quad
 2\langle A,E\rangle=\frac{527}{2}.
\]

The fixture checks the algebraic assembly; it is not BT lattice data.

## Conditioning is a finite-rank correction

Write the real-cosine-conditioned covariance as

\[
 C=C_0-R_h,
\]

where $C_0$ is the mean-zero translation-invariant free covariance and $R_h$
is the rank-one covariance of the removed real cosine.  The cross trace splits
exactly into one bulk term, two single-rank terms, and one double-rank term.

Counting explicit cosine legs shows that $K_E$ has transfer sectors
$\pm p,\pm3p,\pm5p$.  The translation-invariant bulk trace with $K_A$ selects
only $\pm p$.  A single $R_h$ insertion may additionally sample $\pm3p$.
For $L\ge4$, the double-rank term vanishes because $h^TK_Ah=0$: three signs
chosen from $\{\pm p\}$ cannot sum to zero modulo $2\pi$.

Thus conditioning does not turn the calculation into an unrestricted
non-translation-invariant problem.  It leaves a momentum-diagonal bulk plus
an explicit finite-mode correction.

## What remains open

This certificate supplies a formula, not the required estimate.  The next
calculation must evaluate $K_E$ as explicit lattice Fourier sums, combine
terms sharing a loop momentum before taking absolute values, and then bound:

- the transfer-$p$ bulk by hard, one-soft, and all-soft regions; and
- the exceptional transfer-$3p$ finite-rank term directly.

No effective-kernel norm bound, whole-lattice order-$g^4$ decision,
nonperturbative score theorem, interacting $H^{-1}$ moment, continuum
identification, Born rule, Krein reconstruction, or `LORENTZIAN-CAUSAL`
statement follows from this reduction.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_effective_hessian.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_effective_hessian.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_effective_hessian
```

## Verification receipt

The final bounded run used the three commands above under the 500 MB virtual
memory cap.  The deterministic producer check took 0.04 s (20,700 KB peak),
the independent verifier 0.10 s (29,700 KB), and all nine focused tests
0.16 s (30,480 KB).  The direct complete-$g^4$ UV and chaos predecessor
verifiers passed in 0.09 s and 0.10 s.  The Paper 21 claim-map check and its
independent verifier passed in 0.06 s and 0.07 s.  Two successful PDF passes
took 0.77 s and 0.76 s; the final pass used 53,808 KB peak and produced the
54-page paper.

The append-only planning import folded 1,615 nodes with zero invalid items and
zero malformed events in 6.85 s under `GOMEMLIMIT=300MiB`.  The advisory
Science Forge shadow rail completed in 2.15 s and reported, rather than
promoted, the existing forge-stdlib mismatch/E9118 bridge-audit failure and
corpus-baseline drift (1,665 certificates versus the 2026-07-19 baseline of
976).  Its exit zero was advisory and is not a scientific pass.  The prose
advisory also retained the paper's existing parenthetical and abstract-length
findings; it is non-certifying.  The paper-principles path named by the
substrate guide was absent from the current forge checkout.

Tier 0 parse, generation, paper build, and scoped-diff checks passed.  Tier 1
covered the producer, independent verifier, nine mutation tests, and both
Paper 21 claim-map rails.  Tier 2 covered the two direct mathematical
predecessors.  Tier 3 was not run because no freeze, release, shared core
algebra change, theorem lifecycle promotion, or continuum claim is present;
the effective-kernel norm bound remains open.
