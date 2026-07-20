# Berger free-dilation Krein CCR covariance

Dependency tag: `LORENTZIAN-CAUSAL`

The certified free rank-40 Hadamard bisolution can be normalized exactly
against the project causal commutator.  Because the free dilation is real and
formally symmetric, replace a Feynman propagator by

\[
G_F^{\rm sym}=\frac12(G_F+G_F^T).
\]

The transpose average is still an exact Feynman propagator.  The project uses

\[
E=G_{\rm ret}-G_{\rm adv},
\]

opposite to the causal-propagator sign in the source.  Therefore define

\[
W_{\rm free}=+i(G_F^{\rm sym}-G_{\rm adv}).
\]

Then

\[
W_{\rm free}-W_{\rm free}^T=iE_{\rm free}
\]

exactly, while the Hadamard wavefront relation and both field equations are
unchanged.  This yields a normalized global Krein covariance on the
indefinite auxiliary dilation.

The fibre form has signature \((20,20)\), so this quasifree functional is not
a positive state.  Cutoff/full transport, restriction to the raw companion
or graded BV complex, the BRST Ward identity and positivity on physical
cohomology remain open.

The transpose-symmetrization is taken from the proof of Theorem 4 in
Christopher J. Fewster and Alexander Strohmaier, *On the construction of
Hadamard states from Feynman propagators*, arXiv:2510.11492.  Only the
symmetry/CCR step is used; the positive-definite hypothesis required for a
state is not asserted.
