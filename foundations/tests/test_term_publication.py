"""Publication boundaries independent of NLP extraction."""
import gzip
import json
import unittest
from foundations.term_review import ROOT, publication_candidates


class PublicationTests(unittest.TestCase):
    def test_frequency_boundary_and_dictionary_exception(self):
        candidates=[dict(id=name,occurrences=[[i,0,1] for i in range(count)],dictionary_ids=ids)
                    for name,count,ids in [('rare',4,[]),('eligible',5,[]),('defined',1,['aca'])]]
        published=publication_candidates(candidates)
        self.assertEqual([c['id'] for c in published],['eligible','defined'])
        self.assertNotIn('global_occurrence_count',candidates[1])

    def test_published_scopes_use_global_counts_and_valid_contexts(self):
        raw=json.load(gzip.open(ROOT/'foundations/results/TERM_EXTRACTION_V1.json.gz'))
        expected={c['id']:c for c in publication_candidates(raw['candidates'])}
        self.assertTrue(any(c['phrase']=='pointwise polynomial identity' for c in raw['candidates']))
        for scope in ['all','ladder','matrix','atlas','reading','dictionary','papers']:
            data=json.load(gzip.open(ROOT/f'foundations/site/term-candidates-{scope}.json.gz'))
            units={u['id'] for u in raw['units'] if scope=='all' or u['scope']==scope}
            self.assertEqual({c['id'] for c in data['candidates']},
                             {key for key,c in expected.items() if any(o[0] in units for o in c['occurrences'])})
            self.assertEqual(data['publication_filter']['published_candidates'],len(expected))
            for c in data['candidates']:
                self.assertEqual(c['global_occurrence_count'],len(expected[c['id']]['occurrences']))
                for unit,start,end in c['occurrences']:
                    self.assertTrue(0<=start<end<=len(data['units'][str(unit)]['text']))
