# Public-BT polynomial positive quadrupole detector

**Certificate:**
`REVERSE_PHYSICS_BT_AUXILIARY_POLYNOMIAL_QUADRUPOLE_POSITIVE_DETECTOR_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

**Lifecycle:** `COEFFICIENT_COMPUTED`

## Result

The compact quadrupole response has a regular positive-real-structure
realization directly in the public Bateman--Turok auxiliary fields.  It does
not use the obstructed logarithmic hidden-parity image of the scalar density
and does not require the changed two-vacuum theory.

Let (F_2) be the already certified real covariant STF pair symbol and set

\[
 D_X(x)=:X(x_1)F_2X(x_2):\big|_{x_1=x_2=x}.
\]

The responding public-field density is

\[
 \boxed{D_{\rm aux}=D_\Omega+D_\Upsilon.}
\]

It is polynomial and regular at the public perturbative vacuum.  Ghost
parity exchanges its two terms.  Since the public Krein adjoint makes both
fields real while the positive Hilbert adjoint obeys
(Omega^*=\Upsilon), one has on the common selected packet core

\[
 D_{\rm aux}^{\sharp}=D_{\rm aux},\qquad
 D_{\rm aux}^{*}=D_{\rm aux},\qquad
 \kappa D_{\rm aux}\kappa=D_{\rm aux}.
\]

Thus the density passes the real-structure test that the scalar quadrupole
failed.  Its selected compact-spacetime response satisfies

\[
 \boxed{
 {Q_{8,{\rm aux},\rm compact}\over\bar q_4}
 >{1\over18874368000}.}
\]

This is a selected physical coefficient in the public auxiliary theory.  It
is not the standard perfect-square scalar projector or general Eq. (19).

## Exact quadratic classification

Write (Phi=(\Omega,\Upsilon)^T).  A real quadratic density with symmetric
species tensor (C) is ghost even precisely when

\[
 \kappa C\kappa=C,
 \qquad
 \kappa=\begin{pmatrix}0&1\\1&0\end{pmatrix}.
\]

The complete solution is

\[
 C(a,b)=\begin{pmatrix}a&b\\b&a\end{pmatrix}.
\]

There are two qualitatively different directions.  The cross tensor

\[
 C_{\rm n}=\begin{pmatrix}0&1\\1&0\end{pmatrix}
\]

is invariant under the continuous (SO^+(1,1)) boost.  Its pair-annihilation
part removes one quantum of each species.  It therefore has exactly zero
matrix element on both pure active-pair branches of

\[
 u_0={|\Upsilon\Upsilon\Upsilon\rangle
          +|\Omega\Omega\Omega\rangle\over\sqrt2}.
\]

The responding tensor is (C_{\rm r}=I_2).  Its two terms have boost charges
(+2) and (-2).  Consequently a ghost-even quadratic can be both boost
neutral and responsive to this source only if extra charge-carrying apparatus
data are supplied.  This is an exact detector-selection rule, not a failure
of the response.

## Charge-balanced pointer

Introduce a pointer with a neutral ground state (g) and two click states
(e_-), (e_+) of charges (-2,+2), exchanged by pointer ghost parity.  The
interaction is

\[
 V=h\left(
 |e_-\rangle\langle g|\otimes D_\Omega
 +|e_+\rangle\langle g|\otimes D_\Upsilon
 \right)+\text{Krein adjoint}.
\]

Both branches have total charge zero.  Order the three-particle species words
by binary strings with (0=\Upsilon), (1=\Omega), and order the click
outputs as

\[
 (e_-\Upsilon,e_-\Omega,e_+\Upsilon,e_+\Omega).
\]

After factoring the common symmetric Bose pair coefficient, the selected
pair map (M:\mathbb C^8\to\mathbb C^4) has only

\[
 M_{0,0}=1,\qquad M_{3,7}=1.
\]

Let (kappa_3) complement the three bits and let (kappa_{m out})
simultaneously exchange the pointer and spectator species.  Exact matrix
calculation gives

\[
 M\kappa_3=\kappa_{\rm out}M,
 \qquad Q_{\rm out}M=MQ_{\rm in},
\]

and

\[
 M^\sharp M=|000\rangle\langle000|+|111\rangle\langle111|.
\]

Therefore

\[
 M u_0=v_0
 ={ |e_-\Upsilon\rangle+|e_+\Omega\rangle\over\sqrt2},
 \qquad
 \langle u_0,u_0\rangle_K
 =\langle v_0,v_0\rangle_K=1.
\]

Both states are ghost even and positive.  On the truncated input-output
carrier the off-diagonal interaction

\[
 \begin{pmatrix}0&M^\sharp\\M&0\end{pmatrix}
\]

is simultaneously Krein-selfadjoint, Hilbert-selfadjoint and ghost even.  The
pointer therefore restores the continuous charge without losing the positive
selected response.

## Exact dark and bright orders

The (F_2) symbol has zero angular mean on every timelike two-body fibre.
The order-(lambda^2) active amplitude is angle independent, separately on
the two pure species branches.  Hence

\[
 A_{2,\rm aux}(h_R)=0
\]

for every compact cutoff (h_R), including its Paley--Wiener Fourier tails.

At order (lambda^4), the pure three-particle channel is (S=7), together
with its complement.  The public six-point coefficient omits its own
intermediate channel.  On the certified tagged angle family, the two
(t)-exchange and two (u)-exchange terms therefore carry coefficient (2)
rather than the coefficient (10) in the complete positive-jet contraction.
All other terms are independent of the active angle and disappear against
(P_2).  Thus

\[
 J_{\rm tree,pure}={1\over5}J_{\rm tree}>{1\over500}>0.
\]

For the active loop, two quartic vertices and two cross internal lines leave
exactly two external (Omega) and two external (Upsilon) legs.  The same
positive complement-even pure-pair eigenvector is retained.  The independently
certified alternating-series result gives

\[
 J_{\rm loop}>{252416\over73828125}>{1\over400}.
\]

The tree and loop moments therefore have the same positive sign on the public
auxiliary source.  Dropping the positive tree again gives

\[
 J_{R,\rm aux}>{1\over19200}.
\]

The species/pointer map is an isometry, so it introduces no probability
factor.  The earlier Cauchy and compact-cutoff arguments then give

\[
 {Q_{8,{\rm aux},\rm local}\over\bar q_4}
 >{1\over4718592000},
 \qquad
 {Q_{8,{\rm aux},\rm compact}\over\bar q_4}
 >{1\over18874368000}.
\]

At first microscopic detector order,

\[
 p_{\rm click}
 =g_{\rm det}^2\lambda^8Q_{8,{\rm aux},\rm compact}
 +O(g_{\rm det}^2\lambda^{10})+O(g_{\rm det}^4).
\]

## Meaning and boundary

This closes the regular positive-real-structure problem for a selected public
auxiliary quadrupole experiment.  The successful observable is not the scalar
quadrupole transported through hidden parity.  It is a different polynomial
public-field density whose selected matrix element carries the same dark
response.  The charged pointer is part of the apparatus and is necessary if
the total coupling is to retain continuous (SO^+(1,1)) charge.

The result does not establish essential self-adjointness or bounded-region
Haag--Kastler affiliation of the full unbounded density, an exact microscopic
detector probability beyond first order in (g_{\rm det}), control of the
(lambda^{10}) remainder, selection of the source or pointer by the closed
BT Hamiltonian, the standard shift-invariant scalar projector, general
Eq. (19), an all-time scattering operator, gravity/BV--BRST transfer, or
anything `LORENTZIAN-CAUSAL`.

The next direct-physics gate is a self-adjoint closure or affiliated bounded
functional calculus for the charge-balanced compactly smeared coupling,
followed by the (g_{\rm det}^4) and (lambda^{10}) bounds.  Eq. (19)
remains a separate singular, localized, doubled or non-Fock projector problem.

## Verification commands

```text
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_auxiliary_polynomial_quadrupole_positive_detector.py --write --check
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_auxiliary_polynomial_quadrupole_positive_detector.py
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_auxiliary_polynomial_quadrupole_positive_detector
```

## Verification receipt

Every Python and TeX process below ran sequentially under
`ulimit -v 500000`; no out-of-memory event occurred.

- Tier 0 passed: the three changed Python files compile, all four new JSON
  files parse, the certificate validates against its strict schema, and the
  scoped `git diff --check` is clean.
- The exact producer passes 50/50 checks in 0.04 s at 17152 KiB peak RSS.
  The method-distinct verifier reconstructs the predecessor tree weights and
  passes 69/69 checks.  All 38 focused mutation tests pass in 0.38 s at
  18960 KiB peak RSS.
- The affected Tier-2 producer/verifier chain passes for the local quadrupole,
  compact-spacetime q8, scalar compact packet, continuous-angle q6,
  six-point full-phase-space and complete tagged-q6 certificates.  Producer
  check counts are respectively 29, 27, 26, 46, 16 and 25; independent
  verifier check counts are 41, 28, 20, 61, 14 and 25.  The slowest affected
  rail took 0.96 s and the largest peak RSS was 75760 KiB.
- Papers V and VI compile with
  `pdflatex -interaction=nonstopmode -halt-on-error`.  Their final PDFs have
  76 pages and 727536 bytes, and 66 pages and 687977 bytes, with SHA-256
  `421bd59083657718e7164b89847eff7adbf703d8383f9ea427eb6eecfc7e22f1`
  and
  `320b88be65a5f7b168739033f73052419f51a5e05edf08e25e5a00e5e2cfe8c7`.
  The final passes took 0.52 s at 50636 KiB and 0.52 s at 50864 KiB.
  There are no undefined references or citations and no new overfull box.
- Tier 3 is fail-closed, not a repository-wide pass: 2951 tests ran in
  704.147 s (705.21 s enclosing wall time) at 391332 KiB peak RSS, with 31
  failures and 9 skips.  All 38 tests introduced here passed.  The sorted
  failure-name list has SHA-256
  `83a116976bf2fb697b95070337c41d79df0ffc80697a508f29d1240ff0f1bbc0`,
  exactly the established 31-failure baseline set.  The older certificate
  drift and `chain_imports` findings therefore still block a repository
  freeze, but this package adds no Tier-3 failure.
- The append-only Science Forge planning fold accepted 1559 nodes with zero
  invalid work items and zero malformed events in 5.86 s at 225996 KiB peak
  RSS.  It ran without the virtual-address cap because the Go runtime reserves
  a larger virtual arena before execution.
- The advisory Science Forge shadow wrapper exited zero by design in 1.95 s
  at 345264 KiB peak RSS, but its internal bridge audit remains fail-closed:
  the known Forge binary/standard-library mismatch reports `E9118`, and the
  census reports 1619 certificates and 1397 verifier files against the older
  baseline.  These advisory findings establish no theorem pass.

Tier 3 was required because Papers V and VI acquire a new
`COEFFICIENT_COMPUTED` theorem.  No classical snapshot, quantum master
equation state, shared core operator or `LORENTZIAN-CAUSAL` claim changed, so
unrelated classical and quantum freeze chains were not rebuilt separately.
No skipped or failed rail is counted as a pass.

CLOSE-OUT: DONE — a regular polynomial public-field quadrupole with a
charge-balanced pointer is ghost-even, positive on the selected source and
has a strictly positive compact order-eight response; Eq. (19), full local
affiliation and all-order physics remain open.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_AUXILIARY_POLYNOMIAL_QUADRUPOLE_POSITIVE_DETECTOR_V1.json`
