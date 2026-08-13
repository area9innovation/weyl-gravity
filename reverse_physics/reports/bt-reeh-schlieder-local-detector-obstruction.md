# Vacuum-dark bounded-local obstruction for the BT quadrupole instrument

**Certificate:**
REVERSE_PHYSICS_BT_REEH_SCHLIEDER_LOCAL_DETECTOR_OBSTRUCTION_V1

**Dependency tag:** LOCAL-ALGEBRAIC

**Lifecycle:** CLASSIFIED

## Result

The exact compact-spacetime quadrupole Julia instrument cannot be realized by
a bounded local effect in any vacuum representation satisfying the declared
commuting-algebra and complement-cyclicity hypotheses. The obstruction also
applies to a normally coupled tensor-pointer apparatus whose unitary belongs
to the bounded local algebra.

The proof does not require a type-III hypothesis. It uses only the elementary
separating-vacuum consequence of Reeh--Schlieder cyclicity. It is therefore
both stronger and more precisely scoped than the predecessor's statement
that the global rank-one operators had not been identified as local.

This is a conditional abstract theorem. The repository has not constructed
a positive Haag--Kastler net or proved the Reeh--Schlieder property for the
public Bateman--Turok Krein/reduced-mode theory. No model-specific
LORENTZIAN-CAUSAL claim follows.

## Abstract local-algebra theorem

Let \(\mathcal H\) be a positive Hilbert space and let
\(\mathcal M,\mathcal N\subset B(\mathcal H)\) be commuting unital von
Neumann algebras. In a local net one has in mind

\[
 \mathcal M=\mathcal A(O),\qquad
 \mathcal N=\mathcal A(O'),\qquad
 [\mathcal M,\mathcal N]=0,
\]

where \(O'\) is a nonempty spacelike-complement region. Assume that the
vacuum \(\Omega\) is cyclic for \(\mathcal N\):

\[
 \overline{\mathcal N\Omega}=\mathcal H.
\]

Then \(\Omega\) is separating for \(\mathcal M\).

Indeed, suppose \(A\in\mathcal M\) and \(A\Omega=0\). For every
\(B\in\mathcal N\), commutativity gives

\[
 AB\Omega=BA\Omega=0.
\]

Thus \(A\) vanishes on the dense set \(\mathcal N\Omega\). Since \(A\) is
bounded, \(A=0\) on all of \(\mathcal H\).

This is the complete proof. The Reeh--Schlieder theorem supplies the
cyclicity premise in standard positive-energy local-QFT settings; the
separating conclusion used here is derived rather than imported as a black
box.

## Positive-effect corollary

Let \(E\in\mathcal M\) be an effect,

\[
 0\le E\le I,
 \qquad
 \langle\Omega,E\Omega\rangle=0.
\]

The von Neumann functional calculus gives \(E^{1/2}\in\mathcal M\), and

\[
 \|E^{1/2}\Omega\|^2
 =\langle\Omega,E\Omega\rangle=0.
\]

Because \(\Omega\) is separating, \(E^{1/2}=0\), hence \(E=0\).

Therefore every nonzero bounded local positive outcome has strictly positive
vacuum probability under these hypotheses. The statement concerns an
individual positive outcome. A signed difference of two outcomes need not
be positive and can have zero vacuum mean.

## Application to the exact Julia effect

The predecessor constructed

\[
 E_{\rm click}={1\over4}P_u,\qquad
 P_u=|u_2\rangle\langle u_2|,
\]

where \(u_2\) is a normalized two-particle response mode. In the active-field
vacuum representation,

\[
 \langle\Omega,u_2\rangle=0,\qquad
 \langle\Omega,E_{\rm click}\Omega\rangle=0,\qquad
 \langle u_2,E_{\rm click}u_2\rangle={1\over4}.
\]

Thus \(E_{\rm click}\) is nonzero and exactly vacuum-dark. It follows that

\[
 E_{\rm click}\notin\mathcal A(O)
\]

for every bounded region \(O\) satisfying the declared hypotheses.

The two exact Kraus maps fail locality separately. If
\(K_{\rm click}\in\mathcal A(O)\), then
\(K_{\rm click}^*K_{\rm click}=E_{\rm click}\) would be local. If
\(K_{\rm no}\in\mathcal A(O)\), then

\[
 I-K_{\rm no}^*K_{\rm no}=E_{\rm click}
\]

would be local. Both conclusions contradict the effect theorem.

This promotes the predecessor's local-Kraus nonidentification to a no-go
under explicit standard local-net hypotheses. It does not assert that the
public BT representation satisfies those hypotheses.

## Normal local pointer dilations do not evade the theorem

Let a pointer Hilbert space be \(\mathcal K\), let its initial normal state be
\(\omega\), and take a local coupling unitary

\[
 U\in\mathcal M\,\overline\otimes\,B(\mathcal K).
\]

For a pointer effect \(0\le Q\le I\), the induced field effect is

\[
 E=({\rm id}\otimes\omega)
 \left[U^*(I\otimes Q)U\right].
\]

Normal slice maps preserve the von Neumann algebra and positivity, so
\(E\in\mathcal M\) and \(0\le E\le I\). If the pointer has exactly zero click
probability on the vacuum, the positive-effect corollary forces \(E=0\).

Consequently no normal bounded local tensor-pointer unitary can reproduce
the nonzero Julia effect \(P_u/4\). Enlarging the finite Julia pointer does
not fix the problem as long as the coupling is local, the pointer state is
normal, and the induced outcome is exactly vacuum-dark.

## Why the cyclicity hypothesis is essential

The exact two-dimensional countermodel is

\[
 \mathcal H=\mathbb C^2,\qquad
 \mathcal M=B(\mathbb C^2),\qquad
 \Omega=e_0,\qquad
 E=|e_1\rangle\langle e_1|.
\]

Then \(E\ne0\) but
\(\langle\Omega,E\Omega\rangle=0\). The commutant of
\(B(\mathbb C^2)\) is the scalar algebra, whose orbit of \(e_0\) is only
one-dimensional and is not cyclic in \(\mathbb C^2\). Thus dropping
complement cyclicity genuinely invalidates the theorem; it is not decorative
AQFT terminology.

## The balanced-contrast escape

The theorem forbids a nonzero positive effect with zero vacuum probability.
It does not forbid a zero vacuum *contrast*. For any self-adjoint contraction
\(B\in\mathcal M\), define

\[
 E_+={I+B\over2},\qquad
 E_-={I-B\over2}.
\]

These are local positive effects and \(E_++E_-=I\). If
\(\langle\Omega,B\Omega\rangle=0\), then

\[
 p_+(\Omega)=p_-(\Omega)={1\over2},\qquad
 p_+(\Omega)-p_-(\Omega)=0.
\]

The exact diagonal fixture

\[
 B=\operatorname{diag}(1,-1),\qquad
 \Omega={e_0+e_1\over\sqrt2}
\]

realizes this algebraically. Both outcomes have nonzero vacuum baselines,
while their signed contrast is vacuum-dark.

## Conditional bounded-local quadrupole lift

There is an exact general construction of the required bounded contrast once
the unbounded compact quadrupole density has a self-adjoint local
realization. Let \(D\) be self-adjoint and affiliated with
\(\mathcal M\), assume

\[
 \Omega,X_2,X_4\in\operatorname{Dom}(D),
\]

and import the three response identities

\[
 \langle\Omega,D\Omega\rangle=0,\qquad
 \langle\Omega,DX_2\rangle=0,\qquad
 a=\langle\Omega,DX_4\rangle\ne0.
\]

For each positive integer \(n\), spectral functional calculus gives

\[
 D_n=D\,1_{[-n,n]}(D)\in\mathcal M.
\]

Each \(D_n\) is bounded and self-adjoint. Form the real response vector

\[
 v_n=\bigl(
 \langle\Omega,D_n\Omega\rangle,
 \operatorname{Re}\langle\Omega,D_nX_2\rangle,
 \operatorname{Im}\langle\Omega,D_nX_2\rangle,
 \operatorname{Re}\langle\Omega,D_nX_4\rangle,
 \operatorname{Im}\langle\Omega,D_nX_4\rangle
 \bigr)\in\mathbb R^5.
\]

Strong graph convergence on \(\operatorname{Dom}(D)\) gives

\[
 v_n\longrightarrow
 v=(0,0,0,\operatorname{Re}a,\operatorname{Im}a)\ne0.
\]

Let \(V\) be the real linear span of the \(v_n\). Since \(V\) is a subspace
of \(\mathbb R^5\), it is finite-dimensional and closed. Therefore
\(v\in V\), so there are at most five indices \(n_j\) and real coefficients
\(c_j\) such that

\[
 \sum_j c_jv_{n_j}=v.
\]

Consequently

\[
 C=\sum_jc_jD_{n_j}\in\mathcal M
\]

is bounded and self-adjoint, has exactly zero vacuum and \(X_2\) response,
and retains the nonzero \(X_4\) response \(a\). Since \(C\ne0\), normalize

\[
 B={C\over\max(1,\|C\|)}.
\]

Then \(B\) is a bounded self-adjoint local contraction and

\[
 \langle\Omega,B\Omega\rangle=0,\qquad
 \langle\Omega,BX_2\rangle=0,\qquad
 \langle\Omega,BX_4\rangle\ne0.
\]

Thus \(E_\pm=(I\pm B)/2\) are bounded local balanced effects and their
vacuum baselines agree. The response statement uses a phase-reversal
contrast, because the imported quadrupole datum is a vacuum-to-pair matrix
element rather than a diagonal state expectation. For a pair vector
\(X\perp\Omega\), define the unnormalized double contrast

\[
 \mathcal C_B(X)={1\over4}\left[
 \langle\Omega+X,B(\Omega+X)\rangle
 -\langle\Omega-X,B(\Omega-X)\rangle\right]
 =\operatorname{Re}\langle\Omega,BX\rangle.
\]

For normalized \((\Omega\pm X)/\sqrt{1+\|X\|^2}\), the right-hand side is
divided by the same positive denominator. Hence its zero/nonzero status is
unchanged. The contrast is exactly zero for \(X_2\). Since the complex
\(X_4\) matrix element is nonzero, a calibrated phase of the phase-reversed
preparation gives a strictly nonzero real contrast.

This is an exact finite-existence theorem; it does not require a convergent
infinite operator series. It does not compute the cutoffs or coefficients
without the local spectral measures, and it is not a one-shot dark-port
probability or an observable selected by public BT dynamics.

The decisive remaining BT input is now sharper. The public auxiliary theory
needs a positive local net in which the compact quadrupole density is
self-adjoint and affiliated, together with the three domain statements
above. None is supplied by the reduced-mode coefficient calculation. The
finite diagonal fixture alone also does not supply them.

## Claim boundary

Established:

- the abstract commuting-algebra separating-vacuum theorem;
- the no-go for a nonzero exactly vacuum-dark bounded local effect;
- the conditional exclusion of both exact Julia Kraus maps;
- the conditional exclusion of a normal bounded local tensor-pointer
  realization of the same effect;
- an exact countermodel proving complement cyclicity is essential; and
- the algebraic distinction between zero probability and zero balanced
  contrast; and
- conditional on local self-adjoint affiliation and domains, an exact finite
  bounded-spectral-truncation construction of a local phase-reversal
  quadrupole contrast.

Not established:

- a positive Haag--Kastler net for the public BT theory;
- a Reeh--Schlieder vacuum for its Krein or reduced-mode carrier;
- impossibility of all local detectors;
- the positive BT local net, self-adjoint affiliation and domain theorem
  needed to instantiate the conditional balanced contrast;
- an obstruction to approximate, almost-local, unbounded-readout or
  non-normal constructions;
- public-BT selection of the apparatus or phase-reversed preparations;
- the \(\lambda^{10}\) and higher output amplitudes;
- the standard scalar projector or general Eq. (19);
- gravity, metric BV--BRST, QME restoration, residual transfer, or anything
  LORENTZIAN-CAUSAL; or
- literature priority.

The cyclicity input is the standard one introduced by H. Reeh and
S. Schlieder, *Il Nuovo Cimento* **22** (1961) 1051--1068,
DOI 10.1007/BF02787889. The operator-algebra corollaries used here are
proved above. No priority conclusion is drawn from the literature check.

## Verification commands

    ulimit -v 500000; python3 reverse_physics/bt_reeh_schlieder_local_detector_obstruction.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_reeh_schlieder_local_detector_obstruction.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_reeh_schlieder_local_detector_obstruction

## Verification receipt

All Python, TeX and Tier-3 processes ran sequentially under a 500000 KiB
virtual-memory limit; no out-of-memory event occurred.

- Producer: 34/34 exact checks passed in 0.03 s, peak 16228 KiB.
- Independent verifier: 46/46 checks passed in 0.06 s, peak 23616 KiB.
  It reconstructs the Julia effect and both finite fixtures with independent
  rational matrix arithmetic, and checks the abstract proof ledger rather
  than importing the producer.
- Mutation suite: 49/49 tests passed in 0.15 s wall time, peak 24572 KiB
  (0.080 s unittest time).
- Papers 05 and 06 each compiled twice with halt-on-error. Their final
  passes both took 0.49 s at 50600 KiB and 50704 KiB peak,
  respectively. Paper 05 is 73 pages and 714102 bytes, with SHA-256
  99698a9ec244b0b418115e5894cb9c299fd2c8b0e41b9f46610885afb45040a0.
  Paper 06 is 63 pages and 677917 bytes, with SHA-256
  7a0574454a9756604d803efee871803994e6c2c1d1355a1729aee6946179c9af.
  Neither log has undefined references, citations or new overfull boxes.
- Tier 3 ran 2833 tests in 804.830 s (805.90 s wall, peak 391324 KiB).
  All 49 new tests passed. The run remained fail-closed with 32 failures and
  9 skips. Thirty-one failure names match the predecessor baseline. The
  additional test_c1_the_scan_actually_ran failure explicitly records that
  the capped chain-import repository scan returned scan failed; it is not
  treated as a pass or as scientific evidence. The sorted 32-name failure
  list has SHA-256
  aa3bafce92f854ff187965026231c88dd3913d490c610a32a942eee59b68f386.
- Science Forge planning import wrote 1553 nodes with zero invalid work items
  and zero malformed events in 5.86 s, peak 253400 KiB.
- The advisory Science Forge shadow rail inventoried 1616 certificates and
  1394 verifiers in 2.05 s, peak 343864 KiB. It again reported the known
  Forge-stdlib hash mismatch and E9118 bridge-audit failure, plus corpus
  drift from the 2026-07-19 baseline. The advisory wrapper exited zero, but
  the bridge audit remains a recorded failure and establishes no pass.

The generated certificate SHA-256 is
017b62de9583eb962665572848a6a3d779ea47b97cc7d9e71c63fdb92e57a926.
