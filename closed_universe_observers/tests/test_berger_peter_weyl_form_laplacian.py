import sympy as sp
from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import C,block_audit,d_matrix,generators,laplacian
def test_generators_have_berger_commutators()->None:
 g=generators(3);assert sp.simplify(g[0]*g[1]-g[1]*g[0]-C*g[2])==sp.zeros(4);assert sp.simplify(g[1]*g[2]-g[2]*g[1]-g[0]/C)==sp.zeros(4)
def test_de_rham_square_zero()->None:
 for k in range(5):assert all(x==0 for x in block_audit(k)["d_squared_defect_counts"])
def test_laplacians_are_hermitian_and_hodge_dual()->None:
 for k in range(4):
  a=block_audit(k);assert a["all_laplacians_hermitian"];assert a["hodge_dual_spectra_match"]
def test_scalar_spectrum_matches_rods()->None:
 assert block_audit(1)["scalar_eigenvalues"]=={"29/18":2};assert block_audit(2)["scalar_eigenvalues"]=={"49/9":2,"2":1}
def test_harmonic_and_mass_gap_structure()->None:
 assert laplacian(0,0)==sp.zeros(1);assert laplacian(0,3)==sp.zeros(1);assert laplacian(0,1).rank()==3;assert d_matrix(2,1).rows==9
