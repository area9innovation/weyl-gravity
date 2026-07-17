# Plebański–Hacyan stabilizer descent gate

Result:
`PH_STABILIZER_AUTHORITY_AND_GENERIC_PRIMARY_EQUIVARIANCE_CERTIFIED_GAUGE_QUOTIENT_NOT_AUTHORIZED`.

The connected background automorphism algebra of the fixed-flux compactified
Plebański–Hacyan fixture is

```text
R H  direct-sum  R P_x  direct-sum  so(3).
```

Its five generators are time translation, circle translation, and the three
sphere rotations.  The rotations carry the standard patchwise Maxwell gauge
compensators.  The Weyl compensator is zero.  A constant `U(1)` parameter is a
reducibility parameter acting trivially on connection differences, not a sixth
Hamiltonian stabilizer charge.

The full `SO(4,2)` algebra of the conformally flat vacuum cylinder is not a
background stabilizer here.  The nonzero product Weyl tensor, `S1`
periodicity, product topology, and magnetic flux prevent importing that
vacuum residual complex.

For every physical `ell>=2` and allowed compact momentum, the generic axial
and polar modules have the common form

```text
((K[omega]/(p))^2 direct-sum K[omega]/(q)) tensor V_ell.
```

The Einstein image is the `q`-primary summand and the extra quotient consists
of the two `p`-primary summands.  `H` and `P_x` act by multiplication by
`-i omega` and `i k`; rotations act only on `V_ell`.  Hence both primary
sectors, both parities, and their direct Lee–Wald forms are invariant.

This does not authorize a quotient.  The certified nondegenerate extra blocks
give explicit nonzero moment-map matrix elements:

```text
h(e,i rho(H)e)=omega_e h(e,e),
h(e,i rho(P_x)e)=-k h(e,e),
h(e tensor v_m,i rho(J_0)(e tensor v_m))=-m h(e,e) w_m.
```

Thus the stabilizers are not universal presymplectic-radical directions on
the complete generic phase space.  They remain global symmetries unless a
separate moment-map/Taub-zero derived sector is constructed and a null
subalgebra is then proved gauge.

The corrected sequence is therefore:

```text
local Diff x Weyl x U(1) quotient
  -> representation of the five-generator background stabilizer
  -> compute the common moment-map/Taub-zero locus
  -> quotient only by a subalgebra certified null on that declared locus.
```

No residual CE cohomology, cyclic BV enhancement, causal phase space, particle
space, or quantum statement is claimed.

Verification:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_plebanski_hacyan_stabilizer --verify bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json
python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_plebanski_hacyan_stabilizer
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_plebanski_hacyan_stabilizer
```

Tier 0 completed in `0.07` seconds and the scoped Tier-1 rail in `1.15`
seconds, both `PASS`.  No content-addressed upstream operator or current was
changed, so Tier 2 was not required.  Tier 3 was not run because this result
does not freeze a paper theorem, change shared core algebra, prepare a release,
or promote a causal or quantum lifecycle state.
