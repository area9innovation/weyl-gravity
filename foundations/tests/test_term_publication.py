"""Publication boundaries independent of NLP extraction."""
import gzip
import json
import unittest
from foundations.term_review import ROOT, publication_candidates


class PublicationTests(unittest.TestCase):
    @staticmethod
    def candidate(phrase,count,ids=None,start=0):
        return dict(id=phrase,phrase=phrase,kind='term-candidate',
                    occurrences=[[i,0,1] for i in range(start,start+count)],
                    dictionary_ids=ids or [],vocabulary_ids=[],methods=['test'],scopes=['papers'])

    def test_frequency_boundary_and_dictionary_exception(self):
        candidates=[self.candidate('rare phrase',4),self.candidate('eligible phrase',5),
                    self.candidate('defined',1,['aca'])]
        published=publication_candidates(candidates)
        self.assertEqual({c['phrase'] for c in published},{'eligible phrase','defined'})
        self.assertNotIn('global_occurrence_count',candidates[1])

    def test_alias_merge_deduplicates_spans_before_frequency_gate(self):
        candidates=[self.candidate('ACA0',3),self.candidate('ACA_0',3,start=2),
                    self.candidate('ACA₀',1),self.candidate('ACA',5)]
        published=publication_candidates(candidates)
        self.assertEqual({c['phrase'] for c in published},{'ACA₀','ACA'})
        merged=next(c for c in published if c['phrase']=='ACA₀')
        self.assertEqual(merged['global_occurrence_count'],5)
        self.assertEqual(set(merged['aliases']),{'ACA0','ACA_0','ACA₀'})
        self.assertEqual(merged['source_candidate_ids'],sorted(['ACA0','ACA_0','ACA₀']))

    def test_ordinary_single_words_and_technical_exceptions(self):
        words=['absemt','absent','absence','absolute','Appendix','cohomology','graviton','absolute continuity']
        candidates=[self.candidate(word,10) for word in words]
        external=self.candidate('externalword',5);external['vocabulary_ids']=['test-vocabulary']
        published=publication_candidates([*candidates,external])
        self.assertEqual({c['phrase'] for c in published},
                         {'cohomology','graviton','absolute continuity','externalword'})

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
