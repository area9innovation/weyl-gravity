# BT quantum-stochastic Møller dilation

## Result

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.  Lifecycle:
`CLASSIFIED`.

The square-root transition law that obstructed an ordinary additive-resolution
Hamiltonian is exactly the scaling expected from quantum white noise.  On the
certified 152-dimensional positive quotient, put one independent Boson noise
channel on each of the 75 rooted-comb insertion edges and define

\[
 J_e=\sqrt{q_k}\,|c\rangle\langle h|\otimes I_2,
 \qquad
 (q_0,q_1,q_2)=\left(\frac1{48},\frac5{64},\frac{27}{400}\right).
\]

With

\[
 D=\frac12\sum_eJ_e^\dagger J_e,
\]

the levelwise drift eigenvalues are

\[
 \left(\frac1{32},\frac5{32},\frac{27}{160},0\right).
\]

The bounded Hudson--Parthasarathy equation

\[
 dU_a=\left(\sum_eJ_e\,dA_e^\dagger
 -\sum_eJ_e^\dagger dA_e-D\,da\right)U_a,
 \qquad U_0=I,
\]

acts on the system tensored with
\(\Gamma_s(L^2(\mathbb R_+,da)\otimes\mathbb C^{75})\).  For the coefficient
matrix

\[
 G=\begin{pmatrix}-D&-L^\dagger\\L&0\end{pmatrix},
 \qquad \Delta=\operatorname{diag}(0,I_{75}),
\]

both exact structure identities hold:

\[
 G+G^\dagger+G^\dagger\Delta G=0,
 \qquad
 G+G^\dagger+G\Delta G^\dagger=0.
\]

The bounded-coefficient theorem of Hudson and Parthasarathy therefore gives a
unique strongly continuous adapted unitary cocycle.  Under the Fock
factorization into past and shifted future noise it satisfies

\[
 U_{a+b}=\Theta_a(U_b)U_a.
\]

It is stochastic rather than ordinarily differentiable.  In particular, the
hard-vacuum column still has an order-\(\sqrt a\) off-diagonal component, so
the previous strong-derivative obstruction is preserved rather than evaded by
relabeling.

## Exact vacuum reduction

Tracing out vacuum noise gives

\[
 \mathcal L(\rho)=\sum_eJ_e\rho J_e^\dagger
 -\frac12\left\{\sum_eJ_e^\dagger J_e,\rho\right\}.
\]

An independent reconstruction gives the same sparse classical-generator hash
as the channel-resolved branching certificate:

```text
d5410264c4a2015ddbfa7c018771b96089f2eae6c5b9df15bf513c0da7fe33c5
```

The aggregate level probabilities are normalized for every \(a\geq0\).  Their
Laplace transforms are

\[
 \frac{16}{16s+1},\qquad
 \frac{16}{(16s+1)(16s+5)},\qquad
 \frac{400}{(16s+1)(16s+5)(80s+27)},
\]

\[
 \frac{135}{s(16s+1)(16s+5)(80s+27)}.
\]

The hard vacuum amplitude is \(e^{-a/32}\), and the hard survival probability
is \(e^{-a/16}\).  Thus the full dilation is unitary and reversible even
though its vacuum-reduced population process is directed.  The reverse motion
is carried by the \(-J_e^\dagger dA_e\) annihilation terms and is lost when the
environment is discarded.

## Exact finite-jet intertwiner

For one selected rooted-comb path with \(k\) emissions, the ordered-noise
kernel on \(0<t_1<\cdots<t_k<a\) has leading squared norm

\[
 \frac{a^k}{k!}\prod_{j<k}q_j.
\]

Consequently its leading amplitude is

\[
 a^{k/2}\sqrt{\frac{\prod_{j<k}q_j}{k!}}.
\]

The finite coupling jet has edge weights

\[
 (\alpha_0,\alpha_1,\alpha_2)
 =\left(\frac{\sqrt3}{12},\frac{\sqrt{10}}8,\frac9{20}\right),
 \qquad \alpha_j^2=(j+1)q_j.
\]

Therefore, with \(x=\sqrt a\),

\[
 a^{k/2}\sqrt{\frac{\prod_{j<k}q_j}{k!}}
 =x^k\frac{\prod_{j<k}\alpha_j}{k!}.
\]

This reproduces the three selected amplitudes

\[
 \frac{\sqrt3}{12},\qquad
 \frac{\sqrt{30}}{192},\qquad
 \frac{\sqrt{30}}{1280},
\]

and the aggregate leading probabilities

\[
 \frac a{16},\qquad
 \frac{5a^2}{512},\qquad
 \frac{9a^3}{8192}.
\]

The previous finite skew exponential is thus the normalized small-cell
compression of the first three Fock-noise sectors.  It was not the wrong
coefficient model; it was the wrong differentiability category for additive
resolution.

## Minimality and carrier affiliation

The vectorized edge Kraus Gram is

\[
 \operatorname{Tr}(J_e^\dagger J_f)=2q_{k(e)}\delta_{ef}.
\]

Its diagonal entries by level are \(1/24\), \(5/32\), and \(27/200\).  All 75
edge maps have distinct matrix-unit support and are orthogonal to the identity,
so the Gram has rank 75.  This proves noise multiplicity 75 is minimal for the
pinned channel-resolved completely positive map.  It does not prove that every
coherently unmarked dilation with only the same count probabilities needs 75
marks.

The Abel density

\[
 p_s(y)=\frac12\operatorname{sech}^2(y-s)
\]

has unit integral, and

\[
 f(s)e_e\longmapsto f(s)\sqrt{p_s(y)}e_e
\]

is an isometric embedding of the one-particle noise carrier into the existing
Abel--Naimark resolution carrier with the mark space enlarged from the three
first-level pair marks to all 75 insertion edges.  The coordinate \(s\), or
the additive length \(a\), is auxiliary resolution/noise history.  It is not
a new spacetime or physical dimension.

## Independent verification

The independent verifier does not import the producer.  It:

- enumerates rooted combs by choosing a cherry and permuting its complement;
- reconstructs every edge by deleting the newest leaf;
- derives the three rates separately from the five-, six-, and seven-point
  amplitude certificates;
- reconstructs the 75-channel hash and the sparse classical-generator hash;
- proves the diagonal Kraus rank and minimality relative to the pinned map;
- reduces both HP structure identities to exact rational block identities;
- reconstructs the population Taylor series, ODE, normalization, and Laplace
  resolvents;
- derives the three ordered-simplex amplitudes and their finite-jet
  intertwiner; and
- checks that a future fourth edge first changes the four-emission probability
  at order \(a^4\) and the three-emission sector beyond its certified leading
  \(a^3\) term.

The certificate is
`REVERSE_PHYSICS_BT_QUANTUM_STOCHASTIC_MOLLER_DILATION_V1`.

## Claim boundary

This establishes a finite reduced-mode additive-resolution quantum-stochastic
Møller cocycle through all currently computed emission orders.  It does not
establish an ordinary strongly differentiable Hamiltonian, a physical fourth
jump, a unique all-order stochastic law, complete \(2\to n\) probability,
complete degenerate sectors, a continuum or spacetime-local Møller/LSZ/S
operator, identification with the public \(R_t\) map, Eq. (19), a metric/BRST
lift, a new physical dimension, anything `LORENTZIAN-CAUSAL`, or literature
priority.

The level-three reduced vacuum sector has no outgoing fourth jump only because
the input data stop at seven points.  Its large-\(a\) absorption is not
interpreted as physical BT termination.

## Verification receipt

All scientific Python, SymPy, and TeX processes run sequentially under
`ulimit -v 500000`.

| tier | command or check | result | elapsed | peak RSS |
|---|---|---:|---:|---:|
| 0 | Python compile and JSON/schema parse on scoped artifacts | PASS | below 1 s | below 75 MB |
| 0 | `git diff --check` on scoped paths | PASS | below 0.1 s | negligible |
| 1 | exact producer and certificate drift check | PASS, 38/38 | 0.75 s | 71,672 KB |
| 1 | method-distinct verifier | PASS, 26/26 | 0.49 s | 74,140 KB |
| 1 | producer/verifier plus sixteen falsifying mutations | PASS, 18/18 | 6.63 s | 74,284 KB |
| 1 | Paper V final two-pass PDF build | PASS; no new overfull box | 0.48 / 0.50 s | 50,912 / 50,664 KB |
| 1 | Paper VI two-pass PDF build | PASS; no warning or overfull box | 0.49 / 0.54 s | 50,384 / 50,820 KB |
| advisory | Science Forge programme import | PASS; 1,399 nodes, 0 invalid items, 0 malformed events | 8.90 s | 458,196 KB |

The capped Tier 0 command completed Python compilation and JSON parsing, then
Git failed with `unable to create threaded lstat`; that Git attempt is not a
pass.  The uncapped `git diff --check` subsequently passed.  The memory ceiling
is retained for scientific Python, SymPy, and TeX jobs rather than used to
disable Git's status worker.

The advisory Science Forge shadow script exited zero while reporting the
pre-existing Forge binary/stdlib hash mismatch and compiler diagnostic E9118
in the independent bridge audit.  Its coverage census reported drift from the
976-certificate baseline to 1,536 certificates.  These are advisory findings,
not successful verification of this result; only the independent programme
import above is recorded as a pass.

Tier 2 is unnecessary because this certificate is a new consumer of unchanged,
content-addressed amplitude, branching, rigged, and Abel inputs.  Tier 3 is
unnecessary because no freeze, release, shared-core change, lifecycle promotion
beyond `CLASSIFIED`, complete probability, Eq. (19), gravitational transfer,
or Lorentzian theorem is asserted.  No skipped or advisory rail is counted as
a pass.

## Next gate

Compute the complete eight-point pre-trace quotient to determine the fourth
amplitude-affiliated jump and test local finiteness of the growing noise
multiplicity.  In parallel, construct an operator intertwiner from the
Abel-regularized physical collinear direct integral into the 75-mark Fock
noise.  Both are required before the finite reduced-mode cocycle can be
promoted toward a continuum asymptotic Møller construction.  Neither alone is
evidence for Eq. (19) or a Lorentzian S matrix.
