# Every finite tensor cutoff can be positive while the Hadamard continuum cannot

Dependency tag: `REDUCED-MODE`.
Evidence: human analytic proof, exact symbolic producer, independent rational
replay and mutation controls. No quantum lifecycle or paper theorem is promoted.
**Import status: the existing reduced reference fails its current dependency
hash check. The proof below is for its explicitly stated spectral model;
activation as a current-programme physical result is withheld.**

## What this changes

The reduced vacuum-cylinder carrier already has negative physical tensor
modes. The result here answers a different question: can a different choice
of two-point function repair their sign while retaining the same field
commutator and Hadamard short-distance condition?

On the imported free physical TT carrier, **no**. Every smooth repair still
has negative compactly supported test observables at sufficiently high energy.
The argument allows nonstationary repairs and mixing between modes.

Yet **every finite spatial tensor cutoff does admit a positive covariance
with exactly the same truncated commutator**. There is an explicit smooth
bisolution that repairs each such cutoff. Its size in a fixed smooth-kernel
seminorm must diverge as the cutoff grows. Positivity at successively larger
cutoffs, without uniform regularity control, therefore cannot settle the
continuum state question.

This is a useful obstruction for the programme, not a discovery that
higher-derivative gravity has ghosts. It does **not** close the full strict-386
physical-cohomology frontier: the required distributional observable crosswalk
is not supplied by this calculation.

## Inputs and precise statement

The content-addressed inputs are listed in
[`TT_HADAMARD_CUTOFF_OBSTRUCTION_V1.json`](../results/TT_HADAMARD_CUTOFF_OBSTRUCTION_V1.json).
The classical branch spectrum, TT factorization and action residues are
authoritative. The existing reduced
[`VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD`](../../quantum-weyl/lorentzian/certificates/VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD.json)
specifies the reference two-point distribution and its causal pairing.
Its transitive input hashes are audited, not regenerated. Its selected
reduced cohomology has zero differential and nonexact E/A/L representatives;
these are not the centered deformation classes `[W_+^2]`, `[W_-^2]`.

The audit found one stale reference:
`covariant_completion/certificates/curved_direct_causal_pairing_transport.json`.
The reduced reference expects SHA256
`5de7aa9abc9c5c276092cc9c8e61c1046c870fca3a528464410986535a14704b`,
while the current file has
`0ad3161cf1f881294cda1b0d5902855949e93d782023f90b00dc31cdc9670b1e`.
`git diff cfc60932^ cfc60932 --` on that path shows a change to its
`prolonged_current` input hash; the displayed signs are unchanged. That
semantic observation is not an import-gate pass. The upstream verifier
was actually run and failed. Its certificate is preserved, and this result
records `CURRENT_PROGRAMME_PHYSICAL_RESULT_ACTIVATED=false`.

The theorem therefore takes the displayed reduced spectral distribution and
its wavefront property as mathematical premises. It does not certify anew
that the current complete classical complex supplies those premises.

Work on the unit cylinder with action convention
`S=-alpha_g integral C^2`, `alpha_g=1`. Use the standard real metric-field
involution, ordinary positivity on complex test tensors, and the complete
free reduced TT field algebra. Do not change the commutator, throw away the
L branch, alter the involution, or impose extra nonlinear/global constraints.

Let `W0` be the imported E+L reference, assembled on TT metric tests. A candidate
`W` is Hermitian, has the same antisymmetric part as `W0`, and has the same
oriented Hadamard wavefront bound `WF(W) subset C+`. Then `W` is not of positive
type. In fact the conclusion holds for **every smooth kernel** `S` in
`W=W0+S`, without requiring `S` to be stationary, diagonal, or a bisolution.
The quantum application adds the bisolution condition but does not need it
for the contradiction.

## Proof

### 1. One spatial harmonic carries both tensor frequencies

For each integer `n>=4`, choose a real, L2-normalized TT harmonic `u_n` with
`|C_2|=n-1`. The associated E and L frequencies are `n-2` and `n`.
Such harmonics exist at every n: the one-chirality multiplicity is
`n^2-2n-3=(n-3)(n+1)>0`. The same spatial harmonic supports both temporal
branches; an argument that merely selects a spatial harmonic would not
separate their signs.

Writing `tau=t-t'`, the restriction of the reference is

\[
 W_{0,n}(\tau)=
 \frac{e^{-i(n-2)\tau}}{8(n-2)(n-1)}
 -\frac{e^{-in\tau}}{8n(n-1)}.
\]

Both denominators follow from the imported action residues: the squared
frequency gap is `n^2-(n-2)^2=4(n-1)`. The sign of the L term is not fitted
or chosen by the producer.

### 2. A compact time filter isolates the negative expectation exactly

Fix a nonnegative real `chi in C_c^infinity(I)` with integral one, for any
nonempty bounded open time interval I. Set

\[
 d_n=(n-2)^2-n^2=-4(n-1),\qquad
 f_n(t,x)=\frac{\partial_t^2+(n-2)^2}{d_n}
             [\chi(t)e^{-int}]\,u_n(x).
\]

This is a smooth compactly supported spacetime test: S3 is compact. If
`F_n(omega)=integral exp(i omega t) f_n(t) dt` denotes its scalar temporal
Fourier amplitude, integration by parts gives

\[
 F_n(\omega)=\frac{(n-2)^2-\omega^2}{d_n}
                  \widehat\chi(\omega-n).
\]

Thus `F_n(n)=1` and `F_n(n-2)=F_n(-(n-2))=0`, independently of the shape of
chi. With `W(f,f)=integral conjugate(f(x)) W(x,y) f(y)`,

\[
 \boxed{W_0(f_n,f_n)=-\frac1{8n(n-1)}}.
\]

This is a test of the metric TT covariance, rather than an assumed
independently accessible L oscillator. Linear diffeomorphism and Weyl
variations pair to zero with a spatial transverse traceless source having
zero temporal components: integrate the spatial divergence by parts and
use its zero trace. This establishes linear gauge invariance of these
metric tests on the reduced cylinder. It is not a certificate of their
distributional lift into the strict auxiliary-field complex.

### 3. A smooth change is too small at high frequency

The temporal coefficient in `f_n` is

\[
 e^{-int}\left[\chi+\frac{\chi''-2in\chi'}{d_n}\right].
\]

Its L1 norm is bounded uniformly in n by

\[
 B=1+\frac23\|\chi'\|_1+\frac1{12}\|\chi''\|_1,
\]

since `n>=4`. Let `A=C_2^2`, acting on each spatial tensor slot, and define
the finite seminorm

\[
 M=\sup_{t,t'\in\overline I}
 \|(A_x A_y S)(t,\cdot;t',\cdot)\|_{L^2(S^3\times S^3)}.
\]

Here adjoints are taken in the ordinary positive spatial tensor L2 metric.
The tensor curl is formally self-adjoint on TT harmonics, and
`A u_n=(n-1)^2 u_n`. Integrating A by parts in each slot and applying
Cauchy-Schwarz to the normalized product harmonic gives

\[
 |S(f_n,f_n)|\le \frac{B^2 M}{(n-1)^4}.
\]

This estimate allows all off-diagonal mode and time dependence in S.
Consequently

\[
 W(f_n,f_n)\le -\frac1{8n(n-1)}+\frac{B^2M}{(n-1)^4}<0
 \quad\hbox{whenever}\quad (n-1)^3>8B^2Mn.
\]

Such n exist for every finite M. This proves the smooth-repair obstruction.
The machine checks the rational identities and the explicit all-energy
polynomial factors. The integration-by-parts estimate and unbounded-n
argument are human mathematics, not inferred from the sampled rows.

### 4. Why this applies to the whole Hadamard class

For the real bosonic field, equality of commutators implies
`S=W-W0=S^T`, where T swaps spacetime and tensor slots **without complex
conjugation**. The wavefront bound gives `WF(S) subset C+`; symmetry also
gives `WF(S) subset (C+)^T=C-`. These two oriented cones are disjoint, so
`WF(S)` is empty and S is smooth. This uses neither positivity nor
stationarity in obtaining smoothness. Do not replace transpose by Hermitian
adjoint in this argument.

The bound is invoked on the imported reduced TT tensor carrier. No claim
about reducing arbitrary strict BV distributions is hidden in this step.

### 5. Every finite cutoff can nevertheless pass

For a fixed spatial harmonic with L frequency n, put `c_n=1/[8n(n-1)]`.
Add the symmetric bisolution

\[
 S_n(\tau)=c_n(e^{-in\tau}+e^{in\tau}).
\]

It changes the L covariance from `-c_n exp(-in tau)` to
`+c_n exp(+in tau)`. The antisymmetric part is unchanged; the new term is
of positive type because its quadratic form is
`c_n |F(-n)|^2`. The E contribution remains positive. Summing S_n over
all real harmonics with `4<=n<=K` gives a finite-rank smooth symmetric
bisolution S_K. `W0+S_K` retains the full reference wavefront set and
commutator, and is positive on that **truncated** tensor algebra. It is
still negative on sufficiently high modes of the untruncated algebra.

Conversely any smooth repair that makes the test at n=K nonnegative obeys

\[
 B^2 M_K\ge\frac{(K-1)^3}{8K}.
\]

Hence these repairs have no uniform bound in this one fixed seminorm, and
cannot converge in the smooth-kernel topology as K tends to infinity.
The formal all-mode frequency flip does give positive spectral weights,
but loses the selected Hadamard orientation; that loss is essential.

## Consequence, limits, and literature

The important distinction is between an unsuitable reference and an
unsatisfiable conjunction of requirements. On this reduced free carrier,
keeping all TT modes, the real field involution, the commutator and the
Hadamard orientation rules out positivity for every representative.
Adding occupations or finitely many smooth corrections cannot fix it.
This also gives a concrete reason that finite-mode positivity studies need
uniform ultraviolet control before they can support a continuum claim.

To transport this obstruction to `STRICT_PHYSICAL_COHOMOLOGY_POSITIVITY_DECISION`,
one still needs a pairing-preserving map of distributional observables from
the same reduced TT system into strict-386 physical cohomology, with the
same commutator and a controlled wavefront restriction. A field-count match,
an algebraic residual class, or a modal negative norm does not provide it.
The strict frontier remains open in the machine flags. No source certificate,
roadmap lifecycle, full-BV claim, or quantum-master-equation claim is changed.

The broader ghost problem is established literature, including
[Hell, Lust and Zoupanos (2023)](https://arxiv.org/abs/2306.13714), who study
Minkowski/de Sitter perturbations and boundary conditions selecting Einstein
sectors. Their backgrounds and boundary restrictions are not a proof of
this unrestricted compact-cylinder statement. The microlocal framework for
vector-valued fields is developed by
[Sahlmann and Verch](https://arxiv.org/abs/math-ph/0008029); we use the
wavefront property already imported for the reduced carrier, rather than
claiming their wave-equation theorem directly proves a fourth-order theory.

The contribution here is the explicit compact-time filter, the absence of
any smooth positive repair without stationarity, and the quantitative
finite-cutoff counterexample to a naive continuum inference. Publication
novelty is **not established** by the literature check. Independent expert
review of the analytic proof remains appropriate.

## Reproduction and evidence boundary

```bash
python3 foundations/build_tt_hadamard_cutoff_obstruction.py --check
python3 foundations/verify_tt_hadamard_cutoff_obstruction.py
python3 -m unittest foundations.tests.test_tt_hadamard_cutoff_obstruction
python3 quantum-weyl/lorentzian/verify_vacuum_cylinder_reduced_bridge4_hadamard.py
```

The last command currently **fails** on the stale hash described above. It
is listed to expose the boundary, not as a passing validation command.
The producer and upstream verifier require SymPy. For this session it was
installed outside the repository, with SymPy 1.14.0 and mpmath 1.3.0, and
those commands used `PYTHONPATH=/tmp/tt-hadamard-check-deps`. The independent
rational checker and its mutation tests require only the standard library.

The independent rational checker does not import the producer. It checks
input hashes and the exact failure ledger for the reference's transitive inputs, polynomial sign
witnesses, temporal selection, negative expectations, the unchanged
commutator and positivity of the finite repairs, quantitative repair costs,
and fail-closed flags. Mutation controls deliberately corrupt these items.
No finite test suite substitutes for the analytic proof above.

Exact commands, timings and omitted-tier reasons are in
[`tt-hadamard-cutoff-obstruction-v1-validation.json`](../receipts/tt-hadamard-cutoff-obstruction-v1-validation.json).
