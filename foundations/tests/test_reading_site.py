import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from foundations import reading_site
from foundations.verify_reading_site import verify


class ReadingTests(unittest.TestCase):
    def test_independent_structure(self):verify()
    def test_stale_sources_and_missing_editions_fail_build(self):
        d=reading_site.load()
        for kind in ['source','audience','section']:
            v=copy.deepcopy(d)
            if kind=='source':v['sources']['repair']['sha256']='0'*64
            if kind=='audience':del v['topics']['wave']['versions']['mathematics']
            if kind=='section':v['topics']['wave']['versions']['general'][0]['id']='different'
            with tempfile.TemporaryDirectory() as tmp:
                p=Path(tmp)/'content.json';p.write_text(json.dumps(v))
                with self.subTest(kind=kind),patch.object(reading_site,'CONTENT',p),self.assertRaises(ValueError):reading_site.load()

    def test_dictionary_review_gates(self):
        d=json.loads(reading_site.DICTIONARY.read_text())
        for kind in ['source','perspective','duplicate','related','abbreviation']:
            v=copy.deepcopy(d)
            if kind=='source':v['terms'][0]['sources'][0]['sha256']='0'*64
            if kind=='perspective':del v['terms'][0]['explanations']['physics']
            if kind=='duplicate':v['terms'].append(copy.deepcopy(v['terms'][0]))
            if kind=='abbreviation':v['terms'][0]['definitions']['general']='An unexplained abbreviation.'
            if kind=='related':v['terms'][0]['related']=['missing']
            with tempfile.TemporaryDirectory() as tmp:
                p=Path(tmp)/'dictionary.json';p.write_text(json.dumps(v))
                with self.subTest(kind=kind),patch.object(reading_site,'DICTIONARY',p),self.assertRaises(ValueError):reading_site.load()

    def test_dictionary_crosslinks_are_safe_and_not_self_links(self):
        terms=json.loads(reading_site.DICTIONARY.read_text())['terms']
        text=reading_site.linked_text('ACA₀ uses RCA₀; RCA₀ < x. XACA₀',terms,'aca')
        self.assertEqual(text.count('class="dictionary-crosslink"'),1)
        self.assertIn('term-rca.html',text)
        self.assertIn('&lt;',text)
        self.assertNotIn('term-aca.html',text)


if __name__=='__main__':unittest.main()
