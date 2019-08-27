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
        print(get_theme(th_id)['codename'] + '\t', end='')
    print()

    for sth_id in range(0, 467):
        try:
            codename = get_subtheme(sth_id)['codename'] if sth_id else 'no_subtheme'
            print(str(sth_id) + '\t' + codename + '\t' + str(numpy.sum(freqs[sth_id])) + '\t', end='')
            print('\t'.join([str(freqs[sth_id][th_id]) for th_id in range(0, 26)]))
        except KeyError as e:
            pass


if __name__ == '__main__':
    main()
