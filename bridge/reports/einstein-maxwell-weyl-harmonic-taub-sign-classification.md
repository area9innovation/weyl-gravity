# Harmonic Taub-sign stratification on the compact Plebański–Hacyan fixture

## Result

The fixture-level sign pattern extends to the complete *certified
additional-Weyl solution cofiber*, but not to the whole Weyl–Maxwell target.
On the fixed magnetic bundle,

```text
generic p-primary extra modes, ell>=2, all k, both parities:  mu_H < 0,
exceptional extra modes, ell=1, all k, both parities:          mu_H < 0.
```

Fourier, spherical, parity and shell orthogonality make the Hamiltonian
moment map additive.  Opposite momenta have the same frequency squared and
the same action-derived current Gram, so neither their relative phases nor a
sum over several absolute momenta can cancel this negative pure-extra sum.
Consequently every nonzero finite real tangent supported only on certified
extra cofiber oscillators is obstructed at second order, for bounded and
smooth-secular correction classes alike.  No causal/retarded conclusion is
made.

The compensating oscillator sign is structural as well.  For every
`lambda=ell(ell+1)>=6`, in both parities,

```text
r_plus  = 1 + (3/2)sqrt(2 lambda) > 0,
r_minus = 1 - (3/2)sqrt(2 lambda) < 0.
```

Because `mu_H=-(L/4) omega^2 h_+`, the Einstein `q_minus` primary has
positive `mu_H`, opposite to the extra `p` primary and Einstein `q_plus`
primary.  This explains why mixed Einstein–extra balance is possible without
turning the pure-extra theorem into a universal target-space sign claim.

## Exceptional and global strata

The global blocks do not provide extra-Weyl counterexamples:

- the complete homogeneous solution cofiber is zero;
- the complete twist solution cofiber is zero.

They are Einstein-image strata with different Hamiltonian geometry.  In
homogeneous coordinates `(a,b,c,d,Q_e,W_x)`,

```text
mu_H = -a^2 - b^2 + b d - Q_e^2,
inertia(a,b,d,Q_e) = (positive 1, negative 3, zero 0),
kernel = span(c,W_x).
```

For the axial twist `(A,B)`,

```text
mu_H = 2 |B|^2,
inertia(A,B) = (positive 3, negative 0, zero 3).
```

The nonzero constant-position locus `B=0` is an exact mapping-torus family.
It is therefore an exact counterexample to *universal target definiteness*,
while remaining fully consistent with definiteness on the additional-Weyl
solution cofiber.

## Charge fibres

The theorem fixes the magnetic bundle `P_N`.  Uniform magnetic variation is
not a tangent because the Chern class is locally constant.  The electric
tangent is allowed and contributes `-Q_e^2`, the same sign as the pure-extra
sector.  It cannot rescue a pure-extra obstruction.  It can participate in a
mixed balance with the positive `q_minus` or twist-velocity contribution,
but only when present already at first order; a second-order charge shift
cannot change an adjoint-cokernel pairing.

An enlarged continuous-flux family is a different phase space.  It may
absorb the scalar constant-lapse component, but no full second-order
extension map is certified there.

## Evidence and boundary

The machine-readable theorem is
`bridge/certificates/einstein_maxwell_weyl_harmonic_taub_sign_classification.json`.
It imports the independent axial and polar all-`ell` current restrictions,
generic and exceptional extra-current theorems, nonzero-momentum exceptional
cofiber, global moment maps, zero homogeneous/twist cofibers, and a
two-absolute-momentum control.

This is a `LOCAL-ALGEBRAIC`/`REDUCED-MODE` theorem on the compact
Plebański–Hacyan background.  It does not classify the full mixed resonance
cone, final residual descent, all-orders integration, causal propagation,
particles, ghosts or quantum norms.

CLOSE-OUT: DONE — the complete stop condition is met
EVIDENCE: bridge/einstein_sector/receipts/EINSTEIN_MAXWELL_WEYL_HARMONIC_TAUB_SIGN_CLASSIFICATION_V1_TIER_RECEIPT.json
