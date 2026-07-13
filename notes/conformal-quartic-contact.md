# Conformal energy-six quartic contact rail

## Scope

`symbolic/verify_conformal_quartic_contact.py` is an exact four-wave
**contact-only** calculation.  It evaluates the multilinear coefficient of

\[
\sqrt{-g}\left(R_{\mu\nu}R^{\mu\nu}-\frac13R^2\right)
\]

on `R x S3`.  It does not yet contain cubic exchanges, the gauge-bordered
internal inverse, constraint/auxiliary exchanges, reducible-state
subtractions, or the rest of the 2062-dimensional energy-six shell.
Consequently none of its entries is an effective Hamiltonian or an
obstruction coordinate.

The new script is import-safe.  It reuses only definitions from the verified
C1b two-jet kernel, extends the subset algebra to four waves, and includes the
complete fourth-order determinant terms.  The cubic script's top-level
calculation is never executed during import.

## Common `(2,2)` representatives

The exact Clebsch--Gordan construction gives one normalized fixed-parity
highest-weight representative in each reduced channel:

```text
AA = A3+ A3-

EA = parity projection of
     [sqrt(2/3) E2+(mL=2) A4-(mL=0)
      -sqrt(1/3) E2+(mL=1) A4-(mL=1)]

EL = (E2+ L4- + parity * E2- L4+)/sqrt(2).
```

The implementation stores the additional `1/sqrt(2)` parity normalization
inside the EA coefficients.  It verifies exactly that every constituent has
compact energy six and total highest weight `(M_L,M_R)=(2,2)`, and that all
three pair representatives have unit norm.  The cross-chiral bosonic AA copy
occurs only once, so its parity is fixed up to a common intrinsic convention;
the script calls this sign `+` and does not expose a spurious independently
selectable parity-minus AA block.

## First evaluated entry: `AA <-> AA`

The diagonal cross-chiral vector entry is a single curvature evaluation; no
CG or parity sum can cancel it.  Both A3 harmonics are independently verified
to have unit `S3` norm.  The full four-wave inverse metric cancels on all 16
subsets.

Writing `t=tan(beta/2)`, the evaluated pre-measure density is

\[
\mathcal D_{AA,AA}(t)=
\frac{t\left(8t^8-408t^6+407t^4+234t^2+304\right)}
{10800\pi^4(1+t^2)^5}.
\]

The measured integrand is

\[
\mathcal I_{AA,AA}(t)=\frac{2\mathcal D_{AA,AA}(t)}{1+t^2},
\]

and the exact contact coefficient is

\[
\boxed{C^{(4)}_{AA,AA}=\frac{1009}{20250\pi^2}}.
\]

The local density and integral are real, as required for this diagonal
forward/reverse entry.  The nonzero number validates the four-wave engine; it
has no standalone deformation-theory interpretation.

## Branch-changing rail

The cheapest off-diagonal target is `AA <-> EL`.  One chiral seed uses

```text
E2+ L4-  <->  A3+ A3-.
```

Parity covariance supplies the second EL constituent.  In the matching
parity convention the normalized reduced coefficient is `sqrt(2)` times the
raw seed.  The independently evaluated forward chiral density is

\[
\mathcal D_{EL,AA}(t)=
\frac{\sqrt2\,t
\left(89t^8+64t^6+765t^4+337t^2-42\right)}
{34560\pi^4(1+t^2)^5},
\]

with raw and parity-projected contact coefficients

\[
C^{(4),\mathrm{seed}}_{EL,AA}
=\frac{1099\sqrt2}{86400\pi^2},
\qquad
\boxed{C^{(4)}_{EL,AA}=\frac{1099}{43200\pi^2}}.
\]

This is the first nonzero branch-changing contact datum in the common
reduced block.  Forward and reverse seeds were assembled in separate
four-wave curvature runs.  Their complete radial densities agree exactly,
and both give the displayed real coefficient.  Thus the directed entries
obey the physical real-action adjoint relation before any use of the Krein
form.

On the ordered reduced basis `(AA,EL)`, the relevant induced form is

\[
J_{AA,EL}=\operatorname{diag}(+1,-1).
\]

The symmetric real cross contact therefore contributes

\[
C_{\rm contact}=
\begin{pmatrix}0&c\\c&0\end{pmatrix},
\qquad
c=\frac{1099}{43200\pi^2},
\]

and hence

\[
\boxed{
J C_{\rm contact}-C_{\rm contact}^{\dagger}J
=\frac{1099}{21600\pi^2}
\begin{pmatrix}0&1\\-1&0\end{pmatrix}.}
\]

This nonzero matrix is the precise **exchange-cancellation target**.  It is
not an obstruction: cubic exchanges can and generally do contribute to the
same effective-Hamiltonian entry, and only the complete contact-plus-exchange
block may be projected into the deformation cokernel.

The later t-current calculation adds an earlier gate: the selected
energy-six `E/A/L` oscillator block is not yet certified as a physical
compact-cylinder BRST block after global conformal/Taub constraints.  Thus
even the phrase “exchange-cancellation target” refers only to the provisional
oscillator truncation until the linearization-stability audit closes.

## Fail-closed boundary

Running with `--require-effective` exits with an error.  A complete P4
certificate still requires, at minimum:

1. the compact-`S^3` BRST/Taub/linearization-stability state-space audit;
2. all admissible cubic-current exchange orderings after that reduction;
3. the complete gauge/constraint/auxiliary internal harmonic content;
4. the compact-cylinder reduced inverse in every non-null intermediate block;
5. external Ward and BRST-representative checks;
6. reducible external-state subtraction;
7. the independently assembled reverse reduced matrix;
8. completion beyond the selected 75-dimensional magnetic block.
