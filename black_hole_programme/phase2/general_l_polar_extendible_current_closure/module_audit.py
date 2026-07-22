"""Bounded exact algebra for the polar homogeneous-module audit.

The four-state Bach master is deliberately kept distinct from the seven-row
source-zero Ricci kernel.  Conflating them changes the current basis count.
"""

from __future__ import annotations

import sympy as sp


def literal_current_shape(expression: str) -> dict:
    r = sp.Symbol("r")
    names = ["FAa_r", "FBa_r", "FCa_r", "FKa_r", "FAb_r", "FBb_r", "FCb_r", "FKb_r"]
    local = {name: sp.Function(name) for name in names}
    local.update({name: sp.Symbol(name) for name in ("Lambda", "m", "omega", "alpha", "ell")})
    local.update({"r": r, "I": sp.I, "pi": sp.pi, "Derivative": sp.Derivative})
    value = sp.sympify(expression, locals=local)
    numerator, _ = sp.fraction(value)
    terms = sp.Add.make_args(sp.expand(numerator))
    signatures = set()
    for term in terms:
        atoms = [(f.func.__name__, 0) for f in term.atoms(sp.Function) if f.func.__name__ in names]
        for derivative in term.atoms(sp.Derivative):
            if derivative.expr.func.__name__ in names:
                atoms = [a for a in atoms if a[0] != derivative.expr.func.__name__]
                atoms.append((derivative.expr.func.__name__, sum(n for _, n in derivative.variable_count)))
        signatures.add(tuple(sorted(atoms)))
    return {"expanded_numerator_terms": len(terms), "oriented_field_derivative_signatures": len(signatures)}


def master_infinity_audit() -> dict:
    w, z = sp.symbols("omega z", real=True, nonzero=True)
    A = sp.Matrix([
        [0, sp.I*w/2, sp.Rational(1, 2), sp.I*w],
        [0, 0, 1, 0],
        [0, 0, -2*sp.I*w, 0],
        [0, sp.I*w, sp.Rational(1, 2), 0],
    ])
    return {
        "matrix": [[sp.sstr(x) for x in row] for row in A.tolist()],
        "characteristic_polynomial": sp.sstr(sp.factor(A.charpoly(z).as_expr())),
        "zero_algebraic_multiplicity": 3,
        "zero_geometric_multiplicity": len(A.nullspace()),
        "zero_generalized_nullities": [len((A**k).nullspace()) for k in (1, 2, 3)],
        "oscillatory_geometric_multiplicity": len((A+2*sp.I*w*sp.eye(4)).nullspace()),
    }


def polynomial_master_ricci_residual() -> dict:
    """Exact seven-row residual of the advertised polynomial Bach-master mode."""
    L, w, r, k, a0 = sp.symbols("Lambda omega r kappa a0", nonzero=True)
    angp = (L*k + 2*a0 - 2*k)/(2*r**2)
    vv = sp.I*(-sp.I*L*a0 + L*k*w*r + 2*a0*w*r - 2*k*w*r + 6*k*w)/(2*r**2)
    a_for_angp = (2-L)*k/2
    vv_after = sp.factor(vv.subs(a0, a_for_angp))
    return {
        "mode": "Ch=Bh=0, Kh=kappa, Ah=I*omega*kappa*r+a0",
        "nonzero_rows": {"angP": sp.sstr(angp), "vv": sp.sstr(vv)},
        "angP_zero_choice": sp.sstr(a_for_angp),
        "remaining_vv_residual": sp.sstr(vv_after),
        "physical_domain_reading": (
            "The polynomial four-state Bach-master direction is not a nontrivial "
            "source-zero seven-Ricci-row direction for generic Lambda=ell(ell+1), "
            "ell>=2 and real omega!=0."
        ),
    }


def shallow_log_audit() -> dict:
    L, w = sp.symbols("Lambda omega", real=True, nonzero=True)
    defect = 3*L - 48*w**2 + 15 + 12*sp.I*w
    return {
        "defect": sp.sstr(defect),
        "imaginary_part": sp.sstr(sp.im(defect)),
        "nowhere_zero": sp.simplify(sp.im(defect)/(12*w)) == 1,
        "disposition": "NONEXTENDIBLE_SHALLOW_SOURCE_ARTIFACT",
    }


def _differentiate_profile(coeffs, beta, rate, order):
    out=list(coeffs)
    for _ in range(order):
        nxt=[sp.Integer(0)]*(len(out)+1)
        for n,c in enumerate(out):
            nxt[n] += rate*c
            nxt[n+1] += (beta-n)*c
        out=[sp.expand(x) for x in nxt]
    return out


def current_layer_table(current_expression: str, profiles: dict, minimum_power=-1,
                        sector_filter=None, pair_filter=None) -> dict:
    """Accumulate the literal current by radial layer, cancelling once/layer."""
    r=sp.Symbol('r'); L=sp.Symbol('Lambda',real=True); w=sp.Symbol('omega',real=True,nonzero=True)
    alpha=sp.Symbol('alpha'); ell=sp.Symbol('ell',integer=True)
    names=['FAa_r','FBa_r','FCa_r','FKa_r','FAb_r','FBb_r','FCb_r','FKb_r']
    funcs={n:sp.Function(n) for n in names}
    local={**funcs,'r':r,'Lambda':L,'m':sp.Integer(1),'omega':w,'alpha':alpha,'ell':ell,'I':sp.I,'pi':sp.pi,'Derivative':sp.Derivative}
    expr=sp.sympify(current_expression,locals=local)
    pref=4*sp.pi*alpha/(3*(2*ell+1))
    terms=sp.Add.make_args(sp.expand(sp.cancel(expr/pref)))

    def slot(term):
        ds=list(term.atoms(sp.Derivative)); occupied={d.expr for d in ds}
        atoms=[(d.expr.func.__name__,sum(n for _,n in d.variable_count),d) for d in ds]
        atoms += [(f.func.__name__,0,f) for f in term.atoms(sp.Function) if f.func.__name__ in names and f not in occupied]
        if len(atoms)!=2: raise RuntimeError(f'nonbilinear current term: {term}')
        factor=atoms[0][2]*atoms[1][2]; return atoms,sp.cancel(term/factor)
    parsed=[slot(t) for t in terms]
    field_index={'FA':0,'FB':1,'FC':2,'FK':3}
    result={}
    for sector,modes in profiles.items():
      if sector_filter is not None and sector != sector_filter: continue
      entries={}
      labels=list(modes)
      for ia,a in enumerate(labels):
       for b in labels[ia:]:
        if pair_filter is not None and (a,b) != tuple(pair_filter): continue
        left=modes[a]; right=modes[b]
        prepared=[]; structural_max=None
        for atoms,coef in parsed:
            pieces=[]
            for name,order,_ in atoms:
                is_left=name.endswith('a_r'); stem=name[:2]
                prof=left if is_left else right
                cs=prof['coeffs'][field_index[stem]]
                beta=prof['beta']; rate=prof['rate']
                if not is_left:
                    cs=[sp.conjugate(c).subs({sp.conjugate(L):L,sp.conjugate(w):w}) for c in cs]
                    beta=sp.conjugate(beta).subs({sp.conjugate(L):L,sp.conjugate(w):w})
                    rate=sp.conjugate(rate).subs({sp.conjugate(w):w})
                pieces.append((beta,_differentiate_profile(cs,beta,rate,order)))
            rp=coef.as_powers_dict().get(r,0); c0=coef/r**rp
            nz0=[(n,x) for n,x in enumerate(pieces[0][1]) if x!=0]
            nz1=[(n,y) for n,y in enumerate(pieces[1][1]) if y!=0]
            if not nz0 or not nz1: continue
            top=sp.simplify(pieces[0][0]+pieces[1][0]+rp-nz0[0][0]-nz1[0][0])
            if not top.is_integer: raise RuntimeError(f'noninteger stationary power {top}')
            top=int(top); structural_max=top if structural_max is None else max(structural_max,top)
            prepared.append((pieces,c0,int(rp),nz0,nz1))
        closed={}
        cancelled=[]
        for target in range(structural_max if structural_max is not None else minimum_power,minimum_power-1,-1):
            value=0
            for pieces,c0,rp,nz0,nz1 in prepared:
                offset=int(sp.simplify(pieces[0][0]+pieces[1][0]+rp))
                for n,x in nz0:
                    m=offset-target-n
                    if 0<=m<len(pieces[1][1]): value += c0*x*pieces[1][1][m]
            value=sp.expand(value)
            if value!=0:
                closed[str(target)]=sp.sstr(sp.factor(value))
                break
            cancelled.append(target)
        entries[f'{a}|{b}']={'structural_maximum_power':structural_max,
          'exact_zero_cancellations':cancelled,'layers':closed,
          'leading_power':int(next(iter(closed))) if closed else None,
          'disposition':'DANGEROUS' if closed else 'FINITE_BELOW_P_MINUS_1'}
      result[sector]=entries
    return result
