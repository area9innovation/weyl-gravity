# Axial partial-jet endpoint-frame audit

Date: 2026-07-24

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

Lifecycle: report-only exact audit.  No endpoint-jet certificate, outgoing
map, interval transport, Stokes identity, QNM, or time-domain theorem is
promoted here.

## Question

The exact six-state factor gauge has state order

\[
(\text{metric RW tangent},\ \text{carrier RW base},\ L_x\text{ spin one})
\]

and connection

\[
\begin{pmatrix}
A&E&C\\
0&A&D\\
0&0&A_x
\end{pmatrix}.
\]

It is the spin-two-row partial jet of

\[
\mathcal B(\tau)=
\begin{pmatrix}
A+\tau E&D+\tau C\\
0&A_x
\end{pmatrix}.
\]

This audit asks whether the printed future-horizon, incoming-infinity, and
outgoing-infinity endpoint triples can be reissued as endpoint frames of that
partial jet.

## A necessary typing correction

In the partial-jet module, the pure metric Einstein column is **not** the
\(\tau\)-derivative of the carrier column.  It is the
\(\epsilon\)-copy of the carrier RW base germ.  In the ordered coefficient
basis

\[
(\epsilon\,\mathrm{RW},\ \mathrm{RW},\ \mathrm{spin\ one}),
\]

the carrier column contains the derivative in its upper two components:

\[
\begin{pmatrix}
\dot u_2\\ u_2\\0
\end{pmatrix},
\qquad
\text{whereas the metric column is }
\begin{pmatrix}
u_2\\0\\0
\end{pmatrix}.
\]

Thus the exact endpoint check has two parts:

1. the metric and carrier base components must be the same scalar RW Jost
   germ after a scalar rescaling;
2. the upper part of the carrier column must equal \(\dot u_2\), modulo
   addition of the metric column.

The first part is decided below.  The second requires a
\(\tau\)-differentiated endpoint recurrence and is not present in the current
certificates.

## Exact endpoint factor frames

The source triples are

\[
\mathcal H_{\rm reg}=(XH0a,XH0b,EH0),
\]

\[
\mathscr I^-=(XI0,XI1,EI0),
\qquad
\mathscr I^+=(XI2,XI3,EI2).
\]

Here \(\mathcal H_{\rm reg}\) is the frame denoted \(H^-\) in the audit
request and “future-horizon regular” in the imported certificates; the report
does not change the certificates' geometric orientation convention.

For every endpoint, the factor order produced first is

\[
(R,S,E)
=
(\text{carrier spin two},\text{spin one},\text{metric spin two}).
\]

The partial-jet order is

\[
(E,R,S).
\]

Therefore the common column permutation is

\[
[R\ S\ E]
\begin{pmatrix}
0&1&0\\
0&0&1\\
1&0&0
\end{pmatrix}
=[E\ R\ S].
\]

### Future horizon \(\mathcal H^-\)

The already certified quotient amplitudes are

\[
\pi_x(XH0a)=4\omega^2-3i\omega+4,
\]

\[
\pi_x(XH0b)=4(\omega-i)(2\omega-i).
\]

Hence

\[
R_H=XH0a-
\frac{4\omega^2-3i\omega+4}
     {4(\omega-i)(2\omega-i)}XH0b,
\qquad
S_H=XH0b,
\qquad
E_H=EH0.
\]

Their scalar factor amplitudes are

\[
h_R=\frac{i\omega(4\omega-i)}{2(\omega-i)},
\]

\[
h_S=4(\omega-i)(2\omega-i),
\]

\[
h_E=-\frac{i\omega(4\omega-i)}{4(\omega-i)}.
\]

Thus

\[
h_R=-2h_E.
\]

The smallest metric rescaling that matches the carrier RW base germ is

\[
\widetilde E_H=-2E_H.
\]

If unit scalar amplitudes are wanted instead, use

\[
\bar R_H=R_H/h_R,\qquad
\bar E_H=E_H/h_E,\qquad
\bar S_H=S_H/h_S.
\]

The equality of the metric and carrier scalar germs follows from the
one-dimensional future-horizon ingoing RW line, not merely from equality of
their leading numbers.

### Incoming null infinity \(\mathscr I^-\)

The certified quotient amplitudes are

\[
\pi_x(XI0)=2,\qquad
\pi_x(XI1)=-2i\omega.
\]

Therefore

\[
R_-=XI0-\frac{i}{\omega}XI1,
\qquad
S_-=XI1,
\qquad
E_-=EI0.
\]

The scalar amplitudes are

\[
i_R=1,\qquad
i_S=-2i\omega,\qquad
i_E=-i\omega.
\]

Consequently

\[
\widetilde E_-=\frac{i}{\omega}E_-
\]

has the same unit incoming spin-two amplitude as \(R_-\).  A unit spin-one
quotient lift is

\[
\bar S_-=\frac{i}{2\omega}S_-.
\]

### Outgoing null infinity \(\mathscr I^+\)

The current incoming-factor certificate does not print the outgoing
factor frame.  It can nevertheless be recomputed exactly from the imported
all-orders infinity heads and the certified quotient

\[
y=r^2(r-2)Z.
\]

The oscillatory carrier heads have

\[
(P_0,Q_0)_{XI2}=(1,-2),\qquad
(P_0,Q_0)_{XI3}=(0,1),
\]

with powers \(-4i\omega\) and \(-4i\omega-1\), respectively.  Applying the
exact quotient row to the first required coefficients gives

\[
\pi_x(XI2)=2(16\omega^2-4i\omega-5),
\]

\[
\pi_x(XI3)=-2i\omega.
\]

Hence

\[
R_+=XI2-
\frac{i(16\omega^2-4i\omega-5)}{\omega}XI3,
\qquad
S_+=XI3,
\qquad
E_+=EI2.
\]

The carrier RW amplitude of \(R_+\) is \(1\).  Applying the exact Einstein
master map \(U\) to \(EI2\), including the cancellation of its leading
\(r^{1-4i\omega}\) terms, gives outgoing RW amplitude

\[
o_E=\frac12.
\]

Thus

\[
\widetilde E_+=2E_+
\]

matches the carrier RW base germ, while

\[
\bar S_+=\frac{i}{2\omega}S_+
\]

has unit spin-one quotient amplitude.

This outgoing calculation is exact but report-only.  It should be rebuilt by
an independent producer before it is used as a certificate dependency.

## Endpoint derivative law and admissible shears

Let \(\Phi(\tau)\) be the bulk four-state propagator and let
\(F_H(\tau)\), \(F_I(\tau)\) be two-by-two endpoint frames in factor order
\((\mathrm{spin\ two},\mathrm{spin\ one})\).  The base connection is

\[
C(\tau)=F_I(\tau)^{-1}\Phi(\tau)F_H(\tau).
\]

With

\[
K_H=F_H^{-1}\dot F_H,\qquad
K_I=F_I^{-1}\dot F_I,
\]

its exact derivative is

\[
\boxed{
\dot C=
F_I^{-1}\dot\Phi F_H
-K_I C
+C K_H.
}
\]

Preservation of the factor filtration and a \(\tau\)-constant spin-one
quotient normalization permit

\[
K_\star=
\begin{pmatrix}
k_{2,\star}&h_\star\\
0&0
\end{pmatrix}.
\]

The entry \(k_{2,\star}\) adds a multiple of the pure metric column to the
carrier tangent.  The entry \(h_\star\) changes the spin-one lift by a
spin-two lift.  These are exactly the two endpoint ambiguities allowed by the
filtered differential system.  A lower-left entry would violate the
filtration, while a lower-right entry would change the chosen spin-one
quotient normalization.

For the repeated scalar connection entry \(a\), the tangent entry transforms
as

\[
\boxed{
b\longmapsto b+a(k_H-k_I).
}
\]

Therefore

\[
[b]\in\mathcal O/(a)
\]

is independent of analytic filtration-preserving endpoint normalizations
once the analytic endpoint lifts exist.

The printed factor changes and scalar rescalings above depend on \(\omega\)
but not on \(\tau\).  They therefore do not themselves introduce a forbidden
component into \(K_H\), \(K_-\), or \(K_+\).  The spin-one state satisfies
\(Z'=A_xZ\) with no \(\tau\)-dependence, so its leading quotient
normalization can be held exactly constant at all three endpoints.

What is missing is an explicit construction of \(F_\star(\tau)\) and a
calculation of the resulting \(k_{2,\star}\) and \(h_\star\).  The existing
six-state endpoint columns solve the correct tangent equations, and any two
tangent lifts with the same selected endpoint class differ by the indicated
homogeneous shears.  That proves compatibility of the *type* of the missing
\(K_\star\), but it does not calculate it.

## Pass/fail matrix

`PASS` means imported or recomputed exact algebra decides the row.
`OPEN` means the required object is absent; it is not a failed identity.

| gate | \(\mathcal H_{\rm reg}\) | \(\mathscr I^-\) | \(\mathscr I^+\) |
|---|---|---|---|
| selected three-column formal endpoint space exists | PASS | PASS | PASS |
| exact carrier/spin-one factor line identified | PASS, certified | PASS, certified | PASS, report-only recomputation |
| metric RW germ equals carrier RW base germ after scalar rescaling | PASS: \(-2EH0\leftrightarrow R_H\) | PASS: \((i/\omega)EI0\leftrightarrow R_-\) | PASS: \(2EI2\leftrightarrow R_+\) |
| spin-one quotient normalization can be \(\tau\)-constant | PASS | PASS | PASS |
| required column permutation is explicit | PASS: \((R,S,E)\to(E,R,S)\) | PASS: same | PASS: same |
| allowed derivative discrepancy is exhausted by filtration shears | PASS at the module/type level | PASS at the module/type level | PASS at the module/type level |
| explicit \(\tau\)-analytic endpoint frame \(F_\star(\tau)\) constructed | OPEN | OPEN | OPEN |
| exact \(K_\star=F_\star^{-1}\dot F_\star\) computed | OPEN | OPEN | OPEN |
| printed column is literally a derivative without a shear | NOT ESTABLISHED | NOT ESTABLISHED | NOT ESTABLISHED |
| suitable for a certified \(T_\pm=J(C_\pm)\) theorem now | OPEN | OPEN | OPEN |

The literal statement “the metric column is the intrinsic derivative of the
carrier column” is therefore refused.  The correctly typed statement is:

> the metric column is the epsilon-copy of the carrier RW base germ, and the
> upper component of the carrier column is an intrinsic tangent modulo an
> analytic metric shear.

## Apparent frame events

There are three distinct sources of exceptional factors.

### Horizon Frobenius divisors

For the spin-two future-horizon scalar germ, the solved recurrence divisor is

\[
(n+1)(n+1+4i\omega).
\]

Thus the chosen analytic horizon frame has collision points

\[
\omega=\frac{i(n+1)}4,\qquad n\ge0.
\]

The named low points \(i/4\), \(i/2\), and \(i\) are already classified as
frame/reconstruction events, not as certified Evans zeros.  Higher head
denominators, including \(3i/4\), are members of the same Frobenius collision
lattice and require another local frame patch.

The displayed factor normalization also contains

\[
\omega,\qquad \omega-i,\qquad 2\omega-i,\qquad 4\omega-i.
\]

None vanishes for real \(\omega>0\).

### Infinity divisor

Both incoming and outgoing inverse-\(r\) scalar recurrences have divisor
proportional to

\[
2i\omega(n+1).
\]

Hence the exact infinity factor frames above have only the threshold event
\(\omega=0\).  Their coefficient denominators through the imported heads are
powers of \(\omega\); no \(i/4\), \(i/2\), or \(i\) event originates at null
infinity.

### Moving reconstruction divisor

The rational metric-master and partial-jet gauge contains

\[
r\omega-2i.
\]

It is nonzero on \(r>2\) for every real \(\omega>0\), and it is uniformly
excluded on the current non-real QNM seed disk by its strict nonzero real
part.  On the positive imaginary axis it meets the real exterior at

\[
r=\frac{2}{\operatorname{Im}\omega}.
\]

In particular it occurs at \(r=8\) for \(\omega=i/4\), at \(r=4\) for
\(\omega=i/2\), and at the horizon for \(\omega=i\).  A complex-frequency
implementation must use regular factor-frame patches rather than treating
this rational chart divisor as a physical pole.

## Consequence for the outgoing-map shortfall

The local partial-jet identity gives the correct arithmetic target:

\[
\text{shared \(\omega\)-Taylor model}
\ \widehat\otimes\
\mathbb Q[\epsilon]/(\epsilon^2).
\]

It preserves \(b=\dot a\), \(c=\dot d\), and the correlated combination
\(bd-ac\) under multiplication, inversion, and endpoint-frame changes.
However, it does not by itself repair the existing outgoing calculation.
The H4 exterior-norm rail already retained a shared \(\omega\) generator and
failed through Taylor-product conditioning.  A certified \(T_+\) still
requires both:

1. the endpoint \(K_H,K_+\) audit completed below; and
2. a bounded correlated transport in the mixed Taylor/dual algebra.

## Smallest exact successor

The smallest successor is an endpoint-only certificate, before any new
global transport:

1. import the exact six-state factor gauge and all three endpoint recurrence
   systems by content hash;
2. solve the horizon, incoming-infinity, and outgoing-infinity recurrences
   over
   \(\mathbb Q(i,\omega)[\epsilon]/(\epsilon^2)\);
3. hold the spin-one quotient leading coefficient fixed;
4. transform the resulting columns to the normalized factor frames above;
5. solve exactly for
   \[
   K_H,\qquad K_-,\qquad K_+
   \]
   in the upper-triangular allowed class;
6. certify zero residuals, list every denominator and Frobenius collision
   divisor, and supply alternate patches at the named frame events.

Only after this endpoint certificate passes should the transport successor
assert

\[
T_\pm=J(C_\pm),
\qquad
T_+T_-^{-1}=J(C_+C_-^{-1}).
\]

## Evidence used

The audit read the following exact artifacts:

| artifact | SHA-256 at audit time |
|---|---|
| `black_hole_programme/phase3/axial_partial_jet_transport_crosswalk_v1/certificate.json` | `cb14869716885ad4613c2247bc0c484b6d870d05cc40294eca025a86ac630d3a` |
| `black_hole_programme/phase3/axial_complete_reconstruction_repair/certificate.json` | `13a4077ee8c77cc5b99e379d35aa15afa09ebeea78c0df9a4771b4845c00c990` |
| `black_hole_programme/phase3/axial_rw_lx_triangular_preflight/certificate.json` | `1a6ac48dcc52659997cb0ed47709117308ef258c05e6996c559d9ad81f9ae579` |
| `black_hole_programme/phase3/axial_incoming_connection_analytic/certificate.json` | `c7d54c15cd7928227d62ede7825edba2b6ebc51ca6f6c617c7b0b56a74cdd040` |
| `black_hole_programme/phase3/axial_incoming_extended_domain_audit/certificate.json` | `f223358ca9de0f6d819684ce61d62677d6e5f8c5d4edaa600e2bae02719af0ef` |
| `black_hole_programme/phase3/axial_qnm_endpoint_germ_divisor_v1/certificate.json` | `18ed475219790332aa01144bd8ae4bb1d03ed9ffb1f1b4f429ff341b70e1b6f7` |

The outgoing quotient amplitudes and the \(EI2\) factor \(1/2\) were
recomputed directly from
`axial_complete_reconstruction_repair.produce.infinity_carrier_heads`,
`kernel_endpoint_data`, and the exact \(K,U\) maps.  Because this report does
not carry an independent machine verifier, those outgoing formulas remain
report-level until the successor certificate reproduces them.

## Claim boundary

This audit establishes exact endpoint factor compatibility at
\(\tau=0\), the necessary rescalings and permutations, and the allowed form
of endpoint normalization derivatives.  It does **not** establish:

- explicit analytic endpoint families in \(\tau\);
- numerical or symbolic values of \(K_H,K_-,K_+\);
- a certified outgoing map \(T_+\);
- a Stokes or pseudo-unitary scattering identity;
- bounded direct-integral transport;
- a QNM Smith branch, EP2, resolvent pole, or ringdown term.

CLOSE-OUT: SHORTFALL — all three endpoint triples are compatible with the
typed partial-jet factor order, but explicit dual-number endpoint recurrences
and their filtration-preserving \(K_\star\) shears remain unconstructed.

MISSING-DEP: an exact endpoint-only dual-number Frobenius/asymptotic
recurrence certificate for \(K_H,K_-,K_+\).
