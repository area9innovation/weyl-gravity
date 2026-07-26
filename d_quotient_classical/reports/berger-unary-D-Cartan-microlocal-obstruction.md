# Microlocal obstruction to a bare-complex unary D-Cartan homotopy

At the exact null covector (zeta=(1,1,0,0)), the retained Douglis symbol
complex has ranks

\[
3\xrightarrow{K_1}10\xrightarrow{H_4}10\xrightarrow{L_1}3,
\qquad
(\operatorname{rank}K_1,\operatorname{rank}H_4,\operatorname{rank}L_1)
=(3,1,3).
\]

Its symbol-cohomology dimensions are therefore \((0,6,6,0)\). An explicit
field class is \(x=h_{\hat 0 2}\). It is \(H_4\)-closed, and the normalized
functional

\[
\ell(x)=x_{02}-x_{12}
\]

annihilates \(\operatorname{im}K_1\) while satisfying \(\ell(x)=1\).

At the same covector, \(\sigma(D)=\zeta_0=1\). If a finite-order local
\(\iota_D^{(1)}\) obeyed \([q_1,\iota_D^{(1)}]=D\), microlocal inversion of
\(D\) would contract the symbol complex, contradicting the displayed class.
The D-equivariant 54-to-26 SDR transfers the same obstruction to the bare
54-row complex.

This does not obstruct a residual/BFV or causal Cartan extension. It proves
that the next construction must enlarge or derive-reduce the complex rather
than attempting the arity-two equation on the bare local rows.

Reproduce from the standalone `weyl-gravity` repository root with:

```bash
python3 -m d_quotient_classical.backreacted_clock.berger_unary_d_cartan_obstruction --check --guards
python3 -m d_quotient_classical.backreacted_clock.verify_berger_unary_d_cartan_obstruction
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_unary_d_cartan_obstruction -v
```
