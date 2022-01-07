import math
import numpy as np
from objects.helper import *

def area_minus_minarea(x, len_idx, width_idx, min_area):
    term = x[len_idx] * x[width_idx] - min_area

    # print('area_minus_minarea_scipy len:{} width:{}  min_area:{} -- term: {}'.format(x[len_idx],x[width_idx],min_area,term))
    return np.array([term])


def area_minus_minarea_jac(x, len_idx, width_idx, min_area):
    term = np.zeros_like(x)
    term[len_idx] = x[width_idx]
    term[width_idx] = x[len_idx]
    # print('area_minus_minarea_jac -- term: {}'.format(term))
    return term


def maxbound_minus_maxside(x, max_bound, centroid_idx, extension_idx):
    term = max_bound - (x[centroid_idx] + x[extension_idx] / 2.)
    # print('maxbound_minus_maxside -- term: {} bound: {} c: {} l: {}'.format(term,max_bound,x[centroid_idx],x[extension_idx] / 2.))
    return term


def maxbound_minus_maxside_jac(x, max_bound, centroid_idx, extension_idx):
    term = np.zeros_like(x)
    term[centroid_idx] = -1.
    term[extension_idx] = -0.5
    # print('maxbound_minus_maxside_jac -- term: {}'.format(term))
    return term


def minside_minus_minbound(x, min_bound, centroid_idx, extension_idx):
    term = (x[centroid_idx] - (x[extension_idx] / 2.)) - min_bound
    return term


def minside_minus_minbound_jac(x, min_bound, centroid_idx, extension_idx):
    term = np.zeros_like(x)
    term[centroid_idx] = 1.
    term[extension_idx] = -0.5
    # print('minside_minus_minbound_jac -- term: {}'.format(term))
    return term


# abs_approx(x0 - x1) - (len0 + len1) / 2
# dx0: (x0 - x1) / sqrt( (x0-x1)²  + 2/n)
# dlen: -0.5 * len
#
# or_operation
# dx0:self.idx*4
# x1>=0, x2>=0: x1 * (x0 - x1) / sqrt( (x0-x1)²  + 2/n)
# sonst: -x1 * (x0 - x1) / sqrt( (x0-x1)²  + 2/n)


def minus_when_overlap_func(x,
                            x0_idx, y0_idx, len0_idx, width0_idx,
                            x1_idx, y1_idx, len1_idx, width1_idx):
    term = or_operation(
        abs_approx(x[x0_idx] - x[x1_idx]) - (x[len0_idx] + x[len1_idx]) / 2,
        abs_approx(x[y0_idx] - x[y1_idx]) - (x[width0_idx] + x[width1_idx]) / 2
    )
    # term = term * 1e-3
    # print('minus_when_overlap_func: {} from #{} to #{}'.format(term,int(x0_idx / 4),int(x1_idx / 4)))
    return term


def minus_when_overlap_jac(x,
                           x0_idx, y0_idx, len0_idx, width0_idx,
                           x1_idx, y1_idx, len1_idx, width1_idx):
    term = np.zeros_like(x)

    len_term = abs_approx(x[x0_idx] - x[x1_idx]) - (x[len0_idx] + x[len1_idx]) / 2
    width_term =  abs_approx(x[y0_idx] - x[y1_idx]) - (x[width0_idx] + x[width1_idx]) / 2

    term[x0_idx] = term[x1_idx] * (term[x1_idx] - term[x0_idx]) / \
                   math.sqrt(math.pow(term[x1_idx] - term[x0_idx], 2) + 2 / 1e8)
    term[x1_idx] = term[x0_idx] * (term[x0_idx] - term[x1_idx]) / \
                   math.sqrt(math.pow(term[x1_idx] - term[x0_idx], 2) + 2 / 1e8)
    term[len0_idx] = -0.5  * width_term
    term[len1_idx] = -0.5  * width_term
    term[width0_idx] = -0.5  * len_term
    term[width1_idx] = -0.5 * len_term
    if not (width_term >= 0 and len_term >= 0):
        term = -1 * term
    # term = term * 1e-
    return term


def aspect_ratio_term_scipy(ratio, x, y, upper_bound_len):
    term = ratio * x * y - math.sqrt(upper_bound_len)
    return term


#### convenience functions

def abs_approx(x):
    res = math.sqrt(math.pow(x, 2) + 2 / 1e8)
    return res


def or_operation(term1, term2):
    """
    >=0 if one of term1, term2 >=0
    :param term1:
    :param term2:
    :return:
    """
    if (term1 >= 0) and (term2 >= 0):
        res = term1 * term2
    else:
        res = -1 * term1 * term2
    return res
