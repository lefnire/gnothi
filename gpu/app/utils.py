import os, json, math, pdb
import torch
import tensorflow.keras.backend as K
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn import preprocessing as pp


def normalize(x, y=None, numpy=True):
    combine = y is not None
    x = x if torch.is_tensor(x) else torch.tensor(x)
    if combine:
        y = y if torch.is_tensor(y) else torch.tensor(y)
    n = torch.cat((x, y), 0) if combine else x
    n = n / n.norm(dim=1)[:, None]
    if combine:
        x, y = n[:x.shape[0]], n[x.shape[0]:]
        if numpy: x, y = x.cpu().numpy(), y.cpu().numpy()
        return x, y
    if numpy: n = n.cpu().numpy()
    return n


def cosine(x, y, norm_in=True):
    # TODO try https://github.com/facebookresearch/faiss
    # I need [0 1] for hierarchical clustering, and dists.sort_by(0->1), but cosine is [-1 1]
    x, y = torch.tensor(x), torch.tensor(y)
    if norm_in: x, y = normalize(x, y, numpy=False)
    sim = torch.mm(x, y.T)
    # print("sim.min=", sim.min(), "sim.max=", sim.max())

    # See https://stackoverflow.com/a/63532174/362790 for other options
    dist = (sim - 1).abs()
    # dist = sim.acos() / np.pi
    # dist = 1 - (sim + 1) / 2

    return dist.cpu().numpy()


def cluster(x, norm_in=True):
    nc = math.floor(1 + 3.5 * math.log10(x.shape[0]))
    if norm_in: x = normalize(x)
    dists = cosine(x, x, norm_in=False)
    agg = AgglomerativeClustering(n_clusters=nc, affinity='precomputed', linkage='average')
    labels = agg.fit_predict(dists)
    return labels


def clear_gpu():
    torch.cuda.empty_cache()
    K.clear_session()