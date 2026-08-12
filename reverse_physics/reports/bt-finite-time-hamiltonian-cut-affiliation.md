# BT finite-time Hamiltonian cut affiliation

Certificate:
`REVERSE_PHYSICS_BT_FINITE_TIME_HAMILTONIAN_CUT_AFFILIATION_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

The finite-time sinc-squared shell kernel is forced by the BT
interaction-picture generalized Born trace at the cut-probability level.  It
is not merely a regulator chosen to replace the six-point double pole.
Pseudo-unitarity, however, does not by itself derive a positive survival
outcome in a Krein space.

## Hamiltonian origin of the shell kernel

The public Letter assumes a spectral free Hamiltonian, a pseudo-Hermitian
interaction, and

\[
 \operatorname{Prob}(P_{\rm out})=
 \operatorname{tr}(U_T^\dagger P_{\rm out}U_TP_{\rm in}).
\]

It also gives the auxiliary quartic action and states
\(R^\dagger H_{1,1}R=H_\phi\) up to a spatial boundary term.  Insert a
spectral intermediate state of energy mismatch \(\omega=E_m-E_i\).  Let
\(\tau\) and \(\tau'\) be its relative propagation durations on the amplitude
and conjugate amplitude.  Truncating both to the finite observation interval
gives

\[
 \int_0^Td\tau\int_0^Td\tau'\,e^{i\omega(\tau-\tau')}
 =|F_T(\omega)|^2.
\]

Changing to \(\sigma=\tau-\tau'\) gives the exact triangular form

\[
 |F_T(\omega)|^2
 =\int_{-T}^{T}(T-|\sigma|)e^{i\omega\sigma}d\sigma
 =\frac{4\sin^2(\omega T/2)}{\omega^2}.
\]

Thus the same kernel used in the finite-time shell certificate follows from
the two relative propagation intervals across the Hamiltonian cut.  The incoming energy characteristic
has already canceled the independent external
\(\delta_1(0)=L_0\).  The \(T\) above is the internal relative-time interval,
so retaining it is not double-counting the external spacetime volume.

Plancherel and \(s=2E\omega\) give

\[
 \int_{\mathbb R}|F_T(\omega)|^2d\omega=2\pi T,
\]

\[
 \int_{\mathbb R}
 \left|\frac{F_T(s/(2E))}{2E}\right|^2ds
 =\frac{\pi T}{E}.
\]

This promotes the time kernel from `KINEMATIC` to
`BT_INTERACTION_PICTURE_CUT_KERNEL_AFFILIATED` on the declared reduced-mode
domain.  It is not a construction of the complete finite-time Hamiltonian or
an asymptotic wave operator.

## Coefficient match

The fixed-channel history norm is \(9/8\), and the public six-point tree
density multiplier is \(256\lambda^8\).  Therefore the cut shell norm is

\[
 \frac98\,256\lambda^8\frac{\pi T}{E}
 =\frac{288\pi\lambda^8T}{E}.
\]

Multiplication by the exact outgoing shell coarea density reproduces

\[
 \frac{27\lambda^8T}{320\pi^4E}.
\]

At the declared detector fixture \(E=\kappa\), multiplication by
\(N_{\rm in}=5/[48\kappa^3L_xL_y^2L_z^2]\) recovers

\[
 \Gamma_\Xi=
 \frac{9\lambda^8}
 {1024\pi^4\kappa^4L_xL_y^2L_z^2}.
\]

No time-regulator coefficient is fitted anywhere in this chain.

## Why pseudo-unitarity does not finish survival

Let the Krein metric be \(J=\operatorname{diag}(1,-1)\), take
\(P=\operatorname{diag}(1,0)\), and use the exact \(J\)-unitary boost

\[
 U_r=\begin{pmatrix}\cosh r&\sinh r\\
                     \sinh r&\cosh r\end{pmatrix}.
\]

Its two complementary Born weights are

\[
 \operatorname{tr}(U_r^\sharp P U_rP)=\cosh^2r,
\]

\[
 \operatorname{tr}(U_r^\sharp(1-P)U_rP)=-\sinh^2r.
\]

They sum to one, but the complement is negative for every nonzero \(r\).
This exact counterexample proves that pseudo-unitarity conserves the signed
Krein trace without making a detector partition positive.

The earlier history certificate constructs a different object: on its
declared positive detector carrier an ordinary rotation gives
\(\cos^2\theta\) survival and \(\sin^2\theta\) detection.  The new calculation
fixes the angle's leading shell coefficient dynamically, but it does not
embed that positive rotation into the actual BT finite-time Krein evolution.
Such an embedding needs weak ghost symmetry, a positive physical subquotient,
or the missing Eq. (19) projector pushforward.

## Boundary and next gate

We have therefore gained a BT-derived local cut rate, while the survival
column remains an operational detector dilation rather than a computed
virtual BT term.  The next gate is to embed the positive history carrier as a
weakly ghost-symmetric subquotient of finite-time BT wave packets, or obtain
the same complement from Eq. (19).  Only then should the nine physical mixed
\(3|3\) shell channels be glued and their intersections analyzed.

This certificate does not construct the full finite-time Hamiltonian on a
common dense domain, global Møller/LSZ/S operators, Eq. (19), loop positivity,
gravity/BRST transfer, or anything `LORENTZIAN-CAUSAL`.

## Verification receipt

- Tier 0: all new Python and JSON files parse; the scoped diff passes
  `git diff --check`; Papers 5 and 6 compile twice.
- Tier 1: the producer passes 26/26 exact checks, the independent rational-
  fixture verifier passes 23/23 checks, and six mutation tests pass.  All
  scientific processes remain under the 500 MB hard cap.
- Tier 2: the five-certificate dependency fork from the history instrument and
  finite-time shell through the detector cell and this cut affiliation passes
  sequentially.  Producers report 25/25, 23/23, 19/19, 27/27 and 26/26
  checks; independent verifiers report 23/23, 27/27, 21/21, 26/26 and 23/23
  checks.  The combined 31-test chain passes in 3.52 seconds with peak resident
  memory 76,684 KB; every individual producer and verifier stays below 75 MB.
- Tier 3 is not required because no shared core algebra, freeze, release, QME
  state, or Lorentzian claim changes.
- Science Forge reports `CLEAN` for the new work item and append-only `DONE`
  event.  The read-only Go coordinator used one thread and
  `GOMEMLIMIT=300MiB` outside the scientific hard `ulimit` because the Go
  runtime reserves a large virtual arena; peak resident memory was 282,452 KB.

Commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_finite_time_hamiltonian_cut_affiliation.py --write --check
ulimit -v 500000; python3 reverse_physics/verify_bt_finite_time_hamiltonian_cut_affiliation.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_finite_time_hamiltonian_cut_affiliation
```

CLOSE-OUT: DONE -- the finite-time shell kernel and detector-rate coefficient
are affiliated with the BT interaction-picture cut; pseudo-unitarity alone is
exactly insufficient to affiliate the positive survival complement.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_TIME_HAMILTONIAN_CUT_AFFILIATION_V1.json`
