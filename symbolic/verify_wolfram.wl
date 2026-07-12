(* Independent Wolfram-Language audit of the core identities.
   Constructs every matrix from scratch (do NOT paste SymPy output here).
   Run:  wolframscript -file verify_wolfram.wl
   Not yet executed in this repository: no Mathematica installation available.
   Kept as the second-CAS rail required by spec section 17. *)

$Assumptions = gamma > 0 && w1 > w2 > 0;

J  = {{0,0,1,0},{0,0,0,1},{-1,0,0,0},{0,-1,0,0}};
G  = {{gamma (w1^2+w2^2),0,0,-I},{0,gamma w1^2 w2^2,0,0},{0,0,1/gamma,0},{-I,0,0,0}};
G0 = DiagonalMatrix[{gamma w1^2, gamma w1^2 w2^2, 1/gamma, 1/(gamma w1^2)}];

r     = Log[(w1+w2)/(w1-w2)];
alpha = r/(gamma w1 w2);
beta  = alpha gamma^2 w1^2 w2^2;
M  = {{0,beta,0,0},{beta,0,0,0},{0,0,0,alpha},{0,0,alpha,0}};
K  = J.M;

check[id_, expr_] := Print[id, ": ",
  If[Simplify[expr] === True || Simplify[expr] == 0 ||
     (MatrixQ[expr] && AllTrue[Flatten[Simplify[expr]], # == 0 &]),
     "PROVED_SYMBOLICALLY", "FAILED"]];

(* A: Hamiltonian matrix and spectrum *)
check["A1", Simplify[Expand[({x,y,p,q} . G . {x,y,p,q})/2
   - (p^2/(2 gamma) - I q x + gamma/2 (w1^2+w2^2) x^2 + gamma/2 w1^2 w2^2 y^2)]];
check["A2", Simplify[CharacteristicPolynomial[J.G, lam]
   - Expand[(lam^2+w1^2)(lam^2+w2^2)]]];

(* B: r identity *)
check["B2", Simplify[alpha beta - r^2]];

(* C: K^2 = -r^2 *)
check["C1", Simplify[K.K + r^2 IdentityMatrix[4]]];

(* D: exponential, symplecticity, determinant *)
S = MatrixExp[I K/2];                        (* independent: MatrixExp, not the formula *)
Scand = Cosh[r/2] IdentityMatrix[4] + I (K/r) Sinh[r/2];
check["D1", FullSimplify[S - Scand]];
check["D2", FullSimplify[Transpose[S].J.S - J]];
check["D3", FullSimplify[Det[S] - 1]];

(* E: congruence and flow *)
check["E1", FullSimplify[Transpose[S].G.S - G0]];
check["E2", FullSimplify[Inverse[S].(J.G).S - J.G0]];

(* G: matrix-level pseudo-Hermiticity  S^{2T} G S^2 == conj(G) *)
S2 = S.S;
check["G1", FullSimplify[Transpose[S2].G.S2 - Conjugate[G],
  Element[{gamma,w1,w2}, Reals]]];

(* J: spectrum of S'^dag S' after the canonical rescaling *)
d  = Sqrt[gamma w1 w2];
Dm = DiagonalMatrix[{d,d,1/d,1/d}];
Sp = Dm.S.Inverse[Dm];
check["J1_hermitian", FullSimplify[Sp - ConjugateTranspose[Sp],
  Element[{gamma,w1,w2}, Reals]]];
Print["J2 spectrum: ", FullSimplify[Eigenvalues[ConjugateTranspose[Sp].Sp]]];
(* expected {E^r, E^r, E^-r, E^-r} *)
