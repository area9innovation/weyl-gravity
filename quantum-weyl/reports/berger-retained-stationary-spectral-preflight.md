# Berger retained stationary spectral preflight

The retained 26-row causal witness is not itself a uniform fourth-order
Cauchy operator. Exact extraction of its pure temporal leading coefficient
gives ranks

\[
(3,8,8,3)
\]

on bundle ranks \((3,10,10,3)\). In particular, attempting to obtain a
26-row first-order generator by inverting the fourth-time-derivative
coefficient would divide by a singular metric block.

The exact Volterra construction already supplies the correct replacement.
Use rank-six second-order companions for the ghost and identity products,
the exact rank-twenty companion

\[
C_{20}=\begin{pmatrix}\Box_2&-I_{10}\\V_2&\Box_2\end{pmatrix}
\]

for the metric, and its rank-twenty formal-adjoint companion. The resulting
hybrid second-order bundle has rank

\[
6+20+20+6=52,
\]

so its first-order Cauchy generator acts on rank-104 data. This operator,
denoted \(A_{104}\), is the correct stationary spectral target.

The differential block form, temporal degree, leading rank, stationary
action \(D=e_0=\partial_t\), global causal evolution and local metric energy
spaces are now pinned. What is not yet exported is a common graded
Hilbert/Krein Cauchy space and dense graph domain on which \(A_{104}\) is
closed and generates time translation.

Compactness of the spatial Berger sphere and finite-slab energy estimates do
not by themselves prove compact resolvent for this non-self-adjoint
mixed-order Krein generator. Before defining a zero-mode projector, one must
prove compact resolvent, an analytic Fredholm alternative, or another theorem
that isolates zero with finite algebraic multiplicity. Only then may one set

\[
P_0=\frac{1}{2\pi i}\oint(z-A_{104})^{-1}\,dz,
\qquad
E_0=\operatorname{ran}P_0=\bigcup_k\ker A_{104}^k.
\]

The nilpotent Jordan restriction on \(E_0\) must be computed, not only the
ordinary kernel. A finite-rank smooth Riesz projector is permitted for state
selection after isolation is proved; it remains forbidden in the causal
advanced/retarded construction.

The covariance lift is also frozen in an unambiguous two-slot form,

\[
\omega_{54}(f,h)=\omega_{26}(\pi_{\rm cl}f,\pi_{\rm cl}h).
\]

Its operator expression uses the separately certified cyclic adjoint
identification \(\pi_{\rm cl}=\iota_{\rm cl}^{\sharp}\).

The minimal missing carrier is therefore the closed graded/Krein realization
of \(A_{104}\) together with an isolated-zero spectral calculus. No Riesz
projector, frequency splitting, covariance, Hadamard state, positivity, QME
or quantum theorem is claimed.

```text
PYTHONPATH=quantum-weyl python3 -m lorentzian.berger_retained_stationary_spectral_preflight_certificate --check
PYTHONPATH=quantum-weyl python3 -m lorentzian.verify_berger_retained_stationary_spectral_preflight
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_berger_retained_stationary_spectral_preflight.py -v
```
