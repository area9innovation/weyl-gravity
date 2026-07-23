# Axial boundary devissage and no-growth theorem

This package restricts the exact
\(L_{\rm RW},L_{\rm RW},L_x\) filtration of the complete axial
\(\ell=2\) Bach system to the separated-mode boundary class

* future-horizon regular in ingoing Eddington--Finkelstein coordinates;
* zero incoming coefficient (pure outgoing) at spatial infinity.

The repository phase is \(\exp(+i\omega t)\).  Growth therefore means
\(\operatorname{Im}\omega<0\).  In that half-plane, the horizon factor
\(\exp(+i\omega r_*)\) and infinity factor
\(\exp(-i\omega r_*)\) both decay on a constant-\(t\) slice.

Exact local factor frames show that the quotient and inclusion maps preserve
the two boundary germ classes.  Each diagonal scalar factor is a
nonnegative Regge--Wheeler operator, so it has no such lower-half-plane
mode.  Successive quotient elimination then proves that the complete
six-state axial system has no exponentially growing separated mode in this
boundary class.

The intrinsic regularized Evans product is

\[
E_{\rm reg}(\omega)=A_{{\rm in},2}(\omega)^2
                    A_{{\rm in},1}(\omega).
\]

It has no zero for \(\operatorname{Im}\omega<0\).  The upper-half-plane
points \(i/4,i/2,i\) are damped frame/reconstruction events in this phase
convention.  Their regularized Evans status is not classified here.

At a simple damped spin-two scalar QNM, the remaining extension question is
reduced to one Fredholm pairing.  Its value distinguishes the local Smith
types \(\operatorname{diag}(1,\delta^2)\) and
\(\operatorname{diag}(\delta,\delta)\).  That pairing is an explicit next
gate, not a result of this package.
