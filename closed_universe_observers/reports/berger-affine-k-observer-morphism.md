# Berger affine-K observer morphism

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`.

The full `q4` is neither needed nor claimed.  Differentiating the manifest
simultaneous `K` invariance of the covariant 84-row apparatus action fixes the
single contraction required by affine arity three:

```text
q4(K0,x,y,z)=K1 q3(x,y,z)
 -q3(K1x,y,z)-q3(x,K1y,z)-q3(x,y,K1z).
```

An independent rotation-invariant polynomial action with a genuine fifth
derivative verifies this identity exactly; deleting the contraction gives a
nonzero defect.  This selects the required slice among the arbitrary `q4`
completions identified by the predecessor gate while leaving `q4` on a
complement of `K0` open.

The observer evaluation is the covariant chain

```text
external q-closed J -> d G_ret J -> (lim_future m_0, lim_future m_1).
```

It intertwines simultaneous `K` action on the source and apparatus family.
The final memories are constant after detector support, and the detector
coupling depends on `F=dA`; therefore the records are respectively
`K`-covariant and Maxwell-gauge invariant.  Their formal response determinant
has nonzero constant term `C_00 C_11`, so the coefficientwise morphism has
rank two through arity three.  An independent exact periodic specialization
simultaneously translates both detector profiles and fields, obtains two zero
`K`-variation defects, and retains a nonzero diagonal determinant.

This is a family-level affine result.  It is not linear `K` descent at one
fixed apparatus background, a full `q4`, finite-parameter Green
hyperbolicity, localized emitter recoil, or a quantum observer algebra.
