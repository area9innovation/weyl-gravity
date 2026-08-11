# BT Appendix-C squeezed vacuum: ordinary Fock--Krein obstruction

**Result:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

The squeezed vacuum displayed in Appendix C of Bateman--Turok is null in the
indefinite Krein pairing, but it is not a vector in the positive topology of
the stated ordinary massless Fock--Krein carrier after the infrared cutoff is
removed.  The obstruction is already present in its first two-particle
component: its positive norm density diverges as the inverse minimum momentum.
An independent pair-block calculation gives the same obstruction through the
ordinary bosonic Fock Hilbert--Schmidt criterion.

This is a carrier theorem, not a refutation of the authors' algebraic map.
Finite volume is regular, and an explicitly extended or inequivalent non-Fock
representation could still carry the transformation.  Such a representation,
its domains, and its generalized Born trace are not supplied in the public
Letter.

## 1. Finite-box normalization

The Appendix-C cross commutators are

\[
 [b_\Omega(\mathbf p),b_\Upsilon^\dagger(\mathbf q)]
 =[b_\Upsilon(\mathbf p),b_\Omega^\dagger(\mathbf q)]
 =2|\mathbf p|(2\pi)^3\delta^3(\mathbf p-\mathbf q),
\]

with both same-species commutators zero.  Put the system in a periodic cubic
box of side (L), volume (V=L^3), and omit the zero mode before taking the
limit.  With

\[
 \int\frac{d^3p}{(2\pi)^3}\longrightarrow \frac1V\sum_{\mathbf p},
 \qquad b_X(\mathbf p)=\sqrt{2|\mathbf p|V}\,c_{X,\mathbf p},
\]

the discrete cross commutator is one.  The creation half of Eq. (C6) becomes

\[
 Q_+(t)=\sum_{\mathbf p\ne0}
 \frac{e^{2i|\mathbf p|t}}{8|\mathbf p|^2}
 c_{\Upsilon,\mathbf p}^\dagger
 c_{\Upsilon,-\mathbf p}^\dagger .
\]

The sum is over ordered momenta.  The (mathbf p) and (-\mathbf p) terms
therefore combine to amplitude (1/(4|\mathbf p|^2)) for each unordered pair.
These factors are retained explicitly in the certificate; no continuum delta
function is squared.

## 2. The compatible positive topology

On one momentum fiber, in the ordered basis ((\Omega,\Upsilon)), the Krein
Gram matrix is

\[
 J=\begin{pmatrix}0&1\\1&0\end{pmatrix}.
\]

A charge-exchanging fundamental symmetry has zero diagonal.  Requiring it to
be involutive, (J)-self-adjoint, and positive classifies the full family

\[
 \kappa_\rho=\begin{pmatrix}0&\rho\\\rho^{-1}&0\end{pmatrix},
 \qquad
 J\kappa_\rho=\begin{pmatrix}\rho^{-1}&0\\0&\rho\end{pmatrix},
 \qquad \rho>0.
\]

Thus a one-particle (Upsilon) mode has positive norm squared (ho).
Momentum-dependent (ho(\mathbf p)) is allowed, but equivalence to the
ordinary reference Fock topology requires uniform bounds

\[
 0<m\le \rho(\mathbf p)\le M<\infty.
\]

The exact producer checks four rational members of this family.  The
independent verifier reconstructs the classification from a generic
off-diagonal (2\times2) matrix rather than importing the producer.

## 3. Direct two-particle norm

Wick contraction in the positive (kappa_\rho) metric gives

\[
 \|Q_+|0\rangle\|_\kappa^2
 =\sum_{\mathbf p\ne0}\frac{\rho(\mathbf p)^2}{32|\mathbf p|^4}.
\]

For constant (ho), division by the box volume followed by the continuum
limit gives

\[
 \frac1V\|Q_+|0\rangle\|_\kappa^2
 =\frac{\rho^2}{64\pi^2}
 \int_\epsilon^\Lambda\frac{dp}{p^2}
 =\frac{\rho^2}{64\pi^2}
 \left(\frac1\epsilon-\frac1\Lambda\right).
\]

The ultraviolet tail converges; the massless infrared limit does not.  This is
stronger than the usual total-volume divergence.  Even the six ordered momenta
on the lowest shell, (|\mathbf p|=2\pi/L), obey

\[
 \|Q_+|0\rangle\|_\kappa^2
 \ge \frac{3m^2L^4}{256\pi^4},
 \qquad
 \frac1V\|Q_+|0\rangle\|_\kappa^2
 \ge \frac{3m^2L}{256\pi^4}.
\]

The norm density itself therefore grows linearly with box size.  Since
different particle-number sectors are orthogonal in the positive Fock
topology, no higher term in (e^{Q_+}|0\rangle) can cancel the divergent
two-particle sector.

## 4. Independent pair-block check

The commutator with the opposite cross oscillator is

\[
 [c_{\Omega,\mathbf p},Q_+]
 =\frac{e^{2i|\mathbf p|t}}{4|\mathbf p|^2}
 c_{\Upsilon,-\mathbf p}^\dagger .
\]

Consequently the pair-creation block has ordered Hilbert--Schmidt sum

\[
 \|\beta\|_{\rm HS}^2
 =\sum_{\mathbf p\ne0}\frac{\rho(\mathbf p)^2}{16|\mathbf p|^4}
 =2\|Q_+|0\rangle\|_\kappa^2.
\]

For constant (ho), its density is

\[
 \frac{\rho^2}{32\pi^2}
 \left(\frac1\epsilon-\frac1\Lambda\right).
\]

It therefore fails the ordinary bosonic Fock implementability criterion.
This second calculation is an interpretation and cross-check; the direct
two-particle-sector divergence above is the primary proof.  Extended
representations beyond the Hilbert--Schmidt condition are known as a
mathematical possibility, which is exactly why the certificate does not claim
that no representation exists.

## 5. Why nullity and a momentum weight do not repair it

The indefinite Krein norm of the created (Upsilon\Upsilon) sector vanishes
because same-species contractions vanish.  The positive norm does not vanish:
(kappa_\rho) pairs each (Upsilon) direction with a strictly positive
weight.  Indefinite nullity is therefore not a convergence test for the Fock
topology.

One can formally choose (ho(p)\sim p^\alpha).  The radial norm integral then
behaves as

\[
 \int_0 dp\,p^{2\alpha-2},
\]

which converges for (alpha>1/2).  But then (ho^{-1}) is unbounded at the
origin.  This changes to an inequivalent topology; it is not a repair inside
the stated ordinary Fock--Krein space.  It may instead be useful input for a
future extended representation, provided its domains and trace are defined.

The covariant zero-mode factor (Z^2) from the predecessor certificate also
does not alter the (p^{-2}) radial kernel on the candidate orbit module.  On
that module (Z) is isometric after Hilbertization.  A different unbounded
zero-mode representation would be new architecture and needs its own domain
analysis.

## 6. Disposition

Established exactly:

- the complete charge-exchanging positive fundamental-symmetry family on each
  cross-oscillator fiber;
- the finite-box coefficient (1/(8p^2)) and the two-particle positive norm;
- an infrared divergence proportional to (1/\epsilon), with a six-mode
  lower bound whose density grows as (L);
- the matching non-Hilbert--Schmidt pair-block obstruction;
- invariance of the divergence under uniformly equivalent positive metrics;
- the logical separation between indefinite nullity and positive-topology
  normalizability.

Not established:

- failure of the local algebraic canonical transformation;
- failure of Eq. (19) in a rigged, extended, or inequivalent non-Fock carrier;
- failure at finite volume or fixed infrared cutoff;
- the physical (1/48), a complete NLO probability, or beyond-tree
  positivity;
- a gravitational/BRST lift or anything `LORENTZIAN-CAUSAL`.

The work item therefore closes `OBSTRUCTED` on the ordinary Fock--Krein
architecture.  The next gate is constructive: specify an extended
Bogoliubov representation, its positive topology and dense domain, the full
zero-mode module, and a cyclic generalized-Born trace before revisiting
Eq. (19).

Verification commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_squeezed_vacuum_implementability.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_squeezed_vacuum_implementability.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_squeezed_vacuum_implementability
```

## Verification receipt (2026-08-11)

All scoped commands ran sequentially with `ulimit -v 500000`.

- Python parse/compile: PASS, 0.04 s, 15,492 KB peak RSS.
- Exact producer replay: PASS 26/26, 0.04 s, 20,644 KB peak RSS.
- Method-distinct schema, matrix-classification, Wick, shell-bound, pair-block,
  topology, provenance, and claim-boundary verifier: PASS 11/11, 0.12 s,
  30,104 KB peak RSS.
- Producer, verifier, and six decisive mutations: PASS 8/8, 0.80 s,
  30,348 KB peak RSS.  Mutations changed the radial power, Wick coefficient,
  lowest-shell multiplicity, topology-equivalence boundary, nullity inference,
  and extended-representation claim; every mutation was rejected.
- Content-addressed affected chain: inclusive-radical PASS 12/12 in 0.44 s
  (30,372 KB), fixed-vacuum oscillatory PASS 4/4 in 0.32 s (29,716 KB),
  soft-charge flow PASS 7/7 in 0.85 s (30,480 KB), and zero-mode trilemma
  PASS 7/7 in 0.83 s (30,356 KB).
- Papers V and VI: PASS, two `pdflatex -halt-on-error` passes each.  Paper V
  took 0.55/0.47 s; Paper VI took 0.51/0.56 s.  Peak RSS stayed below 51 MB.
  PDF text witnesses found the two-particle, ordinary-Fock, Hilbert--Schmidt,
  infrared-divergence, and extended/non-Fock boundary statements.
- The new schema, certificate, work item, and append-only event parsed as JSON.
  The event uses the established manual event-v0 fallback because the
  coordinator's Go startup is already certified to exceed the mandatory cap;
  its FNV-1a id is independently reproducible and no coordinator pass is
  claimed.
- The advisory Science Forge shadow rail is recorded as **FAIL**, not pass.  It
  was interrupted after 144.45 s (58,464 KB peak wrapper RSS) after two
  read-only corpus-index helper processes aborted and the wrapper stopped
  producing output.  This does not promote or invalidate the independent
  scoped certificate.
- The `s-f git status` wrapper also misrouted its read-only scan to the
  unrelated `bp2transformer` repository despite this working directory being
  `weyl-gravity`; its output was discarded.  Read-only Git plumbing confirmed
  the actual repository root and was used only to inspect this tree.  No
  coordination state was repaired or rewritten.

Tier 2 stopped at the content-addressed affected chain above.  Tier 3 was not
run because this is a `CLASSIFIED` carrier obstruction, not a freeze, release,
shared-core change, or lifecycle theorem promotion.
