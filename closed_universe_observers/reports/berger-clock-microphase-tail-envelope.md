# Berger clock-microphase tail envelope

Status: `CERTIFIED` for a fixed spatial profile; the moving Berger detector
profile and physical full tail remain `OPEN`.

For the normalized clock kernel

`B(s) cos(sqrt(58)s/288) cos(s sqrt(lambda)/48)`,

two integrations by parts give a uniform `1/lambda` envelope.  Boundary
flatness removes all endpoint terms.  The exact identity for `B_ss` has one
sign change, so its `L1` norm is controlled by twice the unique maximum of
`|B_s|`; this avoids a loose pointwise derivative bound.

Combining the envelope with the correlated physical-space `N=1` norm still
leaves the frozen-profile bound non-small above retained `two_j=1024`.  For
this particular bound, retained `two_j=3421` is the first integer cutoff at
which both polarization tails are below one.

This is not yet the physical tail theorem.  The detector one-form itself
moves with the clock-dependent rods and Gram factor, so a clock-derivative or
commutator bound is required before applying the frozen-vector envelope.  A
complete low-mode projection is also still absent.  Full Maxwell and massive
images, response, recoil, and the second-order-cone restriction remain open.
