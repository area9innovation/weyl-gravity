# Dynamical-emitter recoil order and input gate

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

For a record produced from free emitter data, the leading Maxwell signal is
order `g`.  Because the coupled linear operator is bipartite between `A` and
the `K_b`, an emitter-to-Maxwell block contains an odd number of couplings.
There is therefore no absolute `g^2` detector term.  The first recoil path is

```text
K_b^(0) -> A^(1) -> K_c^(2) -> A^(3) -> Q_a,
```

with exact operator

```text
Delta M_ab^(3) = sum_c Q_a[
  d G_A,ret g_c delta h_c G_Ec,ret g_c h_c d
  G_A,ret g_b delta(h_b K_b^(0))
].
```

Thus it is absolute order `g_b g_c^2`, or relative order `g_c^2` compared
with the leading column.  A two-emitter exact fixture verifies both inverse
orders through `g^3`, detects a spurious quadratic term, and detects deletion
of the cubic feedback.

The operator is now fixed, but its detector coefficient is not evaluable from
the existing artifacts.  The rank theorem exports an existence-level
first-nonzero-basis selection and nonzero leading values, not serialized
compact Cauchy profiles, exact switch functions, or evaluated Berger massive
Green images.  Equal leading response does not fix the recoil functional.
Those profiles and kernel evaluations are the next required handoff.  Leading
rank two remains certified: the determinant over the relative-recoil formal
ring has nonzero constant term `kappa_0 kappa_1`, independently of every
unevaluated recoil entry.  Emitter stress, finite-parameter Green theory,
the full Dirac algebra, and quantum claims remain open.
