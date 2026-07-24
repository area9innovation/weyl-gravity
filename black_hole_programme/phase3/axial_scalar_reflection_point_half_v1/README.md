# Scalar reflection at \(\omega=1/2\)

This package replaces the failed shared-frequency reflection cell by a
point-frequency calculation.  It transports the two scalar Regge--Wheeler
interaction systems in Arb ball arithmetic and certifies strict lower bounds
for both outgoing coefficients.

The future-horizon solution uses the programme convention
\(\psi\sim e^{+i\omega r_*}\).  At infinity,
\[
\psi=A_{{\rm in},s}e^{+i\omega r_*}
     +A_{{\rm out},s}e^{-i\omega r_*}.
\]
Thus the transported interaction coefficient \(b(+\infty)\) is exactly
\(A_{{\rm out},s}\).

Two separate Taylor geometries reproduce the conclusion.  Each local step
has an explicit Cauchy coefficient-tail bound and an a posteriori polynomial
defect propagated by Gronwall.  Exact elementary \(L^1\) integrals control
the omitted horizon and infinity tails.

The result is pointwise.  It neither repairs the earlier whole-frequency
cell nor constructs the off-diagonal entries of the full Bach \(T_+\).
