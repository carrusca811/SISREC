# Copyright (c) 2019 smarsu. All Rights Reserved.

"""A tool for compare the difference of the files."""

import sys
import glog
import numpy as np


def show_dis(x, y, thr=1e-4):
    x = x.flatten()
    y = y.flatten()

    def _show(index):
        for i in range(index - 4, index + 5):
            i = i % len(x)

            dis1 = np.abs(x[i] - y[i])
            dis2 = np.abs(x[i] - y[i]) / (np.abs(y[i]) + 1e-12)

            glog.info('{}\t{}\t{}\t{}\t{}'.format(
                i, x[i], y[i], dis1, dis2)) 

            if dis1 > thr and dis2 > thr:
                # raise ValueError()
                return False
        return True

    glog.info('----------------')
    dis = np.abs(x - y)
    index = np.argsort(dis)[-1]
    status1 = _show(index)

    glog.info('----------------')
    dis = np.abs(x - y) / (np.abs(y) + 1e-12)
    index = np.argsort(dis)[-1]
    status2 = _show(index)

    return status1 and status2


def load(path):
    """
    
    Args:
        path: str.

    Returns:
        data: ndarray
    """
    with open(path, 'r') as fb:
        lines = fb.readlines()
        lines = [float(line) for line in lines]
        data = np.array(lines).astype(np.float64)
        return data


def _norm(x, eps=1e-6):
    """
    Args:
        x: ndarray
        eps: float. To avoid div 0.
    
    Return:
        output: x after normalized.
    """
    x = x / np.sqrt(np.sum(np.square(x)) + eps)
    return x


def cosine_similarity(x, y):
    """
    Args:
        x: ndarray
        y: ndarray. The shape of y shape equal to x.

    Return:
        score: float. The cosine similarity of x and y, belong to [-1, 1]
    """
    assert x.shape == y.shape
    x = x.astype(np.float32)
    y = y.astype(np.float32)

    x = _norm(x)
    y = _norm(y)
    score = np.sum(x * y)
    return score


def maer(x, y, eps=1e-6):
    """Mean abs error rate
    
    Args:
        x: ndarray
        y: ndarray. The shape of y shape equal to x.
        eps: float. To avoid div 0.

    Returns:
        score: float. Mean abs error rate, [0, INF]
    """
    score = np.mean(np.abs(x - y) / (np.abs(y) + eps))
    return score


def compare_all(x, y, show=True, thr=1e-4):
    """
    Args:
        x: ndarray
        y: ndarray. The shape of y shape equal to x. y should be the ground truth.
    """
    assert x.shape == y.shape

    cos_sim = cosine_similarity(x, y)
    glog.info('cos_sim: {}'.format(cos_sim))

    meam_abs_error_rate = maer(x, y)
    glog.info('meam_abs_error_rate: {}'.format(meam_abs_error_rate))

    status = True
    if show:
        status = show_dis(x, y, thr)

    # return (1 - cos_sim) < thr and meam_abs_error_rate < thr and status
    return status


if __name__ == '__main__':
    if (not len(sys.argv) == 3):
      raise IOError('Usage: python3 {} path1 path2'.format(sys.argv[0]))

    x = load(sys.argv[1])
    y = load(sys.argv[2])
    compare_all(x, y)
