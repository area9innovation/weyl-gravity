# Typed outgoing joint frame at r=31

This package joins the independently certified outgoing `R+` and `S+`
partial-jet transports at the common radius \(r=31\), audits their realified
row layouts, and embeds the formal \(E,R,S\) columns in the complex six-state
factor order

\[
(X_{\rm tangent\ spin2},Y_{\rm carrier\ spin2},Z_{\rm spin1}).
\]

The selected complex minor on rows \((X_0,Y_0,Z_0)\) is block upper
triangular and has determinant

\[
R_{\rm base,0}^{\,2}S_{Z,0}.
\]

Exact rational hulls derived from the imported degree-four models certify
both factors nonzero on the complete frequency child. Therefore the reduced
outgoing frame has complex rank three.

The `R/E` and `S` artifacts retain different nonzero analytic phase
normalizations. Rank is invariant under those column rescalings, but this
package does not manufacture a common amplitude gauge. It therefore
preserves the formal canonical \(K_+=0\) result without promoting it to a
validated analytic endpoint-frame theorem.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_joint_frame_r31_v1.produce
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_joint_frame_r31_v1.produce --check
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_joint_frame_r31_v1.verify
python3 -m unittest black_hole_programme.phase3.axial_partial_jet_outgoing_joint_frame_r31_v1.test_joint_frame
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_joint_frame_r31_v1.audit
```
