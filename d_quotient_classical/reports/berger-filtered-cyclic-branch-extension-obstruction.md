# Filtered cyclic Einstein--Weyl branch-extension obstruction

## The extension category

On the certified physical principal module, let

\[
A=\mathbb Q(\sqrt{10})[\epsilon]/(\epsilon^2),\qquad
0\longrightarrow H_{\rm hel}\otimes\epsilon A
\longrightarrow H_{\rm hel}\otimes A
\longrightarrow H_{\rm hel}\otimes A/\epsilon A
\longrightarrow0.
\]

The three terms are the principal Einstein layer, repeated-wave Weyl layer,
and additional-Weyl quotient.  An admissible split must lift this sequence to
finite-order support-local filtered chain maps on the retained cyclic BV
complex, preserve the typed pairing and the retained `K_Berger` action, and
use no Green, inverse-Laplacian, helicity-mode, or row-name projector.

## First invariant obstruction

At the first nonzero filtered page the lifting equation is

\[
M X=T,\qquad
M=[\sigma_4(H),J_{\rm phys},\sigma_2(V_2)\sigma_1(K)],\qquad
T=\sigma_2(V_2)I_{\rm phys}.
\]

It already quotients every principal Hessian boundary, physical-equation
representative, and spatial-gauge change of the field representatives.  The
invariant class is

\[
\beta_1=\pi_{\operatorname{coker}M}T.
\]

The certified ranks are `rank(M)=4`, `rank(M,T_plus)=5`, and
`rank(M,T_cross)=4`.  The normalized exact covector annihilates `M` and
evaluates on the two physical columns as `(1,0)`.  Thus the cross
polarization lifts, with coefficient `71/40`, but the complete rank-two
physical module does not.

Any cyclic `L_infinity` branch split has a unary filtered cyclic chain split.
Its restriction to this fibre would force `beta_1=0`.  Therefore no such
split exists on the retained 36-row carrier.  The rank-46 STF2 graph
prolongation cannot change the verdict: it is a cyclic contractible SDR with
Schur complement `A10`, so it induces the same obstruction quotient.

## Complete minimal page repair

For any finite first-page problem let `o:H->Q=coker(M)`.  An enlargement by a
field correction space `Z` contributes a map `j:Z->Q`; cyclicity adds the dual
equation space `Z^vee`.  The enlarged page lifts if and only if

\[
\operatorname{im}o\subseteq\operatorname{im}j.
\]

Consequently the minimum is `dim Z=rank(o)`, and every minimal repair is,
up to filtered cyclic isomorphism and contractible hyperbolic summands, the
hyperbolic completion of `im(o)`.  Contractible SDR enlargements have no new
image in `Q` and cannot repair a nonzero class.

Here `rank(o)=1` at the standard fibre.  Exactly one noncontractible field
direction and its cyclic dual -- two BV rows -- are necessary and sufficient
at this page.  A global support-local repair must instead close the
obstruction image under the residual action and solve the later filtered
pages.  That bundle and its rank are not certified.

## Relation to the retained mixed ell3

This unary extension class and the landed ternary deformation class are
different.  `beta_1` prevents an admissible branch projection from existing;
the separate 22-row witness prevents removal of the mixed retained `ell3`
within the declared filtered cyclic `F2/F3` class on the unsplit carrier.
Neither result authorizes assigning `ell3` coefficients to Einstein-like or
additional-Weyl modes.

CLOSE-OUT: OBSTRUCTED — the first invariant unary extension class is nonzero, and the minimal page-level noncontractible repair is classified
EVIDENCE: d_quotient_classical/certificates/BERGER_FILTERED_CYCLIC_BRANCH_EXTENSION_OBSTRUCTION_V1.json
