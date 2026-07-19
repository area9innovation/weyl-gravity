# Berger recoil switch interval provider

`BERGER_RECOIL_SWITCH_INTERVAL_PROVIDER` exposes the certified normalized
switches (h_0,h_1) and their physical-time derivatives as outward rational
intervals on any rational time cell.  It imports the exact supports and
clock/physical radii together with the directed enclosure of
(C_B=\int_{-1}^1B(s)ds).

The value bound uses monotonicity of (B(|s|)).  The derivative magnitude is
unimodal, with its unique positive critical point fixed by
(1-3s^4=0); a rational bracket encloses that point.  Switch centers have
zero derivative, full supports include both derivative signs, and cells
disjoint from support return structural zero.

This binds the switch factor only.  Finite kernel convolution, typed form
contraction, and harmonic emitter Cauchy coefficients remain open, so no
`I_abc` or recoil value follows.
