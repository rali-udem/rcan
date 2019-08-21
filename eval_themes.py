"""Evaluates themes/subthemes"""
import bz2
from pprint import pprint

import orjson
import os
import pickle
import sys
import tabulate

_ref_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'donnees', 'resources')


def inter_card(lista, listb):
    """Computes the cardinality of the intersection of two lists."""
    seta = set(lista)
    result = len([x for x in listb if x in seta])
    print(lista, listb, result)
    return result


def f1(r, p):
    return 2 * r * p / (r + p)


def evaluate_themes(pred_dict, refs, n_list, run):
    """
    Eval.
    :param pred_dict: Predictions.
    :param refs: References.
    :param n_list: Eval @n for each n in this list.
    :param run: either theme or sub_themes
    :return: a dict of results.
    """
    result = {}

    for n in n_list:
        cur_res = result[n] = {}

        nb_ref_elements = 0
        nb_predicted_elements = 0
        nb_valid_elements = 0

        for doc_id, preds in pred_dict.items():
            if doc_id not in refs:
                print(f"Cannot find your predicted doc id {doc_id} in the reference. Make sure "
                      f"you use ints for doc_id's and theme id's, not strings.", file=sys.stderr)
                sys.exit(1)

            ref_theme = refs[doc_id][0]
            ref_subthemes = refs[doc_id][1:]

            if run == 'theme':
                predicted_elements = [x[0] for x in preds['theme'][0:n]]
                reference_elements = [ref_theme]
            elif run == 'sub_themes':
                predicted_elements = [x[0] for x in preds['sub_themes'][0:n]]
                reference_elements = ref_subthemes

            nb_ref_elements += len(reference_elements)
            nb_predicted_elements += len(predicted_elements)
            nb_valid_elements += inter_card(predicted_elements, reference_elements)

        cur_res[run] = {}
        cur_res[run]['r'] = nb_valid_elements / nb_ref_elements
        cur_res[run]['p'] = nb_valid_elements / nb_predicted_elements
        cur_res[run]['f1'] = f1(cur_res[run]['r'], cur_res[run]['p'])

    return result


def print_eval_metrics(eval_res):
    rows = []
    for n in sorted(eval_res.keys()):
        key = list(eval_res[n].keys())[0]
        infos = eval_res[n][key]

        rows.append([str(n), f"{infos['p']:.3f}", f"{infos['r']:.3f}", f"{infos['f1']:.3f}"],)

    print(tabulate.tabulate(rows, headers=["n", "p", "r", "f1"], tablefmt="simple"))


def main():
    if len(sys.argv) != 2:
        print("Usage: prog predictions.json", file=sys.stderr)
        sys.exit(1)

    preds = orjson.loads(open(sys.argv[1], 'r', encoding='utf-8').read())
    theme_refs = pickle.load(bz2.open(os.path.join(_ref_path, 'ref-rcan-themes.pkl.bz2'), 'rb'))

    # preds = {}
    # for fid in list(theme_refs.keys())[0:100]:
    #     preds[fid] = {'theme': [(theme_refs[fid][0], 0), (theme_refs[fid][0] + 1, 0)],
    #                   'sub_themes': [(theme_refs[fid][1], 0), (theme_refs[fid][1] + 1, 0)]}

    eval_res_th = evaluate_themes(preds, theme_refs, range(1, 6), 'theme')
    eval_res_sth = evaluate_themes(preds, theme_refs, range(1, 6), 'sub_themes')

    # output results on stdout
    print(f"Themes ====================")
    print_eval_metrics(eval_res_th)
    print()

    print(f"SubThemes =================")
    print_eval_metrics(eval_res_sth)


if __name__ == '__main__':
    main()
