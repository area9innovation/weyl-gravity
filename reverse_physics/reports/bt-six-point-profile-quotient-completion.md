# BT six-point profile quotient completion

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

**Lifecycle:** `COEFFICIENT_COMPUTED`

**Certificate:** `REVERSE_PHYSICS_BT_SIX_POINT_PROFILE_QUOTIENT_COMPLETION_V1`

## Result

The minimal grading-faithful four-component carrier resolves the exact
six-point interference obstruction.  The earlier obstruction remains correct
if the constant/linear parent jets are collapsed to two species before the
singleton/pair spectator profiles are separated.  If both gradings are kept,
the complete physical pullback has a canonical two-dimensional kernel that is
nondegenerate, orthogonal to its image, and exactly invisible to the physical
amplitude.  The orthogonal image quotient has a positive scalar raised Gram
above threshold and reproduces the complete six-point scalar contraction
pointwise.

Consequently the second channel-history rate (5/64) is no longer merely a
positive identity-species completion.  It is amplitude-affiliated on the
canonical quotient fibre.  The third (27/400) jump remains a construction
until the seven-point amplitude is resolved on this enlarged architecture.

## Four independent components

Let the parent-jet basis be constant/linear and the spectator-profile basis be

\[
 S_1=a_3+a_4+a_5,
 \qquad
 S_2=a_3a_4+a_3a_5+a_4a_5.
\]

Order the tensor carrier as

\[
 (0,S_1),\ (0,S_2),\ (1,S_1),\ (1,S_2).
\]

The exact parent and profile cross pairings are

\[
 J=\begin{pmatrix}0&1\\1&0\end{pmatrix},
 \qquad
 K=3\begin{pmatrix}0&1\\1&0\end{pmatrix},
\]

so the four-dimensional metric is

\[
 \eta=J\otimes K,
\]

of signature ((2,2)).  The factor (3) in (K) is not a convention: it is
the exact coefficient of (a_3a_4a_5) in a singleton profile times its
complementary pair profile.

The pre-trace six-point factorization supplies

\[
 u=2Q_{\rm inner}
 =\frac{2\tau_1(a_0+a_1)-(a_0-a_1)^2}{2\tau_1^2},
 \qquad
 v=\frac{a_2}{2}.
\]

On the four-component carrier it acts diagonally,

\[
 D=\operatorname{diag}(u,u,v,v).
\]

The physical amplitude coherently forgets the parent-jet label while retaining
the two spectator profiles:

\[
 R=\begin{pmatrix}1&0&1&0\\0&1&0&1\end{pmatrix}.
\]

For (X=(l_0,q_0,l_1,q_1)^T), this gives

\[
 RDX=\binom{ul_0+vl_1}{uq_0+vq_1},
\]

whose (K)-pairing is precisely the complete untraced square-free amplitude

\[
 (RDX)^TK(RDX)=6(ul_0+vl_1)(uq_0+vq_1).
\]

## Pullback spectrum and canonical projector

Pull the physical profile pairing back to the four-component carrier and
raise with (eta):

\[
 A=\eta^{-1}D^TR^TKRD
 =\begin{pmatrix}
 uv&0&v^2&0\\
 0&uv&0&v^2\\
 u^2&0&uv&0\\
 0&u^2&0&uv
 \end{pmatrix}.
\]

It satisfies

\[
 \chi_A(z)=z^2(z-2uv)^2,
 \qquad
 A^2=2uvA.
\]

Above the inner threshold (u>0), while (a_2>0) gives (v>0).  Therefore

\[
 P=\frac{A}{2uv}
 =\begin{pmatrix}
 \tfrac12&0&\tfrac{v}{2u}&0\\
 0&\tfrac12&0&\tfrac{v}{2u}\\
 \tfrac{u}{2v}&0&\tfrac12&0\\
 0&\tfrac{u}{2v}&0&\tfrac12
 \end{pmatrix}
\]

is a regular idempotent and is Krein-selfadjoint:

\[
 P^2=P,
 \qquad
 P^\sharp=\eta^{-1}P^T\eta=P.
\]

The kernel and image have basis matrices

\[
 N_-=egin{pmatrix}v&0\\0&v\\-u&0\\0&-u\end{pmatrix},
 \qquad
 N_+=\begin{pmatrix}v&0\\0&v\\u&0\\0&u\end{pmatrix}.
\]

They obey

\[
 N_-^T\eta N_-=-6uvJ,
 \qquad
 N_+^T\eta N_+=+6uvJ,
 \qquad
 N_-^T\eta N_+=0.
\]

Thus neither subspace is degenerate and they form an exact Krein-orthogonal
direct sum.  Moreover,

\[
 RDN_-=0,
 \qquad
 RDN_+=2uvI_2.
\]

The discarded subspace is therefore not selected for convenience: it is
exactly the part that the physical amplitude cannot see.  On the image,
(A=2uvI_2).  The profile swap (J) is a fundamental symmetry and turns the
image form into

\[
 (6uvJ)J=6uvI_2>0.
\]

## Exact reconstruction

For every four-component profile vector, not merely for the BT kinematic
fixture,

\[
 (RDX)^TK(RDX)=2uv(PX)^T\eta(PX).
\]

This identity includes the two self-profile terms that caused the complex
eigenvalues after premature restriction.  It proves that quotienting does not
alter the scalar amplitude or fit its final value.  It also avoids the
previous normalization singularity at \(\tau_2=2a_2\): the projector depends
only on (u) and (v), so no division by the outer cross component (B_{01})
occurs.

The four-dimensional carrier is minimal among architectures that faithfully
retain two independent parent jets and two independent profiles.  This does
not rule out every unrelated three-dimensional dilation, but such a dilation
would necessarily identify at least one of the declared independent grading
directions.

## Five-point prefix

At five points, the hard parent profiles are pure:

\[
 X_5=(0,\tfrac12,\tfrac12,0)^T,
 \qquad
 u_5=2Q,quad v_5=2L.
\]

The same construction gives

\[
 X_5^T\eta X_5=\frac32,
 \qquad
 R D_5X_5=\binom{L}{Q},
 \qquad
 (RD_5X_5)^TK(RD_5X_5)=6LQ.
\]

The projected parent norm is (3/4).  Including the certified fifth
delta-prime sign, the child-to-hard ratio is

\[
 -\frac{6LQ}{3/2}=-4LQ=\rho.
\]

Hence the quotient carrier restricts to the certified five-point physical
Gram after the natural complementary-profile identification.  It does not
replace the first physical result with a different normalization.

## Second branching jump

The topology-independent tree phase is (-i) for every tree because a tree
with (V) vertices has (V-1) propagators:

\[
 (-i)^V i^{V-1}=-i.
\]

The five-to-six amplitude quotient is consequently real in the declared
convention.  Since the pointwise quotient identity reproduces the complete
six-point integrand, the certified threshold and factorial calculation passes
through unchanged.  The selected-history coefficients give

\[
 q_1=rac{5/3072}{1/48}=\frac5{64}.
\]

This affiliates the second jump with the two-dimensional image of (P),
naturally identified with the singleton/pair profile fibre.  It does not yet
provide the reverse block or a common all-order asymptotic generator.

## Claim boundary and next gate

This is a reduced-mode amplitude quotient, not a complete probability or
spacetime S operator.  The third positive jump (27/400) remains an abstract
completion because the seven-point species/profile tensor has not been
computed before its scalar trace.

The next gate is therefore sharply defined: resolve each seven-point rooted-
comb history on the quotient architecture selected here.  A canonical
collapse-invisible kernel with positive scalar image and conditional rate
(27/400) would affiliate the complete available three-jump instrument.  Its
failure would be the third-jump obstruction.

## Verification

The producer constructs the tensor metric, physical collapse, pullback,
projector, exact kernel/image bases, arbitrary-vector reconstruction identity,
five-point prefix, and rational fixtures symbolically.  The independent
verifier starts from the explicit four-by-four metric and two-by-four collapse
matrices, rebuilds every product, replays three rational fixtures, imports the
three rate coefficients independently from their source certificates, and
checks the predecessor obstruction remains correctly scoped.

All Python jobs ran sequentially under `ulimit -v 500000`.

## Verification receipt

| tier | command or check | result | elapsed | peak RSS |
|---|---|---:|---:|---:|
| 0 | Python byte-compile of three modules and JSON parse of four structured artifacts | PASS | 0.03 s | 14,640 KB |
| 0 | tab audit and uncapped `git diff --check` on scoped paths | PASS | below 0.3 s | negligible |
| 1 | producer exact tensor/Krein construction | PASS, 42/42 | 0.68 s | 68,828 KB |
| 1 | independent explicit-matrix verifier | PASS, 23/23 | 0.46 s | 72,596 KB |
| 1 | producer/verifier and eleven mutations | PASS, 13/13 | 4.50 s | 72,692 KB |
| 1 | Paper V two-pass PDF build | PASS | 0.41 s / 0.41 s | 51,044 / 50,788 KB |
| 1 | Paper VI two-pass PDF build | PASS | 0.43 s / 0.44 s | 50,896 / 50,932 KB |

Tier 2 does not require rebuilding the six-point 220-tree or threshold chain:
their content-addressed inputs and scalar kernel are unchanged, and the new
arbitrary-vector identity reconstructs that exact kernel pointwise.  Tier 3
is not required because there is no freeze, release, shared-core-algebra
change, complete-probability promotion, or Lorentzian theorem.  No skipped or
advisory rail is counted as a pass.

The final capped scientific sequence completed producer, verifier, and tests
before Git's threaded `lstat` scan failed to reserve resources under the
inherited 500 MB virtual-memory limit.  The read-only `git diff --check` was
rerun immediately without that cap and passed.  The capped Git runtime failure
is not counted as a pass; every Python and TeX research process remained
capped.
