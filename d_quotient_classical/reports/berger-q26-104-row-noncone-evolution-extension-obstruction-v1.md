# Berger q26 non-cone evolution-extension obstruction

The exact rational non-cone feasibility differential is nilpotent and has
the retained cohomology dimensions, but it cannot carry the frozen \(A_{104}\)
evolution.

At the left endpoint, source basis vector \(e_{16}\) has differential

\[
d_{-1}e_{16}=(e_5,0),
\]

where the first component is old and the second is new.  The old covector
\(e_{25}^*\) annihilates the old projection of the entire boundary space:

\[
e_{25}^*\,\operatorname{pr}_{\rm old}d_{-1}=0.
\]

But the specialized frozen evolution satisfies

\[
A_{104}^{(0)}e_5=-\frac{51}{2}e_{25}
                  +\frac{111}{4}e_{35},
\qquad
e_{25}^*A_{104}^{(0)}e_5=-\frac{51}{2}.
\]

If \(E\) were any chain endomorphism with old-old degree-zero compression
\(A_{104}^{(0)}\), then the old projection of
\(E_0d_{-1}e_{16}\) would be \(A_{104}^{(0)}e_5\), while the old projection
of \(d_{-1}E_{-1}e_{16}\) would lie in
\(\operatorname{pr}_{\rm old}\operatorname{im}d_{-1}\).  Applying
\(e_{25}^*\) gives \(-51/2=0\), a contradiction.  The argument eliminates
all new-row blocks of \(E\) without solving for them.

This closes only the serialized rational feasibility witness.  It is not a
no-go theorem for every 104-new-row non-cone differential.  The next solve
must impose nilpotence and \(A_{104}\)-equivariance simultaneously before
cyclicity, reality and the retained SDR are tested.
