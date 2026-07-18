# Covariant curvature-squared logarithmic effective action

Status:
`COVARIANT_CURVATURE_SQUARED_C2_LOG_CERTIFIED_CUBIC_COMPLETION_AND_FINITE_NORMALIZATIONS_OPEN`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

## Result

Let `Delta_C` be a positive self-adjoint Laplace-type operator on the
algebraic Weyl-tensor bundle, with a fixed common elliptic domain. On the
source complement of its kernel, define the logarithm spectrally. Covariant
perturbation theory through total curvature order two then gives

\[
 \Gamma_{1,C^2\log}^{(2)}
 =-\frac{1}{(4\pi)^2}\frac{199}{60}
 \left\langle C,\Pi_\perp
 \log\frac{\Delta_C}{\mu^2}\Pi_\perp C\right\rangle .
\]

The exact spectral identity

\[
 \mu\partial_\mu\log(\Delta_C/\mu^2)=-2\Pi_\perp
\]

reproduces the certified scale response `(199/30)<C,C>`. On a flat TT
carrier this reduces to the already certified

\[
 F_C(p^2;\mu)=-\frac{199}{60}\log\frac{p^2}{\mu^2}+z_C(\mu).
\]

## Why the result is operator-independent at this order

Two self-adjoint Laplace-type representatives with the same rough principal
part differ by a curvature-order-one bundle endomorphism:

\[
 \Delta_C'=\Delta_C+V_1+O(\mathcal R^2).
\]

The Fréchet derivative of the spectral logarithm is

\[
 d\log(\Delta_C)[V_1]
 =\int_0^\infty
 (\Delta_C+s)^{-1}V_1(\Delta_C+s)^{-1}\,ds.
\]

Since each exterior Weyl tensor has curvature order one, the change in the
sandwiched functional has order

\[
 1+1+1=3.
\]

Thus the covariant logarithm is universal through `O(mathcal R^2)`. The first
missing completion data for this `C2` carrier are the cubic nonlocal form
factors, not another choice of quadratic Laplacian. This is precisely the curvature-order separation used in
covariant perturbation theory; see
[Barvinsky--Gusev--Zhytnikov--Vilkovisky](https://arxiv.org/abs/0911.1168).
The explicit nonlinear-completion analysis of
[Donoghue--El-Menoufi](https://arxiv.org/abs/1507.06321) likewise shows that
covariantizing a flat logarithm supplies the quadratic-curvature term while
matching corrections begin at cubic curvature order.

## Normalization and global boundary

The additive finite `C2` constant and the independent finite `R2` constant
remain unfixed. The certified anomaly vector does not determine the
independent `R2` form factor or its logarithmic coefficient. Kernel modes,
boundary transgressions and choices of
global elliptic domain remain explicit data; the logarithm at zero eigenvalue
is not silently defined.

The available Berger `34 -> 26` contraction cannot close the compensator
gate. Its symbol `tau` denotes the temporal diffeomorphism ghost of a
positive-Berger gravity--clock complex, whereas Wess--Zumino `tau` is a scalar
Weyl compensator in the local BV theory. They are different generators on
different carriers.

## Claim boundary

This is a covariant Euclidean effective-action result through curvature order
two. It is not the cubic or complete curved Weyl-invariant remainder, a finite
normalization, a local-Weyl completion, a zero-mode theorem, a Lorentzian
branch prescription, a renormalized time-ordered product or BV Laplacian, a
complete `Gamma1` or `Q1`, an extended classical residual contraction,
residual transfer, Bridge 4, Bridge 5, a Hadamard state or a particle result.
