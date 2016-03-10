from reduct_feature_selection.discretize.simple_discretizer import SimpleDiscretizer
from collections import Counter

import math
import numpy as np


class EntropyDiscretizer(SimpleDiscretizer):
    def __init__(self, dec, m):
        self.dec = dec
        self.m = m
        self.MAX_ENT = 1000000

    def entropy(self, U):
        dec_fqs = Counter()
        for elem in U:
            dec_fqs[self.dec[elem[0]]] += 1
        probs = [x / float(len(U)) for x in dec_fqs.values()]
        entropy = sum(map(lambda x: -x * math.log(x, 2), probs))
        return entropy

    def stop_criterion(self, U, min_cut):
        n = len(U)
        U1 = U[min_cut:]
        U2 = U[:min_cut]
        ent_U = self.entropy(U)
        ent_U1 = self.entropy(U1)
        ent_U2 = self.entropy(U2)
        info_gain = ent_U - min_cut / float(n) * ent_U1 + (n - min_cut) / float(n) * ent_U2
        dec_fqs_U = Counter()
        dec_fqs_U1 = Counter()
        dec_fqs_U2 = Counter()
        for i, elem in enumerate(U):
            if i < min_cut:
                dec_fqs_U1[self.dec[elem[0]]] += 1
            else:
                dec_fqs_U2[self.dec[elem[0]]] += 1
            dec_fqs_U[self.dec[elem[0]]] += 1
        r = len(dec_fqs_U.keys())
        r1 = len(dec_fqs_U1.keys())
        r2 = len(dec_fqs_U2.keys())
        stop = math.log(n - 1, 2) / float(n) + \
               (math.log(math.pow(3, r) - 2, 2) - (r * ent_U - r1 * ent_U1 - r2 * ent_U2)) / float(n)
        return info_gain < stop

    def find_cut(self, begin, U):
        n = len(U)
        if n > 1:
            cuts = range(1, n)
            min_cut_ent = self.MAX_ENT
            min_cut = 1
            for cut in cuts:
                cut_ent = cut / float(n) * self.entropy(U[:cut]) + \
                          (n - cut) / float(n) * self.entropy(U[cut:])
                if cut_ent < min_cut_ent:
                    min_cut_ent = cut_ent
                    min_cut = cut
            if not self.stop_criterion(U, min_cut):
                yield begin + min_cut

                for cut in self.find_cut(begin, U[:min_cut]):
                    yield cut
                for cut in self.find_cut(begin + min_cut, U[min_cut:]):
                    yield cut

    def discretize_column(self, column):
        column = list(column)
        dis = 0
        cuts_set = sorted(list(self.find_cut(0, column)))
        cur_cut = cuts_set[0]

        for i, elem in enumerate(column):
            if cur_cut == i:
                dis += 1
            if len(cuts_set) > dis:
                cur_cut = cuts_set[dis]

            yield (elem[0], elem[1], dis)


if __name__ == "__main__":
    # table = np.array([(1, 7), (1, 8), (1, 3), (1, 9), (1, 1), (1, 2), (1, 5), (1, 10)],
    #                  dtype=[('y', float), ('z', float)])
    # U = [(0, 'x', 5), (1, 'x', 8), (2, 'x', 4), (3, 'x', 5), (4, 'x', 2), (5, 'x', 3)]
    # dec = [1, 1, 2, 0, 0, 2]
    # discretizer = EntropyDiscretizer(dec, 3)

    table = np.array([(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10),
                      (1, 11), (1, 12), (1, 13), (1, 14), (1, 15), (1, 16), (1, 17), (1, 18), (1, 19), (1, 20)],
                     dtype=[('y', float), ('z', float)])
    dec_1 = [1,1,1,1,1,0,0,0,0,0,2,2,2,2,2,3,3,3,3,3]
    dec_2 = [0,1,0,1,0,1,0,1,0,1,2,2,2,2,2,3,3,3,3,3]
    attrs_list = ['z']
    discretizer_1 = EntropyDiscretizer(dec_1, 2)
    discretizer_2 = EntropyDiscretizer(dec_2, 2)
    #print discretizer.discretize(table, attrs_list, par=True)
    print discretizer_1.discretize(table, attrs_list, par=False)
    print discretizer_2.discretize(table, attrs_list, par=False)

