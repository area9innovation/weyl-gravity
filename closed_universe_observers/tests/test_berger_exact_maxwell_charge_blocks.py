from fractions import Fraction
import sympy as sp
from closed_universe_observers.generate_berger_exact_maxwell_charge_blocks import charge_block,delta_row,scalar_eigenvalue
def test_block_dimensions_and_hermiticity():
 for tj in range(10):
  j=Fraction(tj,2)
  for n in range(-tj-2,tj+3,2):
   q=Fraction(n,2);members,B=charge_block(tj,q)
   if members:assert 1<=len(members)<=3;assert B==B.conjugate().T
def test_extreme_block_and_scalar_formula():
 members,B=charge_block(138,Fraction(70));assert len(members)==1;assert B[0,0]==sp.Rational(196000,9);assert scalar_eigenvalue(138,Fraction(69))>0
def test_delta_extreme_charge_vanishes():
 members,D=delta_row(138,Fraction(70));assert members and D==D.zeros(1,len(members))
