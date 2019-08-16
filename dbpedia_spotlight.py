"""Extracts entities from DBPedia Spotlight."""

import os
import requests
from requests import HTTPError

from donnees.rcan_coll import *


def main():
    in_dir = sys.argv[1]
    out_dir = sys.argv[2]
    url = "http://octal15.iro.umontreal.ca:8081/rest/candidates"

    coll = RCollection(in_dir)
    nb_docs = 0

    with requests.Session() as session:
        for doc in coll.find():
            nb_docs += 1
            if nb_docs % 1000 == 0:
                print(nb_docs)

            paras = doc.extract_body_paragraphs()
            text = '\n'.join(paras).replace('<', ' ')
            output_file = os.path.join(out_dir, os.path.basename(doc['source_file']))

            if not os.path.exists(output_file):
                try:
                    if paras and 'amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;' not in text:
                        response = session.post(url, {'text': text, 'confidence': 0.4, 'support': -1},
                                                headers={'Accept': 'application/json'},)
                        response.raise_for_status()
                        with open(output_file, 'wb') as fout:
                            fout.write(response.content)
                    else:
                        open(output_file, 'w', encoding='utf-8').write('{ "notext": true }')

                except HTTPError as e:
                    print(f"Problem with {doc['source_file']}: {e}", file=sys.stderr)


if __name__ == '__main__':
    main()
