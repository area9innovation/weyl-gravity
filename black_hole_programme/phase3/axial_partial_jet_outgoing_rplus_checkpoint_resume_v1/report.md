# Outgoing `R+` checkpoint/restart report

This package is intentionally limited to one selected outgoing column and two
bounded transport chunks.

The checkpoint wire format uses the Forge `ivtaylor-degree4-v1` serializer:
exact rational coefficients are canonical strings and every interval endpoint
is stored by its IEEE-754 bit pattern.  The base and intrinsic tangent models
retain the same omega generator.  The artifact also records the omega affine
model, stack order, radius, next panel centre and source hashes.

The restart program contains no call to the infinity seed constructor and
starts at the checkpoint's next panel centre.  Its checkpoint loader is
verified by a separate compile/run that reserializes both models identically,
including exact coefficient strings and interval endpoint bits.

The replay-free program advances the second 16-panel chunk to \(r=31\).  Its
complete terminal base/tangent serialization is required to equal an
independent 32-panel reference exactly.  This comparison detects loss of any
retained coefficient, interval endpoint bit, shared generator, or derivative
correlation.

The package does not establish transport below `r=31`, any complementary
outgoing column, `K_plus`, `T_plus`, reflection, scattering or flux.
