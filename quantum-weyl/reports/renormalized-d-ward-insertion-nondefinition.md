# Complete renormalized \(D\)-Ward insertion: first analytic non-definition

## Result

The classical input is no longer the blocker. On the same unit vacuum
cylinder and the same formal \(\tau\)-adic Wess--Zumino complex, the imported
classical certificate now supplies

\[
Q_0,\quad \iota_{D,0},\quad \mathcal L_{D,0},\quad
\iota,\quad\pi,\quad S,\quad\Omega
\]

with exact SDR, Cartan, cyclicity and equivariance identities for raw
\(D_{\rm compact}=\partial_t\).

We also declare an explicit finite reference convention at a symbolic positive
scale \(\mu_\star\):

\[
z_C(\mu_\star)=0,\qquad z_{\widehat R^2}(\mu_\star)=0.
\]

This is a scheme choice, not a canonical physical normalization. Exact
variation by \((\alpha_C,\alpha_R)\) has bulk response matrix

\[
\begin{pmatrix}1&0\\0&9\end{pmatrix}
\]

on the certified TT/conformal fixtures, so the two finite directions remain
independent.

## First undefined same-background operator

After those two closures, the first missing analytic operator on the
Lorentzian vacuum-cylinder route is

\[
T^{\rm ren}_2:
\mathcal F_{\rm loc}(E_{\rm ext})^{\otimes2}
\longrightarrow
\mathcal F_{\mu c}(E_{\rm ext})[[\hbar]].
\]

Off the total diagonal, the time-ordered contraction is fixed only after
choosing a full \(\tau\)-adic BV Feynman/Hadamard kernel. The repository has
neither that full BRST-compatible kernel nor an extension of the resulting
graded contraction distributions from

\[
M^2\setminus{\rm Diag}_2
\]

across \({\rm Diag}_2\) satisfying local covariance, causal factorization,
scaling-degree bounds, cyclicity and the \(Q_0\) Ward identity. The associated
coincident renormalized BV contraction \(\Delta_{\rm ren}\) is therefore also
undefined.

This names a distribution extension and its domain; it is not merely a
readiness label and not a claim that no such extension can exist.

The next analytic producer request is filed append-only as
`FULL_TAU_ADIC_BV_HADAMARD_FEYNMAN_KERNEL_AND_RENORMALIZED_T2_EXTENSION_ON_VACUUM_CYLINDER`.

## Euclidean branch

The coefficient route supplies a conditional Paneitz/Riegert anomaly-induced
representative and a selected \(C\log\Delta_C C\) carrier. It still requires a
self-adjoint boundary domain, kernel projector and source-compatibility policy,
and it does not supply the Weyl-invariant nonlocal remainder, independent
nonlocal \(\widehat R^2\) form factor, or independent cubic and higher Weyl
form factors. No certified map turns these Euclidean functionals into the
same-background Lorentzian Ward operator.

## Consequence for the Cartan gate

The target remains

\[
\mathcal A_D^{(1)}
=[Q_0,\iota_{D,1}]
+[Q_1,\iota_{D,0}]
-\mathcal L_{D,1}.
\]

Because complete \(Q_1\), \(\iota_{D,1}\), \(\mathcal L_{D,1}\), and the
local-insertion-to-Cartan map are not defined on one common admissible
observable complex, \(\mathcal A_D^{(1)}\) remains
`UNDEFINED_ANALYTICALLY`. It is not classified as zero, exact, or nontrivial,
and residual transfer remains forbidden.

## Claim boundary

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

This result imports the same-background classical contraction, fixes a
declared non-canonical finite reference scheme, and isolates the first missing
Lorentzian distribution extension. It does not construct a Lorentzian
time-ordered product, BV Laplacian, QME, Hadamard state, positivity, particle
space, scattering theory, or unitarity theorem.

## Reproduction

```bash
PYTHONPATH=quantum-weyl python3 -m cartan.renormalized_d_ward_insertion_nondefinition_certificate --check
PYTHONPATH=quantum-weyl python3 -m cartan.verify_renormalized_d_ward_insertion_nondefinition
PYTHONPATH=quantum-weyl python3 -m unittest \
  quantum-weyl/cartan/tests/test_renormalized_d_ward_insertion_nondefinition.py -v
```

CLOSE-OUT: DONE — the fallback stop condition is met by a precise
non-definition theorem naming the first missing distribution extension and
operator domain after importing the classical contraction and declaring finite
normalization conditions.

EVIDENCE:
quantum-weyl/cartan/certificates/RENORMALIZED_D_WARD_INSERTION_NONDEFINITION.json
