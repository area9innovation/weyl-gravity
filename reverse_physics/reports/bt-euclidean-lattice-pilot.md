# Bateman--Turok finite Euclidean lattice pilot

## Result

The Bateman--Turok perfect-square scalar now has a concrete finite-lattice
experiment in this repository.  The construction uses the original positive
Euclidean path integral, not the indefinite two-field theory:

\[
 \Omega_x=e^{\lambda\phi_x}>0,\qquad
 S_{E,L}=\frac1{2\lambda^2}\sum_x
 \left(\frac{(\Delta_L\Omega)_x}{\Omega_x}\right)^2,
 \qquad \sum_x\phi_x=0.
\]

On a connected periodic graph this action is nonnegative, exactly invariant
under a constant shift of \(\phi\), and has one zero-action orbit.  Fixing the
mean of \(\phi\) selects the unique vacuum \(\phi=0\).  Its vacuum Hessian is
the square of the graph Laplacian, so the free lattice propagator has the
expected inverse fourth-power spectrum.  The gauge-fixed action is coercive,
so its finite-dimensional partition function is finite.  These are exact finite-dimensional
statements carrying `LOCAL-ALGEBRAIC` and `EUCLIDEAN-SPECTRAL`; they do not use
or establish `LORENTZIAN-CAUSAL` data.

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_LATTICE_PILOT_V1`.

## A normalization issue in the new renormalization paper

Anderson, Bateman, Herzog and Turok, arXiv:2608.12210v1 (12 August
2026), make the lattice continuum limit an explicit proposed next project.
Their Eqs. (49), (51), (53) and (54) are mutually compatible, but the middle
expression displayed in Eq. (52) is not compatible with them as printed.

After integration by parts, Eq. (51) is pointwise quadratic in \(\Upsilon\):

\[
 L=-A\Upsilon-\frac g6B\Upsilon^2,
 \qquad A=\Box\Omega,\quad B=\Omega^2.
\]

Exact completion of the square gives

\[
 L=-\frac{gB}{6}\left(\Upsilon+\frac{3A}{gB}\right)^2
   +\frac{3A^2}{2gB}.
\]

Thus integrating out \(\Upsilon\) yields the coefficient \(3/(2g)\), not the
displayed \(1/(2g)\).  With their Eq. (54), \(g=-3\lambda^2\), the derived
coefficient becomes \(-1/(2\lambda^2)\), exactly reproducing their
perfect-square action after \(\Omega=e^{\lambda\sigma}\).  The displayed
coefficient would instead give \(-1/(6\lambda^2)\), a factor of one third.

The certificate classifies this as a displayed normalization inconsistency,
most naturally a missing factor three in Eq. (52).  It is not evidence against
their beta-function relation: the stated coupling map is precisely the one
selected by the corrected Gaussian elimination.

## Why this discretization

Discretizing \((\Delta\phi+\lambda(\partial\phi)^2)^2\) term by term leaves a
choice of lattice derivatives and loses the continuum chain rule at finite
spacing.  Discretizing the combined positive variable instead,

\[
 \frac{\Delta_L e^{\lambda\phi}}{\lambda e^{\lambda\phi}},
\]

preserves three structural facts exactly:

1. the action remains a real sum of squares;
2. \(\phi\mapsto\phi+c\) is an exact symmetry because the common scale of
   \(\Omega\) cancels in every ratio;
3. the measure \(\prod_x d\Omega_x/\Omega_x\) is flat in \(\phi\), up to an
   irrelevant constant Jacobian.

For a connected graph, \(S_{E,L}=0\) implies \(\Delta_L\Omega=0\); the kernel
of a connected graph Laplacian consists of constants.  At \(\phi=0\),

\[
 \frac{\Delta_L e^{\lambda\phi}}{\lambda e^{\lambda\phi}}
 =\Delta_L\phi+O(\lambda),
\]

so the Hessian is \(\Delta_L^2\).  On the periodic \(4^4\) pilot lattice, the
positive Laplacian eigenvalues and multiplicities are

| \(\widehat p^2\) | 0 | 2 | 4 | 6 | 8 | 10 | 12 | 14 | 16 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| multiplicity | 1 | 8 | 28 | 56 | 70 | 56 | 28 | 8 | 1 |

and the Hessian eigenvalues are their squares.  The single zero mode is removed
by \(\sum_x\phi_x=0\).

Normalizability follows from the same graph structure.  Let \(R\) be the
range of \(x=\lambda\phi\), let \(D\) be the graph diameter, and let \(q=2d\)
be the degree.  A shortest path from a minimum to a maximum contains an
oriented edge \(u\to v\) with \(x_v-x_u\ge R/D\).  At its lower endpoint,
\((\Delta_L\Omega)_u/\Omega_u\ge e^{R/D}-q\).  Hence, once the right-hand side
is positive,

\[
 S_{E,L}\ge \frac{(e^{R/D}-q)^2}{2\lambda^2}.
\]

On the mean-zero hyperplane the field norm can diverge only if \(R\) diverges.
The Boltzmann weight therefore decays faster than an exponential in every
unbounded direction and is integrable.  For the \(4^4\) graph, \(D=8\).

## Bounded HMC pilot

The producer ran a zero-mode-projected hybrid Monte Carlo chain in pure Python
on 256 variables.  Both runs used 400 warm-up trajectories, 800 recorded
samples separated by two trajectories, 18 leapfrog steps of size 0.035, and 20
blocked means.  The random seeds are fixed in the certificate.

| check | free \(\lambda=0\) | interacting \(\lambda=0.4\) |
|---|---:|---:|
| acceptance | 0.8755 | 0.8675 |
| action density | \(0.50060\pm0.00328\) | \(0.49332\pm0.00332\) |
| virial \(\langle\phi\cdot\nabla S\rangle/(N-1)\) | \(1.0051\pm0.0066\) | \(0.9975\pm0.0067\) |
| lowest-mode \(\widehat p^4\langle|\widetilde\phi_p|^2\rangle\) | \(1.0014\pm0.0268\) | \(0.9766\pm0.0134\) |
| action split-half \(z\) | 0.976 | 0.201 |

For the free mean-zero Gaussian, the exact action density is
\((256-1)/(2\cdot256)=255/512\), the virial ratio is one, and the normalized
mode ratio is one.  The free run agrees with all three.  The interacting run
satisfies the integration-by-parts/Schwinger--Dyson identity
\(\langle\phi\cdot\nabla S\rangle=N-1\).  A forward/backward leapfrog test has
maximum position and momentum residuals of order \(10^{-17}\).

The numerical values are typed `NUMERICAL_PILOT_OBSERVED`.  Re-running a fixed
seed reproduces them; it is not an independent scientific rail.  The separate
verifier instead re-derives the Gaussian coefficient, computes the graph
Laplacian kernel by exact rational elimination, obtains the \(4^4\) spectrum by
an independent convolution, and checks the nonlinear force against finite
differences.

## What this means

The computational experiment is operational.  We can generate configurations
from a finite positive Euclidean measure and measure nonperturbative
finite-volume correlation functions.  This is a substantive step beyond a
formal assertion that a lattice formulation exists.

It is not yet a test of whether the BT theory is a real continuum quantum field
theory.  A positive Boltzmann weight is not Osterwalder--Schrader reflection
positivity, and a Euclidean correlator is not automatically a Krein-space
scattering probability.  Nothing here measures the selected Lorentzian
\(q_8\) or \(q_{10}\) coefficients, supplies Eq. (19), or transfers the scalar
construction to full Weyl gravity.

## Next falsifiable gate

The next experiment should be a two-volume step-scaling study, but only after
an independent sampler reproduces the finite-volume observables.  A useful
sequence is:

1. implement an independent local Metropolis or Fourier-accelerated sampler;
2. compare both algorithms at \(L=4\) and \(L=6\) for the same action and
   zero-mode prescription;
3. define a renormalized coupling from connected finite-momentum correlators;
4. match physical volumes and measure its step scaling at several bare
   couplings;
5. compare the weak-coupling trend with the six-loop beta function of
   arXiv:2608.12210, then attempt a controlled continuum extrapolation.

Failure of sampler agreement, scaling collapse, or continuum extrapolation is
a genuine negative result.  Success would establish a Euclidean continuum
candidate, still leaving reconstruction and Lorentzian physics as separate
gates.

## Verification receipt

All scientific processes ran sequentially under `ulimit -v 500000` with the
mise Python 3.12.13 interpreter and single-thread numerical-library settings.

| tier | command or rail | result | elapsed | peak RSS |
|---|---|---:|---:|---:|
| 0/1 | producer, `--write` | PASS, 24/24 | 31.62 s | 18,040 KiB |
| 1 | independent verifier | PASS, 22/22 | 0.08 s | 24,532 KiB |
| 1 | scoped unit/mutation suite | PASS, 22 tests including 13 mutations | 33.03 s | 25,696 KiB |
| 2 | affected legacy IR-regulator producer/verifier/tests | PASS, hash-only certificate refresh; 9 tests | 0.36 s for tests | below 25 MiB |
| paper | Paper V, two final `pdflatex -halt-on-error` passes | PASS, 86 pages; six pre-existing overfull boxes, no undefined reference | 0.55 s final pass | 50,764 KiB |
| advisory | paper prose heuristic | NON-CERTIFYING finding: old parenthetical/abstract density remains | 1.1 s | not recorded |

The strict Science Forge shadow wrapper did not complete: after 17 minutes it
was stopped while blocked inside the external seed-studio `cbp query stdlib:`
shim; process inspection showed several identical audits orphaned for days.
This is recorded fail-closed, not as a pass.  Running `sfc conform planning`
directly with a sanitized path validated both new nodes, but the aggregate
command refused ten pre-existing `forge-requests/` states (`PROPOSED` or
`OPEN`).  The local producer/schema/verifier rails above do not depend on that
wrapper.  Tier 3 was not run: this delivery adds a `CLASSIFIED` finite-volume
pilot and a non-theorem paper paragraph, not a freeze, lifecycle promotion,
shared-core change, or release.

CLOSE-OUT: DONE -- the positive finite Euclidean BT lattice and bounded HMC
pilot are operational, with an exact factor-three normalization audit and no
continuum or Lorentzian promotion.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_LATTICE_PILOT_V1.json`
