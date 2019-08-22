"""Evaluates themes/subthemes"""
import bz2
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
    return result


def f1(r, p):
    return 2 * r * p / (r + p)


def toggle_type(id):
    if type(id) == int:
        result = str(id)
    elif type(id) == str:
        try:
            result = int(id)
        except ValueError as e:
            result = id

    return result


def update_confusion(freq_dict, predicted_elements):
    for el in predicted_elements:
        cur_freq = freq_dict.get(el, 0) + 1
        freq_dict[el] = cur_freq


def update_label_stats(by_label_stats, reference_elements, predicted_elements):
    for ref in reference_elements:
        stat = by_label_stats.get(ref, {'ref': 0, 'pred': 0, 'valid': 0, 'confused_with': {}})
        stat['ref'] += 1
        if ref in predicted_elements:
            stat['valid'] += 1
        else:
            update_confusion(stat['confused_with'], predicted_elements)
        by_label_stats[ref] = stat

    for pred in predicted_elements:
        stat = by_label_stats.get(pred, {'ref': 0, 'pred': 0, 'valid': 0, 'confused_with': {}})
        stat['pred'] += 1
        by_label_stats[pred] = stat


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
        by_label_stats = {}

        nb_ref_elements = 0
        nb_predicted_elements = 0
        nb_valid_elements = 0

        for doc_id, preds in pred_dict.items():
            if doc_id in refs:
                effective_doc_id = doc_id
            else:
                effective_doc_id = toggle_type(doc_id)
                if effective_doc_id not in refs:
                    print(f"Cannot find your predicted doc id {doc_id} in the reference. Make sure "
                          f"you use ints for doc_id's and theme id's, not strings.", file=sys.stderr)
                    sys.exit(1)

            ref_theme = refs[effective_doc_id][0]
            ref_subthemes = refs[effective_doc_id][1:]

            if run == 'theme':
                predicted_elements = [x[0] for x in preds['theme'][0:n]]
                reference_elements = [ref_theme]
            elif run == 'sub_themes':
                predicted_elements = [x[0] for x in preds['sub_themes'][0:n]]
                reference_elements = ref_subthemes

            nb_ref_elements += len(reference_elements)
            nb_predicted_elements += len(predicted_elements)
            nb_valid_elements += inter_card(predicted_elements, reference_elements)
            update_label_stats(by_label_stats, reference_elements, predicted_elements)

        cur_res[run] = {}
        cur_res[run]['r'] = nb_valid_elements / nb_ref_elements
        cur_res[run]['p'] = nb_valid_elements / nb_predicted_elements
        cur_res[run]['f1'] = f1(cur_res[run]['r'], cur_res[run]['p'])
        cur_res[run]['by_label'] = by_label_stats

    return result


def print_eval_metrics(eval_res):
    rows = []
    for n in sorted(eval_res.keys()):
        key = list(eval_res[n].keys())[0]
        infos = eval_res[n][key]

        rows.append([str(n), f"{infos['p']:.3f}", f"{infos['r']:.3f}", f"{infos['f1']:.3f}"],)

    print(tabulate.tabulate(rows, headers=["n", "p", "r", "f1"], tablefmt="simple"))
    print()


def print_eval_metrics_by_class(eval_res, run_name, n):
    if n in eval_res:
        rows = []

        label_stats = eval_res[n][run_name]['by_label']
        for label in sorted(list(label_stats.keys())):
            info = label_stats[label]

            precision = f"{info['valid'] / info['pred']:.3f}" if info['pred'] else 'n.a.'
            recall = f"{info['valid'] / info['ref']:.3f}" if info['ref'] else 'n.a.'
            fmeas = f1(info['valid'] / info['ref'], info['valid'] / info['pred']) if info['pred'] and info['ref'] and info['valid'] else 0

            confused_with = sorted(list(info['confused_with'].keys()), key=lambda x: info['confused_with'][x], reverse=True)
            sum_confused = sum(info['confused_with'].values())
            confusion_text = ' '.join([f"{x} ({100*info['confused_with'][x]/sum_confused:.0f}%)" for x in confused_with])

            rows.append([str(label), precision, recall, f"{fmeas:.3f}", confusion_text])

        print(tabulate.tabulate(rows, headers=["label", "p", "r", "f1", "Confused with..."], tablefmt="simple"))


def main():
    if len(sys.argv) != 2:
        print("Usage: prog predictions.json", file=sys.stderr)
        sys.exit(1)

    print("Loading...", end='\n\n', file=sys.stderr, flush=True)
    preds = orjson.loads(open(sys.argv[1], 'r', encoding='utf-8').read())
    theme_refs = pickle.load(bz2.open(os.path.join(_ref_path, 'ref-rcan-themes.pkl.bz2'), 'rb'))

    first_eval = preds[list(preds.keys())[0]]

    if 'theme' in first_eval:
        eval_res_th = evaluate_themes(preds, theme_refs, range(1, 6), 'theme')
        print(f"Themes ====================")
        print_eval_metrics(eval_res_th)
        print(f"By label @ 1 --------------")
        print_eval_metrics_by_class(eval_res_th, 'theme', 1)

    if 'sub_themes' in first_eval:
        eval_res_sth = evaluate_themes(preds, theme_refs, range(1, 6), 'sub_themes')
        print(f"SubThemes =================")
        print_eval_metrics(eval_res_sth, 1)
        print(f"By label @1 ---------------")
        print_eval_metrics_by_class(eval_res_sth, 'sub_themes', 1)


if __name__ == '__main__':
    main()
