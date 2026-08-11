# BT neutral bosonic composite lift

**Certificate:**
`REVERSE_PHYSICS_BT_NEUTRAL_BOSONIC_COMPOSITE_LIFT_V1`

**Lifecycle:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The rank-two negative fourth-profile block has an exact charge-neutral
bosonic higher-composite realization.  Its minimal total boson degree is
four, not two.  The construction breaks the neutral-composite dimension
barrier, but it exposes the next one: the required negative directions are
ghost-parity odd, so this finite block is not the ghost-even neutral operator
claimed in Bateman--Turok Eq. (19).

Let the two hard-profile fibres be labelled $i=33,34$.  In the transported
null charge basis, write $p_i$ and $m_i$ for charge $+1$ and $-1$,
with one-particle pairings

\[
 \langle p_i,m_j\rangle=\rho^2\delta_{ij},\qquad
 \langle p_i,p_j\rangle=\langle m_i,m_j\rangle=0,
 \qquad \rho=\frac{819}{4000}.
\]

These are two orthogonal copies of the charge fibre already fixed by the
physical Møller complement.  The calculation below uses the canonical
symmetric-boson contraction induced by this pairing.

## Why degree two is too small

A neutral state of total degree $2k$ contains $k$ positive- and $k$
negative-charge quanta.  With two profile modes there are

\[
 d=k+1
\]

occupation types for each sign.  A neutral occupation basis is therefore
indexed by ordered pairs \((\alpha,\beta)\), with dimension $d^2$.  Its
Gram pairs \((\alpha,\beta)\) with \((\beta,\alpha)\), multiplied by positive
factorials.  Consequently its inertia is

\[
 \left(\frac{d(d+1)}2,\frac{d(d-1)}2\right).
\]

Thus

| total degree | neutral dimension | positive index | negative index |
|---:|---:|---:|---:|
| 0 | 1 | 1 | 0 |
| 2 | 4 | 3 | 1 |
| 4 | 9 | 6 | 3 |

Odd degrees have no charge-zero sector.  Since

\[
 K_4=\operatorname{diag}(-6699/128,-7149/128)
\]

has negative rank two, the degree-two neutral sector cannot carry it.  Degree
four is the first possible symmetric-bosonic carrier.

## Exact degree-four construction

At degree four, the positive- and negative-charge occupation types are

\[
 A=(2,0),\qquad B=(1,1),\qquad C=(0,2).
\]

Write $e_{\alpha\beta}=p^\alpha m^\beta$.  The induced Gram is

\[
 \langle e_{\alpha\beta},e_{\gamma\delta}\rangle
 =\alpha!\,\beta!\,\rho^8
   \delta_{\alpha\delta}\delta_{\beta\gamma}.
\]

Occupation swap \(\kappa e_{\alpha\beta}=e_{\beta\alpha}\) is the induced
ghost parity.  The metric multiplied by \(\kappa\) is diagonal and strictly
positive, so symmetric occupation combinations are positive and
antisymmetric combinations are negative.

Choose

\[
 u_1=\frac{e_{AB}-e_{BA}}{\sqrt2\,\rho^4},\qquad
 u_2=\frac{e_{BC}-e_{CB}}{\sqrt2\,\rho^4}.
\]

They are genuine symmetric-Fock states: the antisymmetry is between the two
distinct hard-profile occupation assignments, not between boson slots.  They
obey

\[
 q(u_1)=q(u_2)=0,\qquad
 \kappa u_i=-u_i,\qquad
 \langle u_i,u_j\rangle=-2\delta_{ij}.
\]

The forward block

\[
 B_4=\begin{pmatrix}u_1&u_2\end{pmatrix}
 \operatorname{diag}\left(\frac{\sqrt{6699}}{16},
                           \frac{\sqrt{7149}}{16}\right)
\]

therefore satisfies exactly

\[
 B_4^\sharp B_4
 =\operatorname{diag}\left(-\frac{6699}{128},
                            -\frac{7149}{128}\right)
 =K_4.
\]

On the direct sum of the positive profile source and the neutral degree-four
sector,

\[
 \mathcal K_4=
 \begin{pmatrix}0&-B_4^\sharp\\B_4&0\end{pmatrix}
\]

is exactly Krein skew and commutes with total charge.  This is the first
explicit charge-compatible neutral composite generator carrying both hard
profile amplitudes.

## The new Eq. (19) gate

The same construction is not ghost even.  The source profile metric is
positive, hence its fundamental symmetry is $+I_2$, while

\[
 \kappa B_4=-B_4,
 \qquad
 \kappa_{\rm total}\mathcal K_4\kappa_{\rm total}=-\mathcal K_4.
\]

This is structural: every negative direction of the neutral occupation-swap
Gram is ghost odd.  Bateman--Turok's neutral $P$ term in Eq. (19), by
contrast, is asserted to be ghost even.  Therefore the minimal block cannot
be identified with that $P$ term when the two-point profile source is kept
as the declared positive, ghost-even carrier.

Indeed, any ghost-even forward block $D$ from that source obeys
$\kappa D=D$, and hence

\[
 D^\sharp D=D^TG_4D=D^T(G_4\kappa)D\succeq0,
\]

because $G_4\kappa$ is the explicitly certified positive diagonal
fundamental metric.  Such a block cannot equal the strictly negative $K_4$.
This is a forward-block obstruction, not a no-go for a larger projector
carrying additional source parity.

The remaining possibilities are now narrower:

1. the actual BT projector supplies a ghost-odd source partner, so the
   complete map is ghost even although this forward subblock is odd;
2. a larger neutral projector contains additional terms that change the
   scalar profile pullback before the trace; or
3. a zero-mode/dynamical trace realizes the cross term without treating this
   finite forward block as the complete $P$ operator.

The first option is the next finite algebraic gate.  It must satisfy
idempotence, Krein self-adjointness, total charge zero, and ghost evenness
simultaneously while reducing to the certified $Q_1=0$ order-
\(\lambda\) sector.

## Claim boundary

Established exactly:

- the symmetric-bosonic neutral-sector inertia formula over two profile
  modes;
- the degree-two negative-index obstruction;
- minimality of total degree four for a rank-two negative pullback;
- the complete nine-dimensional degree-four neutral Gram and fundamental
  symmetry;
- two orthogonal normalized charge-zero negative vectors;
- exact reconstruction of both entries of $K_4$;
- a charge-neutral Krein-skew finite block generator; and
- ghost oddness of that generator with a ghost-even positive profile source.

Not established:

- the all-order Bateman--Turok Eq. (19);
- a BT derivation of the degree-four coefficients or carrier;
- a ghost-even complete projector;
- weak ghost symmetry of a scattering process;
- a generalized-Born trace;
- a normalized fourth event or complete probability;
- a spacetime Møller, LSZ, or S operator;
- a gravity/BRST lift or anything `LORENTZIAN-CAUSAL`; or
- literature priority.

## Verification receipt

All commands ran sequentially on 2026-08-12 with `ulimit -v 500000` and
Python 3.12.13 from
`/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3`.

- Tier 0 Python compilation passed for the producer, verifier, and mutation
  tests (`0.05 s`, peak `15320 KiB`).
- Tier 0 JSON parsing passed for the work item, transition event, certificate,
  and schema (`0.18 s`, peak `14176 KiB`).
- `python3 reverse_physics/bt_neutral_bosonic_composite_lift.py --check`
  passed `26/26` exact checks (`0.80 s`, peak `69404 KiB`).
- `python3 reverse_physics/verify_bt_neutral_bosonic_composite_lift.py`
  passed `25/25` independent checks, including schema validation
  (`0.97 s`, peak `72924 KiB`).
- `python3 -m unittest
  reverse_physics.tests.test_bt_neutral_bosonic_composite_lift` passed
  `20/20` falsification tests (`12.88 s`, peak `73276 KiB`).
- Two-pass `pdflatex` builds of Paper V passed (`0.54 s`, `0.49 s`; peak
  `50516 KiB`, `50808 KiB`), retaining exactly its four pre-existing overfull
  boxes and introducing no new one.
- Two-pass `pdflatex` builds of Paper VI passed (`0.52 s`, `0.50 s`; peak
  `50624 KiB`, `50444 KiB`) with no overfull box or undefined reference.

The producer imports every mathematical predecessor by content hash.  The
degree-four Fock reconstruction and independent verifier form the affected
Tier 2 chain.  Tier 3 is not required because this result does not change a
shared core, freeze, release, theorem lifecycle beyond `CLASSIFIED`, or any
Lorentzian claim.
