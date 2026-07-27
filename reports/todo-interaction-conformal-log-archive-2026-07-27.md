# Archived TODO log — interaction-deformation and conformal residual streams

Date: 27 July 2026

## Why this file exists

`TODO.md` states that it "holds only open items," but item 14 had grown into a
554-line running log of *completed* work spanning the interaction-deformation
program (steps 1–15), the gravity rail (G13–G18), and the conformal residual
cohomology stream (C0a through C2l-P). That log recorded finished results, not
open tasks, and it stopped at Paper 6 while the programme has since published
through Paper 18.

This pass moves the log out of `TODO.md` verbatim and restores that file to an
open-items list. Nothing scientific is added, removed, promoted, or demoted
here. The transcription below is byte-faithful to what `TODO.md` contained at
commit `df710e96`; where it disagrees with a later report or certificate, the
later artifact governs.

## Status of the streams recorded below

- The interaction-deformation and gravity-rail entries (steps 1–16, G13–G18)
  are complete and are published as Papers 05 and 06.
- The conformal residual entries (C0a–C2l-P) were marked IN PROGRESS in this
  log. They have since been superseded by Papers 07, 08, and 12 and by the
  `covariant_completion/` and `residual_atlas/` certificate chains. Do not
  treat the "Next (C2i)" paragraph below as the current work front; consult
  `planning/work-items/` for that.
- The `NEXT (ON5)` boundary Born-trace specification was never executed and is
  carried forward as an open item in `TODO.md`.
- The `DEFERRED` list at the end remains deferred.

## Verbatim transcription from TODO.md

14. [~] Interaction-deformation program (other team's direction,
    2026-07-13, ACTIVE — see reports entry + verify_interaction_
    deformation.py ID1–ID10 ALL PASS):
    - DONE: cubic PU first order verified (their R₁ exact); second
      order computed: generic unobstructed w/ end-to-end O(λ²)
      Hermiticity; **obstruction 27√3/(320ω₂⁴)(a₁a₂†³−a₁†a₂³) at
      ω₁ = 3ω₂, unremovable**; R₂ = O(ε⁻³) ⇒ R_n ~ ε^{−3n/2},
      λ_c ~ ε^{3/2} conjecture.
    - DONE (step 2): selection-rule lattice theorem (candidates =
      transfers with |d₁|+|d₂| ≤ n+2, parity n mod 2); third-order
      audit: generic clean, R₃ odd/Hermitian, **NEW obstruction at
      3:2, order 3: −(117√30/1120)i(a₁²a₂†³+a₁†²a₂³), gauge-indep**;
      2:1, 4:1 escape (odd-mode-2-transfer rule, mechanism open);
      R₃ = O(ε⁻⁹ᐟ²). Refined conjecture: p:q first obstructs at order
      p+q−2 for odd p.
    - DONE (step 3): spectral PT-breaking VERIFIED at 3:1 (E=27ω₂
      shell: κ± = 2.4488 ± 0.2246i, 13 digits; exact diagonalization
      confirms pair in truncated spectrum ⇒ no positive metric exists
      there at all); lowest doublet real; tongue δ_c = 38.4151λ²;
      perfect-square vertex = ½λ_K(p₁²,p₂²,p₃²) with massless &
      one-Jordan-leg vanishing, Jordan-PAIR coupling, threshold
      factorization m₁²(m₁−2m₂)(m₁+2m₂). "Expanding hierarchy" (not
      dense) wording adopted.
    - DONE (step 4, perfect square first order, both completions):
      even-ghost selection rule ⇒ 𝔬₊^(1) = 0 IDENTICALLY (even above
      threshold); 𝔬_K^(1) ∝ λ_K ≠ 0 above threshold (real ghost decay);
      scaling: massive confluence both δ^{−3/2}; massless Jordan paths:
      positive δ^{−1/2} path-independent, Krein exceptional path
      α = 2/7 δ^{−3/2}; Jordan-chain lemma: κ ≠ per-block sign
      (verify_perfect_square.py PS-A..H).
    - DONE (step 5): exact two-field rewriting verified (ℒ = −∂U∂V +
      (λ²/2)U²V², O(1,1) form); **constructive κ₀ = U↔V exact symmetry,
      nonlinear in (φ,ψ): (φ,ψ) → ((1/λ)log(ψ/λ) − φ, ψ)**; sector
      swap (1,0)↔(0,1) consistent with PS-H; linearization about null
      background = exact □² Jordan pair (□v = 0, □u = λ²v); Legendre
      warning: do second-order source in two-field frame
      (verify_two_field.py TF1–TF7).
    - DONE (step 6): **OUTCOME A — the pointed-sector positive
      completion is obstructed at second order by generic
      branch-changing 2→2 scattering** (contact piece vanishes;
      exchange piece nonzero at three tuned kinematics; truncation-
      complete). Compatible with exact κ (sector exchange, not
      in-sector parity). verify_sector_obstruction.py SO1–SO7.
    - DONE (step 7): hardening — EXACT obstruction 401√6/39424 at the
      rational CM point (open-subset genericity); CONFLUENT PARITY
      THEOREM (P_δ unbounded in one sector; δ-independent sector
      exchange on the oppositely-oriented doubling). **PAPER 5 DRAFTED**
      (05-interaction-obstructions.tex, 12 pp.).
    - DONE (step 8): paper-5 referee pass applied (matrix convention,
      ρ±=∓δ/(2g), ω₂^{−13/2} scale, PT proposition, exact Sturm
      certificate, narrowed genericity, truncation lemma, chart
      distinction, six derivation appendices, new title); paper 0
      revised per team spec (new interaction section and diagram; this
      was later superseded by the six-paper Paper-VI synthesis).
    - DONE (step 9, 2026-07-13): doubled/Krein verification suite
      (verify_doubled_theory.py DQ1–DQ9 ALL PASS): mirror-adjoint
      relation H_B = WH_A†W† EXACT with W = ι∘(−1)^{N_ghost} — i.e.
      it IS Krein pseudo-Hermiticity, the "doubled pairing" is the
      two-sector unfolding of BT's κ; on-shell T exactly
      Krein-pseudo-Hermitian (GTG = T†) while Hilbert-Hermiticity
      fails; **obstruction lives entirely in the κ-odd block**
      (T(out,in) = −401√6/78848); finite-time S_B†WS_A = W exact;
      graph theorem both directions; O(1,1) polar form r,χ; classical
      Ward with exact regulator breaking εu(1+u) − μ²v. Literature
      repositioning applied to papers 5+0 (BT attribution for O(1,1)/
      exchange/quantum embedding; new refs Mostafazadeh-nd, Feinberg–
      Znojil, Mannheim CPT, Liu–Modesto–Calcagni, Azizov–Iokhvidov;
      new Prop. cprop:krein + separation-of-completions discussion).
    - DONE (step 10, 2026-07-13): **5:1 CONFIRMED at order 4**
      (verify_51_order4.py FO1–FO9 ALL PASS): 𝔬₊^(4) =
      −(203125√5/2341011456)(a₁a₂†⁵−a₁†a₂⁵) exactly, orders 2–3
      vanish at 5:1, gauge-independent, ω₂^{−9} scaling (series
      𝔬₊^(n) ∝ ω₂^{−(5n−2)/2}), R₄ = O(ε⁻⁶) (4th point of ε^{−3n/2}).
      Hierarchy conjecture p+q−2 (odd p) now verified at 3 points.
    - DONE (step 11, 2026-07-14): obstruction-to-null STAGE 1
      (verify_obstruction_null.py ON1–ON4 ALL PASS + paper-5 Lemma
      lem:chargenull + Comp. Prop. cprop:embedding, tag paper5-v1.1):
      charge-null lemma self-contained (graded Krein trace, kinematic);
      canonical Bogoliubov map to the BT charge basis; **EXACT law
      S_UU/S_VV = (δ/2g)² = ε/g** for the mapped vacuum's charged
      squeezing — one-sided iff ε = 0 (the O(1,1)-symmetric confluent
      line; BT's massless point also requires μ² = 0); confluent
      S_VV → −g/(4w²), or −1/(4w²) at g = 1, matching BT (C5)–(C6)
      at μ² = 0. Reference-dispersion no-go is exact; the broader
      charge-preserving-frame search runs away numerically to a
      degenerate frame. BT null-relocation is exact at the massless
      boundary; ε/g contamination at split is the charge-frame image
      of PS-D broken parity and is not assumed small away from the
      boundary.
    - DONE (step 12, 2026-07-14): **GRAVITY G13–G14 ALL PASS**
      (verify_gravity_cubic.py, multi-wave perturbiner engine, exact
      ℚ(i) kinematics): one-M rule A₃(Mhh) = 0 at the physical decay
      point (20 exact zeros; Einstein-truncation/Bach-flat, supports
      gravitational 𝔬₊^(1) = 0); Ward identities exact; A₃(MMM) ≠ 0,
      A₃(MMh) ≠ 0 exact; **factorization residue at P² = M² nonzero
      ⇒ MM→Mh not identically zero ⇒ [(-1)^{N_M},S] ≠ 0** (naive
      massive parity; other gradings open).
      Independent Einstein-frame rail verify_gravity_factorization.py
      closes the factorization sum exactly: the traceless potential's
      cubic `tr Phi^3` terms cancel; the nonlinear kinetic term gives
      A₃(MMM)=−sqrt(6)/8, while A₃(MMh)=−sqrt(2)/8; the arbitrary-xi
      Ward identity and massive-leg exchange symmetry vanish exactly.
      The complete five-polarization residue numerator is sqrt(3)/32.
      The internal TT inverse kernel is (P²+M²)/4 in the script's L_M
      normalization, so the pole-normalized residue is sqrt(3)/8
      (overall action normalization conventional): NONZERO.  By
      real-analyticity/Zariski density of the physical 2→2 component,
      MM→Mh is nonzero on a nonempty open real-shell subset.  This
      supplies the existence input for the second-order obstruction;
      the explicit real point is now a hardening certificate.
    - DONE (step 13, 2026-07-14): **GRAVITY G15 ALL PASS** at the
      interior rational point.  The exact contact plus all three
      gauge-fixed exchanges gives
      A_K(MM→Mh) = 7881241032/5584765625 ≠ 0 at
      s = 25/4 M², cosθ = 3/5 with real polarizations.  The total Ward
      identity, initial-M Bose symmetry, gauge-representative and
      internal-gauge independence are exact; the threshold value is
      −509784/390625.  The shifted massive-pole residue reproduces the
      G14 factorization contraction with the ghost kinetic sign.
    - DONE (step 14, 2026-07-14): **GRAVITY G17 ALL PASS**
      (`verify_gravity_obstruction.py`).  The quartic contact and every
      exchange channel were exposed separately; the physical-adjoint
      reverse process agrees term by term.  Under M = −i Mhat, the
      contact, internal-massless exchange, and internal-massive exchange
      all acquire +i (the last includes the compensating −1 of the
      quarter-turned massive inverse kernel).  Therefore
      Π_shell(B₂†−B₂) = −2i A_K σ_x, with exact off-diagonal element
      −15762482064 i/5584765625 ≠ 0.  External EOM, total Ward, and
      axial/de Donder checks pass.  The result is independent of the
      first-order metric commutant: the complete connected cubic
      physical-shell block vanishes, hence
      Π_E[G,v₁+v₁†]Π_E = 0 for every [G,h₀]=0.
      G17g now verifies the exact finite-shell identity
      P_E[(v₂†−v₂)+1/2[R₁,v₁+v₁†]]P_E = B₂†−B₂, closing the
      amplitude-to-deformation-cocycle bridge raised in Paper-6 review.
    - DONE (step 15, 2026-07-14): **GRAVITY G18 ALL PASS**
      (`verify_gravity_krein.py`) on physical BRST cohomology under the
      conventional natural-lift class: nondegenerate one-particle
      fundamental symmetry, agreement with the free Krein real form,
      and particle-number-diagonal cluster-multiplicative Fock lift.  The
      proper-orthochronous commutant is
      diag(ε₊,ε₋,ε_M I₅); parity/real-field compatibility equates ε₊ and
      ε₋, while the free signature fixes (+,+,−) even without that extra
      condition.  Tensor multiplicativity uniquely gives
      J_F=(−1)^{N_M}.  For t=iA_K,
      Tr(X^sharp X)=−A_K²≠0, and for the full G17 obstruction
      Tr(O^sharp O)=−8A_K²≠0: Z₂-odd is neutral after squaring, not null.
      The verified MMM/MMh vertices force 3q_M=2q_M=0 and hence q_M=0
      for any uniform abelian charge; the physical block also survives
      BRST cohomology and cannot be BRST-exact.
    - DONE (step 16, 2026-07-14): **PAPER 6 DRAFT + MAJOR-REVIEW
      REVISION.**  The source is correctly ordered and compiles; the
      manuscript now proves the Born--deformation identity, states the
      regulated full cubic-shell lemma including spectators and soft-mode
      prescription, maps covariant graphs to the stationary Born series
      with LSZ/Bose conventions, narrows the metric/Fock/BRST scope, and
      includes a one-command archived reproduction suite.  README and
      Paper 0 now synthesize Paper 6.  The G16 250-polarization scan
      remains optional regression hardening and is not on the theorem
      path.
    - DONE (literature-positioning pass, 2026-07-13): Paper VI now
      distinguishes its exact physical `MM -> Mh` amplitude and the
      resulting Born/deformation cocycle from the established quadratic-
      gravity spectrum, auxiliary Einstein frame, pseudo-Hermitian metric
      perturbation theory, and conformal BRST/LSZ literature.  The
      comparison with Kuntz's PT-symmetric quadratic-gravity proposal is
      explicit: the free rotation and physical massive spectrum agree,
      while his interacting metric calculation is mode-truncated and
      does not include the exact degenerate gravitational shell.  The
      paper also states why unstable-resonance and fakeon prescriptions
      lie outside its physical-`M`, analytic-metric hypotheses.  The
      programme overview remains unchanged pending review.
    - DONE (CONFORMAL C0a, 2026-07-13):
      `verify_conformal_free_pairing.py` exactly verifies auxiliary
      elimination to `Ricci^2-R^2/3`, the TT double-pole/cross propagator,
      the action-derived `J1=sigma_x` Jordan Gram form, forced
      indefiniteness of every nondegenerate Jordan-invariant form, the
      absence of a regular local elementary `O(1,1)` presentation, the
      symmetric two-particle lift and conditional `LLLL=ELLL=0` pattern,
      and the coupling normalization.  It also translates the published
      Kubo--Kuntz flat BRST algebra into two TT Jordan blocks plus two
      ordinary vector modes.  Research ledger:
      `notes/conformal-c0.md`.
    - DONE (CONFORMAL C0b, 2026-07-13):
      `verify_conformal_cylinder_form.py` reconciles Paper IV,
      Kubo--Kuntz, Metsaev, and the exact `S^1 x S^3` Weyl-graviton
      spectrum.  The compact cylinder Hamiltonian is diagonal, not
      Jordan: the TT energies are `n+2` and `n+4`, while the vector
      energy is `n+2` starting at `n=1`.  The flat Jordan generator is
      `P_0`; cylinder time is `D`.  The three towers reproduce
      `Z_2=(10q^2-18q^4+8q^5)/(1-q)^4` exactly.  The level-one
      Shapovalov form of the `Delta=2` Weyl primary has eigenvalues
      `+8 x24` and `-2 x16` after both chiralities: precisely the lower
      TT and vector degeneracies at energy 3.  Metsaev's transverse
      boost chain `E -> A -> L` fixes the flat six-mode form up to one
      scale, so the vector sign is not an independent conformal choice.
      With the energy-2 primary positive, the complete compact-energy
      signature is `N_+=2(E-1)(E+3)` and, for `E>=4`,
      `N_-=4(E+1)(E-2)` (`N_-(3)=16`).  The conventional radial-adjoint
      form is therefore nondegenerate but indefinite; this does not yet
      test a separately defined Mannheim left-right/CPT adjoint.
    - DONE (CONFORMAL C0c, 2026-07-13):
      `verify_conformal_mannheim_adjoint.py` separates right kets,
      ordinary-adjoint bras, left bras, the intertwiner `G`, and the
      spectral `C` operator.  Every nondegenerate conserved Hermitian form
      on a rank-two Jordan block has `det G=-c^2<0`.  Bender--Mannheim's
      published equal-frequency overlap (their Eq. (95)) is exactly
      congruent to `sigma_x` after the allowed generalized-vector shift,
      and hence is the same Jordan-dual algebra as the Kubo--Kuntz cross
      commutator.  In the universal split regulator, the positive
      `V_delta=P C_delta=diag(delta,1/delta)` and the nontrivial spectral
      `C_delta` both become singular; only the indefinite cross form stays
      finite.  At the Jordan point a commuting involution is only `+-I`.
      C0b uniqueness then implies that every fixed, standard-real,
      full-`SO(4,2)` Hermitian extension is `c J_conf`, not a second
      positive metric.  A distinct Mannheim proposal must therefore be
      dynamical/time-dependent, singular, doubled, state-restricted, or a
      genuinely modified probability functional.  The exact first-order
      Jordan metric-deformation map and its two-real-dimensional cokernel
      are recorded as the interface to C1.
    - DONE (CONFORMAL C1a, 2026-07-13):
      `verify_conformal_cubic_shell.py` separates the two interaction
      complexes which the initial C1 proposal conflated.  The two C0c
      obstruction coordinates belong to the flat `P_0` Jordan block;
      on a fixed compact-`D` shell the free Hamiltonian is scalar and the
      entire anti-Hermitian source is the cokernel.  The exact Fock-shell
      scan gives dimensions 137, 536, and 2062 at energies 4, 5, and 6.
      The Einstein rule `A(E,E,X)=0` kills the complete energy-4 cubic
      shell.  At energy 5 the only surviving block joins two negative-sign
      sectors, and the published finite `EAA` amplitude is certified
      nonzero at an exact complex spinor point.  At energy 6, `SO(4)` and
      the selection rule isolate the first possible opposite-sign block as
      `A_3 A_3 <-> L_6`; the vector alternative is representation-forbidden.
      Kubo--Kuntz's result is also classified correctly as nonpositivity of
      the indefinite completeness sum, not a computed nonzero
      `J V-V^dagger J` source.  Finally, analytic deformation of the fixed
      indefinite `J_conf` cannot change its inertia and therefore cannot
      produce a positive metric even if the conservation equation is
      soluble.
    - DONE (CONFORMAL C1b, 2026-07-13):
      `verify_conformal_aal_vertex.py` constructs the normalized
      Hamada--Horata `S^3` vector and upper-TT harmonics and evaluates the
      complete metric Weyl cubic coefficient with an exact curved-cylinder
      multilinear perturbiner.  The allowed Gaunt overlap is
      `sqrt(6)/(3 pi)`, but the full `A_3 A_3 -> L_6` density is a radial
      boundary term and integrates to zero.  By the unique `(3,1)` reduced
      matrix element plus parity, the complete first opposite-sign oscillator
      block at energy six vanishes.  Its promotion to the compact physical
      BRST block remains conditional on the global conformal/Taub audit.
      Three higher-spin hardening channels
      `(J1,J2)=(1,3/2),(3/2,3/2),(1,2)` also vanish.  With
      `S=J1+J2`, their pre-measure density is
      `D=C t[(2S-2)t^2-1]/(1+t^2)^(2S-1)`, while the measured integrand is
      `I=2D/(1+t^2)=d[-C t^2/(1+t^2)^(2S-1)]/dt`.  The normalizable resonant
      `E_2 A_3 -> A_5` cylinder channel is separately hardened: its normalized
      algebraic overlap is `-1/(2 pi)`, its local Weyl density is nonzero, and
      its measured density is an exact boundary derivative with both endpoint
      values and a direct integral checked independently.  The conjugate
      `A_5 -> E_2 A_3` process is assembled as a separate exact perturbiner
      run.  Both coefficients vanish, and with the induced same-sign pairing
      `J_EAA=-I_2` their off-diagonal block contributes exactly zero to
      `J V-V^dagger J`.  This does not contradict the nonzero complex
      flat-momentum amplitude.  EAA therefore realizes another exact
      compact-cylinder boundary zero and motivates, but does not prove, the
      stronger resonant-shell conjecture `P_Delta V_3 P_Delta=0`.  The finite
      hierarchy is evidence, not yet an all-spin theorem.  All four measured
      constants also fit the single normalized prefactor formula recorded in
      `notes/conformal-c0.md`.
    - IN PROGRESS (CONFORMAL C1c/P4, 2026-07-13):
      `verify_conformal_cubic_channels.py` now gives the exact all-energy
      resonant classification.  After Einstein selection the only families
      are same-sign EAA, same-sign EAL, and opposite-sign AAL.  EAL has a
      second mixed-chirality parity orbit for `J_E>=3/2`; this was absent
      from the earlier coarse classification.  `verify_conformal_eal_vertex.py`
      and four independent curvature runs close the first same-chirality
      seed `E_2 A_3 <-> L_5`: its allowed derivative overlap is nonzero, but
      its measured density is a degree-one Legendre/Jacobi polynomial and
      both directed coefficients vanish separately.  The mixed seed
      `E_3 A_3 -> L_6` is now closed by four further independent curvature
      runs: its nonzero allowed overlap survives, but the projected measured
      density is `(1-u)P_1^(1,0)` and both directions vanish separately.
      The symbolic Jacobi rail proves that
      every already observed AAL density integrates to zero for arbitrary
      spin parameter and identifies EAA with the same degree-one mechanism;
      `verify_conformal_aal_highest_harmonics.py` additionally derives and
      certifies the closed Hamada--Horata highest-weight `q` and `q tensor q`
      oscillator harmonics, their Clebsch--Gordan recurrences, null identities,
      and normalization.  A bounded generic two-spin curvature attempt did
      not finish, so deriving the generic Weyl density from those recurrences,
      both all-spin EAL identities, BRST/complete-shell adjoint closure, and
      the compact conformal-Killing reducibility/global-charge audit remain
      explicit theorem obligations.  Until the last audit closes, these are
      oscillator/mode-representative coefficients rather than asserted full
      physical-BRST matrix elements.

      The energy-six P4 staging is also exact and fail-closed.  The common
      parity-fixed `(2,2)` target is the provisional oscillator three-channel
      block
      `(|A_3A_3>,|E_2A_4>,|E_2L_4>)` with `H0=6I` and
      `J=diag(1,-1,-1)`, representing 75 of the full 2062 oscillator-shell
      states before global conformal/Taub reduction.
      Compact `D` uses ordinary semisimple denominators, never the flat
      `P_0` Jordan series.  The raw full Feshbach exchange has infinite
      self-energy tails, whereas the explicitly normal-ordered connected
      contact-plus-one-line-exchange tree operator is finite after vacuum
      cancellation and external-state subtraction.  The four-wave engine
      gives `C_AA,AA=1009/(20250 pi^2)` and independently assembled
      `C_EL,AA=C_AA,EL=1099/(43200 pi^2)`.  The latter produces the
      contact-only source
      `[1099/(21600 pi^2)] [[0,1],[-1,0]]`, which is an exact
      exchange-cancellation target, not an obstruction.
      `verify_conformal_deformation_bridge.py` now proves the exact
      Born--deformation identity
      `P S2 P=J_P B2-B2^dagger J_P` with
      `B2=P[V2+V1 Q(E-H0)^(-1)Q V1]P`, and exhibits why full
      `P V1 P=0` (not merely first-order source closure) is needed for
      independence from homogeneous first-order metric freedom.
      The exact scalar covariant-action Hessians are now
      `kappa_s=131712`, `kappa_t=0`, `kappa_u=960`.  The s/u bordered gauges
      agree.  The t Hessian is null; its nonzero slice currents pass direct
      pure-gauge Ward probes, parity adds rather than cancels, reverse currents
      obey the ordinary coefficient-kernel dagger relation, and the quotient
      is the frequency derivative
      of the `ell=omega=1` conformal-Killing reducibility modulo gauge.  No
      `1/kappa_t`, ordinary t exchange, `Veff`, or obstruction is claimed.
      C2a now constructs all 15 cylinder Diff x Weyl reducibilities, verifies
      their `SO(4,2)` algebra/Jacobi identities, and fixes the selected
      action-normalized Taub map exactly:
      `Q_s=-i s C_s`, with
      `Q_xi-[E_+^dagger,A_+]=-sqrt(5)/(5 pi)` and
      `Q_xi+[L_-^dagger,A_-]=sqrt(10)/(5 pi)`.  These are mixed EA/LA
      bilinears, not `Q[A_3,A_3]`; reverse and parity rails pass.  Next:
      C2b reconstructs the complete `(1/2,1/2)` magnetic multiplets generated
      by these two mixed seeds.  Wigner--Eckart multiplicity is one in both
      adjacent blocks, with exact reduced coefficients
      `R_AE=-sqrt(10)/(5 pi)` and `R_LA=sqrt(2)/(2 pi)`.  The resulting
      36-dimensional low-mode matrices obey every `SU(2)_L x SU(2)_R` ladder
      identity, `[D,Q_-]=-Q_-`, parity, and ordinary kernel-dagger covariance,
      and reproduce the curvature seed matrices on projection.  An exact
      cancelling superposition demonstrates a point on the seeded quadratic
      Taub-constraint zero locus, not a common operator kernel or a linear
      state exclusion.  C2f-N now supplies the previously missing absolute
      symplectic normalization and kernel-to-generator bridge.

      C2c-I now gives the exact representation-theoretic workload.  A
      proper-conformal lowering charge can occur in six branch families per
      chirality,
      `E->E`, `A->E`, `A->A`, `L->E`, `L->A`, and `L->L`; every block is
      multiplicity one and parity pairs the chiral copies.  There are seven
      parity-reduced coefficients through source energy four (five unknown)
      and nineteen through energy six (seventeen unknown).

      C2c-E proves partial tensor/coadjoint covariance of the seeded kernels
      under the independently known `D x SO(4)` oscillator action.  Its
      phase-adjusted raising family is an algebraic Condon--Shortley
      completion, not an independently measured physical adjoint.  This is
      not full `SO(4,2)` equivariance: a bilinear charge kernel has not yet
      been converted into its Hamiltonian generator by the required
      symplectic/Poisson normalization.

      C2d finds that the four-mode cancellation is regular for this seeded
      Taub-constraint map only: its Wirtinger rank is four and its real rank
      is eight in the full 36-complex-dimensional low-mode sum.  This real
      rank uses the ordinary coefficient slice `zbar=conj(z)`, not a certified
      globally reduced `J_conf` real slice.  The seeded real tangent has
      dimension 64; the independently known `D x SO(4)` orbit has rank seven
      and lies in it, leaving a merely formal tangent-space vector quotient
      count 57.  These numbers are not dimensions of a quotient manifold or
      the physical phase space because the other charge blocks, seven Killing
      constraints, and proper-conformal orbit directions are absent.

      C2e constructs the universal algebra-only minimal BRST complex from the
      exact fifteen-generator conformal structure constants.  The ghost,
      formal-adjoint, and ghost-momentum differentials are nilpotent; ghost
      number rises by one and compact-energy degree is zero.  This does not
      represent the charges on pure-Weyl oscillator/Fock states, combine them
      with local Diff x Weyl BRST, compute cohomology, or induce a pairing.

      C2f-N derives the action-normalized oscillator form in the exact C2a
      wave coordinates.  Hamada--Horata's canonical form is
      `G_HH=diag(+E,-A,-L)` with unit magnitudes; for the literal reduced
      action used by C2a,
      `G_red=-G_HH/2` and `J_comm_red=-2 G_HH`.  The seeded CK component has
      the exact phase `xi_repo=-i sqrt(2)/pi xi_HH`, and both independent
      curvature kernels generate the published oscillator action after the
      mixed-polarization and target-sign maps.  This closes the normalization
      bridge rather than fitting one coefficient.

      C2f-A solves the actual proper-conformal generator ansatz through source
      energy four.  All sixteen `[K^-,K^+]` brackets close on the complete
      energy-two and energy-three interior for both chiralities; the invariant
      lowering--raising products are
      `(96/5,-16/5,35,-2,18,-1,4)`.  The algebra forces `E` to have the
      opposite sign from `A/L`.  In canonical normalization the seven
      lowering coefficients are
      `(4 sqrt(6/5),4/sqrt(5),sqrt(35),sqrt(2),3sqrt(2),-1,2)`.

      C2f-M assembles the seven compact kernels and eight proper-CK kernels
      into a 132-dimensional, two-chirality fifteen-component moment-map jet
      through source energy four.  For `Omega=i dzbar J wedge dz`, every
      kernel obeys `M_X=J K_X`; compact kernels are Hermitian, raising kernels
      are lowering daggers, and the exact interior algebra passes.  The raw
      parity-reduced Taub coefficients are now fixed to
      `(-2sqrt(15)/(5pi),-sqrt(10)/(5pi),-sqrt(70)/(4pi),-1/(2pi),`
      `3/(2pi),sqrt(2)/(4pi),sqrt(2)/(2pi))`; the two direct-curvature seeds
      are reproduced independently.  The former four-mode seeded
      cancellation still kills all proper-CK lowering values but has
      `mu_D=-6` and `mu_Rz=-3`, so it is not on the full conformal zero locus.
      The energy-four cutoff is only a buffer: closure on its top states needs
      source-energy-five blocks, and no finite-cutoff cohomology is claimed.

      C2g-W/A identifies the complete oscillator tower with the two chiral
      on-shell Weyl-curvature modules.  Per chirality its exact character is
      `V(2;2,0)-V(4;1,1)+V(5;1/2,1/2)`, and the all-level proper-conformal
      coefficients close exactly on every finite-buffer interior.  The hard
      energy-five/six dimensions are `136,202` after parity, with cumulative
      one-particle dimension `470` through energy six.

      C2g-R/F/N then closes the first cutoff-complete free residual-BRST
      window.  The complete matter-weight-four Fock shell has dimension 137
      and signature `(97,40)`.  Its relative primary-scalar kernel is exactly
      the two normalized chiral Weyl-square states and has matter Gram `I2`.
      Independently, the absolute global-only one-particle window
      `290 -> 1311 -> 3657` is acyclic, while the particle-number-two window
      `0 -> 55 -> 385 -> 1155` has exact outgoing rank 53 and no incoming
      space.  The matter-vacuum `H4` vanishes by semisimple Lie-algebra
      cohomology.  Thus the complete
      centered free-Fock result is
      `H4_delta=0=span{W_+^2,W_-^2}`.

      C2g-G constructs Hamada's residual ghost polarization explicitly.
      The eight dynamic ghosts have inserted-form signature `(128,128)`, the
      centered degree-four block has `(35,35)`, and the selected ghost vacuum
      has norm `+1`.  Consequently the exact **global-only residual** class
      Gram is `I2`.  This is not yet the full pure-Weyl physical pairing:
      the fixed insertion is degenerate on the unrestricted fifteen-ghost
      exterior algebra, and the local Diff x Weyl BV zero-mode split and
      anomaly conditions remain unproved.

      C2g-Cartan supplies the structural simplification.  On total compact
      degree `delta`, `d i_D+i_D d=delta I`, so every `delta != 0` absolute
      residual sector is contractible.  The matter-weight-six target has
      `delta=6-4=2`; its 53,056-dimensional middle cochain space therefore
      has zero cohomology without rank reduction.  The provisional compact
      quartic oscillator block is not a physical absolute-global block when
      cylinder time translation is gauged.  It remains meaningful only in a
      fixed-cylinder or boundary setting where `D` is retained as a physical
      charge.  The vacuum coefficient needs no matrix rail:
      `H*(so(4,2);C)=Lambda(u3,u5,u7)`, so `H4=0`.  Since the ghost floor is
      `-4` and every particle has weight at least two, the N=0,1,2 results
      exhaust the centered minimal free residual complex:
      `H4_residual,min=span{W_+^2,W_-^2}` with Gram `I2`.

      C2h formulates the exact bridge criterion.  The local pure-Weyl
      contraction must be a strong deformation retract in the category of
      compact-energy-graded complexes.  Cyclic HPL is no longer a separate
      norm calculation: in the repo's plus-sign convention an exact dressed
      fixture proves `I^sharp=P`, `PI=1`, `I^sharp I=1`, and skew-adjointness
      of the nonzero transferred differential.  A finite-dimensional cyclic
      SDR exists algebraically once the local kernel has a nondegenerate
      induced form.  The field-theory choice must still be made jointly
      `D`-equivariant, zero-mode compatible, and well defined on the chosen
      domains.

      C2i-D now fixes the formal local detour input.  Branson--Gover gives the
      self-adjoint `K -> B_lin -> K^sharp` complex on Bach-flat backgrounds;
      on the conformally flat cylinder the reduced Weyl-squared action gives
      the stronger action-normalized identity `B_lin=C1^sharp C1`.  Exact
      action-derived scalar `s,t,u` blocks obey both Ward kernels and
      frequency adjointness.  A complementary Euclidean homogeneous-jet
      calculation separates all fifteen conformal-Killing zero modes and
      constructs exact `K,C1,B1` matrices through the finite buffer, with
      quotient ranks `(10,40,82,136,202)` at degrees two through six,
      matching the independent `E/A/L` character exactly.  These are
      formal/finite rails, not yet the all-level Lorentzian cylinder theorem.

      C2j-D fixes the interpretation of the centered `I2`.  Hamada's
      residual formulas give the exact top-degree descent
      `[omega V4] <-> [integral V4]`; hence the two chiral Weyl-square
      survivors are positive residual vertex/deformation classes, not a
      propagating graviton Hilbert space.  In the parity basis they are the
      Weyl-square coupling and the Pontryagin/theta direction (with the
      Lorentzian `i` convention explicit).  The literature-seeded,
      parity-preserving **projected type-B** one-loop map has rank one,
      `(199/30,0)`.  This is not the full anomaly map: the independent
      type-A Euler class requires a general curved-background local-BV
      calculation.  Hamada's `-1/15` Riegert contribution gives the exact
      beta-numerator arithmetic `197/30`, while Riegert dressing permits
      higher matter weights to return to total weight four and therefore
      destroys the strict pure-Weyl finite inventory.  Tseytlin's regulated
      2013 all-spin CHS `a` sum vanishes in its zeta prescription; a later
      `S4_q` calculation selects the `r=-1` prescription and reports both
      regulated `a` and `c` sums zero.  Neither free-tower result is an
      interacting anomaly-cancellation theorem.

      C2k separates the coefficient triangle.  For
      `S=kappa t^-2 integral C2` and a signed counterterm numerator `k_ct`,
      `beta_t=-rho k_ct t^3/[2 kappa (4pi)^2]`; this proves that the
      comparison convention `1/(2t^2)` doubles Hamada's `1/t^2`
      normalization before overall action/Wick signs are compared.  The
      trace coefficient follows from a declared evanescent Weyl variation,
      while the local BV/QME coefficients remain undetermined pending a
      direct calculation.  Adjoining `s tau=c_W` makes the type-B class exact.
      On the conformally flat cylinder `tau C2` begins cubically, but the
      type-A WZ action has a nonzero quadratic `tau-tau` block and possible
      `tau E4^(1)[h]` mixing, so the full compensated free complex must be
      recomputed rather than inheriting `I2`.

      C2l-P splits the exact residual pairing as
      `I2=I1_dynamical + I1_topological`.  Chern--Weil transgression proves
      that the parity-odd Pontryagin direction is locally variationally
      trivial; the Euler--Lagrange quotient is the single positive `C2`
      direction.  A theta term is locally a canonical, J-unitary boundary
      phase but can remain globally or at boundaries.  The literature-seeded
      type-B row has the same rank-one support, subject to C2k's unresolved
      direct BV coefficient.

      Next (C2i): prove the remaining local-kernel identification
      `ker B_lin / im K = W_+ + W_-` on complete Lorentzian cylinder harmonic
      blocks and eliminate all relevant local/nonminimal doublets.  Then
      choose the simultaneous `D`-equivariant cyclic retract and derive the
      transferred one-ghost/two-matter term as the normalized Taub moment map
      `M_Taub=-sqrt(2)/(4pi) J K^-`, alongside the universal residual ghost
      differential and its `-4` vacuum shift.  Finally show the local/global
      spectral sequence collapses in the centered row.  Only after that
      should an interaction act on the reduced classes.  Quantum survival
      separately requires an anomaly-free nilpotent Diff x Weyl BRST charge.
      The flat `P_0` Jordan cokernel and noncompact/boundary scattering remain
      distinct problems.
    - NEXT (ON5, precise spec): boundary Born-trace evaluation —
      build the mapped process operator A_s = Σ(T_s)_xy|x_s⟩⟨y_s|
      on a truncated charge-Fock space with the squeezed vacuum;
      charge-decompose; verify the obstruction coefficient never
      enters the boundary NEUTRAL component B_0; compute τ(B_s†B_s)
      vs τ_φ(A_s†A_s), including the first ε/g correction. Use an
      on-shell path to the BT point, naturally m_L = 4s, m_H = 6s,
      |k_out| = 3s, μ² = 26s², εg = 100s⁴, and prove the s → 0 limit
      rather than varying only the embedding while holding the split
      DQ8 matrix fixed. This yields the obstruction-to-null theorem
      (paper-5 capstone). Machinery: cross-paired Gram + graded trace
      from ON1, map from ON2, squeezing from ON3.
    - GRAVITY RAIL STATUS: the originally proposed M→h+h test is now
      closed (zero by Einstein truncation), cubic order is protected,
      and G17 proves the second-order MM→Mh positive-metric obstruction.
      G18 rules out nullity for the canonical natural,
      particle-number-diagonal cluster-multiplicative lift induced on
      physical BRST cohomology.  Paper 6 is drafted and post-review
      revised; do not broaden its no-go beyond those explicit classes.
    - DEFERRED, not in the active queue: vacuum-overlap / superselection
      at r = 0; normal-ordered internal-charge Ward identity;
      confluent-state R₁ matrix elements; field-theory complex-spectrum
      question; 5:3 at order 6 and the even-mode-2-transfer exclusion
      mechanism. Do not extend the doubled-scalar reconstruction before
      the Einstein–Weyl calculation.
