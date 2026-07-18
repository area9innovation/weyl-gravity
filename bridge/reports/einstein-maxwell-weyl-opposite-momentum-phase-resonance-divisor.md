# Opposite-momentum phase resonance divisor

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The paired-momentum common-zero cone is not uniformly nonresonant.  If the
two input squared shell offsets are `A,B`, the target offset is `C`, and the
output spatial momentum is either `K=0` or `K=+/-2k`, squaring the resonance
condition gives a linear equation for `u=k^2`.  Thus each fixed harmonic
channel contributes at most one exact resonance radius, but the resulting
finite divisor is nonempty.

In fact, every `ell>=2` has the relative-phase-sensitive family

```text
Einstein-minus(ell,+k) + Einstein-minus(ell,-k)
  -> extra(L=2ell,K=0)
```

at

```text
k^2=sqrt(2ell(ell+1))-ell/2-1/6 > 0.
```

The exact shell identity is

```text
4*(k^2+ell(ell+1)-sqrt(2ell(ell+1)))
  =2ell(2ell+1)-2/3.
```

The top Gaunt coefficient is nonzero, including on the rank-one `m=0`
standing-wave face, so angular selection does not remove the channel.  Any
nonzero bilinear source projection is proportional to the product of the
`+k` and `-k` amplitudes and therefore retains their relative phase.  This
certificate does not claim that the dynamical projection is nonzero.

This forces a correction-space distinction.  Moment-map cancellation alone
does not prove a bounded or finite-quasiperiodic correction on the resonance
divisor.  It does suffice for the constraint-adjoint obstruction, while a
nonzero-frequency resonant source is removable in the smooth-global class by
an exponential-polynomial secular inverse.  The fiberwise Smith factors
reduce this statement to the elementary scalar resonant-forcing lemma.

The remaining smooth-global gate is the static, phase-sensitive
`L=0,K=2k` target block.  It is kept open rather than inferred from the
generic harmonic operator.

## Verification receipt

Date: 2026-07-18.  Tier 0 scoped compilation, JSON, and diff checks passed
in `0.05 s`; Tier 1 producer replay, independent verifier, and four tests
passed in `1.1 s`.  Tier 2 imports the five unchanged operator/cone inputs by
content hash.  Tier 3 was not run because the static exceptional block and
bounded resonant source projection remain open.
