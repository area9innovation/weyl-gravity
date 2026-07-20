# Asymptotic Bach raw-flux corner obstruction

## Disposition

The requested linear null-infinity phase space does not close on the existing
reduced transverse-traceless indicial seed with the raw fourth-order
Lee--Wald current.

For

\[
S_{\rm red}=\frac12\int(\Box\phi)^2,\qquad
\chi=\Box\phi ,
\]

the exact Green/Lee--Wald current is

\[
j^\mu(\phi_1,\phi_2)=
\chi_1\nabla^\mu\phi_2-(\nabla^\mu\chi_1)\phi_2-(1\leftrightarrow2).
\]

In outgoing retarded coordinates, the large-\(r\) cut density
\(r^2j^r\) has the following certified behavior:

| input channels | leading cut behavior | disposition |
|---|---|---|
| \(p=0\) with \(p=0\) | \(2r(f_0g_0''-g_0f_0'')\) | generic linear divergence |
| \(p=0\) with \(p=1\) | \(2(f_0'g_0'-g_0f_0'')\) | finite cross term, not a \(p=1\)-\(p=1\) radiative form |
| \(p=1\) with \(p=1\) | coefficients at \(r^1,r^0,r^{-1}\) all vanish | zero raw \(\mathscr I^+\) flux |

The divergent coefficient is the exact retarded-time derivative

\[
\partial_u\!\left[2(f_0g_0'-g_0f_0')\right].
\]

It is therefore a corner term after integrating over all retarded time, but
it does not define a finite cutwise phase-space form.  Excluding \(p=0\) by
fixing the unphysical boundary metric removes the divergence and
simultaneously makes the remaining \(p=1\) carrier radical.

Hence the first honest boundary gate closes as

```text
asymptotically flat D verdict: PHASE_SPACE_NOT_CLOSED
Einstein verdict:              EINSTEIN_OPEN
```

This is a reduced-mode obstruction, not a no-go for a renormalized tensor
BV--BFV phase space.  The missing object is a covariant tensor boundary
counterterm and corner prescription whose improved current is finite,
conserved and gauge compatible.

## Generator and charge disposition

The four generators remain distinct:

| generator | boundary disposition | charge disposition |
|---|---|---|
| \(P_0=\partial_u\) | tangent to \(\mathscr I^+\) | `OPEN`; raw form divergent or radical |
| \(D_M=u\partial_u+r\partial_r\) | tangent to \(\mathscr I^+\) | `OPEN`; raw form divergent or radical |
| \(H_{\rm ESU}=(P_0+K_0)/2\) | not tangent to the boundary of one fixed Minkowski patch | `OBSTRUCTED` on this fixed-patch phase space |
| \(D_{\rm rad}\) | no real Lorentzian boundary lift declared | `NO_CERTIFIED_MAP` |

No ADM/Bondi charge, flux, charge algebra, particle, scattering, stability,
unitarity or compact-to-asymptotic mode map has been inferred.

## Domain ledger

The certificate declares the two-term \(p=0\) and \(p=1\) scalar TT
amplitudes for one angular eigenmode.  It leaves the following fields
fail-closed:

- ghosts and antifields;
- Coulombic aspects;
- \(\mathscr I^-\) and \(i^0\) matching;
- full tensor reconstruction;
- polyhomogeneous logarithmic/Jordan channels;
- a renormalized boundary potential.

The result carries only `LOCAL-ALGEBRAIC` and `REDUCED-MODE`.  It carries no
`LORENTZIAN-CAUSAL` tag.

## Evidence and verification

- certificate:
  `bridge/certificates/asymptotic_bach_raw_flux_corner_obstruction.json`;
- independent verifier:
  `bridge/einstein_sector/verify_asymptotic_bach_raw_flux_corner_obstruction.py`;
- generated atlas row:
  `einstein.asymptotic.minkowski.weyl.raw_flux_corner_obstruction`;
- receipt:
  `bridge/einstein_sector/receipts/ASYMPTOTIC_BACH_RAW_FLUX_CORNER_OBSTRUCTION_V1_TIER_RECEIPT.json`.

Tier 0, scoped Tier 1 and the atlas consumer chain pass.  Tier 3 is not
required because this is an explicitly reduced obstruction rather than a
freeze, release or shared-core promotion.

The next admissible gate is to derive the full tensor Bondi Lee--Wald
potential, boundary counterterm and \(i^0/\mathscr I^+\) corner prescription,
then repeat the differentiability tests for \(P_0\) and \(D_M\).

CLOSE-OUT: OBSTRUCTED — the first boundary/corner obstruction is certified
EVIDENCE: ASYMPTOTIC_BACH_RAW_FLUX_CORNER_OBSTRUCTION_V1_TIER_RECEIPT
