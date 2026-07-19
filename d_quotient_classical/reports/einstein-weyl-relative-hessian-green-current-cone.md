# Relative Hessian Green-current cone

The complete action-derived Einstein--Maxwell and Weyl--Maxwell unary physical
Hessians define a local relative operator (E_{\rm rel}).  The serialized rows
are relative to the fixed product volume, so the coordinate-density operator
used here is (\widehat E_{\rm rel}=\sin\theta\,E_{\rm rel}).  Applying the
ordered multivariate Lagrange identity to every exact coefficient-jet monomial
constructs a Green concomitant (B_E) satisfying

\[
d_HB_E(u,v)=\langle u,\widehat E_{\rm rel}v\rangle
             -\langle \widehat E_{\rm rel}^{\sharp}u,v\rangle .
\]

The coefficient-jet replay verifies
(\widehat E_{\rm rel}^{\sharp}=\widehat E_{\rm rel}) directly, and
antisymmetrization gives the canonical current representative

\[
\omega_G(u,v)=\frac12\bigl(B_E(u,v)-B_E(v,u)\bigr).
\]

The finite telescoping replay is exact on all fourteen physical rows and all
coefficient jets.  The four components contain respectively
`922, 922, 928, 932` nonzero PBW terms, with maximum total derivative order
three.

This closes the relative Hessian divergence cone.  It does not yet precompose
the five stabilizer actions, compare this Green representative to the
Lee--Wald representative by a horizontal improvement, add cyclic BV-dual
rows, or reproduce the complete global five-charge operation by Cauchy-slice
integration.
