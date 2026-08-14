# BT free Euclidean reconstruction obstruction

**Certificate:** `REVERSE_PHYSICS_BT_EUCLIDEAN_FREE_RECONSTRUCTION_OBSTRUCTION_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

**Lifecycle:** `OBSTRUCTION_PROVED`

## Result

The zero-mode-fixed positive BT Euclidean lattice fails ordinary
Osterwalder--Schrader reflection positivity at its free endpoint.  The
obstruction is finite-volume, exact, and shift invariant.  It is not a Monte
Carlo sign estimate and does not use the gauge-fixed constant mode.

On the periodic $6^4$ lattice, reflect time through the links by

\[
             \theta(t,\mathbf x)=(1-t\bmod 6,\mathbf x)
\]

and take the positive half to be $t=1,2,3$.  Write

\[
 A_t=6^{-3}\sum_{\mathbf x}\phi_{t,\mathbf x},
 \qquad F=-A_1+2A_2-A_3 .
\]

The coefficients of $F$ sum to zero, so $F$ is unchanged by the global
shift symmetry.  For the free BT Gaussian measure

\[
 S_{0,L}(\phi)=\frac12\sum_x(\Delta_L\phi_x)^2,
 \qquad \sum_x\phi_x=0,
\]

exact rational inversion on the spatially constant sector gives

\[
             \langle (\theta F)F\rangle_{0,6}=-\frac1{1296}<0.
\]

Ordinary reflection positivity requires this quadratic form to be
nonnegative for every positive-time cylinder function.  This one strict
negative value is therefore a finite-volume obstruction.

The obstruction is not confined to the single point $\lambda=0$.  On this
fixed graph write

\[
 S_{\lambda}(\phi)=\lambda^{-2}A(\lambda\phi).
\]

On the mean-zero hyperplane, $A$ has a unique zero at the origin, a positive
bilaplacian Hessian there, and the already-certified exponential coercive tail.
Consequently $A(\psi)\geq c_G\|\psi\|_2^2$ for some graph-dependent
$c_G>0$.  Thus $e^{-S_\lambda}$ and the quadratic witness have a common
Gaussian dominating function near zero.  Dominated convergence makes the
normalized reflected expectation continuous at $\lambda=0$, so its strict
negative sign persists for all $|\lambda|<\epsilon_G$ for some
$\epsilon_G>0$.  This existence proof does not quantify $\epsilon_G$ and
does not decide the simulation coupling $\lambda=0.4$.

## Exact calculation

The spatially constant sector reduces to a six-site mean-zero cycle.  Its
bilaplacian covariance has first row

\[
 C_6(0,\cdot)=\frac1{864}(329,119,-151,-265,-151,119).
\]

For $t,u\in\{1,2,3\}$, the reflected covariance is

\[
 K_{tu}=C_6(1-t,u)=\frac1{864}
 \begin{pmatrix}
 119&-151&-265\\
 -151&-265&-151\\
 -265&-151&119
 \end{pmatrix}.
\]

With $a=(-1,2,-1)$, exact arithmetic gives $a^TKa=-1/6$.  A spatial
slice average has covariance $C_6/6^3$, producing $-1/1296$ in four
dimensions.  The independent verifier does not invert the producer's matrix:
it checks the five-point bilaplacian difference equation, reconstructs the
reflection kernel, and evaluates the quadratic form separately.

## First volume-uniform estimate

The same free family decides which elementary topology can support the next
continuum step.  Let the trigonometric interpolation on the unit four-torus
have Fourier coefficients

\[
 \widehat\Phi_L(n)=L^{-4}\sum_x\phi_xe^{-2\pi i n\cdot x/L}.
\]

For $n\ne0$,

\[
 \mathbb E|\widehat\Phi_L(n)|^2
 =\frac{L^{-4}}{\omega_L(n)^2},\qquad
 \omega_L(n)=4\sum_{j=1}^4\sin^2\!\frac{\pi n_j}{L}.
\]

Using $2x/\pi\leq\sin x\leq x$ on
$0\leq x\leq\pi/2$ gives

\[
 \frac{16|n|^2}{L^2}\leq\omega_L(n)
 \leq\frac{4\pi^2|n|^2}{L^2}.
\]

The number of integer modes with $|n|_\infty=m$ is

\[
 (2m+1)^4-(2m-1)^4=64m^3+16m.
\]

The upper spectral bound and the shell count imply the exact uniform estimate

\[
 \sup_L\mathbb E\|\Phi_L\|_{H^{-1}(\mathbb T^4)}^2
 \leq\frac5{16}\sum_{m\geq1}\frac1{m^3}
 \leq\frac{15}{32}.
\]

The opposite inequality gives

\[
 \mathbb E\|\Phi_L\|_{L^2(\mathbb T^4)}^2
 \geq \frac{H_{\lfloor(L-1)/2\rfloor}}{4\pi^4}.
\]

Thus the unrenormalized free family has logarithmically divergent $L^2$
second moment.  A negative Sobolev topology is not optional bookkeeping: it
is the first simple volume-uniform rail that survives this critical
four-dimensional spectrum.

The $H^{-1}$ estimate is only a first estimate.  By itself it does not prove
tightness in $H^{-1}$, represented convergence, identification of a limit,
or an interacting estimate.

## Scientific meaning

The positive Boltzmann density is not sufficient for ordinary Hilbert-space
Euclidean reconstruction.  The free fourth-order sector already carries a
negative reflected direction.  This is consistent with the programme's
Krein motivation, but it does not construct a Krein reconstruction.

The explicit rational value is at $\lambda=0$, and the fixed-volume
continuity argument extends its sign to an unquantified open interval.  It
does not prove that the displayed witness remains negative at $\lambda=0.4$,
nor that every nonzero coupling fails reflection positivity.  The next
falsifiable gate is to quantify the interval or decide the sign directly at
$\lambda=0.4$, while seeking an interacting negative-Sobolev moment estimate.

## Verification

```text
python3 reverse_physics/bt_euclidean_free_reconstruction_obstruction.py --check
python3 reverse_physics/verify_bt_euclidean_free_reconstruction_obstruction.py
python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_free_reconstruction_obstruction
```

## Boundaries

- This does not establish reflection-positivity failure at $\lambda=0.4$ or every nonzero coupling.
- This does not exclude a modified Euclidean construction or an indefinite-metric reconstruction.
- This does not construct a continuum or infinite-volume BT measure.
- This does not promote the free $H^{-1}$ estimate to the interacting measure.
- This does not establish a Born rule, a scattering probability, or an event rate.
- This does not establish anything tagged `LORENTZIAN-CAUSAL`.

## Verification receipt

All rails were run sequentially.  The paper pass used a 500,000 KiB virtual
memory ceiling; no exhaustive reconstruction or large lattice job was run.

| tier or rail | result | elapsed | peak RSS |
|---|---:|---:|---:|
| Tier 0 parse, schema, generated JSON, scoped diff | pass | below 1 s | below 31 MiB |
| deterministic producer | 21/21 pass | 0.04 s | 20,736 KiB |
| method-distinct verifier | 19/19 pass | 0.10 s | 30,244 KiB |
| unit and six-mutation suite | 10 tests pass | 0.11 s | 30,408 KiB |
| Paper 21 bounded `pdflatex` pass | 38 pages, pass | 0.73 s | 53,020 KiB |

Tier 2 used the unchanged numerical pilot by content hash; it did not reproduce
the sampler.  Tier 3 was not run because no shared classical operator, freeze,
release, quantum lifecycle, or Lorentzian claim changed.  The prose advisory
is non-certifying: body budgets pass, while the pre-existing abstract remains
over its advisory word and numeric budgets.

CLOSE-OUT: SHORTFALL -- ordinary OS is obstructed near the free endpoint and the free topology rail is decided; lambda=0.4 and interacting uniform control remain open.

EVIDENCE: `reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FREE_RECONSTRUCTION_OBSTRUCTION_V1.json`
