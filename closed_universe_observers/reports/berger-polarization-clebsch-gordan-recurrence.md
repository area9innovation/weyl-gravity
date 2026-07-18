# Berger polarization Clebsch--Gordan recurrence

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

Each coordinate factor in the Berger detector polarizations is a linear
combination of conjugate spin-one-half representation coefficients.  The
Clebsch--Gordan product formula therefore rewrites
`x conjugate(D^j_rc)` using the two neighboring representations
`J=j+1/2` and `J=j-1/2`.  Axial averaging retains only diagonal scalar
coefficients.  An exact polynomial audit modulo the unit-sphere relation
passes through `two_j=4`; deleting the lower-spin channel produces nonzero
remainders.

For representation dimension `d`, the four coordinate factors have exactly
`6d-4` supported matrix entries and `16d-12` scalar recurrence terms, with at
most four terms in any supported entry.  Summing through the necessary
`two_j=138` capacity rail gives 57,824 entries and 154,012 scalar terms.  The
detector-specific coframe factors and the external clock factor `a(t)` are
retained explicitly.

This removes high-degree form-polynomial expansion from the selected
adaptive route.  It does not yet evaluate the neighboring scalar coefficient
stream, perform clock or temporal Green integration, certify the
Green-weighted tail, construct full Maxwell images, evaluate recoil, restrict
responses to the second-order cone, or activate the physical-branch bridge.
