"""Core coverage and publication boundaries; prose correctness remains editorial."""
import json
from pathlib import Path
import unittest
from foundations import reading_site

ROOT=Path(__file__).resolve().parents[2]


class CoreDictionaryTests(unittest.TestCase):
    def test_implemented_batches_have_four_distinct_accounts_and_links(self):
        proposal=json.loads((ROOT/'foundations/editorial/core-terminology-proposal.json').read_text())
        dictionary=json.loads(reading_site.DICTIONARY.read_text())
        expected={e['id'] for e in proposal['entries'] if e['batch']<=2}
        self.assertEqual({t['core_proposal_id'] for t in dictionary['terms']},expected)
        self.assertEqual(len(dictionary['terms']),143)
        ids={t['id'] for t in dictionary['terms']}
        for term in dictionary['terms']:
            with self.subTest(term=term['id']):
                self.assertEqual(set(term['definitions']),{'general','physics','mathematics','specialist'})
                self.assertEqual(len(set(term['definitions'].values())),4)
                self.assertTrue(set(term['related'])<=ids)
                self.assertGreaterEqual(len(term['related']),2)
                self.assertNotIn(term['id'],term['related'])
                for a,definition in term['definitions'].items():
                    expanded=' '.join(b['text'] for b in term['explanations'][a])
                    self.assertGreaterEqual(len((definition+' '+expanded).split()),40)
                    self.assertNotEqual(definition,expanded)
        self.assertEqual(next(t for t in dictionary['terms'] if t['id']=='field')['auto_annotate'],False)

    def test_base_systems_do_not_annotate_distinct_bare_systems(self):
        terms=json.loads(reading_site.DICTIONARY.read_text())['terms']
        for id,bare in [('aca','ACA'),('rca','RCA')]:
            term=next(t for t in terms if t['id']==id)
            self.assertNotIn(bare,term['aliases'])
            for definition in term['definitions'].values():self.assertIn(term['expansion'],definition)
        text=reading_site.linked_text('ACA and RCA differ from ACA₀ and RCA₀.',terms,'field')
        self.assertEqual(text.count('class="dictionary-crosslink"'),2)
