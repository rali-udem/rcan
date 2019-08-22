import bz2

import orjson
import os
import pickle
import sys

from donnees import rcan_coll
from donnees.rcan_coll import *

_ref_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'donnees', 'resources')


def main():
    if len(sys.argv) < 3:
        print("Usage: prog coll_dir predictions.json+")
        sys.exit(1)

    coll_dir = sys.argv[1]
    pred_files = sys.argv[2:]

    theme_refs = pickle.load(bz2.open(os.path.join(_ref_path, 'ref-rcan-themes.pkl.bz2'), 'rb'))
    rows = {}
    sys_names = []

    for pred_file in pred_files:
        preds = orjson.loads(open(pred_file, 'r', encoding='utf-8').read())
        sys_names.append(pred_file)

        for raw_doc_id, info in preds.items():
            doc_id = int(raw_doc_id)
            pred_theme = info["theme"][0][0]
            row = rows.get(doc_id, {'ref_theme': theme_refs[doc_id][0],
                                    'url': RDocument(orjson.loads(open(os.path.join(coll_dir, str(doc_id) + ".json"), 'r').read())).url,
                                    'preds': []})
            row['preds'].append(pred_theme)
            rows[doc_id] = row

    print('\t'.join(["doc_id", "url", "ref", "unanimity"] + sys_names))
    for raw_doc_id in sorted(rows.keys()):
        l = []
        doc_id = int(raw_doc_id)
        cur_row = rows[doc_id]
        unanimity = len(cur_row['preds']) == len(set(cur_row['preds']))

        l.extend([str(raw_doc_id), cur_row['url'], rcan_coll.get_theme(cur_row['ref_theme'])['name']])
        l.append("True" if unanimity else "False")
        l.extend([rcan_coll.get_theme(x)['name'] for x in cur_row['preds']])
        print('\t'.join(l))


if __name__ == '__main__':
    main()