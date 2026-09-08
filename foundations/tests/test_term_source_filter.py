import unittest
from foundations.term_source_filter import source_spans,prose_text

class SourceFilterTests(unittest.TestCase):
    def fragments(self,text,markdown=False):
        ranges,excluded,kept=source_spans(text,['ACA0','RCA0'],markdown)
        for a,b in ranges:
            self.assertFalse(any(a<e['end'] and b>e['start'] for e in excluded))
        return [prose_text(text[a:b]) for a,b in ranges],excluded,kept
    def test_math_and_citations_keep_surrounding_prose(self):
        raw=r'''Cauchy sequence $A^2B^2$ and Weyl curvature.
\[\begin{aligned}N_{28}^{123}&=A^2B^2C^2(2A-B-C)\end{aligned}\]
so the quotient relation is a pointwise polynomial identity.
A result~\citep[Section 2]{AbbottGW17,Other} remains useful.
\begin{thebibliography}{99}
\bibitem{AbbottGW17} B.~P.~Abbott et al. A title.
\end{thebibliography}'''
        fragments,excluded,_=self.fragments(raw);text=' '.join(fragments)
        for bad in ['Abbott','GW17','A^2','aligned','N_']:self.assertNotIn(bad,text)
        for good in ['Cauchy sequence','Weyl curvature','pointwise polynomial identity','remains useful']:self.assertIn(good,text)
        self.assertEqual({e['reason'] for e in excluded},{'MATH','CITATION','BIBLIOGRAPHY'})
    def test_math_delimiters_comments_and_registered_symbols(self):
        raw=r'''Keep $\mathsf{ACA}_0$ and \(\mathrm{RCA}_0\).
% not a closing delimiter \]
\[ x=1 % \] in comment
 +2\] Keep this. $$y^2=z$$ \(u+v\)'''
        fragments,excluded,kept=self.fragments(raw);text=' '.join(fragments)
        self.assertIn('ACA0',text);self.assertIn('RCA0',text);self.assertIn('Keep this.',text)
        self.assertNotIn('in comment',text);self.assertNotIn('x=1',text)
        self.assertEqual(len(kept),2)
        self.assertFalse(any(e.get('unclosed') for e in excluded))
    def test_attributions_are_not_a_surname_blacklist(self):
        raw='B. P. Abbott et al., observations. Weyl curvature and Cauchy sequences; Noether theorem. Abbott et al. report this.'
        fragments,excluded,_=self.fragments(raw);text=' '.join(fragments)
        self.assertNotIn('Abbott',text)
        for concept in ['Weyl curvature','Cauchy sequences','Noether theorem']:self.assertIn(concept,text)
        self.assertEqual(len(excluded),2)
    def test_code_and_bibliography_markdown(self):
        raw='Wave equation.\n\n```python\nAbbottGW17 = 2\n```\n\nCauchy sequence `key_123` [@AbbottGW17].\n## References\nAbbott author.\n## Appendix\nWeyl curvature.'
        fragments,_,_=self.fragments(raw,True);text=' '.join(fragments)
        self.assertNotIn('Abbott',text);self.assertNotIn('key_123',text)
        self.assertIn('Cauchy sequence',text);self.assertIn('Weyl curvature',text)
    def test_unclosed_math_is_not_prose(self):
        fragments,excluded,_=self.fragments(r'Good prose. \[ A^2 unfinished')
        self.assertEqual(' '.join(fragments),'Good prose.')
        self.assertTrue(excluded[0]['unclosed'])
    def test_catalog_citation_and_keys(self):
        citation='Vasco Brattka, A paper title (2008).'
        raw=r'\hypertarget{atlas-evidence-41}{\cert{brattka-2008}}. '+citation+' Cauchy sequence remains.'
        ranges,excluded,_=source_spans(raw,citations=[citation])
        text=' '.join(prose_text(raw[a:b]) for a,b in ranges)
        self.assertNotIn('Brattka',text);self.assertNotIn('brattka-2008',text)
        self.assertNotIn('atlas-evidence',text);self.assertIn('Cauchy sequence',text)
        self.assertTrue(any(e['reason']=='BIBLIOGRAPHIC_RECORD' for e in excluded))
    def test_literal_percent_preserves_following_prose(self):
        fragments,_,_=self.fragments(r'20\% of the energy is retained.')
        self.assertIn('20% of the energy is retained.',' '.join(fragments))
    def test_escaped_symbolic_names_are_not_equations(self):
        fragments,_,_=self.fragments(r'RCA\_0 and ACA\_0 support a Cauchy sequence.')
        self.assertEqual(' '.join(fragments),'RCA0 and ACA0 support a Cauchy sequence.')
    def test_table_markup_preserves_terms(self):
        fragments,_,_=self.fragments(r'\begin{tabularx}{\textwidth}{@{}Yrrrr@{}} Weyl curvature & Cauchy sequence \\ \end{tabularx}')
        text=' '.join(fragments);self.assertIn('Weyl curvature',text);self.assertIn('Cauchy sequence',text)
        self.assertNotIn('Yrrrr',text);self.assertNotIn('tabularx',text)
    def test_code_and_macro_bodies(self):
        raw=r'\newcommand{\foo}[1]{x^{#1}} \verb|a_b $not math$| \begin{verbatim}AbbottGW17\end{verbatim} Genuine prose.'
        fragments,_,_=self.fragments(raw);text=' '.join(fragments)
        self.assertIn('Genuine prose.',text);self.assertNotIn('Abbott',text);self.assertNotIn('not math',text)

if __name__=='__main__':unittest.main()
