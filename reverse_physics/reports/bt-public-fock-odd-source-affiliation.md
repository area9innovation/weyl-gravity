# BT public-Fock odd-source affiliation

**Certificate:**
`REVERSE_PHYSICS_BT_PUBLIC_FOCK_ODD_SOURCE_AFFILIATION_V1`

**Lifecycle:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The ghost-odd source type required by the finite neutral graph projector is
not merely an abstract added summand.  It occurs canonically inside the public
two-profile $O(1,1)$ cross-Krein Fock carrier.  Moreover, the fourth
symmetric power of the already certified complement map gives an exact
charge- and parity-compatible metric affiliation between this public odd
sector and the selected complement composite.

This removes the **carrier-existence** obstruction.  It does not derive the
graph slope, show that the physical $\phi$ projection has support on the
sector, or prove the nonlinear Bateman--Turok $R_t$ identity in Eq. (19).
The remaining gate is dynamical rather than dimensional or representation
theoretic.

## Public neutral degree-four sector

Use two hard-profile copies of the public one-particle charge fibre with

\[
 J=\begin{pmatrix}0&1\\1&0\end{pmatrix}.
\]

At total degree four and total charge zero, two plus-charge and two
minus-charge quanta are distributed over the two profiles.  The occupation
types for each sign are

\[
 A=(2,0),\qquad B=(1,1),\qquad C=(0,2).
\]

Thus the neutral basis $e_{\alpha\beta}$ has nine elements.  Its public
Gram is

\[
 \langle e_{\alpha\beta},e_{\gamma\delta}\rangle_J
 =\alpha!\,\beta!\,
   \delta_{\alpha\delta}\delta_{\beta\gamma}.
\]

Ghost parity exchanges the two occupation indices,
$\kappa e_{\alpha\beta}=e_{\beta\alpha}$.  The fundamental metric
$W\kappa$ is the strictly positive diagonal matrix

\[
 \operatorname{diag}(4,2,4,2,1,2,4,2,4),
\]

and the public neutral sector has inertia

\[
 (n_+,n_-)=(6,3).
\]

Two of its negative directions are

\[
 w_1=\frac{e_{AB}-e_{BA}}2,
 \qquad
 w_2=\frac{e_{BC}-e_{CB}}2.
\]

They obey exactly

\[
 \langle w_i,w_j\rangle_J=-\delta_{ij},\qquad
 q(w_i)=0,\qquad
 \kappa w_i=-w_i.
\]

Their span is therefore precisely a two-dimensional neutral ghost-odd
source with metric $-I_2$, the type used in the preceding graph-projector
certificate.

## The induced map is exact

Let

\[
 C=\begin{pmatrix}-\rho&-1\\0&1\end{pmatrix},
 \qquad
 S=\begin{pmatrix}1&1\\0&-\rho\end{pmatrix},
 \qquad
 \rho=\frac{819}{4000}.
\]

The columns of $S$ are the complement charge eigenvectors
$n_+=(1,0)$ and $n_-=(1,-\rho)$.  Direct multiplication gives the
load-bearing identity

\[
 CS=-\rho I_2.
\]

Thus $C$ maps each complement charge line to the corresponding public
charge line with the same factor $-\rho$.  On total degree four the sign
disappears, and

\[
 \Phi=\operatorname{Sym}^4(C)=\rho^4 I_9
\]

in the occupation charge basis.  If $W$ is the public nine-dimensional
Gram and $G=\rho^8W$ the complement Gram, then

\[
 \Phi^T W\Phi=G.
\]

So the induced map is an isometry on the complete neutral degree-four sector,
not merely on the two selected vectors.

The complement vectors certified previously are

\[
 u_1=\frac{e_{AB}-e_{BA}}{\sqrt2\,\rho^4},
 \qquad
 u_2=\frac{e_{BC}-e_{CB}}{\sqrt2\,\rho^4},
\]

with Gram $-2I_2$.  Their exact images are

\[
 \Phi u_i=\sqrt2\,w_i.
\]

Equivalently, the selected inverse affiliation from the public odd sector to
the complement composite is

\[
 A=\frac1{\sqrt2}I_2,
 \qquad
 A^T(-2I_2)A=-I_2.
\]

Both selected spaces have total charge zero and ghost parity $-I_2$, hence
$A$ is charge neutral and ghost even.

## What changes in the graph construction

The abstract odd source $O$ in the preceding graph projector may now be
identified with

\[
 O=\operatorname{span}\{w_1,w_2\}
\]

inside the public two-profile Fock carrier.  The finite graph carrier is then
the concrete public/complement space $O\oplus\operatorname{span}\{u_1,u_2\}$,
not a formally adjoined parity label.

The graph slope remains

\[
 T=\operatorname{diag}\left(
   \frac{\sqrt{6699}}{16},
   \frac{\sqrt{7149}}{16}
 \right).
\]

It is not $A$, and it is not derived by
$\operatorname{Sym}^4(C)$.  The map $A$ identifies the carrier and its
metric type; $T$ contains the two eight-point response amplitudes.  A public
$R_t$ calculation must still generate $T$ dynamically.

The earlier positive-source obstruction also remains valid in its stated
scope.  The collapsed scalar hard-profile source has metric and parity
$+I_2$, whereas $O$ has metric and parity $-I_2$.  It cannot be directly
identified with $O$.  The new point is that the **full public Fock carrier**
is larger than that collapsed source and already contains the required odd
sector.

## Eq. (19) boundary

Established exactly:

- the public two-profile neutral degree-four Gram, parity and inertia
  $(6,3)$;
- a canonical two-dimensional public neutral ghost-odd subspace with Gram
  $-I_2$;
- $CS=-\rho I_2$ on the transported charge basis;
- the full-sector identity
  $\operatorname{Sym}^4(C)^TW\operatorname{Sym}^4(C)=\rho^8W$;
- the selected relation
  $\operatorname{Sym}^4(C)u_i=\sqrt2\,w_i$;
- the inverse charge-zero ghost-even isometry
  $A=(1/\sqrt2)I_2$; and
- a concrete public realization of the graph projector's odd source type.

Not established:

- support of the physical $\phi$ projection on this public odd sector;
- nonlinear $R_t$ production of the degree-four sector;
- the graph slope $T$ or its coefficients from $R_t$;
- the all-order Eq. (19) projector identity;
- a continuum or thermodynamic generalized-Born trace;
- weak ghost symmetry of a complete scattering process;
- a normalized fourth event or complete probability;
- a spacetime Møller, LSZ, or $S$ operator;
- a gravity/BRST lift or anything `LORENTZIAN-CAUSAL`; or
- literature priority.

## Next falsifying calculation

Compute the first nonlinear public $R_t$ term that can land in the neutral
degree-four sector, project it onto $\operatorname{span}\{w_1,w_2\}$, and
compare its exact graph coefficient with $T$.  Projector idempotence must be
enforced together with the already certified order-$\lambda$ corner
$Q_1=0$.

A mismatch would be a scoped dynamical obstruction.  A match would close the
finite coefficient gate, but the continuum trace and asymptotic domain would
still be required before promoting Eq. (19) or physical positivity.

## Verification receipt

All commands ran sequentially on 2026-08-12 under `ulimit -v 500000` with
Python 3.12.13 from
`/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3`.

- Tier 0 Python compilation and JSON parsing passed for all scoped files
  (`0.17 s`, peak `15020 KiB`).
- The producer passed 31/31 exact checks (`0.37 s`, peak `68292 KiB`).
- The independent verifier passed 24/24 checks, including schema and input
  hash validation (`0.54 s`, peak `70468 KiB`).
- The falsification suite passed 21/21 tests (`7.04 s`, peak `70920 KiB`),
  including mutations of the
  public Gram, parity, symmetric-power map, selected isometry, graph slope,
  $R_t$, Eq. (19), physical disposition and input hashes.
- Paper V built twice (`0.45 s`, `0.47 s`; peak `50080 KiB`, `50604 KiB`),
  retaining exactly its four pre-existing overfull boxes and adding none.
- Paper VI built twice (`0.48 s`, `0.47 s`; peak `50688 KiB`, `50956 KiB`)
  with no overfull box or undefined reference.
- The optional whole-program Science Forge import was **not passed** and was
  not used as evidence: the Forge Go runtime first exceeded the `500000 KiB`
  virtual-address cap and, on a capped retry, could not create a runtime
  thread.  Direct JSON parsing of the new append-only work item and event did
  pass.  This is a coordination-tool environment limitation, not a scientific
  verifier result.

The full degree-four reconstruction and independent verifier form the
affected Tier 2 chain.  Tier 3 is unnecessary because this result changes no
shared core, freeze, release, lifecycle state beyond `CLASSIFIED`, or
Lorentzian claim.
