"""
Prints theme/subtheme stats on theme/subthemes.
"""
import pickle

from donnees.rcan_coll import *

import numpy
import tqdm


def main():
    coll = RCollection('/data/rali6/Tmp/gottif/radiocan/data/radio-can-articles/')

    if os.path.exists('matrix.pkl'):
        freqs = pickle.load(open('matrix.pkl', 'rb'))
    else:
        freqs = numpy.zeros((467, 26))

        for doc in tqdm.tqdm(coll.find(), total=601000):
            theme = doc.theme['id'] if doc.theme else 0
            subthemes = [x['id'] for x in doc.subthemes] if doc.subthemes else [0]

            for sth in subthemes:
                freqs[sth][theme] += 1

        pickle.dump(freqs, open('matrix.pkl', 'wb'))

    print("SubThemeId\tSubThemeCodename\tTotalOccurences\t", end='')
    for th_id in range(0, 26):
        print(get_theme(th_id)['codename'] + ('' if get_theme(th_id)['active'] else ' (inactif)') + '\t', end='')
    print()

    for sth_id in range(0, 467):
        try:
            codename = get_subtheme(sth_id)['codename'] if sth_id else 'no_subtheme'
            if sth_id != 0 and not get_subtheme(sth_id)['active']:
                codename += ' (inactif)'

            print(str(sth_id) + '\t' + codename + '\t' + str(numpy.sum(freqs[sth_id])) + '\t', end='')
            print('\t'.join([str(freqs[sth_id][th_id]) for th_id in range(0, 26)]))
        except KeyError as e:
            pass

    print('\n\n\n')

    # print child-parent matrix
    for sth_id in range(0, 467):
        try:
            parent_id = get_subtheme(sth_id)['theme'] if sth_id else 0
            if type(parent_id) == list:
                assert len(parent_id) == 0
                parent_id = 0

            row = [0] * 27
            row[0] = sth_id
            row[parent_id + 1] = 1
            print('\t'.join([str(x) for x in row]))
        except KeyError as e:
            pass


if __name__ == '__main__':
    main()
