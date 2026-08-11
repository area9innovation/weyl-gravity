# BT neutral graph projector extension

**Certificate:**
`REVERSE_PHYSICS_BT_NEUTRAL_GRAPH_PROJECTOR_EXTENSION_V1`

**Lifecycle:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The neutral degree-four composite block now admits an exact finite projector.
The minimum repair is a two-dimensional ghost-odd source partner.  On the
augmented odd carrier, the resulting projector is idempotent, Krein
self-adjoint, charge neutral, ghost even, and has finite algebraic
generalized-Born trace two.

That does not yet prove Bateman--Turok Eq. (19).  The graph is negative
definite and cannot be affiliated to the original positive hard-profile
source by a nonzero ghost-even or norm-preserving map.  The calculation
therefore constructs the missing finite projector type while locating its
remaining missing object: the source-parity bridge that the public
$R_t$ data do not supply.

## Minimal odd source partner

Use the two normalized negative composite directions certified previously.
Their metric is

\[
 \eta_N=-2I_2.
\]

The original profile source has metric $+I_2$ and ghost parity $+I_2$.
A ghost-even forward block into the negative composite is impossible from
that source.  Adjoin instead an odd source $O$ with

\[
 \eta_O=-I_2,\qquad \kappa_O=-I_2.
\]

The exact graph slope is

\[
 T=\operatorname{diag}\left(
 \frac{\sqrt{6699}}{16},
 \frac{\sqrt{7149}}{16}\right),
\]

and it retains the fourth-profile block:

\[
 T^T\eta_NT
 =\operatorname{diag}\left(-\frac{6699}{128},
                           -\frac{7149}{128}\right)
 =K_4.
\]

Since both $T$ and $K_4$ have rank two, every source supporting an injective
realization has dimension at least two.  The displayed odd partner is
therefore minimal.

## Exact graph projector

On $O\oplus N$, put

\[
 \eta=\operatorname{diag}(-I_2,-2I_2),\qquad
 L=\binom{I_2}{T}.
\]

The graph Gram is

\[
 L^T\eta L=-M,\qquad
 M=I_2+2T^2
 =\operatorname{diag}\left(\frac{6827}{128},
                            \frac{7277}{128}\right)>0.
\]

The Krein-orthogonal graph projector is

\[
 P=L(L^T\eta L)^{-1}L^T\eta
 =
 \begin{pmatrix}
 128/6827&0&16\sqrt{6699}/6827&0\\
 0&128/7277&0&16\sqrt{7149}/7277\\
 8\sqrt{6699}/6827&0&6699/6827&0\\
 0&8\sqrt{7149}/7277&0&7149/7277
 \end{pmatrix}.
\]

Exact arithmetic gives

\[
 P^2=P,\qquad P^\sharp=P,\qquad
 [P,H_{\rm total}]=0,\qquad [P,\kappa_{\rm total}]=0,
\]

with $\kappa_{\rm total}=-I_4$.  Moreover,

\[
 \operatorname{rank}P=\operatorname{tr}P=2,\qquad
 \operatorname{tr}(P^\sharp P)=2.
\]

Thus the finite algebraic generalized-Born trace is positive.  It is a rank
weight, not a normalized fourth-event probability and not the continuum BT
trace.

The orthogonal complement is the graph

\[
 N_\perp=\binom{-2T}{I_2},
\]

for which

\[
 PN_\perp=0,\qquad
 L^T\eta N_\perp=0,\qquad
 N_\perp^T\eta N_\perp=-2M.
\]

Both range and kernel are negative definite, as required for a projector
living entirely in the odd fundamental-symmetry sector.

## Why it still does not attach to the positive source

Let $F$ map the original even profile source into the new odd partner.
Ghost evenness would require

\[
 (-I_2)F=F(+I_2),
\]

or $-F=F$.  The four-coefficient linear system has rank four and the unique
solution is

\[
 F=0.
\]

The metric obstruction is independent.  Every map into the graph has the
form $LA$, with pullback

\[
 (LA)^T\eta(LA)=-A^TMA\preceq0.
\]

It cannot equal the positive source metric $+I_2$.  Hence there is no
nonzero norm-preserving affiliation from the original positive source to
this minimal graph, over either real or complex Hilbert coefficients with
the corresponding adjoint.

This is not a contradiction with the graph construction: the projector is
perfectly valid on the added odd sector.  What is absent is evidence that
the BT homomorphism maps the physical $\phi$ projection into that sector.

## Eq. (19) boundary

Established exactly:

- minimal odd source-partner dimension two;
- exact reconstruction of $K_4$ as the graph slope pullback;
- the graph range and complementary kernel;
- projector idempotence and Krein self-adjointness;
- total-charge neutrality and ghost evenness;
- projector rank and finite algebraic Born trace two;
- the rank-four parity obstruction to direct affiliation; and
- the signature obstruction to a norm-preserving positive-source map.

Not established:

- that $R_t$ supplies the odd source partner;
- affiliation to the original $\phi$ projection;
- the all-order Eq. (19) identity;
- the continuum or thermodynamic generalized-Born trace;
- weak ghost symmetry of a complete scattering process;
- a normalized fourth event or complete probability;
- a spacetime Møller, LSZ, or S operator;
- a gravity/BRST lift or anything `LORENTZIAN-CAUSAL`; or
- literature priority.

## Next gate

The smallest remaining algebraic problem is a signature-balanced extension:
add a positive target/source sector alongside the odd graph and solve the
complete ghost-even projector equations with a nonzero corner from the
certified positive profile source.  The public $R_t$ compression and the
order-$\lambda$ result $Q_1=0$ must remain fixed corners.

If such a projector exists, its trace must be compared with the exact
eight-point profile response before any physical promotion.  If it does not,
the affiliation obstruction advances from this minimal graph to the complete
finite public carrier.

## Verification receipt

All commands ran sequentially on 2026-08-12 under `ulimit -v 500000` with
Python 3.12.13 from
`/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3`.

- Tier 0 Python compilation passed for the producer, verifier, and mutation
  tests (`0.03 s`, peak `15036 KiB`).
- Tier 0 JSON parsing passed for the work item, transition event, certificate,
  and schema (`0.13 s`, peak `14136 KiB`).
- `python3 reverse_physics/bt_neutral_graph_projector_extension.py --check`
  passed `26/26` exact checks (`0.34 s`, peak `68620 KiB`).
- `python3 reverse_physics/verify_bt_neutral_graph_projector_extension.py`
  passed `26/26` independent checks, including schema validation
  (`0.39 s`, peak `72600 KiB`).
- `python3 -m unittest
  reverse_physics.tests.test_bt_neutral_graph_projector_extension` passed
  `21/21` falsification tests (`6.53 s`, peak `72724 KiB`).
- Two-pass `pdflatex` builds of Paper V passed (`0.45 s`, `0.45 s`; peak
  `50792 KiB`, `51012 KiB`), retaining exactly its four pre-existing overfull
  boxes and introducing no new one.
- Two-pass `pdflatex` builds of Paper VI passed (`0.47 s`, `0.47 s`; peak
  `50632 KiB`, `51140 KiB`) with no overfull box or undefined reference.

The producer imports every mathematical predecessor by content hash.  The
graph-projector reconstruction, parity system, and independent verifier form
the affected Tier 2 chain.  Tier 3 was unnecessary because no shared core,
freeze, release, lifecycle promotion beyond `CLASSIFIED`, or Lorentzian claim
changed.
