# C2g checkpoint: the complete minimal residual free sector

## Result

The first cutoff-complete residual-conformal BRST window is nontrivial and,
within that global-only free complex, positive.

The matter oscillator tower is the two-chirality on-shell Weyl-curvature
module.  For one chirality its character is

\[
\chi_+(q)
=\chi_{(2;2,0)}-\chi_{(4;1,1)}
+\chi_{(5;\frac12,\frac12)}
=\frac{5q^2-9q^4+4q^5}{(1-q)^4}.
\]

The three terms are the Weyl-curvature primary, the Bach equation, and its
divergence identity.  The exact all-level cylinder action reconstructed from
this module agrees with the `E/A/L` tower and its invariant form

\[
J_{\rm conf}=+I_E\oplus(-I_A)\oplus(-I_L).
\]

At matter weight four, the complete Fock shell has dimension

\[
82+\dim\operatorname{Sym}^2(\mathbb C^{10})=137
\]

and ambient signature `(97,40)`.  The relative primary conditions

\[
(D-4)|\Psi\rangle=0,
\qquad R|\Psi\rangle=0,
\qquad K^-|\Psi\rangle=0
\]

have exactly two solutions.  They are the normalized chiral Weyl-square
states

\[
|W^2_+\rangle,\qquad |W^2_-\rangle,
\]

and their matter Gram matrix is exactly

\[
J_{\rm rel}^{(4)}=I_2.
\]

The independent absolute global-only calculation closes the corresponding
kernel/image problem:

\[
0\longrightarrow C^4_0(55)
\mathop{\longrightarrow}^{d_4} C^5_0(385)
\mathop{\longrightarrow}^{d_5} C^6_0(1155),
\]

with

\[
d_5d_4=0,
\qquad \operatorname{rank}d_4=53.
\]

There is no incoming `C^3_0` space in this particle-number-two sector.
Consequently

\[
\boxed{
H^4_{\delta=0,\,N=2}(Q_{\rm residual})
=\operatorname{span}\{|W^2_+\rangle,|W^2_-\rangle\}.}
\]

By contrast, the one-particle window is exactly acyclic:

\[
C^3_0(290)\to C^4_0(1311)\to C^5_0(3657),
\qquad H^4_{\delta=0,N=1}=0.
\]

## Pairing

The residual ghost vacuum contains the four ghosts dual to the raising
generators and has compact ghost energy `-4`.  Hamada's seven-zero-mode
insertion normalizes this vacuum
to one.  In the exact exterior realization, the dynamic eight-ghost form is
nondegenerate with signature `(128,128)`, its centered degree-four block has
signature `(35,35)`, and the selected residual vacuum has norm `+1`.

Multiplying that unit ghost overlap by the matter restriction gives

\[
\boxed{J^{(4)}_{\rm global-only}=I_2.}
\]

This is the centered sector on which global conformal reduction removes all
forty negative matter directions and leaves a nonzero positive candidate
sector.  It is stronger than a sample cancellation: the complete incoming
and outgoing global differentials at this degree have been included.

Cartan localization makes the statement exhaustive for the minimal free
residual polarization.  The absolute residual differential obeys

\[
d\iota_D+\iota_Dd={\cal L}_D.
\]

Every total compact-degree sector `delta != 0` is therefore contractible.
At physical ghost number four the ghost degree is bounded below by `-4`, so
`delta=0` permits matter weight at most four and particle number at most two.
The remaining vacuum coefficient module has

\[
H^\bullet(\mathfrak{so}(4,2);\mathbb C)
\simeq\Lambda(u_3,u_5,u_7),
\qquad H^4=0.
\]

Together with the exact one- and two-particle results above, this proves

\[
\boxed{
H^4_{\rm residual,min}
=\operatorname{span}\{[W_+^2],[W_-^2]\},
\qquad G=I_2.}
\]

Thus `I2` is the complete centered cohomology of the minimal free residual
complex, not merely the beginning of a higher-weight tower.

## Interpretation

Parity exchanges the two chiral generators.  Their even and odd combinations
correspond, up to Lorentzian phase conventions, to the local densities

\[
C_{\mu\nu\rho\sigma}C^{\mu\nu\rho\sigma},
\qquad
C_{\mu\nu\rho\sigma}\widetilde C^{\mu\nu\rho\sigma}.
\]

The first is the pure-Weyl action density; the second is the Pontryagin
combination.  A later local-BV calculation must decide whether both survive
as state classes or whether the topological combination is identified or
removed.  The global calculation itself imposes no optional parity
projection and retains both with positive norm.

This result is compatible with three independent pieces of prior structure:

- Kubo--Kuntz identify the local gauge-reduced transverse Weyl sector but
  retain an indefinite unreduced physical form
  ([arXiv:2202.08298](https://arxiv.org/abs/2202.08298));
- Hamada exhibits a weight-four Weyl-square primary in a broader
  Riegert--Weyl residual-BRST construction
  ([arXiv:1202.4538](https://arxiv.org/abs/1202.4538)); and
- Boulanger--Henneaux identify the Weyl-square interaction as the consistent
  four-derivative deformation of linear conformal gravity under their
  locality assumptions
  ([hep-th/0106065](https://arxiv.org/abs/hep-th/0106065)).

None of those references alone proves the present pure-Weyl global reduction.
Conversely, the present calculation does not establish the local quantum
BRST or anomaly statements made in the broader Hamada model.

## Exact boundary of the claim

What is closed is the **free residual-global** complex built on the already
gauge-reduced pure-Weyl oscillator module.  The remaining bridge is to derive
the conformal-Killing zero-mode split from the full pure-Weyl Diff `x` Weyl
BV complex and prove that the associated spectral sequence collapses in this
sector.  Until that is done, `I_2` is not called the full physical Hilbert
space of pure Weyl gravity.

In particular this checkpoint does not yet prove:

1. anomaly-free nilpotency and adjointness of the complete quantum
   pure-Weyl BRST charge;
2. survival of both classes in combined local-plus-global cohomology;
3. interaction invariance of the reduced pairing; or
4. the corresponding statement when `D` is retained as an asymptotic or
   boundary charge rather than gauged.

The next discriminating problem is C2i: construct a compact-degree-equivariant
cyclic strong deformation retract of the full pure-Weyl local BV complex and
show that its transferred one-ghost/two-matter charge is the residual Taub
moment map already normalized in C2f.  The quantum Diff `x` Weyl anomaly is a
subsequent, logically separate obstruction.
