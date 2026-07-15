# Compensated sourced-defect Ward chain map

## Why the target had to be split

A fixed external source is not a dynamical BV field.  It has no kinetic
equation, gauge ghosts, antifields, or BV pairing.  Consequently there is no
universal “matter-inclusive BV complex” until a matter action is selected.

There is, however, a universal external-source Ward complex.  On the constant
compensator frame its degree-zero source multiplet is

\[
(T_{\mu\nu},J_\phi),
\]

and its Ward map is

\[
W_S(T,J)=
\left(
\partial^\mu T_{\mu\nu},
T^\mu{}_\mu-vJ_\phi
\right).
\]

This is the strongest model-independent object to which the Einstein defect
can be lifted.  The genuine matter BV realization is a subsequent,
model-dependent theorem.

## Exact obstruction chain map

Define

\[
Q(T)_{\mu\nu}
=\frac12\Box T_{\mu\nu}
-\frac16(\eta_{\mu\nu}\Box-\partial_\mu\partial_\nu)T^\rho{}_\rho.
\]

Let the obstruction Ward map record divergence and trace.  Exact polynomial
calculation gives

\[
\partial^\mu Q(T)_{\mu\nu}
=\frac12\Box\partial^\mu T_{\mu\nu},
\qquad
Q(T)^\mu{}_\mu=0.
\]

Thus the square

\[
\begin{array}{ccc}
(T,J) & \xrightarrow{W_S} &
(\partial\!\cdot T,\operatorname{tr}T-vJ)\\
\downarrow Q && \downarrow
\operatorname{diag}(\tfrac12\Box I_4,0)\\
Q(T) & \xrightarrow{(\partial\cdot,\operatorname{tr})} &
(\partial\!\cdot Q(T),\operatorname{tr}Q(T))
\end{array}
\]

commutes exactly.  In particular, \(Q\) maps source Ward cycles to conserved,
traceless obstruction tensors.  It does not vanish on all Ward cycles.

## Exact Einstein-defect chain map

For the invariant metric perturbation define

\[
\Delta_{\mu\nu}
=G^{(1)}_{\mu\nu}(\widehat h)-\frac1{c_1}T_{\mu\nu}.
\]

The independently exported compensated operator verifies

\[
K_{EW}=c_1G^{(1)}+2\alpha QG^{(1)}.
\]

The Bianchi identity produces the second commuting square:

\[
\partial^\mu\Delta_{\mu\nu}
=-\frac1{c_1}\partial^\mu T_{\mu\nu},
\qquad
\Delta(R_{\rm diff}\xi,0,0)=0.
\]

Most importantly, the full sourced Einstein--Weyl residual factors exactly as

\[
\boxed{
E_{EW}
=(c_1I+2\alpha Q)\Delta
+\frac{2\alpha}{c_1}Q(T)
}.
\]

Therefore, on the Einstein locus \(\Delta=0\), the Einstein--Weyl equation is
satisfied with the same source if and only if

\[
\boxed{Q(T)=0}.
\]

This is now a chain-map theorem, not only an equation-level interpretation.

## Exact admissible-source fibers

At `v=1`, the simultaneous kernel of the Ward map and \(Q\) has:

| Representative covector | Ward-cycle dimension | \(W_S=0\) and \(Q(T)=0\) dimension |
|---|---:|---:|
| generic `p=(2,1,0,0)` | 6 | 1 |
| nonzero null `p=(1,0,0,1)` | 6 | 5 |
| zero `p=0` | 10 | 10, ledger only |

The certificate exports an exact inclusion matrix for every listed kernel.
The generic result makes the main obstruction particularly clear: Diff x Weyl
Ward compatibility alone leaves five additional source directions that excite
the non-Einstein branch.

At nonzero null momentum, \(Q(T)=0\) reduces the six Ward-compatible source
directions to the five conserved traceless directions.  This is a local symbol
statement, not a classification of global matter solutions.

## Dressed source

The higher-derivative dressing

\[
T_{EW}=T+\frac{2\alpha}{c_1}Q(T),
\qquad
J_{EW}=J,
\]

is itself an exact endomorphism of the source Ward complex.  This explains why
it is consistent.  It still changes the coupling and therefore does not turn
the same-source Einstein sector into a generic equivalence.

## Interpretation and next gate

The result establishes the universal part of the sourced problem:

\[
\boxed{
\text{external source Ward complex}
\longrightarrow
\text{Einstein-defect Ward complex}
}.
\]

It deliberately does not assert

\[
\text{external source complex}=\text{matter BV complex}.
\]

The next theorem must select a matter action and construct its Euler,
gauge/ghost, antifield, Noether, pairing, and cyclicity rows.  The stress/source
realization must then be proved to intertwine that matter BV differential with
the universal Ward complex above, and the matter equations must preserve
\(Q(T)=0\).

The positive Berger conformal-scalar model is a concrete candidate.  Its
current certificate constructs an exact support-local cyclic SDR for the eight
temporal/Weyl clock and minimal-dual rows, leaving a 26-row retained minimal
complex.  The retained coefficientwise `q1`, nonminimal rows, Green homotopies,
and stability remain open, so it is not yet a full matter-BV input for this
lift.  Moreover, its curved compact background is not silently identified
with the flat compensator phase used here.

Only after that lift should the programme construct retarded/advanced defect
propagation.

Machine certificate:
`bridge/certificates/compensated_sourced_defect_chain_map.json`.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.
