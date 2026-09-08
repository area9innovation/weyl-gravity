"""Check corpus boundaries and independently count a sample term family."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from foundations import build_term_inventory as inventory

class InventoryTests(unittest.TestCase):
    def test_corpus_and_counts(self):
        result=json.loads(inventory.OUT.read_text())
        cells=json.loads((inventory.ROOT/'foundations/site/data.json').read_text())['cells']
        self.assertEqual(len(cells),576)
        state=next(t for t in result['candidates'] if t['term']=='state')
        # Independent raw prose count: this family is unaffected by TeX normalization.
        matching=[c for c in cells if re.search(r'\bstates?\b',' '.join(c.get(k,'') for k in ['summary','boundary','migration_rationale']),re.I)]
        self.assertEqual(state['cell_count'],len(matching))
        for path,digest in result['inputs_sha256'].items():
            self.assertEqual(hashlib.sha256((inventory.ROOT/path).read_bytes()).hexdigest(),digest,path)
        docs,_=inventory.corpus()
        paper_paths=[Path(d['source']) for d in docs if d['kind']=='paper']
        self.assertTrue(all(p.suffix in ['.tex','.md'] for p in paper_paths))
        self.assertFalse(any(p.suffix=='.md' and (inventory.ROOT/p.with_suffix('.tex')).exists() for p in paper_paths))
        self.assertEqual(len({d['id'] for d in docs}),len(docs))
    def test_tex_normalization(self):
        self.assertEqual(inventory.normalize(r'\mathsf{RCA}_0 and ACA₀'), 'RCA0 and ACA0')
        self.assertEqual(inventory.normalize(r'word \label{private-key} more'), 'word more')

if __name__=='__main__':unittest.main()
