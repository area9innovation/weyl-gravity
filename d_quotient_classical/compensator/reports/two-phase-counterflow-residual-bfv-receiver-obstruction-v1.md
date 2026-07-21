# Two-phase counterflow residual BFV receiver obstruction

## Result

The selected Berger counterflow background has the exact infinitesimal
stabilizer

\[
\mathfrak g_{\rm stab}=\mathfrak{su}(2)_L\oplus\mathfrak u(1)_{R_3}
\oplus\mathbb R_K,
\qquad \dim\mathfrak g_{\rm stab}=5.
\]

The generated Chevalley--Eilenberg differential has zero Jacobi defects.  The
diagonal internal U(1) has no constant reducibility: its constant ghost moves
the Stueckelberg scalar and the whole sector is an exact contractible pair.

This abstract algebra cannot yet be promoted to the requested residual BFV
receiver.  The pinned 70-row causal parent exports exact unary, pairing and
causal Green data and the K/R_rel/D/U1 Cartan ledger, but it does not serialize
the four spatial actions (L_1,L_2,L_3,R_3) on its ordered rows or their
Hamiltonian moment maps.  Consequently the first undefined carrier identity is

\[
[L_{L_1},L_{L_2}]=L_{L_3}
\]

on the actual 70-row complex.  Without those matrices one cannot form or
verify the matter-representation and equivariant-moment-map terms of
(Q_BFV), the five-generator Taub ideal, the full causal Cartan contraction, or
the bulk-to-time-slice chain map.

The charge-clock complementarity theorem also prevents hiding this gap by
switching charge sectors: the fixed-charge branch has no clock, whereas the
unrestricted branch retains a physical clock but has an exact secular
zero-frequency Jordan chain.  The receiver must therefore be charge-typed.

## Round-cylinder comparison

The preserved spatial generators are explicitly

\[
L_1=(R_{01}+R_{23})/2,\quad L_2=(R_{02}-R_{13})/2,
\]

\[
L_3=(R_{03}+R_{12})/2,\quad R_3=(R_{03}-R_{12})/2,
\]

and the helical generator is the internal lift
(K=D_{old}-\Omega R_{rel}).  The remaining two right rotations and eight
proper-conformal generators are broken.  This is a subalgebra, not a quotient:

\[
[K^+_0,K^-_0]=2D_{old}
\]

shows that the broken complement is not an ideal.

## Exact next export

The minimal missing carrier is

```text
BERGER_COUNTERFLOW_70_ROW_SPATIAL_STABILIZER_LIFT_AND_MOMENT_MAPS
```

It must contain the four rowwise spatial actions, their brackets with Q70 and
cyclic adjoints, the four quadratic Hamiltonian matrices, fixed-leaf tangency,
causal Cartan homotopies and the bulk-to-time-slice transgression.

This result is `LOCAL-ALGEBRAIC` with the unary parent imported as
`LORENTZIAN-CAUSAL`.  It certifies no full residual receiver, residual
cohomology, descended pairing, anomaly restriction, observer class, Hadamard
state, QME, particle or asymptotic statement.

## Evidence

- `d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_RESIDUAL_BFV_RECEIVER_OBSTRUCTION_V1.json`
- `d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_RESIDUAL_BFV_RECEIVER_OBSTRUCTION_PAYLOAD_V1.json`
- `d_quotient_classical/compensator/verify_two_phase_counterflow_residual_bfv_receiver_obstruction.py`
- `residual_atlas/two-phase-counterflow-residual-bfv-receiver-obstruction-fragment-v1.json`

CLOSE-OUT: DONE — the complete stop condition is met
EVIDENCE: TWO_PHASE_COUNTERFLOW_RESIDUAL_BFV_RECEIVER_OBSTRUCTION_V1_TIER_RECEIPT
