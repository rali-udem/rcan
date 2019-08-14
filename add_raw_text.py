"""Adds the field body_paragraphs to all json files in the coll."""
import os
import sys

from donnees.rcan_coll import *


def main():
    in_dir = sys.argv[1]
    out_dir = sys.argv[2]

    coll = RCollection(in_dir)
    nb_docs = 0

    for doc in coll.find():
        nb_docs += 1
        if nb_docs % 1000 == 0:
            print(nb_docs)

        try:
            doc._d['BodyParagraphs'] = doc.extract_body_paragraphs()
            doc.write_to(os.path.join(out_dir, os.path.basename(doc['source_file'])))
        except:
            print(f"Problem with {doc['source_file']}: {sys.exc_info()[0]}", file=sys.stderr)


if __name__ == '__main__':
    main()
