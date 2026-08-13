# Localized affine BT hidden parity and the origin of the second sheet

**Certificate:**
`REVERSE_PHYSICS_BT_LOCALIZED_AFFINE_HIDDEN_PARITY_ORBIT_V1`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.
**Lifecycle:** `CLASSIFIED`.

## Result

Localization at the perfect-square field strength does generate the missing
parity-conjugate sheet from the **same scalar action**, but only as a pair of
on-shell nonvacuum background representations.  It does not generate it on
the public perturbative vacuum.

Write

\[
 F(\phi)=\Box\phi+\lambda(\partial\phi)^2,
 \qquad
 E(\phi)=\Box F-2\lambda\partial_\mu(F\partial^\mu\phi).
\]

On the algebra where \(F\) is invertible and a logarithm branch is chosen,
the public hidden transformation

\[
 h(\phi)=-\phi+\lambda^{-1}\log F
\]

obeys the exact off-shell identity

\[
 \boxed{F(h\phi)-F(\phi)={E(\phi)\over\lambda F(\phi)}.}
\]

Consequently

\[
 h^2\phi-\phi={1\over\lambda}
 \log\!\left(1+{E\over\lambda F^2}\right).
\]

Hidden parity preserves \(F\) and squares to one precisely after imposing the
field equation \(E=0\).  The localization route is therefore an on-shell
quotient architecture, not the missing off-shell projector automorphism.

The smallest homogeneous localized backgrounds are

\[
 \phi_v(x)=v\!\cdot\!x+c,
 \qquad f_0=F(\phi_v)=\lambda v^2\ne0.
\]

They solve \(E=0\), and hidden parity sends

\[
 (v,c)\longmapsto
 \left(-v,-c+\lambda^{-1}\log f_0\right).
\]

Thus the two sheets in the preceding formal repair have a same-action
interpretation: they are the parity orbit of the \(v\) and \(-v\) background
representations.  They are not a new field, particle, spacetime dimension or
independent scalar theory.

But no localized affine background is parity fixed.  Fixedness requires
\(v=-v\), hence \(v=0\), for which \(f_0=0\) and the localized algebra ceases
to exist.  Moreover, the parity intertwiners become singular as \(v\to0\).
There is no strong limit on a fixed dense massless packet core or on the
double-pole Jordan jet.  The affine completion therefore cannot affiliate the
public zero-vacuum characteristic projector or its completed \(q_{10}\)
coefficient.

## Exact localized identity

The Euler--Lagrange equation follows directly from
\(S=-\frac12\int F^2\):

\[
 E=\Box F-2\lambda\partial_\mu(F\partial^\mu\phi)=0.
\]

Use the exponential identity

\[
 F(\psi)=\lambda^{-1}e^{-\lambda\psi}\Box e^{\lambda\psi}
\]

with \(\psi=h\phi\), so

\[
 e^{\lambda\psi}=e^{-\lambda\phi}F.
\]

An exact product expansion gives

\[
 \lambda F(\psi)
 ={1\over F}\left[
 \Box F-2\lambda\partial\phi\!\cdot\!\partial F
 +(\lambda^2(\partial\phi)^2-\lambda\Box\phi)F
 \right].
\]

Subtracting \(\lambda F\) leaves exactly

\[
 \Box F-2\lambda\partial\phi\!\cdot\!\partial F
 -2\lambda F\Box\phi=E.
\]

This proves the boxed identity without an expansion in \(\lambda\) or field
degree.  It also identifies the precise cost of the classical statement that
hidden parity is an involution: both localization and the equation-of-motion
quotient are essential.

## The affine parity orbit

For \(\phi_v=v\cdot x+c\),

\[
 \Box\phi_v=0,
 \qquad (\partial\phi_v)^2=v^2,
 \qquad F=\lambda v^2=f_0.
\]

Since \(F\) and \(v\) are constant, \(E(\phi_v)=0\).  A real logarithm chart
requires \(f_0>0\); algebraically it is enough that \(f_0\) be invertible with
a declared log branch.

Translations change \(v\cdot x\) by a constant and are therefore compensated
by the exact global shift symmetry.  The background is homogeneous in this
qualified sense, but a nonzero \(v\) breaks Lorentz symmetry to its stabilizer.
It is not the Lorentz-invariant \(\phi=0\) perturbative vacuum.

The parity image is

\[
 h(\phi_v)=-v\cdot x-c+\lambda^{-1}\log f_0.
\]

Applying \(h\) again returns \(\phi_v\).  Thus the localized source theory
contains a canonical orbit of two affine sectors.  A parity representation
must either exchange those sectors or omit the symmetry.

## Linearized involution

Put \(\phi=\phi_v+\eta\), and define the commuting constant-coefficient
operators

\[
 D=\Box,
 \qquad V=v\cdot\partial,
 \qquad L_v=D+2\lambda V,
 \qquad L_{-v}=D-2\lambda V,
 \qquad a=\lambda f_0=\lambda^2v^2.
\]

Then

\[
 \delta F=L_v\eta
\]

and the linearized equation is

\[
 E_v^{(1)}\eta
 =\left(L_{-v}L_v-2aD\right)\eta
 =\left[D^2-4\lambda^2V^2-2\lambda^2v^2D\right]\eta.
\]

The tangent of hidden parity from the \(v\) chart to the \(-v\) chart is

\[
 T_v=-1+{L_v\over a}.
\]

Exact operator multiplication yields

\[
 \boxed{
 T_{-v}T_v-1={E_v^{(1)}\over a^2},
 \qquad
 T_vT_{-v}-1={E_{-v}^{(1)}\over a^2}.}
\]

Hence on

\[
 \ker E_v^{(1)}\oplus\ker E_{-v}^{(1)}
\]

the off-diagonal operator

\[
 K_{\rm aff}(\eta_v,\eta_{-v})
 =(T_{-v}\eta_{-v},T_v\eta_v)
\]

satisfies \(K_{\rm aff}^2=1\).  This is the exact linearized source
affiliation of the parity double.  Its qualification—on-shell, two
backgrounds—is load-bearing.

## Why the perturbative-vacuum limit fails

Scale \(v=\epsilon u\), with \(u^2\ne0\).  On a Fourier mode \(k\),

\[
 T_\epsilon(k)
 =-1+{-k^2+2i\lambda\epsilon(u\cdot k)
       \over\lambda^2\epsilon^2u^2}.
\]

For generic off-shell modes,

\[
 \epsilon^2T_\epsilon(k)
 \longrightarrow-{k^2\over\lambda^2u^2}.
\]

For massless modes with \(u\cdot k\ne0\),

\[
 \epsilon T_\epsilon(k)
 \longrightarrow {2i(u\cdot k)\over\lambda u^2}.
\]

Thus the map diverges as \(\epsilon^{-2}\) off shell and
\(\epsilon^{-1}\) on an open set of the massless shell.  The only finite
massless slice has \(k^2=u\cdot k=0\), where \(T_\epsilon=-1\).  That slice
has measure zero in the massless momentum measure; it supports no nonzero
\(L^2\) packet subspace and cannot be advertised as a dense domain.

The coincident-pole Jordan direction is worse, not better.  On the exact
two-jet fixture

\[
 D=N=\begin{pmatrix}0&1\\0&0\end{pmatrix},
 \qquad V=0,
 \qquad \lambda=u^2=1,
\]

one gets

\[
 T_\epsilon=-I+{N\over\epsilon^2},
 \qquad
 \lVert T_\epsilon\rVert_F^2=2+\epsilon^{-4}.
\]

The nilpotent direction that distinguishes the \(1/k^4\) carrier therefore
has no finite affine-to-vacuum limit.

## Meaning for Eq. (19) and the physical route

This result refines the earlier alternatives:

1. On the public zero-vacuum off-shell chart, a regular one-sheet hidden
   parity is obstructed.
2. On an \(F\)-localized affine chart, hidden parity exists exactly on shell,
   but it exchanges two background representations.
3. The direct sum of these representations supplies a same-action meaning for
   the two-sheet parity completion.
4. The completion has no strong \(v\to0\) limit on the public particle/Jordan
   carrier, so it does not prove the public Eq. (19).

The completed selected probability

\[
 \lambda^8q_8+\lambda^{10}q_{10}
\]

remains valid on its declared zero-background finite-time packet ideal.  It
cannot be transported to the affine sectors without re-expanding the action,
states and detector around \(\phi_v\).  Conversely, the affine parity theorem
cannot be pulled back through a singular limit and called a proof of that
selected zero-background experiment.

## Boundary and next gate

Established:

- the exact off-shell identity \(F(h\phi)-F=E/(\lambda F)\);
- the exact second-iterate defect;
- existence of localized affine solutions with \(F=\lambda v^2\ne0\);
- the two-element \(v\leftrightarrow-v\) background orbit;
- absence of a nonzero parity-fixed localized affine chart;
- the exact linearized parity intertwiners;
- involutivity modulo the linearized equation of motion;
- a same-source-action interpretation of the doubled sheet;
- \(\epsilon^{-1}\) divergence on generic massless modes;
- \(\epsilon^{-2}\) divergence on the Jordan jet; and
- non-affiliation with the public perturbative vacuum and \(q_{10}\).

Not established:

- an off-shell localized projector theorem;
- a one-background hidden-parity representation;
- classification of nonaffine localized backgrounds;
- a no-go for arbitrary singular, nonlocal, unbounded or non-Fock maps;
- a time-independent affine asymptotic projector or continuum trace;
- transfer of the zero-background \(q_{10}\) calculation;
- full public Eq. (19), all-channel probability or an all-time S operator;
- metric BV--BRST, gravity, QME or `LORENTZIAN-CAUSAL` physics; or
- literature priority.

The next Eq. (19) question is whether a nonaffine on-shell background with
invertible \(F\) can be asymptotically stationary and parity fixed up to the
exact shift/Poincare symmetries.  A no-go would make background-orbit doubling
necessary throughout the localized theory.  In parallel, the direct physical
route should seek an all-time limit of the already positive zero-background
packet process rather than use the singular affine limit.

## Verification receipt

All scientific Python and TeX commands ran sequentially under
`ulimit -v 500000`; the Tier-3 rail additionally used
`PATH=/usr/local/bin:/usr/bin:/bin`.

| Tier | Command or rail | Result | Elapsed | Peak RSS |
|---|---|---:|---:|---:|
| 0 | Python compile and JSON parse | PASS | 2.60 s aggregate with scoped rails | 66,556 KiB aggregate maximum |
| 0/1 | exact producer `--write --check` | PASS, 38/38 | 0.47 s | 66,252 KiB |
| 1 | dependency-free sparse-polynomial independent verifier | PASS, 41/41 | 0.08 s | 23,940 KiB |
| 1 | focused adversarial suite | PASS, 19 tests including 17 mutations | 1.67 s | 65,988 KiB |
| 2 | three predecessor verifiers plus the new verifier | PASS, 32/32, 38/38, 54/54 and 41/41 | 0.30 s total | 24,936 KiB |
| 2 | combined affected tests | PASS, 110 tests | 4.77 s | 69,644 KiB |
| 0 | Paper V, two `pdflatex` passes | PASS | 0.52 s, 0.53 s | 51,048 KiB maximum |
| 0 | Paper VI, final two `pdflatex` passes | PASS | 0.59 s, 0.59 s | 51,056 KiB maximum |
| 2 | Science Forge planning import/fold | PASS, 1,587 nodes; 0 invalid items; 0 malformed events | 7.58 s | 294,600 KiB |
| 3 | final-byte full `unittest discover` | **FAIL-CLOSED**, 3,478 tests: 31 failures, 9 skips | 737.903 s test time; 1,875.76 s outer rail under shared-machine scheduling | 391,276 KiB |

The Tier-3 total increased by exactly the nineteen new tests relative to the
preceding 3,459-test run.  The failure and skip counts are unchanged.  All
failures remain in the same older certificate/hash-drift families and the two
existing `chain_imports` assertions; the new producer, verifier and test
family do not occur in the failure list.  The repository-wide rail is not
called a pass and promotes no freeze.  An unrelated foundations workstream
changed its own files concurrently during the final run; none overlaps or is
included in this package.  The unchanged failure profile is recorded as a
shared-tree diagnostic, not as a static-snapshot release certification.

The advisory Science Forge shadow rail completed in 1.97 s at 335,196 KiB.
It inventories 1,633 certificates and 1,414 verifier files, while retaining
the known Forge 0.0.2/stdlib mismatch, bridge-audit E9118 and baseline corpus
drift.  Its advisory exit zero is not certified success.
The mandatory `s-f work check` wrapper was also invoked and failed visibly
at its known `sfc` build gate; it is not recorded as a pass.  The
method-distinct planning import above nevertheless folded the same work-item
corpus with zero invalid items or malformed events.

Paper V has 83 pages, 767,456 bytes and SHA-256
`480f063e4666c0b2ac32ad5b8fdc4930bb388f20e55ac688c82d7a5ae1fc1035`.
Paper VI has 71 pages, 730,670 bytes and SHA-256
`5f210c2d2796d21aadf1b66a777ac886b71b090272649e70895cd71a7ad3f1fc`.
There are no undefined references; all six Paper-V and two Paper-VI overfull
boxes predate and lie outside the new passages.  The certificate SHA-256 is
`2ee7fd4c281a42ccfb783ebf04d06184d7e5d7126edac4adab87eedc0966500f`.

CLOSE-OUT: DONE -- localization derives the two parity sheets as affine
background representations of the same scalar action, but the singular
zero-background limit prevents this completion from proving the public Eq.
(19) or transporting the selected \(q_{10}\).

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_LOCALIZED_AFFINE_HIDDEN_PARITY_ORBIT_V1.json`
