# Digest: Bateman & Turok, "Escape from Ostrogradsky via Hidden Ghost Parity"

**arXiv:2607.00096v1 [hep-th], 30 Jun 2026.** Sam Bateman (Higgs Centre, Edinburgh), Neil Turok (Higgs Centre + Perimeter). 6-page Letter. Companion long paper: [17] Bateman & Turok, *Unitarity and Positivity in Higher Derivative QFTs from Hidden Ghost Parity* (2026), **to appear** — several key proofs (notably the decomposition Eq. (19)) are deferred to it. Related: [23] Anderson, Bateman, Herzog, Turok, *Renormalization of a Four-Derivative Theory* (to appear); [25] same authors, *Conformally Flat Limit of Quadratic Gravity* (to appear).

Source of this digest: full arXiv LaTeX source (`main.tex`) of v1; all equations below are verbatim, with the equation numbers as they appear in the published PDF (revtex sequential numbering (1)–(21), appendix numbering (A1)–(A2), (B1)–(B5), (C1)–(C6)).

**Conventions** (their footnote 4): they follow Bogolubov–Logunov–Oksak–Todorov, *General Principles of Quantum Field Theory* [24]. Tildes denote Fourier transforms, momentum measure $d_n p \equiv d^n p/(2\pi)^n$, delta functions normalized $\delta_n(p) \equiv (2\pi)^n \delta^n(p)$. Metric signature is not stated explicitly, but the pole structure (Feynman propagator $-i/(p^2+i\epsilon)^2$ with double poles at $p^0 = \pm(|\mathbf{p}| - i\epsilon)$) and the support $\theta(x^2)$ of the commutator function (timelike $x^2>0$) fix mostly-minus, $(+,-,-,-)$, consistent with ref. [24].

---

## 0. What the paper claims (one paragraph)

A four-derivative "perfect square" (PS) scalar QFT, $\mathcal{S}_\phi = -\tfrac12\int d^4x\,(\square\phi + \lambda(\partial\phi)^2)^2$, quantized covariantly on a **Krein space** with the spectral condition (all particle states $p^0>0$), has: (a) perturbative causality + unitarity (optical theorem) **to all orders** given the spectral property and Hermitian interaction Lagrangian; (b) **positive transition probabilities at tree level**, proven via a generalized Born rule $\mathrm{Prob}(A) = \mathrm{tr}(A^\dagger A)$ and a hidden discrete "ghost parity" symmetry that becomes manifest when the PS theory is embedded (by a nonlinear field redefinition + auxiliary field) into a two-derivative, two-field $O(1,1)$ model. The embedding is implemented quantum-mechanically by an operator-algebra homomorphism $R$ (asymptotically $R_{\pm\infty}$), under which every physical projection maps to a "weakly ghost symmetric" operator $B + C$ with $B$ ghost-even and $C$ purely negatively charged, null, and traceless against $B$.

---

## 1. The two-field O(1,1) action and the map to the fourth-order scalar

### The fourth-order (perfect square, PS) theory

Eq. (2) (`eq:PStheory`), Lorentzian action:

$$\mathcal{S}_\phi = -\frac{1}{2}\int d^4x \left(\square \phi + \lambda (\partial \phi)^2\right)^2 \tag{2}$$

- Single asymptotically free coupling $\lambda$; $\phi$ is dimension-zero, massless; free field equation $\square^2\phi = 0$.
- Special case of Holdom's shift-invariant renormalizable four-derivative theories [21,22]; Holdom found the tree 2→2 cross section positive, this paper explains/generalizes that.
- PS theory has a **positive Euclidean action** (hence a nonperturbative lattice formulation); the two-field model below does **not**.

### Intermediate step (Ω form)

Define $\Omega \equiv \lambda^{-1} e^{\lambda\phi}$; then

$$\mathcal{S}_\Omega \equiv -\frac{1}{2\lambda^2}\int d^4x \left(\square\Omega/\Omega\right)^2 \quad \text{(unnumbered, Sec. IV)}$$

### The two-field O(1,1) model

Eq. (14) (`eq:UVaction`), introducing $\Upsilon$ to render the Lagrangian polynomial:

$$\mathcal{S}_{1,1} = \int d^4x \left(\partial\Omega\, \partial\Upsilon + \frac12 \lambda^2\, \Omega^2 \Upsilon^2\right) \tag{14}$$

with path-integral measure $\mathcal{D}\Omega\,\mathcal{D}\Upsilon$. Notes on signs/normalization:

- Kinetic term is the off-diagonal $\partial\Omega\,\partial\Upsilon$ — **indefinite**. In the diagonal basis $(\Omega,\Upsilon) = (\mathcal{T}+\mathcal{X},\, \mathcal{T}-\mathcal{X})$, $\mathcal{T}$ has a positive kinetic term, $\mathcal{X}$ a negative one; $\mathcal{X}$ is the ghost.
- The potential term enters with **the wrong sign** ("its kinetic term is indefinite and its potential has the wrong sign"): with mostly-minus conventions the interaction is a **negative quartic**. They state the perturbative expansion "exactly matches a *complex* two-derivative scalar field $\varphi$, with a *negative* quartic potential $-\frac12\lambda^2(\varphi^*\varphi)^2$, long-known to be asymptotically free" (Symanzik [26]; recent: Romatschke [27]).

### The map back (nonlinear field redefinition)

Integrating the kinetic term by parts and doing the **purely algebraic Gaussian path integral over $\Upsilon$** gives

$$\Upsilon = \frac{\square\,\Omega}{(\lambda\Omega)^2} = \lambda^{-1} e^{-2\lambda\phi}\, \square\, e^{\lambda\phi} \quad \text{(unnumbered, Sec. IV)}$$

and recovers $\mathcal{S}_\phi$ with functional measure $\mathcal{D}\Omega/\Omega \propto \mathcal{D}\phi$. So the classical dictionary is:

| PS variable | O(1,1) variable |
|---|---|
| $\phi$ | $\Omega = \lambda^{-1} e^{\lambda\phi}$ |
| $\lambda^{-1} e^{-2\lambda\phi}\,\square e^{\lambda\phi}$ (on the $\Upsilon$ saddle) | $\Upsilon$ |

**Crucial domain mismatch** (their words, Sec. IV): "the $\phi$ and $\Omega,\Upsilon$ path integrals are **inequivalent**. The former integrates over $\Omega > 0$ whereas the latter integrates over all $\Omega$." See §6 below.

---

## 2. Symmetries: SO⁺(1,1) boost, exchange, "ghost parity" vs "charge conjugation"

Sec. IV ("Classical ghost symmetry"). The action (14) has global symmetry

$$O(1,1) \cong SO^+(1,1) \rtimes K_4, \qquad K_4 = \mathbb{Z}_2\times\mathbb{Z}_2 \text{ (Klein group)}.$$

- **Continuous part** $SO^+(1,1)$: the scale transformation $(\Omega,\Upsilon) \mapsto (e^\sigma \Omega,\, e^{-\sigma}\Upsilon)$, "under which $\Omega$ and $\Upsilon$ are respectively **positively and negatively charged**. This corresponds to the **shift symmetry** of (2)" [i.e., $\phi \to \phi + \sigma/\lambda$].
- **Noether charge**: the paper never writes the Noether charge explicitly. The charge grading is instead specified at the operator level in Appendix C: $b_\Omega(\mathbf{p})$ **and** $b_\Omega^\dagger(\mathbf{p})$ carry positive charge; $b_\Upsilon(\mathbf{p})$ **and** $b_\Upsilon^\dagger(\mathbf{p})$ carry negative charge. (Note this is a boost-weight grading, not a particle/antiparticle U(1): creation and annihilation operators of the same field carry the **same** charge.)
- **Discrete exchange**: "One of the discrete $\mathbb{Z}_2$ subgroups is **charge conjugation** $(\Omega,\Upsilon)\mapsto(\Upsilon,\Omega)$ **which is ghost parity**." In the diagonal basis, "The symmetry $\kappa: \mathcal{X} \leftrightarrow -\mathcal{X}$, i.e., $\Omega\leftrightarrow\Upsilon$, is ghost parity." So in this paper *charge conjugation of the O(1,1) boost charge* and *ghost parity* are the same $\mathbb{Z}_2$; the name "ghost parity" is introduced earlier (Sec. I, Eq. (1) context) as physics terminology adopted from Holdom [19] for the Krein fundamental symmetry $\kappa$, and Sec. IV identifies the field-theoretic realization. (The other $\mathbb{Z}_2$ in $K_4$ is not spelled out; presumably $(\Omega,\Upsilon)\to(-\Omega,-\Upsilon)$.)
- **Ghost parity in $\phi$ variables** — the "hidden" symmetry, Eq. (15) (`eq:HGP`):

$$\phi \mapsto -\phi + \frac{1}{\lambda}\ln\left(\square\phi + \lambda(\partial\phi)^2\right) \tag{15}$$

"which can be shown to be an involution **using the field equation for $\phi$**. As one can easily check, (15) is an **on-shell symmetry** of $\mathcal{S}_\phi$." (So in the PS variables ghost parity is nonlinear, nonlocal-looking, and only on-shell; it is exact and linear only in the $(\Omega,\Upsilon)$ variables.)

---

## 3. The quantum embedding: R, R_t, Hamiltonians, S-matrices

Sec. V ("Quantum Ghost Symmetry") + Appendix C.

### The homomorphism R

"The classical embedding just explained induces a quantum embedding. Namely, an **operator algebra homomorphism** that acts on local fields as" Eq. (16):

$$R^\dagger \Omega R = \frac{1}{\lambda} e^{\lambda\phi}, \qquad R^\dagger \Upsilon R = \frac{1}{\lambda} e^{-2\lambda\phi}\,\square\, e^{\lambda\phi} \tag{16}$$

So conjugation by $R$ pulls $O(1,1)$-model fields back to composite operators of the $\phi$ theory. As a state map, $R$ sends the $\phi$-theory Krein space into the $(\Omega,\Upsilon)$ Krein space (see the vacuum relation below: $R_t \Psi_0^{(\phi)} = e^{Q_t}\Psi_0^{(\Omega\Upsilon)}$). The paper gives no more formal domain/codomain characterization than this — no statement about ranges, dense domains, or invertibility beyond $R_t R_t^\dagger = \mathbf{1}$.

### Hamiltonian relation

Verbatim: "In fact, the full Hamiltonians of the two field theories are related: $R^\dagger H_{1,1} R = H_\phi$ **up to a spatial boundary term**." The boundary term is not written down or characterized further anywhere in the Letter (presumably in [17]).

### Time-translated homomorphism and asymptotic limits

$$R_t = e^{iH^0_{\Omega\Upsilon} t}\, R\, e^{-iH^0_\phi t} \quad \text{(unnumbered, after (17))}$$

"the $R$ homomorphism translated to the time $t$ using the **free** $\phi$ Hamiltonian on the right and the **free** $O(1,1)$ Hamiltonian on the left. This defines a **Bogoliubov transformation**, detailed in Appendix C, that maps the asymptotic states of the perfect square theory to those of the $O(1,1)$ model in the limits $t\to\pm\infty$." $R_{\pm\infty}$ are simply these $t\to\pm\infty$ limits; no independent construction of the limits (existence, topology of convergence) is given in the Letter.

### S-matrix relation

Eq. (17) (`eq:isom`):

$$S_\phi = R_\infty^\dagger\, S_{\Omega\Upsilon}\, R_{-\infty} \tag{17}$$

(follows "from the interaction picture"). Note dagger placement: dagger on $R_\infty$ only.

### Explicit Bogoliubov data (Appendix C)

Mode expansions, Eqs. (C1)–(C3):

$$\Omega(x) = \int \frac{d_3\mathbf{p}}{2|\mathbf{p}|}\left(e^{-ipx} b_\Omega(\mathbf{p}) + h.c.\right) \tag{C1}$$
$$\Upsilon(x) = \int \frac{d_3\mathbf{p}}{2|\mathbf{p}|}\left(e^{-ipx} b_\Upsilon(\mathbf{p}) + h.c.\right) \tag{C2}$$

with **nonzero commutators only cross-wise**: $[b_\Omega(\mathbf{p}), b_\Upsilon^\dagger(\mathbf{q})] = [b_\Upsilon(\mathbf{p}), b_\Omega^\dagger(\mathbf{q})] = 2|\mathbf{p}|\,\delta_3(\mathbf{p}-\mathbf{q})$. So each of the $b_\Omega$, $b_\Upsilon$ oscillators is **null** by itself; the inner product pairs $\Omega$-quanta with $\Upsilon$-quanta. Charge assignments: $b_\Omega, b_\Omega^\dagger$ positive; $b_\Upsilon, b_\Upsilon^\dagger$ negative.

$$\phi(x) = \int \frac{d_3\mathbf{p}}{(2|\mathbf{p}|)^3}\Big(e^{-ipx} a_1(\mathbf{p}) + e^{-ipx}\,(1 + 2i|\mathbf{p}|t)\, a_2(\mathbf{p}) + h.c.\Big) \tag{C3}$$

with nonzero commutators $[a_1(\mathbf{p}), a_2^\dagger(\mathbf{q})] = [a_2(\mathbf{p}), a_1^\dagger(\mathbf{q})] = (2|\mathbf{p}|)^3\,\delta_3(\mathbf{p}-\mathbf{q})$. The $(1+2i|\mathbf{p}|t)$ factor is the secular/"growing" dipole mode of the degenerate double pole (their footnote 3: growing modes "appear to violate time translation invariance. However ... these cancel out of scattering cross sections").

**Appendix C label consistency warning (repository calculation,
2026-08-10).**  Equation (31) as printed assigns the ordinary mode to $a_1$
and the growing mode to $a_2$, but this cannot imply the next two displayed
equations.  Direct symplectic extraction makes $\Box\phi$ select the growing
oscillator, so Eq. (32) requires that oscillator to be $a_1$; Eq. (33)
likewise requires ordinary $a_2$ and growing $a_1$.  Exchanging
$a_1\leftrightarrow a_2$ in Eq. (31) repairs both.  Because the commutator
algebra is symmetric under the exchange, the Letter alone does not decide
whether Eq. (31) or Eqs. (32)--(33) contain the typographical error.  The
exact certificate
`REVERSE_PHYSICS_BT_RT_JORDAN_KERNEL_V1` declares the repaired convention it
uses rather than silently choosing one.

With $\omega_t(f,g) = \int_{x^0=t} d^3\mathbf{x}\, f \overleftrightarrow{\partial_0} g$ (symplectic form on the slice $x^0 = t$) and $p = (|\mathbf{p}|, \mathbf{p})$, Eqs. (C4)–(C5):

$$R_t^\dagger\, b_\Upsilon(\mathbf{p})\, R_t = \omega_t\!\left(i e^{ipx},\, R^\dagger \Upsilon R\right) \simeq a_1(\mathbf{p}) \tag{C4}$$

$$R_t^\dagger\, b_\Omega(\mathbf{p})\, R_t = \omega_t\!\left(i e^{ipx},\, R^\dagger \Omega R\right) \simeq \frac{a_2(\mathbf{p}) + 2i|\mathbf{p}|t\, a_1(\mathbf{p}) + e^{2i|\mathbf{p}|t}\, a_1^\dagger(-\mathbf{p})}{4|\mathbf{p}|^2} \tag{C5}$$

where $\simeq$ means **equality up to $\mathcal{O}(\lambda)$** (i.e., these are free-theory / leading-order statements). "Thus $R_t$ is a Bogoliubov transformation and satisfies $R_t^{\phantom\dagger} R_t^\dagger = \mathbf{1}$." (Only $R_t R_t^\dagger = \mathbf{1}$ is asserted; $R_t^\dagger R_t$ is not discussed.)

Note the structure of (C5): $R_t^\dagger b_\Omega R_t$ contains the **creation** operator $a_1^\dagger(-\mathbf{p})$ with an oscillating phase $e^{2i|\mathbf{p}|t}$ and a **secularly growing** term $2i|\mathbf{p}|t\,a_1(\mathbf{p})$. This is why the $t\to\pm\infty$ limits are delicate and why only the charge-neutral parts of mapped operators are claimed to have well-defined limits (see §4).

### Vacuum relation

$$R_t\, \Psi_0^{(\phi)} = e^{Q_t}\, \Psi_0^{(\Omega\Upsilon)}, \qquad Q_t = \frac12 \int \frac{d_3\mathbf{p}}{(2|\mathbf{p}|)^3}\left(e^{2i|\mathbf{p}|t}\, b_\Upsilon^\dagger(\mathbf{p})\, b_\Upsilon^\dagger(-\mathbf{p}) - h.c.\right) \tag{C6}$$

$Q_t$ is "an anti-Hermitian, **negatively charged** squeezing operator. In a positive quantum field theory, the analogous squeezed states are orthogonal to the vacuum. However, in our case, since the $b_\Upsilon$ oscillator is null, $\langle \Psi_0^{(\Omega\Upsilon)}, R_t \Psi_0^{(\phi)}\rangle = 1$." (The squeezing is entirely in the null $b_\Upsilon$ directions — the deviation of $R_t\Psi_0^{(\phi)}$ from the O(1,1) vacuum is invisible to the inner product against neutral/positively-charged states.)

---

## 4. Krein-space QM: κ, generalized Born rule, weak ghost symmetry, B + C, positivity

### Krein space and κ (Sec. I)

Eq. (1) (`eq:Krein_decomp`): the Krein space admits an orthogonal decomposition

$$\mathcal{K} = \mathcal{K}_+ \oplus \mathcal{K}_-, \tag{1}$$

$\mathcal{K}_\pm$ positive/negative definite subspaces, and $\kappa\,\mathcal{K}_\pm = \pm\mathcal{K}_\pm$. "Adopting physics terminology [Holdom, ref 19], we shall call $\kappa$ **ghost parity**." $\kappa$ induces a norm topology via the positive-definite inner product $\langle\_|\kappa|\_\rangle$. "There is no preferred choice of ghost parity, however, all such norms are equivalent [20]." Key interpretive sentence: "probabilities are calculated using the **indefinite** inner product: $\kappa$ is merely a useful tool for proving their positivity."

Quantization data for the PS theory (Sec. I): covariant commutator Eq. (3) $[\phi(x),\phi(y)] = i\Delta(x-y)$ with

$$\Delta(x) = -\frac{1}{8\pi}\,\epsilon(x^0)\,\theta(x^2) \;\Leftrightarrow\; \tilde\Delta(p) = \epsilon(p^0)\,\delta_1'(p^2) \tag{4}$$

and spectral Wightman function (drop negative-$p^0$ part of $\tilde\Delta$):

$$\tilde W(p) = \theta(p^0)\,\delta_1'(p^2). \tag{5}$$

"The Wightman function defines the inner product on the space of states. Since the derivative of a delta function is indefinite, so is the inner product." The O(1,1) counterpart (Sec. V, after Eq. (20)): $W^{\Omega\Upsilon}(p) = W^{\Upsilon\Omega}(p) = \theta(p^0)\,\delta_1(p^2)$, $W^{\Omega\Omega} = W^{\Upsilon\Upsilon} = 0$.

### Generalized Born rule (Sec. II)

In an indefinite space with null states ($\langle\Psi|\Psi\rangle = 0$) the conventional Born rule fails (can't normalize). Provided the inner product is **non-degenerate**, define projection operators $P$ with $P^2 = P = P^\dagger$ and $\sum P = \mathbf{1}$. A physical process is an operator $A$ built from these; for scattering, $A = P_{out}\, S\, P_{in}$. Eq. (6) (`eq:BornRule`):

$$\mathrm{Prob}(A) = \mathrm{tr}\big(A^\dagger A\big) = \mathrm{tr}\big(S^\dagger P_{out}\, S\, P_{in}\big) \tag{6}$$

The usual Born rule is recovered for pure-state density matrices $P = |\Psi\rangle\langle\Psi| / \langle\Psi|\Psi\rangle$. Kolmogorov's axioms: (i) additivity from linearity of trace; (ii) conservation of probability from (pseudo)-unitarity $S^\dagger S = \mathbf{1}$ (which holds "if the interaction Lagrangian is (pseudo)-Hermitian", given the spectral condition) with $P_{out} = \mathbf{1}$ giving $\mathrm{Prob}(A) = \mathrm{Prob}(P_{in})$; (iii) positivity is the nontrivial one, below.

**Caveat (our reading, not stated explicitly in the Letter):** the paper never spells out what $\dagger$ and $\mathrm{tr}$ mean in Krein space. Everything is consistent only if $\dagger$ is the **Krein adjoint** (adjoint w.r.t. the indefinite inner product) and $\mathrm{tr}$ the trace built from the indefinite pairing (dual bases w.r.t. $\langle\cdot|\cdot\rangle$). This is what makes $\mathrm{tr}(C^\dagger C) = 0$ possible for $C \neq 0$ and what makes the positivity argument (next) nontrivial. Under the positive product $\langle\_|\kappa|\_\rangle$ the adjoint is $\kappa A^\dagger \kappa$ and the trace is $\mathrm{tr}(\kappa \cdot \kappa\,\cdot)$-related, which is exactly how Eq. (8) becomes manifestly positive.

### Ghost symmetry and the positivity mechanism (Sec. II)

- **Ghost symmetric**: $B = \kappa B \kappa$. "This implies that $\mathrm{Prob}(B) = \mathrm{tr}(B^\dagger \kappa B \kappa)$, which is positive since it is equivalent to a trace computed with respect to the positive definite inner product $\langle\_|\kappa|\_\rangle$." [Mechanism: for ghost-symmetric $B$, $\mathrm{tr}(B^\dagger B) = \mathrm{tr}(B^\dagger \kappa B\kappa)$, and $\kappa B^\dagger \kappa$ is the $\kappa$-adjoint $B^{\ddagger}$, so this is $\mathrm{tr}_{\kappa}(B^{\ddagger} B) \geq 0$ — a Hilbert–Schmidt norm in the auxiliary Hilbert space.]
- **Weakly ghost symmetric**, Eq. (7) (`eq:weak_decomposition`): $A$ is weakly ghost symmetric if

$$A = B + C \tag{7}$$

"with $B$ ghost symmetric and $C$ **null and orthogonal to $B$**, meaning $\mathrm{tr}(C^\dagger C) = 0 = \mathrm{tr}(B^\dagger C)$." Then Eq. (8):

$$\mathrm{Prob}(A) = \mathrm{tr}\big(B^\dagger \kappa B \kappa\big) \geq 0 \tag{8}$$

"a sufficient condition for an indefinite QFT to admit a probabilistic interpretation. We claim that the perfect square theory (2) is just such a QFT."

### How the PS theory achieves weak ghost symmetry (Sec. V) — the B + C decomposition

General $n$-particle projection in the $\phi$ theory, Eq. (18):

$$P_\chi^{(\phi)} = \frac{1}{n!}\int (d_4 p)^n\, \chi(p)\, \tilde W(p)\, \big|\tilde\Psi(p)\big\rangle \big\langle \tilde\Psi(p)\big| \tag{18}$$

($p = (p_1,\dots,p_n)$; $\tilde W(p)$ here is the product of single-particle Wightman factors; $\chi$ a characteristic function, $\chi^2 = \chi$). Since $m$- and $n$-particle projections are orthogonal for $m \neq n$, it suffices to treat $A = P_{out}(S-1)P_{in}$ with $\chi_{in}, \chi_{out}$ supported in fixed particle-number subspaces.

**Key decomposition**, Eq. (19) (`eq:P_f_decomposition`) — stated with proof deferred: "We find that [17]"

$$R_t\, P_\chi^{(\phi)}\, R_t^\dagger = P_\chi^{(\Omega\Upsilon)} + Q_\chi^{(\Omega\Upsilon)} \tag{19}$$

"where $P_\chi^{(\Omega\Upsilon)}$ is a **charge neutral** operator while $Q_\chi^{(\Omega\Upsilon)}$ contains **only negatively charged** operators. The charge neutral term has no dependence on $t$ and so is well defined in the limits $t\to\pm\infty$." For $n=1$, Eq. (20):

$$P_\chi^{(\Omega\Upsilon)} = \int d_4 p\, \chi(p)\, \tilde W^{ij}(p)\, \big|\tilde\Psi_i(p)\big\rangle \big\langle \tilde\Psi_j(p)\big|, \qquad i,j \in \{\Omega,\Upsilon\} \tag{20}$$

with $W^{\Omega\Upsilon} = W^{\Upsilon\Omega} = \theta(p^0)\delta_1(p^2)$, $W^{\Omega\Omega} = W^{\Upsilon\Upsilon} = 0$. "$P_\chi^{(\Omega\Upsilon)}$ is covariant and, most important, it is **even under ghost parity**." [Even because $\Omega \leftrightarrow \Upsilon$ swaps $i \leftrightarrow j$ and the off-diagonal Wightman matrix is symmetric.]

**Nullity argument (verbatim logic):** "Since the $R_t$ homomorphism **does not yield any positively charged operators**, the negatively charged operators in $Q_\chi^{(\Omega\Upsilon)}$ cannot contribute to the trace, that is, $Q_\chi^{(\Omega\Upsilon)}$ is null and orthogonal to $P_\chi^{(\Omega\Upsilon)}$." [The trace pairs charge $+q$ with charge $-q$; if the whole image of $R_t\,\cdot\,R_t^\dagger$ contains only charge $\leq 0$ pieces, no positively-charged partner exists to pair against $Q$'s negative charge, so every trace involving $Q$ vanishes. This is the *entire* mechanism by which $C$ decouples: it is an $SO^+(1,1)$ charge selection rule, not a dynamical cancellation.]

Hence a general scattering process decomposes as Eq. (21) (`eq:A_decomposition`):

$$R_\infty\, A^{(\phi)}\, R_{-\infty}^\dagger = B^{(\Omega\Upsilon)} + C^{(\Omega\Upsilon)} \tag{21}$$

"where $B^{(\Omega\Upsilon)}$ is ghost symmetric and $C^{(\Omega\Upsilon)}$ is orthogonal and null. Since $R_t^{\phantom\dagger} R_t^\dagger = \mathbf{1}$, the generalized Born rule yields $\mathrm{Prob}(A^{(\phi)}) > 0$ and so leads to consistent transition probabilities." [Chain: $\mathrm{Prob}(A^{(\phi)}) = \mathrm{tr}(A^{(\phi)\dagger} A^{(\phi)})$; insert $R^\dagger R$-type identities using $R_t R_t^\dagger = \mathbf{1}$ to rewrite as the trace of the mapped operator; then (7)–(8) with $B = B^{(\Omega\Upsilon)}$.]

Dagger placement summary (load-bearing for the planned calculation):
- (17): $S_\phi = R_\infty^\dagger S_{\Omega\Upsilon} R_{-\infty}$ (pull O(1,1) S-matrix back to $\phi$).
- (19): $R_t P^{(\phi)} R_t^\dagger = \dots$ (push $\phi$ projections forward to O(1,1)).
- (21): $R_\infty A^{(\phi)} R_{-\infty}^\dagger = B + C$ (push forward; different $R$'s on the two sides because $A$ straddles in/out).

---

## 5. Optical theorem / pseudo-unitarity: exactly what is claimed proven

- **Causality + unitarity (optical theorem): all orders, conditional.** "Provided the interaction Lagrangian is Hermitian, the **spectral property is sufficient to ensure perturbative causality and unitarity in the form of the optical theorem** [16 = 't Hooft–Veltman, Diagrammar] (see also [17])." Abstract: "using covariant methods which ensure perturbative causality and unitarity (in the form of the optical theorem) **to all orders**." So: all-orders, but resting on the Diagrammar-style largest-time-equation argument given the spectral condition; details in the companion paper [17].
- **Pseudo-unitarity**: $S^\dagger S = \mathbf{1}$ "if the interaction Lagrangian is (pseudo)-Hermitian" (Sec. II) — used for conservation of probability. In Krein language the theory is "pseudo-unitary, not unitary" (Sec. I).
- **Positivity of transition probabilities: tree level only.** Abstract: "prove that **all tree level** transition probabilities are positive." Conclusions: "providing a general proof of the positivity of transition probabilities **at tree level**. The main obstacle to extending the proof to higher orders is that, like QCD, the massless theory has **collinear infrared divergences which affect asymptotic states**. These need to be carefully regulated and resummed." Supporting result: with Anderson & Herzog they "have proven that PS theory is free of **IR loop divergences**" [23]; via the optical theorem "this suggests that IR divergences due to massless external states can be consistently resummed" (suggestive, not proven).
- The Bogoliubov relations (C4)–(C5) are explicitly leading order ($\simeq$ = up to $\mathcal{O}(\lambda)$); the Eq. (19) decomposition is asserted with proof in [17].
- **Cross-section check** (Sec. III, App. B): the generalized Born rule reproduces Holdom's tree 2→2 result. Off-shell amplitude defined by Eq. (9): $\langle\tilde\Psi(q_1,q_2)|S-1|\tilde\Psi(p_1,p_2)\rangle = \delta_4(q_1{+}q_2{-}p_1{-}p_2)\mathcal{M}$; duality $\langle\tilde\Psi(p)|\tilde\Psi(q)\rangle \tilde W(q) = \delta_4(p-q)$; covariant projector Eq. (10); Born-rule trace Eq. (11); relation to cross section Eq. (12): $\mathrm{tr}(A^\dagger A) = \frac{1}{\mathrm{Area}}\int_{S^2} d\Omega \frac{d\sigma}{d\Omega}$; and Eq. (13):

$$\frac{d\sigma}{d\Omega} = \frac{\partial^4}{\partial m_1^2\,\partial m_2^2\,\partial m_3^2\,\partial m_4^2}\left.\left(\frac{|\mathbf{p}_1|\,|\mathcal{M}|^2}{(16\pi)^2 |\mathbf{q}_1|\, s}\right)\right|_{m^2=0} = \frac{3\lambda^4}{32\pi^2 s} \tag{13}$$

using $\delta'(p^2) = -(\partial/\partial m^2)\delta(p^2 - m^2)|_{m^2=0}$ with **independent masses per external leg**. Their flagged novelty: "our construction does not put the amplitude $\mathcal{M}$ on-shell, but rather the squared amplitude $|\mathcal{M}|^2$ which is differentiated before being put on-shell... **only on-shell probabilities, not amplitudes, are physically meaningful**." Feynman rules (App. B): cubic vertex $-2i\lambda(p_1^2\, p_2\!\cdot\!p_3 + \mathrm{perm.})$ (B1), quartic vertex $-4i\lambda^2(p_1\!\cdot\!p_2\; p_3\!\cdot\!p_4 + \mathrm{perm.})$ (B2); tree $\mathcal{M}$ = contact + s + t + u exchange (B3); characteristic distribution $\chi(p^\mu) \simeq \delta_1(p^\mu)/L^\mu$ (B4), CoM-frame product (B5); the $\delta_4(0) = L^0L^1L^2L^3$ spacetime volume in (11) cancels against $\chi$'s denominators leaving the transverse Area of (12).

### Repository extension beyond the Letter (2026-08-10)

The loop-completion stream has now crossed two partial gates, without changing
the tree-only positivity boundary above:

1. `REVERSE_PHYSICS_BT_PERFECT_SQUARE_RG_SEPARATRIX_V1`
   (`LOCAL-ALGEBRAIC`, `COEFFICIENT_COMPUTED`) proves from Holdom's published
   beta functions that the PS coupling relation is one-loop RG invariant and
   asymptotically free.  This establishes ultraviolet closure of the special
   action, not an inclusive probability.
2. `REVERSE_PHYSICS_BT_FOUR_POINT_BUBBLE_LOG_JET_V1` and
   `REVERSE_PHYSICS_BT_TRIANGLE_BOX_LOG_JET_V1` (`REDUCED-MODE`,
   `COEFFICIENT_COMPUTED`) compute the complete cut-constructible logarithmic
   four-mass one-loop topology jet.  The separate bubble, triangle, and box
   sectors contain `r^-2` and `r^-1` collinear terms, but they cancel exactly in
   the topology sum:

   $$J_B+J_T+J_X=15(L_s+L_t+L_u)=15(3L-\ell)+O(r).$$
3. `REVERSE_PHYSICS_BT_EXTERNAL_PROJECTOR_CARRIER_MISMATCH_V1`
   (`REDUCED-MODE`, `COEFFICIENT_COMPUTED`) applies Eq. (13)'s external
   four-mass phase projector to that complete hard-region logarithm.  The
   interference already starts at total mass degree four, so all analytic
   phase-density derivatives decouple and

   $$\frac{d\sigma_{\rm virt,log}}{d\Omega}
     =\frac{5\lambda^6}{256\pi^4s}(L_s+L_t+L_u).$$

   This also corrects an imprecise matching target: the surviving
   $\ell=\log(-t/s)$ is a hard Mandelstam-ratio logarithm, whereas the real
   threshold contains $-(3/8)x_0x_1\log(x_1/x_0)$.  Rescaling the latter mass
   ratio changes the real finite part by $-(3/8)\log c$ and the computed hard
   virtual logarithm by zero.  The current carriers therefore cannot decide
   cancellation; a nonanalytic virtual external-mass boundary layer is the
   missing object.
4. `REVERSE_PHYSICS_BT_EXTERNAL_MASS_BOUNDARY_LOG_JET_V1`
   (`REDUCED-MODE`, `COEFFICIENT_COMPUTED`) computes that missing nonanalytic
   virtual carrier on the physical collinear family, with the real threshold's
   fixed hard fixture retained as a control.  An external
   cut factorizes into the cubic splitting vertex times the complete 25-graph
   five-point tree, so it includes lower-point insertions and 1PI triangle/box
   boundary pieces together.  A symbolic square-free jet proves that the cut
   polynomial is independent of splitting fraction and outer scattering
   ratio.  The result is

   $$E_i=\left[-2x_i\sum_{j\ne i}x_j
   +10\sum_{j<k;\,j,k\ne i}x_jx_k\right]\log(-\mu^2/x_i),$$

   $$\frac{d\sigma_{\rm boundary,log}}{d\Omega}
   =\frac{3\lambda^6}{128\pi^4s}\sum_{i=1}^4\log(-\mu^2/x_i).$$

   The external regulator response is therefore nonzero and exact.  The
   remaining comparison is no longer an unknown virtual integral: it is the
   definition of a common regulator map from the virtual recombined parent
   mass to the two real daughter masses, together with the full real
   splitting-fraction/inner-angle integral and identical-particle sum.
5. `REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1` (`REDUCED-MODE`,
   `COEFFICIENT_COMPUTED`) performs that comparison on the ordinary
   axis-compatible regulator class.  In the complete five-point square the
   spectator-projected real kernel is exactly independent of both splitting
   fraction and outer ratio, so the inner solid angle is `4*pi`.  Restoring
   the five-delta-prime sign `(-1)^5`, the `1/(2!*3!)` projector weight,
   factorized three-body phase space, and the three unordered final-pair
   regions gives

   $$\Delta_c\frac{d\sigma_{\rm real}}{d\Omega}
   =\frac{3\lambda^6}{512\pi^4s}\log c.$$

   For every parent map `G(x,y)=x*g(y/x)` with `g` continuous at zero and finite nonzero `g(0)`, including
   the physical threshold `G=(sqrt(x)+sqrt(y))^2`, one has
   `G(x,c*y)/G(x,y) -> 1` as `y/x -> 0`.  The complete virtual external-mass
   logarithm therefore has zero constant daughter-ratio response and cannot
   cancel the displayed real shift.  A deliberately non-axis-compatible map
   `x^(11/12)*y^(1/12)` can engineer per-pair cancellation, which makes the
   scope sharp: the result stops the ordinary independent-mass prescription,
   not distributional, dressed-state, enlarged-degenerate-state, or resummed
   architectures.

Both virtual logarithmic carriers and the complete real final-pair
normalization response have now been passed through their external projectors.
Their responses do not cancel under physical axis-compatible recombination.
The remaining project is therefore architectural rather than another ordinary
mass-regulated loop integral: define a distributional normalization from the
generalized Born rule, include degenerate incoming/dressed states, or resum the
collinear sector before testing the quotient trace.  The full NLO quotient
trace, physical KLN construction, and positivity beyond tree level remain
open.  None of these scalar results is a tensor/BRST or
`LORENTZIAN-CAUSAL` gravity result.

---

## 6. The nonperturbative caveat (verbatim, Sec. IV)

> "While the former [PS theory] has a positive Euclidean action, the latter [O(1,1) model] does not. Its kinetic term is indefinite and its potential has the wrong sign. Similarly, the $\phi$ and $\Omega,\Upsilon$ path integrals are inequivalent. **The former integrates over $\Omega > 0$ whereas the latter integrates over all $\Omega$. Although $\mathcal{S}_{1,1}$ does not define a meaningful theory, it has a well-defined perturbative expansion** [23, 25]. In fact, this exactly matches a complex two-derivative scalar field $\varphi$, with a negative quartic potential $-\frac12\lambda^2(\varphi^*\varphi)^2$, long-known to be asymptotically free [26]."

So the embedding, and everything built on $R$ (Eqs. (16)–(21)), is a statement about **perturbative expansions around the free theories**, order by order. The two-field model is a scaffold: it "does not define a meaningful [nonperturbative] theory" (indefinite kinetic term, wrong-sign potential, no positive Euclidean action), and its configuration space ($\Omega \in \mathbb{R}$) differs from the image of the field redefinition ($\Omega = \lambda^{-1}e^{\lambda\phi} > 0$). The only other domain/boundary remarks in the paper: the unspecified "spatial boundary term" in $R^\dagger H_{1,1} R = H_\phi$, and the functional-measure statement $\mathcal{D}\Omega/\Omega \propto \mathcal{D}\phi$. Nonperturbative physics of PS theory itself (positive Euclidean action) is deferred to the lattice: mass gap and $\langle(\partial\phi)^2\rangle \neq 0$ generation "in a manner similar to QCD" (initial investigations with P. Morandes), dynamical breaking of scale symmetry, "PS theory may be the simplest nontrivial four dimensional scalar QFT with a continuum limit."

---

## 7. Odds and ends the team asked about

- **Complex energies / conjugate pairs**: Not discussed. The only complex displacements are the Feynman $i\epsilon$'s: double poles at $p^0 = \pm(|\mathbf{p}| - i\epsilon)$. No complex-conjugate-pair energy eigenvalues, no discussion of PT-broken regimes.
- **Jordan blocks**: never named, but structurally present as the degenerate double pole / dipole pair: propagator $-i/(p^2+i\epsilon)^2$; footnote 3's "growing modes"; the printed mode expansion (C3) with secular factor $(1 + 2i|\mathbf{p}|t)a_2(\mathbf{p})$ (subject to the label inconsistency above); and the null cross-paired oscillator algebras $[a_1, a_2^\dagger] = [a_2, a_1^\dagger] \neq 0$ with $[a_i, a_i^\dagger] = 0$ (same pattern as $b_\Omega, b_\Upsilon$). The "dipole ghost" literature is cited ([2]: Flato–Fronsdal; Binegar et al.). Growing modes claimed to "cancel out of scattering cross sections" (footnote 3); the repository's exact order-$\lambda$ two-annihilator calculation now verifies a stronger local statement: after the repaired leading map is inverted onto the $(\Omega,\Upsilon)$ carrier, every $t$ and $t^2$ coefficient cancels.  The oscillatory algebraic sector remains open.  The squeezed-vacuum topology is now classified separately: it is null in the indefinite pairing but its first two-particle positive norm diverges in the ordinary massless Fock--Krein topology.
- **Massless / equal-frequency limit**: the theory is *intrinsically* at the degenerate point — massless $\square^2\phi = 0$ is the equal-frequency (resonant) Pais–Uhlenbeck limit. There is no unequal-frequency deformation anywhere in the paper; no mass terms are considered (they would break the shift symmetry / scale invariance and the dimension-zero structure). The paper's whole construction (δ′ Wightman function, dipole modes, off-shell states) is tailored to the degenerate case.
- **Interactions beyond the perfect-square form**:
  - PS is a special case of Holdom's general shift-invariant renormalizable four-derivative scalars [21,22]; the paper's proof is stated for PS specifically.
  - Outlook item 2: "The perfect square theory is merely the simplest of a **large class** of scalar four-derivative theories with hidden ghost parity which we expect to be quantum consistent. For example... a $N$-component, four-derivative dimensionless scalar on $\mathbb{R}\times S^{N-1}$ which embeds in a **$O(N,N)$-invariant** model of two-derivative fields" (has a large-$N$ limit for analytic strong-coupling study). "We have also studied **gauged versions**: the results will be presented elsewhere."
  - Outlook item 4: consistency requires the discrete hidden ghost parity, **not** shift symmetry — "shift non-invariant terms... are allowed by hidden ghost parity" (relevant to the cosmology mechanism of [14]).
- **Relation to quadratic gravity** (outlook item 1): PS theory = conformally flat limit of quadratic gravity [25]; diffeomorphism Ward identity protects the PS form under renormalization; graviton, its ghost partner and a vector mode [28] decouple in that limit; the long-wavelength classical instability of PS-as-spacetime = de Sitter scale-factor blowup, harmless in the usual cosmological sense once zero modes are handled.
- **Coherent states vs Ostrogradsky** (App. A): displacement operator identity $e^{i\phi(f)}\phi(x)e^{-i\phi(f)} = \phi(x) + \Delta f$ (A1); $\langle f|\hat H(\phi)|f\rangle = \langle 0|\hat H(\phi + \Delta f)|0\rangle = E(\Delta f)$ (A2). Ostrogradsky lives on in **expectation values** (unbounded below via coherent states) while the **spectrum** of $\hat H$ stays non-negative — reconciled only because the inner product is indefinite. This is their resolution of the correspondence-principle tension.
- **Asymptotic freedom**: single coupling $\lambda$, asymptotically free (matches Symanzik's negative-quartic scalar); strong coupling in the IR ⇒ expected mass gap + $\langle(\partial\phi)^2\rangle$ condensate.

---

## What we still don't know from the paper

Deferred to the companion papers or simply absent from the Letter:

1. **Proof of Eq. (19)** ($R_t P_\chi^{(\phi)} R_t^\dagger = P^{(\Omega\Upsilon)} + Q^{(\Omega\Upsilon)}$ with $Q$ purely negatively charged), and of the key lemma "the $R_t$ homomorphism does not yield any positively charged operators." Both cited to [17] (Bateman–Turok long paper, *to appear* as of v1). This lemma is exactly what the team's null-component test hinges on; we only have the statement, plus the $\mathcal{O}(\lambda^0)$ Bogoliubov data (C4)–(C5) as evidence.
2. **Explicit construction of $R$ itself.** Eq. (16) defines $R$ only through its adjoint action on the two generators $\Omega, \Upsilon$. No closed-form expression for $R$ (e.g., as a normal-ordered exponential / squeeze-displacement kernel), no domain/codomain analysis, no statement of whether $R^\dagger R = \mathbf{1}$ (only $R_t R_t^\dagger = \mathbf{1}$), no injectivity/surjectivity discussion, no characterization of $\ker R^\dagger$ or the orthogonal complement of $\mathrm{ran}\,R$.
3. **Existence/convergence of the limits $R_{\pm\infty}$.** Given the secular $2i|\mathbf{p}|t$ and oscillating $e^{2i|\mathbf{p}|t}$ terms in (C5) and in $Q_t$ (C6), the sense in which $R_t \to R_{\pm\infty}$ (weak limits on which domain? after smearing?) is not specified. Only the charge-neutral part is said to be $t$-independent and "well defined in the limits."
4. **The spatial boundary term** in $R^\dagger H_{1,1} R = H_\phi$: never written down, its role never analyzed.
5. **Definition of $\dagger$ and $\mathrm{tr}$ in Krein space.** Our identification ($\dagger$ = Krein adjoint w.r.t. the indefinite inner product; trace via the indefinite pairing) is an inference from consistency of Eqs. (6)–(8), not an explicit definition in the paper. Also unaddressed: trace-class issues, whether $\mathrm{tr}(A^\dagger A)$ converges before the finite-volume regularization of App. B, and uniqueness of the $B + C$ splitting in Eq. (7).
6. **The explicit $\kappa$ for the interacting theory.** $\kappa$ is defined abstractly (Eq. (1)) and identified with $\Omega\leftrightarrow\Upsilon$ / $\mathcal{X}\to-\mathcal{X}$ at the field level; the paper never writes $\kappa$ as an operator on the Fock/Krein space (e.g., its action on the $b_\Omega, b_\Upsilon$ or $a_1, a_2$ oscillators), nor which particular $\kappa$ (fundamental decomposition) makes $B^{(\Omega\Upsilon)}$ ghost symmetric — only that $P^{(\Omega\Upsilon)}_\chi$ is "even under ghost parity."
7. **The Noether charge** of $SO^+(1,1)$: no explicit charge operator $\hat Q$ or its expression in oscillators; only charge assignments of $b_\Omega, b_\Upsilon$ (both creation and annihilation of a given field carry the same sign).
8. **All-orders positivity**: open. Obstacle = collinear IR divergences affecting asymptotic states; resummation program only sketched (IR-finiteness of loops from [23] plus optical theorem). The repository has since established one-loop RG closure, the complete cut-constructible hard logarithmic four-mass jet, its external phase projection, and the separate nonanalytic external-mass boundary logarithm `3 lambda^6 sum_i L_i/(128 pi^4 s)` on the real fixture. The remaining logarithmic comparison requires a full real splitting-fraction integral and an explicit common regulator gluing between one virtual parent mass and two real daughter masses; it is no longer blocked on an unknown virtual boundary integral.
9. **Higher orders of the Bogoliubov map**: (C4)–(C5) hold only up to $\mathcal{O}(\lambda)$; the interacting corrections to $R_t$'s action on oscillators are not given in the Letter.  The repository has now expanded Eq. (16) and computed the complete resonant two-annihilator order-$\lambda$ coefficient after the label repair (`REVERSE_PHYSICS_BT_RT_JORDAN_KERNEL_V1`).  Its apparent secular terms cancel on the BT carrier, but its fixed-splitting Krein Gram has cubic endpoint poles.  `REVERSE_PHYSICS_BT_ENDPOINT_EXTENSION_AMBIGUITY_V1` further proves that reflection-even scaling-degree-three extensions have three independent endpoint constants: triple-plus and cutoff finite-part prescriptions already disagree on the inclusive constant test, and `1/48` can be fitted by an allowed delta term but is not predicted.  The fixed-vacuum oscillatory certificate `REVERSE_PHYSICS_BT_OSCILLATORY_RADICAL_NO_MATCHING_V1` remains correct on its declared oscillator grading: there $a_1^\dagger\mapsto b_\Upsilon^\dagger$ has charge $-1$, $Q_t$ has charge $-2$, and the certified negative radical is trace-null.  Its use as an exclusion theorem does not transfer to the covariant broken-vacuum carrier described below.  The apparent coisometric range gap is nevertheless absent perturbatively: `REVERSE_PHYSICS_BT_PERTURBATIVE_COISOMETRY_RIGIDITY_V1` uses the published cross-CCR to prove $R_t^\dagger R_t=1$ at free order, and $\Pi^2=\Pi$ then kills every formal correction to $\Pi$.  Finally, `REVERSE_PHYSICS_BT_CANONICAL_ENDPOINT_AMBIGUITY_V1` supplies an exact four-channel countermodel to uniqueness: skew canonical transport, CCR preservation, projector idempotence, trace preservation, and reflection symmetry all hold for a three-parameter endpoint family.  The target $1/48$ is algebraically compatible but is not selected.  This does not prove that every family member is realized by BT; it proves that the published canonical identities alone cannot determine the missing continuum transport.

   The exact successor `REVERSE_PHYSICS_BT_FULL_OFF_RESONANT_PROJECTOR_V1` retains $d=e_1+e_2-E_{\rm parent}$ through the complete quadratic carrier and restores the full daughter measure in $K^\sharp K$.  All explicit $t,t^2$ terms still cancel and $d=0$ exactly recovers the resonant kernel, but new $d$-dependent channels survive.  On the full soft chart $e_1=r$, $e_2=1$, $d=\alpha r$, the ordered cross-Gram has universal leading term $-1/(2r^3)$; multiplying by $r^2dr$ leaves $-(1/2)dr/r$.  Thus the flat three-jet ambiguity is reduced, on this declared chart, to one logarithmic soft normalization, not removed.  Rescaling a common cutoff shifts the finite part by $(1/2)\log c$, so ordinary off-resonant composition still does not select $1/48$.  The next missing object is a BT soft-collinear asymptotic Hamiltonian or hard matching operator whose regulator response cancels this shift before any finite coefficient is read off.  This is a `LOCAL-ALGEBRAIC`, `REDUCED-MODE` scalar result, not a complete probability or a gravitational/causal claim.

   `REVERSE_PHYSICS_BT_SOFT_CHARGE_RESOLVED_FLOW_V1` performs that normalization and charge audit.  Parent-index raising, the Bose factor, the angular measure, and the outgoing $2!/3!$ projector ratio turn the raw soft residue into exactly $+1/48$ per unordered pair and $+1/16$ for all three pairs; projector idempotence fixes a candidate hard response to $-1/16$ (absolute Born response $-3/512$).  Sharp and $r/(r+a\epsilon)$ smooth cutoffs have the same leading logarithmic response, and the formal finite-cutoff flow $K_t=e^{-idt}D-e^{idt}D^\sharp$ is anti-Krein.  But the two logarithmic contractions have fixed-vacuum generator charges $(+1,-1)$ and $(-1,+1)$, each of residue $-1/4$.  A prior one-sided nonpositive projection therefore makes this pushforward logarithmic residue zero.  A covariant zero-mode completion requires both compensating charge signs, and the Letter supplies neither that operator nor the full order-$\lambda$ pushforward.  This carrier classifies the Eq. (19) pushforward and does not by itself determine the distinct physical S-matrix coefficient.  The physical five-point response and the missing hard/dressed cancellation are typed separately below.

   `REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1` constructs the genuine global shift-orbit part of that missing carrier.  Writing $\phi=\phi_0+\varphi$ and $Z=e^{\lambda\phi_0}$ factorizes Eq. (16) exactly as $\Omega=Z\widehat\Omega$, $\Upsilon=Z^{-1}\widehat\Upsilon$ on the Laurent operator algebra $\mathbb Q[Z,Z^{-1}]$.  The unique covariant $Z$ dressing neutralizes every quadratic number-lowering generator, and the two logarithmic $Z$ powers cancel in the Gram, so the conditional neutral soft response remains $1/48$ per pair.  The same completion, however, changes the Appendix-C squeeze to $Z^2(b_\Upsilon^\dagger)^2$, of total charge zero rather than $-2$.  Setting $Z=1$ recovers the apparent negative grading but is not an invariant charge quotient: $\delta(Z-1)=Z\equiv1\pmod{Z-1}$.  Thus fixed-vacuum negative-charge selection and covariant zero-mode completion do not commute.  The Letter's missing full dynamical zero-mode module and generalized-Born trace are needed to decide the neutral squeeze and finish $R_tP_2R_t^\dagger$.  Eq. (19), the physical $1/48$, and the complete probability remain unestablished; the new result is an exact `LOCAL-ALGEBRAIC`, `REDUCED-MODE` obstruction, not evidence against an unpublished completion.

   `REVERSE_PHYSICS_BT_SQUEEZED_VACUUM_IMPLEMENTABILITY_V1` audits whether the displayed Appendix-C vacuum relation exists on the ordinary carrier before its charge is used.  In a periodic box the creation generator is $\sum_{p\ne0}e^{2i|p|t}(c_{\Upsilon,p}^\dagger c_{\Upsilon,-p}^\dagger)/(8|p|^2)$ in normalized discrete modes.  The complete charge-exchanging fundamental-symmetry family has positive metric $\mathrm{diag}(\rho^{-1},\rho)$ with $\rho>0$.  Its first two-particle norm density is $\rho^2(\epsilon^{-1}-\Lambda^{-1})/(64\pi^2)$, while the Bogoliubov pair-block Hilbert--Schmidt density is twice that value.  Both diverge in the massless infrared limit for every uniformly equivalent topology; the six lowest modes alone give density at least $3m^2L/(256\pi^4)$.  The vanishing indefinite norm therefore does not make the squeezed state a positive-topology vector.  A power weight $\rho(p)\sim p^\alpha$ can converge only for $\alpha>1/2$, where $\rho^{-1}$ becomes unbounded and the topology is inequivalent.  This is an exact ordinary-Fock--Krein obstruction, not a proof against a rigged or extended Bogoliubov representation.  Such a representation, its domain, zero-mode module, and cyclic generalized-Born trace are now the constructive next gate.

   `REVERSE_PHYSICS_BT_EXTENDED_SQUEEZE_CARRIER_V1` performs the full-series test and constructs the smallest explicit vacuum repair found so far.  For each unordered momentum pair the normalized amplitude is $z(p)=\rho(p)/(4p^2)$, so the exponential exists only if every $|z|<1$ and the squared amplitudes are summable.  A boundedly equivalent $\rho\ge m$ fails the first condition once $L\ge4\pi/\sqrt m$.  The inequivalent weight $\rho_\mu(p)=4\gamma\mu^2p^2/(p^2+\mu^2)$, $0<\gamma<1$, instead gives $z_\mu(p)=\gamma\mu^2/(p^2+\mu^2)$ and exact unordered square-sum density $\gamma^2\mu^3/(16\pi)$.  Its inverse grows as $p^{-2}$, its total logarithmic norm is extensive, and its normalized vacuum overlap tends to zero with volume: it is a different thermodynamic representation, not another bounded fundamental symmetry of the ordinary BT Krein space.  There is a second import barrier.  The raw cross-Krein shear has positive-Hilbert coefficients $u=1,v=z$, so $u^2-v^2=1-z^2$, not one.  Lill's generic extended positive-boson construction therefore supplies architecture guidance but not a theorem for this BT map, and its formal extended state space does not supply the missing positive cyclic generalized-Born trace.  We now have an explicit candidate vacuum carrier, but not an implementation of $R_t$, Eq. (19), or the physical $1/48$ on it.

   `REVERSE_PHYSICS_BT_CROSS_KREIN_TRACE_LIMIT_V1` constructs the next layer directly rather than importing a positive-Hilbert Bogoliubov theorem.  The orbit algebra completes on $\ell^2(\mathbb Z)$ with $[e_m,e_n]=\delta_{m+n,0}$ and bounded fundamental symmetry $J_0e_n=e_{-n}$; $Z$ is the bilateral shift, with $Z^\dagger=Z$.  On its tensor product with the weighted oscillator Fock space, the covariant generator $Q=\sum[z_pZ^2A_p^*A_{-p}^*-\bar z_pZ^2D_pD_{-p}]$ obeys $Q^\dagger=-Q$.  Its exponential is a densely defined closable cross-Krein squeeze on paired polynomial/Gaussian cores, and the canonical finite-rank trace is cyclic and invariant under its transport.  The trace obstruction is now exact.  If a cyclic trace on the full orbit algebra has finite normalized identity weight and is positive on the ghost-even projection cone, translation covariance makes all $E_n=Z^nE_0Z^{-n}$ have the same weight $c$; the symmetric rank-$(2N+1)$ projection gives $(2N+1)c\le1$ for all $N$, hence $c=0$.  The alternative finite-rank trace has $\operatorname{Tr}(E_0)=1$ but infinite identity weight.  Moreover the BT-normalized transported vacuum projector has trace norm $\exp(V\ell+o(V))$, where $\ell=\mu^3[(1+\gamma)^{3/2}+(1-\gamma)^{3/2}-2]/(12\pi)>0$.  Thus the finite-regulator squeeze and trace exist, but a normal thermodynamic Born trace does not follow.  A semifinite, relative, or non-normal weight and the full nonlinear Eq. (19) transport remain missing; $1/48$ is still conditional.

   `REVERSE_PHYSICS_BT_SEMIFINITE_RELATIVE_BORN_WEIGHT_V1` constructs the first of those alternatives on the finite detector ideal.  The canonical faithful normal semifinite trace on $B(\ell^2(\mathbb Z))$ has $\operatorname{Tr}_{\!\infty}(E_n)=1$ and $\operatorname{Tr}_{\!\infty}(1)=+\infty$.  For a finite-trace incoming projection $P_{\rm in}$ and a finite exhaustive output partition, the conditional weights $p_i=\operatorname{Tr}(A_i^\dagger A_i)/\operatorname{Tr}(P_{\rm in})$ are nonnegative and sum to one whenever each $A_i=P_iSP_{\rm in}$ satisfies the BT weak ghost decomposition.  The construction does not contradict the normalized-trace no-go because the normalized corner functional is not cyclic: $P=E_{00}$, $X=E_{01}$, $Y=E_{10}$ give $\omega_P(XY)=1$ and $\omega_P(YX)=0$.  Thus the finite identity weight is not needed for conditional scattering probabilities.  The remaining gate is whether the zero-mode-completed nonlinear Eq. (19) pushforward of a physical finite detector projector lies in this $\operatorname{Tr}_{\!\infty}$-finite paired ideal and admits a local non-normal thermodynamic limit.  The certificate does not establish that domain statement, Eq. (19), or the physical $1/48$.

   `REVERSE_PHYSICS_BT_FINITE_DETECTOR_PUSHFORWARD_V1` performs that domain test on the available zero-mode-completed logarithmic two-annihilator sector.  With $N$ orthogonal logarithmic detector cells and $a=\sqrt3/12$, the exact skew generator $Kh=a\sum_i d_i$, $Kd_i=-ah$ gives $P(\lambda)=P_0+\lambda P_1+\lambda^2P_2+O(\lambda^3)$, where $P_1=a\sum_i(|d_i\rangle\langle h|+|h\rangle\langle d_i|)$ and $P_2=a^2\sum_{ij}|d_i\rangle\langle d_j|-Na^2|h\rangle\langle h|$.  Projector idempotence holds exactly through $\lambda^2$.  The unique $Z$ dressing makes this entire certified sector neutral, so its strictly negative radical is zero.  For every finite $N$ the coefficients remain finite rank on the weighted-squeeze Gaussian core; at $z=1/2$ the exact one-cell sizes are $\|SP_1S^{-1}\|_1^2=80/243$ and $\|SP_2S^{-1}\|_1=29/324$.  The soft limit nevertheless fails in the positive trace ideal: although $\operatorname{Tr}P_1=\operatorname{Tr}P_2=0$ and the hard/soft $P_2$ traces cancel as $-N/48+N/48$, one has $\|P_1\|_1^2=N/12$ and $\|P_2\|_1=N/24$.  Thus the finite detector architecture works, but algebraic trace cancellation is not a uniform trace-class continuum limit.  A missing full-pushforward cancellation, hard matching operator, or explicitly local non-normal renormalized weight is still required; the sector certificate does not reproduce Eq. (19) or establish the physical $1/48$.

   `REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1` completes the public order-$\lambda$ quadratic map over all annihilator/creator signs and all three leading inverse images of a target $b_\Upsilon(s,p)$.  The symplectic phase of the opposite-sign $a_2(-s,-p)$ preimage cancels its Appendix-C oscillatory phase, so this off-resonant term contributes to the same constant coefficient as the two resonant preimages.  The exact sum leaves only $\delta b_\Omega=(s_1e_1+s_2e_2)b_\Omega^{(s_1)}b_\Omega^{(s_2)}/(2e_1e_2)$ and $\delta b_\Upsilon=-s_2b_\Omega^{(s_1)}b_\Upsilon^{(s_2)}/(2e_1)-s_1b_\Upsilon^{(s_1)}b_\Omega^{(s_2)}/(2e_2)$.  All secular terms and all three endpoint-dangerous rows cancel; the parent cross-Gram and its off-diagonal trace are exactly zero, and 48 exact cross-CCR Ward fixtures close.  With the unique $Z$ dressing the finite-mode quadratic pushforward therefore has the Eq. (19) form through order $\lambda$ with $Q_1=0$.  The conditional $1/48$ logarithmic carrier and its finite-cell trace growth are not instantiated by this completed quadratic map.  This does not determine a physical response because the S-matrix transition block is a distinct operator.  The squeezed-vacuum contribution, dynamical $p=0$ projector trace, continuum domain, and higher orders remain outside the Eq. (19) certificate.  The result has dependency tags `LOCAL-ALGEBRAIC` and `REDUCED-MODE`.

   `REVERSE_PHYSICS_BT_SQUEEZED_DETECTOR_SIMILARITY_V1` closes the finite-regulator Appendix-C squeeze question.  On the paired core $S^\dagger=S^{-1}$, so $K_S=SKS^{-1}$ gives $K_S^\dagger K_S=S(K^\dagger K)S^{-1}$ and a covariantly transported detector is conjugated by the same $S$.  Finite-rank cyclicity therefore preserves the completed quadratic trace at exactly zero; the squeeze is not an additive projector sector.  The normalized $z=1/2$ squeezed vacuum has bare one-pair occupation $3/16$, but this keeps a bare $b$-Fock detector fixed and is not the transported Eq. (19) observable.  Thus all public finite-regulator order-$\lambda$ quadratic pushforward sources have zero Born trace.  The squeezed projectors have no trace-norm thermodynamic limit, and the dynamical $p=0$ module, local non-normal weight, and higher composite orders remain missing within Eq. (19); independently, this projector result is not an S-matrix coefficient.  The dependency tags are `LOCAL-ALGEBRAIC` and `REDUCED-MODE`.

   `REVERSE_PHYSICS_BT_CYLINDER_BORN_LIMIT_V1` constructs the corresponding thermodynamic conditional functional on the inductive algebra of processes supported on finitely many paired detector cells.  Tensoring a local process with any number of squeezed spectator projections multiplies its Krein Born trace by one.  The exact weak-ghost weights $9/25,16/25,0$ are consequently volume independent, nonnegative, and normalized even though the representing corner has positive trace norm $(4/3)^N$.  The pointwise zero completed quadratic trace therefore has an exact regulator-independent directed cylinder limit equal to zero.  This removes the thermodynamic spectator-normalization barrier, not the whole physical barrier: the pair-cylinder algebra is not yet a spacetime-local AQFT or inclusive LSZ detector algebra, and the dynamical $p=0$ module and higher orders remain missing.  The result is `LOCAL-ALGEBRAIC` and `REDUCED-MODE`.

   `REVERSE_PHYSICS_BT_INCLUSIVE_NLO_OBJECT_LEDGER_V1` separates two operators that must not be conflated.  The orthogonal-block lemma in `REVERSE_PHYSICS_BT_INCLUSIVE_PHYSICAL_COEFFICIENT_V1` is exact, as are its signed-kernel, squeeze, and finite-detector calculations, but its physical identification is superseded: the zero kernel is the Eq. (19) projector pushforward $R_t P R_t^\dagger$, not the physical transition block $P_{\rm out}(S-1)P_{\rm in}$.  The independently certified five-point response therefore remains $+1/512$ per pair and $+3/512$ over three pairs in absolute $\lambda^6\log(c)/(\pi^4s)$ units, equivalently $1/48$ per pair and $1/16$ total after division by the Born coefficient $3/32$.  The axis-compatible physical virtual daughter-ratio response is zero, so the physical real-plus-virtual response remains $+3/512$.  The complete public $R_t$ pushforward response is also zero, but it is a distinct Eq. (19) object and is not added to the S-matrix ledger.  An independently constructed physical hard/dressed matching response $-3/512$ is still required.  The Callan--Symanzik hard scale log has zero daughter-ratio response and cannot be substituted for this missing endpoint object.  The physical complete NLO probability and all-order Eq. (19) remain unestablished.  The dependency tags are `LOCAL-ALGEBRAIC` and `REDUCED-MODE`.

   `REVERSE_PHYSICS_BT_PHYSICAL_SHELL_PSEUDOUNITARY_COMPLETION_V1` fixes the missing coefficient without returning to the $R_t$ pushforward.  On a positive regulated hard-plus-collinear generalized-Born quotient, write $S_{\rm phys}(x)=1+xA+x^2B+O(x^3)$ with $x^2=\lambda^2\log(c)/\pi^2$.  Pseudo-unitarity gives $A^\dagger=-A$ and $B+B^\dagger+A^\dagger A=0$.  The physical five-point column has norm squared $1/48$ per pair and $1/16$ in total, so the hard diagonal identity is $2\operatorname{Re}B_{hh}=-\|Ah\|^2=-1/16$.  Thus $\operatorname{Re}B_{hh}=-1/32$, and multiplication of the hard survival response by the Born coefficient $3/32$ forces the absolute term $-3/512$.  Channel phases and anti-Hermitian second-order freedom cannot change it.  The exact finite witness $S_{\rm witness}(x)=\exp(xA)$ with $Ah=(\sqrt3/12)\sum_i r_i$ proves algebraic compatibility.  The cancellation is conditional on existence of the regulated physical Møller/dressed S-matrix on a complete degenerate trace domain; the certificate does not construct that continuum object, establish beyond-tree positivity, compute the finite NLO constant, or prove Eq. (19).  Its dependency tags are `LOCAL-ALGEBRAIC` and `REDUCED-MODE`.

   `REVERSE_PHYSICS_BT_LOG_SHELL_MOLLER_LIMIT_V1` resolves the ordinary-carrier part of that existence gate.  In $y=-\log r$, normalized width-$\ell=\log c$ shell vectors $u_{n,i}$ supported on disjoint intervals $[2n\ell,(2n+1)\ell]$ move to $r=0$.  The physical columns obey $\|A_nh\|^2=1/16$ but $\|A_nh-A_mh\|^2=1/8$ for $n\ne m$, so no strong perturbative Møller limit exists on $\mathbb C h\oplus L^2((0,\infty),dy)\otimes\mathbb C^3$.  The exact exponential strengthens this: for $v_n=4A_nh$, $e^{xA_n}h=\cos(x/4)h+\sin(x/4)v_n$, whose distinct-shell distance squared is $2\sin^2(x/4)$.  The ordinary weak limit loses the real column and has pseudo-unitarity defect $-x^2|h\rangle\langle h|/16$.  A regulator-pulled-back alternative does exist: the isometries $J_ne_i=u_{n,i}$ identify every moving shell with a fixed four-dimensional endpoint fibre, on which $J_n^\dagger e^{xA_n}J_n=e^{xA_*}$ and the $-1/16+1/16=0$ probability ledger is regulator independent.  This is an exact leading-log dressed-shell bundle, not yet a local LSZ/AQFT affiliation or the full dynamical S-matrix.  The result is `LOCAL-ALGEBRAIC` and `REDUCED-MODE`.

   `REVERSE_PHYSICS_BT_DETECTOR_RESOLUTION_DILATION_V1` gives that bundle its first non-fitted physical affiliation.  On the asymptotic momentum-resolution algebra $L^\infty(\mathbb R,dy)\bar\otimes\mathbb C^3$, let $q_R(y)=q(y-R)$ for any monotone cutoff profile with unit endpoint jump.  The positive detector cell $d_{R,a}=q_{R+a}-q_R$ has exact semifinite trace $\int d_{R,a}\,dy=a$, and its normalized square root $u_{R,a}=\sqrt{d_{R,a}/a}$ obeys $u_{R+b,a}=T_bu_{R,a}$.  Thus $J_{R,a}e_i=u_{R,a}$ is derived from mass-resolution dilation rather than chosen after the coefficient is known.  A sharp cutoff and a $C^1$ cubic smoothstep both give trace one for a unit shift; the latter splits into two positive rational-polynomial pieces of integral $1/2$.  The certified generalized-Born density $1/48$ per pair therefore gives $+1/16$ in three channels for every admissible profile, while physical-shell pseudo-unitarity gives the hard response $-1/16$.  The physical NLO leading-log resolution response on the declared final-pair cylinder is exactly zero.  This is not a time-Møller construction: the BT soft-collinear asymptotic Hamiltonian, complete incoming sectors, spacetime-local detector algebra, finite NLO constant, beyond-tree positivity, and all-order Eq. (19) remain open.  The dependency tags are `LOCAL-ALGEBRAIC` and `REDUCED-MODE`.
10. **The second $\mathbb{Z}_2$** in $K_4 = \mathbb{Z}_2\times\mathbb{Z}_2$ is never identified explicitly (presumably $(\Omega,\Upsilon)\to(-\Omega,-\Upsilon)$), nor is any role assigned to it.
11. **Whether/how the $\Omega > 0$ vs $\Omega \in \mathbb{R}$ domain mismatch feeds back into perturbation theory** (e.g., instanton/boundary contributions distinguishing the two path integrals): stated as inequivalence, not analyzed.
12. **Uniqueness/scheme-dependence of the off-shell state construction** $\tilde\Psi(p)$ (Eq. (9) duality): the off-shell states are defined by the duality relation $\langle\tilde\Psi(p)|\tilde\Psi(q)\rangle\tilde W(q) = \delta_4(p-q)$; existence/uniqueness not discussed in the Letter.
13. No discussion of: unequal-frequency (massive) PU deformations, complex-conjugate energy pairs, PT-symmetric quantization comparisons (Bender–Mannheim is cited [5] but not engaged), Jordan-block language, or positivity of the pseudo-Hermitian metric as an operator-deformation problem.
