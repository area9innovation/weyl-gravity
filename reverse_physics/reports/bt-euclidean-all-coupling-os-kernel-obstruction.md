# BT all-coupling ordinary-OS kernel obstruction

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_ALL_COUPLING_OS_KERNEL_OBSTRUCTION_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

Lifecycle:
`ALL_NONZERO_COUPLING_EVEN_VOLUME_ORDINARY_OS_OBSTRUCTION_PROVED`

## Result

The exact reflected-density witness previously certified only at
\(\lambda=0.4\) actually obstructs ordinary Osterwalder--Schrader reflection
positivity at every finite nonzero coupling. Zero-padding the two half-fields
also extends the sign from the periodic \(6^4\) lattice to every even
periodic \(L^4\) lattice with \(L\geq6\).

Write the physical log field as \(\psi=\lambda\phi\) and

\[
 A_L(\psi)=\frac12\sum_x r_x(\psi)^2,
 \qquad S_{\lambda,L}(\phi)=\frac{A_L(\lambda\phi)}{\lambda^2}.
\]

For each declared lattice, two positive-time half-configurations \(p_L,q_L\)
give

\[
 \Delta A_L=
 A_L(p_L,p_L)+A_L(q_L,q_L)-2A_L(p_L,q_L)>0.
\]

Therefore, for every \(\lambda\ne0\),

\[
 \Delta S_{\lambda,L}=\frac{\Delta A_L}{\lambda^2}>0
\]

and the two-by-two reflected density kernel obeys

\[
 \det K_\lambda
 =e^{-S_{pp}-S_{qq}}\left(1-e^{\Delta S_{\lambda,L}}\right)<0.
\]

As in the predecessor, equal compact bumps around the two half-fields turn
the point-kernel negative direction into an admissible positive-time cylinder
function with a strictly negative OS quadratic form. Thus this is an
integral obstruction, not a statement about zero-measure configurations.

The separate free Gaussian certificate already obstructs \(\lambda=0\) on
\(6^4\). Hence no point on the coupling axis supplies an ordinary positive-
Hilbert regulator reconstruction on that volume, and every nonzero coupling
is obstructed on an unbounded sequence of even volumes.

## Why the coupling disappears from the sign

The old calculation inserted \(\lambda=2/5\) before recording the action.
Its factor

\[
 \frac{1}{2\lambda^2}=\frac{25}{8}
\]

is strictly positive. Removing that factor leaves the unscaled physical-
field gap

\[
 \Delta A_6=\frac{774441}{128}>0.
\]

At another nonzero coupling the same physical \(\psi\)-centers correspond to
half-fields \(\phi=\psi/\lambda\). Reflection positivity must hold for every
admissible cylinder function, so allowing the test function to depend on
\(\lambda\) is legitimate. The only change in the exponent gap is division
by \(\lambda^2\), which cannot change its sign.

This argument also covers negative real \(\lambda\), although the physical
programme uses positive coupling. It makes no assertion at an infinite or
singular coupling.

## Every even volume from one padded witness

Let \(L=2n\), reflect through the links by

\[
 \theta(t,\mathbf x)=(1-t\bmod L,\mathbf x),
\]

and take the positive half to be \(t=1,\ldots,n\). Start with

\[
 p=(-7,0,7),\qquad q=(-6,3,3),
\]

and, when \(n>3\), append \(n-3\) zeros. Both half sums vanish. Consequently
all four reflected pairs lie on the global mean-zero carrier.

For \(L=6\), exact powers-of-two arithmetic gives the gap per spatial site

\[
 \delta A_6=\frac{28683}{1024},
 \qquad
 \Delta A_6=6^3\delta A_6=\frac{774441}{128}.
\]

For every \(n\geq4\), the nonzero residual rows are already all present in
the \(n=4\) fixture. Increasing \(n\) only inserts sites whose value and two
temporal neighbors are zero, so their residuals vanish. The four reduced
actions remain unchanged and

\[
 \delta A_{2n}=\frac{1023}{4},
 \qquad
 \boxed{\Delta A_L=L^3\frac{1023}{4}>0\quad(L\geq8\text{ even}).}
\]

The independent verifier does not import this reduction. It enumerates all
sites and all eight neighbors on the full \(6^4\) and \(8^4\) lattices, then
checks additional padded half-lengths with its own temporal action routine.

## What the theorem does and does not decide

This closes a genuine loophole in the reconstruction status. Ordinary OS
positivity is not lost only near the free theory or at one simulated
coupling, and it is not a small-volume accident. The declared positive BT
lattice regulator fails it for all nonzero couplings and every even
\(L\geq6\).

The result does not prove that every possible continuum limit fails OS
positivity. The negative test functions move to field amplitude
\(O(1/\lambda)\) when expressed in \(\phi\), and this theorem does not show
that a fixed cutoff-independent observable retains a negative limit. That
would require a separate scaling-limit theorem.

It also does not say that the positive Euclidean measure is ill-defined.
Most importantly for the active continuum programme, it neither proves nor
obstructs the interacting bound

\[
 \sup_L\mathbb E\|\Phi_L\|_{H^{-1}}^2<\infty.
\]

The annealed conditional-center and full-Witten Schur routes remain the live
ways to decide that estimate. Ordinary OS reconstruction, a modified or
Krein reconstruction, and positive-measure moment control are distinct
questions.

## Boundary

This certificate does not establish failure of every continuum OS limit for
a fixed cutoff-independent observable class, construct or rule out a Krein
reconstruction, bound or diverge the interacting \(H^{-1}\) moment, construct
a continuum Euclidean measure, derive a Born rule, or establish anything
`LORENTZIAN-CAUSAL`. Paper 21 imports the stronger regulator theorem while
retaining these open continuum and reconstruction boundaries.

## Verification

Run sequentially under the 500 MB Python cap:

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_all_coupling_os_kernel_obstruction.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_all_coupling_os_kernel_obstruction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_all_coupling_os_kernel_obstruction
```

Tier 2 uses exact hashes of the unchanged \(\lambda=0.4\) density-kernel and
finite-volume obstruction but does not promote the interacting
\(H^{-1}\), continuum, quantum, Krein, or Lorentzian lifecycle.

The producer passed 16/16 checks in 0.04 seconds at 20,468 KiB; the
nonimporting verifier passed 12/12 checks in 0.22 seconds at 30,732 KiB; and
eleven direct and mutation tests passed in 1.11 seconds at 31,448 KiB. The
Paper 21 claim map regenerated and independently verified, and two bounded
LaTeX passes produced 70 pages with no undefined references or overfull
boxes. The planning import accepted 1,685 nodes with zero invalid items and
zero malformed events in 6.54 seconds at 222,676 KiB under the Go memory cap.
The advisory shadow wrapper exited zero, but its bridge audit failed closed
because the external `bp2transformer` verifier lacks `sympy`; its census also
reported 1,839 certificates versus the stale baseline of 976. Those findings
remain failures and drift, not scientific passes.
