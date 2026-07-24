# Outgoing typed reduced frame at r=31

## Established

The existing `R+` and `S+` checkpoints are now joined with an explicit row
crosswalk. The four rows in each `R+` model are the realification of one
complex two-state spin-two column. The eight rows in each `S+` model are the
realification of the complex four-state \((Y,Z)\) base and its
\((X,0_Z)\) tangent.

In six-state factor order the columns are

\[
E=(R_{\rm base},0,0),\qquad
R=(R_{\rm tangent},R_{\rm base},0),\qquad
S=(S_{\rm tangent},S_Y,S_Z).
\]

On rows \((X_0,Y_0,Z_0)\), their determinant is

\[
R_{\rm base,0}^{\,2}S_{Z,0}.
\]

The exact real hull of \(R_{\rm base,0}\) lies strictly above zero, as does
the exact real hull of \(S_{Z,0}\). Hence the minor is nonzero throughout the
frequency child \([1/2,4097/8192]\), and the reduced outgoing frame has
complex rank three in common generator 7315. The wide tangent remainders do
not enter this filtration minor.

The nominal spin-one rows in the stored `S+` tangent have exactly zero Taylor
coefficients. Their interval padding contains zero; the exact zero is typed
by the imported partial-jet crosswalk and is not inferred from a narrow
floating-point enclosure.

## Fail-closed endpoint conclusion

This closes the correlated-`S+` and common-radius rank gates, but it does not
promote the formal canonical \(K_+=0\) calculation to an analytic endpoint
jet frame. The `R/E` reduced phase is

\[
e^{-2i\omega r}r^{-4i\omega},
\]

whereas the stored `S` phase is

\[
e^{-2i\omega(r-32)}(r/32)^{-4i\omega-1}.
\]

At \(r=31\) their ratio is the nonzero analytic scalar

\[
\frac{32}{31}e^{i\omega(64+4\log 32)}.
\]

This leaves rank unchanged, but no certified common amplitude gauge,
analytic endpoint \(\tau\)-family, moving-exponent derivative, or endpoint
frame-derivative matrix has yet been applied. Accordingly analytic
\(K_+\), \(T_+\), scattering, Stokes, and flux claims remain false.

CLOSE-OUT: SHORTFALL — typed reduced E/R/S rank-three frame certified at r=31; analytic K_plus and common amplitude frame remain open.

EVIDENCE: `black_hole_programme/phase3/axial_partial_jet_outgoing_joint_frame_r31_v1/certificate.json`

MISSING-DEP: common analytic endpoint phase/amplitude gauge with a certified tau-family and endpoint derivative matrices
