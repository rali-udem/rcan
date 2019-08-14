"""
Prints cute stats on JSON fields.
"""
from donnees.rcan_coll import *

import re


def stat_keys(d, stat_info):
    for key_name, value in d.items():
        has_value = True
        cur_type = type(value)

        if cur_type == str:
            has_value = len(value.strip()) > 0
        elif cur_type == object:
            has_value = value is not None
        elif cur_type == dict or cur_type == bool or cur_type == int:
            has_value = True
        elif cur_type == list:
            has_value = len(value) > 0
        elif value is None:
            has_value = False
        else:
            raise ValueError("Cannot find type.")

        if key_name == 'ThemeId':
            has_value = value != 0

        if has_value:
            if key_name not in stat_info:
                stat_info[key_name] = {'freq': 0, 'children': {}}

            stat_info[key_name]['freq'] += 1

            if cur_type == dict:
                stat_keys(value, stat_info[key_name]['children'])


def rec_print(stat_info, depth, nb_docs):
    indent = depth * '\t'
    for key in sorted(stat_info.keys()):
        print(f"{indent}{key}: {100 * stat_info[key]['freq'] / nb_docs:.1f}%")
        if stat_info[key]['children']:
            rec_print(stat_info[key]['children'], depth + 1, nb_docs)


def main():
    coll = RCollection('/data/rali6/Tmp/gottif/radiocan/data/radio-can-articles/')
    stat_info = {}
    nb_docs = 0
    nb_paras = 0
    nb_toks = 0

    for doc in coll.find():
        stat_keys(doc._d, stat_info)

        nb_docs += 1
        nb_paras += len(doc.extract_body_paragraphs())
        for para in doc.extract_body_paragraphs():
            for tok in re.split(r'\s|,|;|:|"', para):  # very rougly, no tokenizer
                if tok:
                    nb_toks += 1

    rec_print(stat_info, 0, nb_docs)
    print(f"Nb docs: {nb_docs}, body paragraphs: {nb_paras}, body tokens: ~{nb_toks}")


if __name__ == '__main__':
    main()
