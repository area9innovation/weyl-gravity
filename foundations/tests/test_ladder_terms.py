import hashlib,json,unittest
from foundations import ladder_terms

class LadderTermsTests(unittest.TestCase):
    def test_index_has_exact_source_locations(self):
        root=ladder_terms.ROOT
        index=json.loads((root/'foundations/site/ladder-terms.json').read_text())
        steps=json.loads((root/'foundations/site/data.json').read_text())['ladder']
        by_level={s['level']:s for s in steps}
        self.assertEqual(index['stage_count'],len(steps))
        self.assertEqual(index['terms'],sorted(index['terms'],key=lambda t:t['label'].casefold()))
        self.assertEqual(len({t['id'] for t in index['terms']}),index['term_count'])
        for term in index['terms']:
            self.assertTrue(term['matches'])
            for match in term['matches']:
                raw=by_level[match['level']]
                # Independently locate the exact display text in the original record.
                strings=[text for value in raw.values() for text in (value if isinstance(value,list) else [value]) if isinstance(text,str)]
                self.assertIn(match['text'],strings)
                self.assertIn(match['text'][match['start']:match['end']].casefold(),[a.casefold() for a in term['aliases']])
        for path,digest in index['input_hashes'].items():
            self.assertEqual(hashlib.sha256((root/path).read_bytes()).hexdigest(),digest)
        self.assertTrue(any(m['field']=='separation' for t in index['terms'] for m in t['matches']))
        self.assertTrue(any(m['field']=='excluded' and m['level'].startswith('L3') for t in index['terms'] for m in t['matches']))
    def test_conditional_fields_are_included(self):
        step=dict(level='X',status='OPEN',object='object',candidate_upper_bound='upper',establishes_if_formalized=['conditional'],open=['not proved'],separation='important distinction')
        self.assertIn(('base','upper'),ladder_terms.displayed_fields(step))
        self.assertIn(('establishes','conditional'),ladder_terms.displayed_fields(step))
        self.assertIn(('excluded','not proved'),ladder_terms.displayed_fields(step))
        self.assertIn(('separation','important distinction'),ladder_terms.displayed_fields(step))

if __name__=='__main__':unittest.main()
