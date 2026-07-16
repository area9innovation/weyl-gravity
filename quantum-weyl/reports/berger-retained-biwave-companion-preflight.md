# Berger retained biwave companion preflight

The support-local classical contraction does more than remove clock rows from
the abstract complex. Independent exact PBW projection verifies

\[
P_{26}=\pi_{\rm cl}P_{34}^{\rm raw}\iota_{\rm cl},
\qquad
(P_{26})_{\rm metric}=A_{10}=\Box_2^2+V_2.
\]

Thus the lower-by-two tensor biwave is exactly the metric operator that must
be solved on the retained `3|10|10|3` endpoint. It is not merely a convenient
raw-coordinate surrogate.

The local twenty-row companion is

\[
\mathcal C_{20}=
\begin{pmatrix}
\Box_2&-I_{10}\\
V_2&\Box_2
\end{pmatrix},
\qquad
J(h)=(h,\Box_2h),
\]

and the exact graph identity is

\[
\mathcal C_{20}J(h)=(0,A_{10}h).
\]

Its order-two principal symbol is block lower triangular with determinant
`q^20`. At the exact rational Berger fixture it has rank seven on a metric-null
covector and rank twenty off the metric cone. Unlike the full 13-row
clock/graph endpoint, this retained companion introduces no extra
characteristic cone.

This is the correct starting point for a causal Volterra construction, not
the construction itself. Convergence, global causal support, advanced and
retarded operators, the 26- and 54-row chain homotopies, Hadamard data and all
quantum claims remain open. No inverse spatial Laplacian or mode projector is
allowed.

```text
PYTHONPATH=quantum-weyl python -m lorentzian.retained_biwave_companion_preflight_certificate --check
PYTHONPATH=quantum-weyl python -m unittest quantum-weyl/lorentzian/tests/test_retained_biwave_companion_preflight.py -v
```
