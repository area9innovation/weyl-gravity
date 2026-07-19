# Invariant proof of the Einstein metric biwave identity

Fix the project conventions in dimension four and let the background satisfy

\[
\operatorname{Ric}(g)=g,
\qquad R(g)=4.
\]

Let \(K:T^*M\to S^2_0T^*M\) be the conformal-Killing operator, let
\(D=\operatorname{div}\), and let

\[
\mathcal G(h)=\delta\bigl(\operatorname{Ric}-\tfrac12Rg+g\bigr)(h)
\]

be the linearized cosmological Einstein operator.  The Pauli--Fierz algebraic
map and its inverse are

\[
F(h)=h-g\operatorname{tr}h,
\qquad
F^{-1}(t)=t-\tfrac13g\operatorname{tr}t.
\]

## 1. Einstein detour identity

Linearize

\[
B^{\rm std}_{ab}=\nabla^c\nabla^dC_{acbd}
 +\tfrac12R^{cd}C_{acbd}
\]

at the Einstein background.  Substitute the variation of the Levi--Civita
connection in both derivative slots, use the differential Bianchi identity,
\(\nabla^a\mathcal G_{ab}=0\), and \(R_{ab}=g_{ab}\).  The trace part is
removed by \(F^{-1}\).  In the conventions used by the repository this gives

\[
B_{\rm std}=-\mathcal G F^{-1}\mathcal G-\frac13\mathcal G.
\tag{1}
\]

The action Hessian is \(B_{\rm action}=-2B_{\rm std}\).  Equation (1) is an
identity of natural differential operators; it does not assume
\(\nabla C=0\).  The exact unit-Nariai PBW replay independently fixes the two
coefficients in (1) to \((-1,-1/3)\), with coefficient and augmented ranks
both equal to two.

The same Einstein-background detour identity is obtained from the auxiliary
quadratic conformal-gravity action in Deser--Joung--Waldron,
[*Partial Masslessness and Conformal Gravity*](https://arxiv.org/abs/1208.1307),
Eq. (12).  Their signs and cosmological-constant normalization differ from
the repository convention; the PBW replay above fixes that translation rather
than importing it by inspection.

## 2. Gauge-fixed Einstein identity

On trace-free symmetric tensors, commute the two derivatives in
\(\mathcal G\) and use the Einstein curvature decomposition.  With the
project's normalization of \(K\) and \(D\),

\[
-2\Pi_{\rm TF}\mathcal G+KD
 =\Box+2C\!\cdot-\frac23
 =:L_E,
\tag{2}
\]

where \((C\!\cdot h)_{ab}=C_a{}^c{}_b{}^dh_{cd}\).  The contracted Bianchi
identity and (1), followed by one further derivative commutation, give

\[
B_{\rm action}+\frac12KT
 =\frac12L_E\left(L_E-\frac23\right),
\tag{3}
\]

with

\[
T=\Box D-\frac13dDD+\frac13D.
\tag{4}
\]

The corresponding ghost identity is

\[
TK=(\Box+1)(\Box+\tfrac13).
\tag{5}
\]

All terms containing derivatives of the Weyl tensor in the expansion of the
left-hand side of (3) are precisely those produced when the left factor in
the right-hand side differentiates the zeroth-order Weyl action.  Therefore
they are retained, rather than discarded by a parallel-curvature
specialization.

## 3. Green operators

Set

\[
L_{\rm PM}=L_E-\frac23
 =\Box+2C\!\cdot-\frac43.
\]

Both \(L_E\) and \(L_{\rm PM}\) have scalar metric principal symbol and are
normally hyperbolic.  The Weyl action is a pointwise endomorphism and is
self-adjoint for the trace-free fibre pairing.  Moreover

\[
[L_E,L_{\rm PM}]=0
\]

identically because the two operators differ by the constant scalar shift
\(-2/3\).  Let \(G_{E,\pm}\) and \(G_{{\rm PM},\pm}\) be their unique
advanced/retarded Green operators.  Then

\[
G_{{\rm metric},\pm}
 =2G_{{\rm PM},\pm}G_{E,\pm}
\]

is both a left and right Green inverse of the metric witness block in (3).
The composition is same-sided, hence its support remains in
\(J^\pm(\operatorname{supp}f)\).  Equation (5) gives the analogous ghost
inverse.  Formal self-adjointness and uniqueness give advanced/retarded
adjoint reversal, and the already certified four-row witness construction
then supplies the degree-minus-one Green homotopies.

## 4. Kantowski--Sachs application and boundary

Every exact member of the certified common-slab Kantowski--Sachs family
satisfies \(\operatorname{Ric}=g\).  Each open slab is globally hyperbolic
with compact Cauchy surfaces and all metrics share a declared wider reference
cone.  Thus the preceding construction applies on every such slab even though
the Weyl tensor is not parallel for nonzero deformation parameter.

This proof concerns the four-row metric endpoint.  It does not identify the
six geometric operator differences in the rank-310 HPL presentation and does
not by itself transport the endpoint Green homotopy to all 310 rows.
