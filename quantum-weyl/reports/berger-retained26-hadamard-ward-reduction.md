# Berger retained-26 Hadamard Ward reduction

Result: `BERGER_RETAINED26_HADAMARD_WARD_REDUCTION`

Dependency tag: `LORENTZIAN-CAUSAL`.

The twenty metric/formal-adjoint rows and six ghost/identity rows now all
have global exact Hadamard carriers. Let their degreewise direct sum be
\(H_{26}^{+}\), and let \(W_{26}\) be the certified cyclic backward witness:

\[
P_{26}=q_{26}W_{26}+W_{26}q_{26}.
\]

The natural retained candidate is

\[
\Omega_{26}^{+}=W_{26}H_{26}^{+}.
\]

Cyclicity and the degreewise exact Pauli--Jordan normalizations give the
full exact graded CCR. The Ward calculation is

\[
\begin{aligned}
\delta_q\Omega_{26}^{+}
&=q_{26}W_{26}H_{26}^{+}
 +W_{26}H_{26}^{+}q_{26}\\
&=P_{26}H_{26}^{+}
 +W_{26}(H_{26}^{+}q_{26}-q_{26}H_{26}^{+})\\
&=W_{26}[H_{26}^{+},q_{26}].
\end{aligned}
\]

The local Hadamard singular parts intertwine the differential, so
\([H_{26}^{+},q_{26}]\) is smooth. This is the entire remaining Ward defect.

The current causal homotopies satisfy

\[
q_{26}\Lambda_{26}^{\pm}+\Lambda_{26}^{\pm}q_{26}=1
\]

on compactly supported smooth sources. That statement cannot automatically
be applied to an arbitrary smooth two-variable kernel. The missing analytic
carrier is therefore precise: either select the global Feynman/Hadamard
bisolutions \(q_{26}\)-equivariantly, or export a continuous homotopy on a
declared past/future-compact or time-slice smooth bikernel class and construct
\(S_{26}\) with

\[
\delta_qS_{26}=-W_{26}[H_{26}^{+},q_{26}].
\]

Until that support-class step is supplied, the exact-CCR object remains a
candidate and no retained-26 BRST Hadamard flag is promoted.
