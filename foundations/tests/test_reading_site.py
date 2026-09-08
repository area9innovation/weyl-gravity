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


if __name__=='__main__':unittest.main()
