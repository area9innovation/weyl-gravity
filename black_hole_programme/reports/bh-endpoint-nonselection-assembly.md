# BH endpoint-selection assembly — infinity Einstein selection, horizon non-selection

**Work item:** `black-hole-endpoint-nonselection-assembly`
**Certificate:** `black_hole_programme/certificates/BH_ENDPOINT_NONSELECTION_ASSEMBLY.json`
**Verdict token:** `BH_ONE_ENDED_ENDPOINT_SELECTION_INFINITY_EINSTEIN_HORIZON_NONSELECTION`
**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE` · **Lifecycle:** `CLASSIFIED`

Assembles the certified horizon and infinity data into the strongest invariant
**one-ended** endpoint-condition selection/nonselection statement actually
supported for pure-Weyl perturbations of Schwarzschild (axial `l = 2`, real
`omega != 0`; polar fixture-only), and names the exact missing analytic object.
All arithmetic exact.

## The assembled theorem

### 1. Invariant pairing rank (exact)

On `span(Einstein, extra)` the Lee–Wald Gram is `G = [[0, a],[conj a, b]]`, with
`a = a(omega) = i F^r/(pi alpha)` the certified cross invariant (nonzero for
every real `omega != 0` — its only real zero is the excluded `omega = 0`) and `b`
the representative-dependent extra self-pairing. Then
`det G = -|a|^2 = -9216 omega^2 (omega^2+4)(16omega^2+1)^2 / [25(omega^2+1)(4omega^2+1)] < 0`
strictly for all real `omega != 0`, so `G` has **rank 2 and signature (1, 1)**,
**independent of the representative `b`**: the Einstein self-pairing is null
(BH2A RW-null theorem) yet the extra branch is symplectically non-degenerate
against Einstein. (The verifier confirms this by an independent eigenvalue route.)

### 2. Horizon non-selection

Future-horizon analyticity admits **both** the Einstein (RW ingoing, dimension 1)
and the extra (two-parameter ingoing-regular, indicial `{0(×2), -4imω, -2-4imω}`)
families (`BH2A_HORIZON_REACH`, `BH2A_CAUSAL_DISPOSITION`). Horizon analyticity
alone does **not** force `delta R_ab = 0`.

### 3. Infinity selection

The finite-Lee–Wald-flux asymptotic phase space at infinity contains **exactly
the Einstein sector** — extra slice-norm divergent — for every real `omega != 0`
(axial literal-symbolic, `BH2C_SYMBOLIC_FLUX_RADIATION_CLASS`; plus the
`omega = 3/5` fixture `BH2C_FLUX_CLASS`; polar fixture-only).

### 4. Endpoint disposition

Horizon analyticity **plus** the certified infinity finite-flux class force
`delta R_ab = 0` **on the finite-flux phase space**; the additional solution
**exists** (horizon-regular) but is excluded at infinity by symplectic-norm
finiteness — a phase-space normalization, **not** a local boundary or initial
condition. Exceptional set: `omega = 0` only (excluded exceptional carrier; no
other real exceptional frequency).

### 5. Separation from the local Cauchy truncation

The certified **local** truncation
(`delta R|Sigma = nabla_n delta R|Sigma = 0 => delta R = 0` modulo conformal
gauge, `BH_LOCAL_EINSTEIN_CAUCHY_TRUNCATION`) is a Cauchy-slice uniqueness
statement; the endpoint selection here is a **global two-ended boundary**
statement. Distinct objects — neither implies the other.

### Counterexample mutations (rejected)

- imposing a **local** horizon boundary condition that drops the extra ingoing
  family — rejected: horizon analyticity provably admits the two-parameter extra
  family, so no local horizon condition removes it;
- calling the infinity finite-norm selection a local boundary condition —
  rejected: it is a phase-space normalization;
- asserting the Einstein–extra pairing is degenerate at some real `omega != 0` —
  rejected: `det G < 0` strictly (rank 2, signature (1,1)).

## Missing analytic object (named, per the stop condition)

The **exact global linear map from ingoing horizon data to infinity radiation
data** — the connection problem of the master ODE — is a **confluent-Heun
connection** (transcendental; the connection coefficients are not elementary).
Without it the full two-ended scattering map is not constructed; only the
one-ended endpoint disposition and the exact invariant pairing are certified.
Per the work item's note, the assembly closes with this exact missing object
rather than combining local series rhetorically.

## What is NOT established (fail-closed)

- the global horizon-to-infinity connection map / a two-ended scattering matrix;
- any polar endpoint theorem beyond the preserved fixture (needs the polar
  route-B symbolic identity);
- general `l`; the exact extra self-pairing invariant `b` (representative-
  dependent — only rank/signature are invariant);
- no QNM, stability, ringdown, scattering, particle, or ghost claim; no
  additional classical branch is a particle or ghost; no claim that every local
  differential boundary/initial condition fails; no parity-complete claim.

## Verification

- `python3 black_hole_programme/verify_bh_endpoint_nonselection_assembly.py`
  — exact: schema + nine anchor hashes; independent eigenvalue recomputation of
  the pairing rank/signature and strict `det G < 0`; anchor-consistency of the
  horizon/infinity/Cauchy/polar statements; claim-boundary + vocabulary.
- `pytest black_hole_programme/tests/test_bh_endpoint_nonselection_assembly.py`
  — structural Tier-1 rail.

## Receipts

- Generator: `black_hole_programme/bh_endpoint_nonselection_assembly.py` — imports
  nine anchors by content hash and recomputes the invariant pairing exactly.

## Paper 14

The justified lifecycle is an assembly (`CLASSIFIED`) with a named missing
object, not a new paper theorem. A scoped Paper 14 / claim-map upgrade citing
this certificate (the one-ended endpoint disposition, the invariant pairing
rank/signature, and the confluent-Heun connection as the missing object) is the
recommended coordinator-integration follow-up; the certificate is the
authoritative handoff.

EVIDENCE: `black_hole_programme/certificates/BH_ENDPOINT_NONSELECTION_ASSEMBLY.json`

CLOSE-OUT: DONE — one-ended endpoint selection assembled (infinity Einstein
selection + horizon non-selection + exact invariant pairing rank/signature +
Cauchy separation), with the exact global connection map named as the missing
object, as the work item permits.
