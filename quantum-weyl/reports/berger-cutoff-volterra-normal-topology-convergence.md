# Berger cutoff Volterra normal-topology convergence

The cutoff companion Volterra series now converges on every compact time
slab in the fixed Hörmander normal topology, for both causal signs and for
the formal-transpose series.

The load-bearing simplification is the certified finite triangular
reduction.  The order-two term

\[
V_\chi=\chi(t)V_2
\]

is absorbed before the infinite series is formed.  The remaining incidence
is the constant order-zero block

\[
N=\begin{pmatrix}0&-I_{10}\\0&0\end{pmatrix}.
\]

This reduction is imported from
`BERGER_TYPED_COMPANION_MOLLER_PREFLIGHT`, including all eight exact
noncommutative intertwining and adjoint checks; it is not reconstructed from
the displayed block matrix.

Consequently every \(n\)-th kernel term is a finite sum of proper
push-forwards over an ordered \(n\)-simplex of compact-parameter families of
normally-hyperbolic wave FIOs and smooth local insertions.  The normal
topology makes the required tensor products, smooth multiplications and
proper push-forwards uniformly controlled on compact parameter sets.

For every defining normal seminorm \(p\), only a fixed number \(r_p\) of
symbol derivatives is tested.  A finite chart/block alphabet contributes at
most exponentially in \(n\), while Leibniz distribution contributes
\(\binom{n+r_p}{r_p}\).  The ordered time simplex gives the decisive
factorial:

\[
p(K_n)\le
A_p\binom{n+r_p}{r_p}
\frac{(B_p|I|)^n}{n!}.
\]

The exact ratio is

\[
\frac{a_{n+1}}{a_n}
=
(B_p|I|)
\frac{n+r_p+1}{(n+1)^2}
\longrightarrow0.
\]

Thus the series is absolutely summable in every normal seminorm.
Completeness of \(\mathcal D'_{\Gamma_\pm}\) supplies the limit.  Reversing
the factors gives the same argument for the formal transpose in the
opposite-oriented cone.

It follows that

\[
\operatorname{WF}'(G_{\chi,\pm})
\subset\Delta\cup R_\pm,
\]

the cutoff Pauli--Jordan kernel is null-cone decomposable, the Hermitian
dilation remains decomposable, and the two regular Cauchy morphisms have the
cone action required for Hadamard transport.

This does not yet perform that transport.  No covariance on the full
dilation, raw companion, or graded BV complex is claimed; BRST Ward
identities, physical positivity, renormalized Lorentzian products and the
Lorentzian QME remain open.

Primary analytic inputs:

- [Dabrowski--Brouder, functional properties and completeness of
  \(\mathcal D'_\Gamma\)](https://arxiv.org/abs/1308.1061);
- [Brouder--Dang--Hélein, normal-topology operations and parameter
  families](https://arxiv.org/abs/1409.7662);
- [Fewster, decomposable Green-hyperbolic Hadamard
  transport](https://arxiv.org/abs/2503.12537).

```text
PYTHONPATH=quantum-weyl python -m lorentzian.berger_cutoff_volterra_normal_topology_convergence_certificate --check
PYTHONPATH=quantum-weyl python -m lorentzian.verify_berger_cutoff_volterra_normal_topology_convergence
PYTHONPATH=quantum-weyl python -m unittest quantum-weyl/lorentzian/tests/test_berger_cutoff_volterra_normal_topology_convergence.py -v
```
