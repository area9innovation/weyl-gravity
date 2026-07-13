# Conformal cubic channel enumeration

Status: exact representation-theoretic certificate implemented by
`symbolic/verify_conformal_cubic_channels.py`. This is a research ledger,
not a manuscript claim or programme-overview update.

## Inputs and scope

The enumerator uses the normalizable one-particle oscillator towers isolated
in C0b and C1a. For every half-integer `J>=1`, they are

```text
E_J: Delta=2J,   (J+1,J-1) + parity, sign +,
A_J: Delta=2J+1, (J+1/2,J-1/2) + parity, sign -,
L_J: Delta=2J+2, (J+1,J-1) + parity, sign -.
```

Here `A` is the complete helicity-one descendant tower in the linearized
oscillator construction, not an extra independently signable sector; `E`
and `L` are the lower- and upper-TT cylinder towers. Auxiliary, gauge, and
Stueckelberg representatives are absent because this is a representation-
theoretic enumeration of those oscillator towers. Promotion to the full
compact-cylinder BRST cohomology remains conditional on the global
conformal-charge/Taub audit; contractible representatives also remain
necessary in off-shell exchange graphs.

The script classifies fundamental one-to-two cubic transitions. Adding a
spectator in a larger Fock shell copies one of these reduced transitions and
does not create a new cubic family.

## Exact all-energy classification

Energy conservation fixes

```text
J_out = J_1 + J_2
        + (offset(B_1)+offset(B_2)-offset(B_out))/2,
```

where the offsets of `(E,A,L)` are `(0,1,2)`. For either SU(2) factor the
target spin can be written as

```text
j_out = j_1+j_2-r.
```

Tensor-product membership is exactly the statement that `r` is a
nonnegative integer and

```text
r <= 2 min(j_1,j_2).
```

The value of `r` depends only on the three branch and chirality labels, not
on `J_1,J_2`. Thus the two SU(2) rules reduce to a finite affine-depth
calculation plus exact lower bounds on the input spins. This proves, without
an energy cutoff, that the only representation-allowed orientations are

```text
EE -> A,
EE -> L,
EA -> A,
EA -> L,
AA -> L.
```

The first two contain at most one non-Einstein direction and vanish by the
exact Einstein-subsector rule `A(E,E,X)=0`. The complete post-selection list
is therefore

| process | field family | Fock signs | parity-reduced chiral channels | exact range |
| --- | --- | --- | --- | --- |
| `E+A -> A` | `EAA` | `- -> -` | `(-,+,-) ~ (+,-,+)` | `J_E,J_A>=1` |
| `E+A -> L` | `EAL` | `- -> -` | `(-,-,-) ~ (+,+,+)` | `J_E,J_A>=1` |
| `E+A -> L` | `EAL` | `- -> -` | `(-,+,-) ~ (+,-,+)` | `J_E>=3/2`, `J_A>=1` |
| `A+A -> L` | `AAL` | `+ -> -` | `(-,-,-) ~ (+,+,+)` | `J_1,J_2>=1` |

Each fixed-chirality `SU(2)_L x SU(2)_R` tensor product has multiplicity
one. Parity pairs the displayed chirality assignment with its global sign
reversal. The second EAL line is consequently a genuine second reduced
SO(4)-plus-parity channel, not a Clebsch--Gordan multiplicity inside one
chiral product. Full `SO(4,2)` descent could still relate the two EAL
coefficients; compact energy, `SO(4)`, parity, and Bose symmetry do not.

For identical A inputs, the allowed same-chirality `A_J A_J -> L_(2J)`
output lies in the symmetric square for every `J>=1`. Bose symmetry does
not remove the AAL family.

## What this changes

AAL and the single computed EAA coefficient do **not** exhaust the cubic
theorem obligations.

The first EAL channel occurs at energy five:

```text
E_2 A_3 -> L_5.
```

At energy six a second independent EAL tensor structure appears:

```text
E_3 A_3 -> L_6,
```

with both the same- and mixed-chirality parity orbits. Therefore the
conjecture

```text
P_Delta V_3 P_Delta = 0
```

cannot be promoted to a theorem using only the current AAL boundary
identity and the `E_2 A_3 <-> A_5` certificate. At minimum it still needs:

1. an all-spin EAA identity;
2. both all-spin EAL reduced identities, including the high-spin mixed
   chirality structure;
3. the existing all-spin AAL density derivation;
4. BRST-representative and same-shell adjoint closure.

Subsequent exact curvature runs have now closed one seed in each EAL orbit,
`E_2 A_3 <-> L_5` and mixed-chirality `E_3 A_3 <-> L_6`; both vanish by
measured Jacobi boundary identities.  Those two seed certificates do not
replace item 2: their all-spin radial recurrence remains open.

The sign result remains useful. EAA and EAL connect equal negative Fock
sectors. AAL is the unique opposite-sign family. Thus the finite AAL
hierarchy is sufficient for the opposite-sign part of cubic protection once
its all-spin radial identity and BRST descent are proved, but not for the
stronger claim that the entire resonant cubic Hamiltonian vanishes.

## Finite regression versus theorem

The default finite check enumerates every parity-completed mode with output
energy `Delta<=12`. It finds

```text
410 chiral reduced channels / 205 parity orbits before Einstein selection,
232 chiral reduced channels / 116 parity orbits after selection.

EAA: 36 spin processes, 36 parity-reduced channels,
EAL: 36 spin processes, 64 parity-reduced channels,
AAL: 16 spin processes, 16 parity-reduced channels.
```

The 28 extra EAL channels are exactly the processes with `J_E>=3/2`; each
has reduced multiplicity two. These numbers are cutoff-dependent regression
data. The five pre-selection orientations, the three post-selection
families, and the EAL threshold/multiplicity statement follow instead from
the all-energy affine proof.

## Limitations

This certificate establishes kinematic representation content, inherited
oscillator-form signs, and multiplicities. It does not calculate a Weyl
vertex, prove that a representation-allowed coefficient is nonzero, certify
that an individual oscillator state survives the global BRST/Taub
constraints, or include contractible intermediate fields. Parity is used
only to organize conjugate chiral irreps; any convention-dependent intrinsic
parity phase belongs in the subsequent vertex calculation.
