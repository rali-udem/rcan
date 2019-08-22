import math
import os
import pickle
import random
import sys

from donnees.rcan_coll import *

random.seed(42)


def valid_theme(theme):
    return theme['id'] != 0 and theme['active']


def valid_subtheme(subtheme):
    return subtheme['active']


def valid_subthemes(subthemes):
    result = len(subthemes) > 0
    for st in subthemes:
        if not valid_subtheme(st):
            result = False
            break
    return result


def write_subset(sublist, fout_name):
    with open(fout_name, 'w') as fout:
        for id in sorted(sublist):
            print(id, file=fout)


def main():
    coll_dir = sys.argv[1]
    out_dir = sys.argv[2]
    validate_subthemes = sys.argv[3] == 'valid_themes_and_subthemes'

    if validate_subthemes:
        print("Themes and subthemes must be valid")
    else:
        print("Only themes must be valid")

    coll = RCollection(coll_dir)
    reference = {}

    good_article_ids = set()
    nb_bad_articles = 0
    nb_docs = 0
    for doc in coll.find():
        nb_docs += 1
        if nb_docs % 1000 == 0:
            print(f"{nb_docs}...")

        if valid_theme(doc.theme) and (not validate_subthemes or valid_subthemes(doc.subthemes)):
            good_article_ids.add(doc.id)
            reference[doc.id] = [doc.theme['id']] + [x['id'] for x in doc.subthemes]
        else:
            nb_bad_articles += 1

    print(f"{len(good_article_ids)} good articles, {nb_bad_articles} bad ones.")

    with open(os.path.join(out_dir, 'all_good.ids'), 'w') as fout:
        for id in sorted(good_article_ids):
            print(str(id), file=fout)

    good_ids = list(sorted(good_article_ids))
    random.shuffle(good_ids)

    nb_good_ids = len(good_ids)
    valid_split = math.floor(0.8 * nb_good_ids)
    test_split = math.floor(0.9 * nb_good_ids)

    write_subset(good_ids[0:valid_split], os.path.join(out_dir, 'train.ids'))
    write_subset(good_ids[valid_split:test_split], os.path.join(out_dir, 'valid.ids'))
    write_subset(good_ids[test_split:], os.path.join(out_dir, 'test.ids'))
    pickle.dump(reference, open(os.path.join(out_dir, 'ref-themes.pkl'), 'wb'))


if __name__ == '__main__':
    main()
