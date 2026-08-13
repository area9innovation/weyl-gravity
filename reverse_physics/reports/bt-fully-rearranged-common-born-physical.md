# Fully rearranged common-Born BT physical probability

**Certificate:** `REVERSE_PHYSICS_BT_FULLY_REARRANGED_COMMON_BORN_PHYSICAL_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

**Lifecycle:** `COEFFICIENT_COMPUTED`

## Result

The certified fully rearranged finite-time detector has a complete leading BT
transition coefficient whose public generalized-Krein and positive-Hilbert
probability operators are identical.

Write the perturbative expansion with the coupling outside the coefficient,

\[
 P_Y(U_T-I)P_X=\lambda^4L_{4,YX}+O(\lambda^5).
\]

The disconnected-support theorem exhausts all 202 disconnected partitions of
the six external legs and proves that each vanishes between these packet
supports.  Therefore

\[
 L_{4,YX}=T_{4,YX}=P_YT_4P_X,
\]

where \(T_4\) is the coherent unit-weight ten-channel connected coefficient.
This is why the theorem concerns the complete leading transition, not merely
the connected graph column.

## Why restriction preserves ghost parity

The incoming and outgoing projectors act on momentum support.  Three-particle
ghost parity acts on the eight-dimensional species carrier:

\[
 P_X=|X\rangle\langle X|\otimes I_8,\qquad
 P_Y=|Y\rangle\langle Y|\otimes I_8,\qquad
 \kappa_{\rm tot}=I_{XY}\otimes\kappa_3.
\]

Thus

\[
 [P_X,\kappa_{\rm tot}]=[P_Y,\kappa_{\rm tot}]=0.
\]

The coherent Choi coefficient was already proved fixed,
\(\kappa_3T_4\kappa_3=T_4\).  Consequently

\[
 \kappa_{\rm tot}T_{4,YX}\kappa_{\rm tot}
 =P_Y(\kappa_3T_4\kappa_3)P_X=T_{4,YX}.
\]

The certificate checks this with exact rational arithmetic on
\(\operatorname{span}\{|X\rangle,|Y\rangle\}\otimes\mathbb C^8\).  Its
\(16\)-by-\(16\) projectors are orthogonal and idempotent, total parity squares
to one, both commutators vanish, and the restricted transition is fixed.  The
generic ten-coefficient trace fixture gives

\[
 \operatorname{Tr}(T_{4,YX}^{\sharp}T_{4,YX})
 =\operatorname{Tr}(T_{4,YX}^{*}T_{4,YX})=770,
\]

with exact defect zero.

## Complete-leading probability

Fixedness makes the two adjoints equal, so the order-\(\lambda^8\) effect
coefficient obeys

\[
 \boxed{
 E_8^{\rm public}=L_{4,YX}^{\sharp}L_{4,YX}
 =L_{4,YX}^{*}L_{4,YX}=E_8^{\rm Hilbert}.
 }
\]

For the declared dressed positive source,

\[
 q_{\rm click}=16\lambda^8
 \left\|\sum_{B=1}^{9}P_YK_{B,T}P_XF\right\|^2+O(\lambda^9),
\]

and its common leading coefficient satisfies

\[
 q_{\rm click}^{(8)}\le {81\lambda^8T^2\over200\pi^6}.
\]

Every coherent cross term remains.  Input-output orthogonality removes the
identity and forward/survival block from this first nonzero coefficient.

## Meaning

This is the strongest current answer to the physical route.  It supplies a
nonempty class of concrete finite-time packet experiments for which:

- every connected and disconnected contribution at the leading amplitude
  order is accounted for;
- the actual coherent ten-channel BT coefficient is used;
- the public Krein and positive Hilbert Born rules give the same operator;
- the resulting leading probability coefficient is nonnegative and bounded.

It is a complete-leading public auxiliary physical probability, not a general
scattering theory and not general Eq. (19).

## Boundary

The result does not establish spectator-overlap detectors, the sign or size
of the \(O(\lambda^9)\) remainder, a derived all-order survival block, an exact
finite-coupling probability, an all-time operator, loops or KLN completion, a
packet-independent cross section, general Eq. (19), gravity or metric
BV--BRST transfer, anything `LORENTZIAN-CAUSAL`, or literature priority.

## Verification

All scientific Python, TeX and repository-test processes ran sequentially
under the 500 MB virtual-memory ceiling.

- Tier 0 passes.  The three Python files compile, all changed JSON parses, the
  strict Draft-2020-12 schema and certificate validate, an injected additional
  property is rejected, and scoped `git diff --check` is clean.  Schema
  validation took `0.09 s` at `21800 KiB` peak RSS.
- The exact producer passes `25/25` checks in `0.08 s` at `16616 KiB`.  The
  independent verifier reconstructs the full rational \(16\)-by-\(16\) tensor
  witness, both commutators, restriction, adjoints, effects and predecessor
  support ledger without importing the producer; it passes `52/52` checks in
  `0.07 s` at `15624 KiB`.  All `40` adversarial mutation tests pass in
  `2.133 s` (`2.17 s` enclosing wall time) at `18540 KiB`.
- The affected Tier-2 chain passes for the fully rearranged physical packet,
  complete connected common-Born packet and global connected finite-time
  column.  Its six producer/verifier commands took `0.46 s` at `63912 KiB`.
- Papers V and VI compile twice with
  `pdflatex -interaction=nonstopmode -halt-on-error`.  Their PDFs have `79`
  pages and `738286` bytes, and `68` pages and `696510` bytes, with SHA-256
  `848a640f389ae6df0cb13acea4dea1ba4d3dfb4de006febb3afe24c0dee345df`
  and
  `c7237df6d8ae05e9ab7c3599996b6afeab21bdea6994da1831fb4b5076bb902d`.
  The two-pass commands took `1.12 s` at `51016 KiB` and `1.08 s` at
  `50772 KiB`.  There are no undefined references or citations and no new
  overfull box; Paper V retains six known boxes and Paper VI two.
- The comparable Tier-3 run, with system tools ahead of the semantic-search
  shims, is fail-closed rather than a repository-wide pass: `3137` tests ran
  in `781.959 s` (`783.14 s` enclosing wall time) at `391100 KiB`, with `31`
  failures and `9` skips.  This is the established failure/skip census plus
  all `40` passing tests introduced here.  Older certificate drift remains,
  and the `chain_imports` outside-reference list has independently grown to
  thirteen paths.  No failed or skipped rail is counted as a pass.  A first
  Tier-3 attempt through the semantic-search `grep` shim ran `834.121 s` and
  reported `32` failures because its repository scan failed; an isolated
  system-`grep` rerun restored the established two `chain_imports` failures,
  so that contaminated attempt is not used as theorem evidence.
- The append-only Science Forge fold accepts `1567` nodes with zero invalid
  items and zero malformed events in `1.57 s` at `14040 KiB`.  The cached
  coordinator is used because rebuilding the moving substrate is currently
  blocked by its known toolchain mismatch.
- The advisory shadow wrapper exits zero by design in `1.17 s` at `33012 KiB`,
  while its bridge audit remains fail-closed with the Forge binary/standard-
  library mismatch and `E9118`.  Its census reports `1623` certificates and
  `1404` verifier files against the older baseline; this is not a theorem
  pass.

Tier 3 was required because Papers V and VI acquire a
`COEFFICIENT_COMPUTED` physical theorem.  No classical freeze, QME state,
shared core algebra, residual transfer or `LORENTZIAN-CAUSAL` state changed.
The final certificate SHA-256 before staging is
`7ade5768a01cc42cf0ef1edfea9c8cf4c52cc716956a7abfc280c1def5611d47`.

## Next gate

Compute the first higher transition coefficient \(T_5\) on the same detector
and the interference \(2\operatorname{Re}(T_4^*T_5)\).  Test total-\(\kappa\)
fixedness before claiming finite-coupling positivity.  The separate all-channel
extension composes lower connected blocks on spectator-overlap supports;
general Eq. (19) remains a nonregular projector problem.
