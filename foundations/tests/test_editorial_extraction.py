import gzip,hashlib,json,tempfile,unittest
from unittest.mock import patch
from pathlib import Path
from foundations.extract_editorial_terms import ROOT,OUT,check_cached,paper_paths
from foundations.import_editorial_vocabulary import OUT as VOCAB,generate

class ExtractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=json.loads(gzip.decompress(OUT.read_bytes()))
    def test_vocabulary_reproduction(self):self.assertEqual(VOCAB.read_bytes(),generate())
    def test_source_freshness(self):check_cached()
    def test_stale_input_fails_closed(self):
        data=dict(self.data);data['inputs_sha256']=dict(self.data['inputs_sha256']);data['inputs_sha256']['foundations/editorial/dictionary.json']='0'*64
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'stale.json.gz';path.write_bytes(gzip.compress(json.dumps(data).encode(),mtime=0))
            with patch('foundations.extract_editorial_terms.OUT',path):
                with self.assertRaisesRegex(ValueError,'Extraction stale'):check_cached()
    def test_new_paper_requires_extraction(self):
        with patch('foundations.extract_editorial_terms.paper_paths',return_value=paper_paths()+[ROOT/'paper/new-source.tex']):
            with self.assertRaisesRegex(ValueError,'paper corpus membership changed'):check_cached()
    def test_spans_and_matches(self):
        d=self.data;dictionary=json.loads((ROOT/'foundations/editorial/dictionary.json').read_text())['terms']
        aliases={t['id']:{a.casefold() for a in t['aliases']} for t in dictionary}
        vocabulary={t['id']:{a.casefold() for a in t['aliases']} for t in json.loads(VOCAB.read_text())['terms']}
        for c in d['candidates']:
            self.assertTrue(any(ch.isalpha() for ch in c['phrase']))
            self.assertGreaterEqual(len(c['phrase'].strip()),2)
            self.assertEqual(c['review_state'],'UNREVIEWED')
            self.assertEqual(set(c['perspectives']),{'general','physics','mathematics','specialist'})
            for unit,start,end in c['occurrences']:
                text=d['units'][unit]['text'][start:end]
                self.assertEqual(' '.join(text.casefold().split()),' '.join(c['phrase'].casefold().split()))
            for id in c['dictionary_ids']:self.assertIn(c['phrase'].casefold(),aliases[id])
            for id in c['vocabulary_ids']:self.assertIn(c['phrase'].casefold(),vocabulary[id])
        self.assertFalse(d['scientific_claims_promoted'])
        self.assertTrue(any('keyphrase-vectorizers' in c['methods'] for c in d['candidates']))
        self.assertTrue(any('spacy-noun-phrase' in c['methods'] for c in d['candidates']))
        self.assertTrue(any(c['vocabulary_ids'] for c in d['candidates']))
    def test_user_ladder_example(self):
        fixture=json.loads((ROOT/'foundations/tests/fixtures/ladder-explanation-coverage.json').read_text())
        unit_ids={u['id'] for u in self.data['units'] if u['scope']=='ladder' and u['location'].startswith('/ladder/0/')}
        present={c['phrase'].casefold() for c in self.data['candidates'] if any(o[0] in unit_ids for o in c['occurrences'])}
        for phrase in fixture['required_candidates']+fixture['required_explanation_units']:
            self.assertIn(phrase.casefold(),present,phrase)
        self.assertFalse(any('fixtures/' in p for p in self.data['inputs_sha256']))

if __name__=='__main__':unittest.main()
