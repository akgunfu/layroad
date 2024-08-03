from typing import List, Any

import numpy as np
from kneed import KneeLocator
from sklearn.cluster import KMeans

from geometry import Rectangle

RANDOM_SEED = 42


def cluster_rectangles(rects: List[Rectangle], mode='size'):
    """Cluster rectangles by size or distance."""
    if not rects or len(rects) <= 1:
        for rect in rects:
            rect.set_cluster(0)
        return rects

    if mode == 'size':
        return _cluster_by_size(rects)
    elif mode == 'distance':
        return _cluster_by_distance(rects)
    else:
        raise ValueError("Invalid mode. Choose either 'size' or 'distance'.")


def _cluster_by_size(rects: List[Rectangle]) -> List[Rectangle]:
    """Cluster rectangles by their size."""
    sizes = np.array([rect.w * rect.h for rect in rects]).reshape(-1, 1)
    num_clusters = _determine_optimal_clusters(sizes)
    num_clusters = min(len(sizes), num_clusters)
    kmeans = KMeans(n_clusters=num_clusters, random_state=RANDOM_SEED)
    labels = kmeans.fit_predict(sizes)
    return _create_clustered_rects(rects, labels)


def _cluster_by_distance(rects: List[Rectangle]) -> List[Rectangle]:
    """Cluster rectangles by their proximity."""
    centers = np.array([(rect.x + rect.w / 2, rect.y + rect.h / 2) for rect in rects])
    num_clusters = _determine_optimal_clusters(centers)
    num_clusters = min(len(centers), num_clusters)
    kmeans = KMeans(n_clusters=num_clusters, random_state=RANDOM_SEED)
    labels = kmeans.fit_predict(centers)
    return _create_clustered_rects(rects, labels)


def _determine_optimal_clusters(data: np.ndarray[Any, np.dtype], max_clusters=15, min_clusters=3) -> int:
    """Determine the optimal number of clusters using the elbow method."""
    distortions = []
    K = range(1, min(len(data), max_clusters) + 1)  # Ensure the range does not exceed the number of samples
    for k in K:
        kmeans = KMeans(n_clusters=k, random_state=RANDOM_SEED)
        kmeans.fit(data)
        distortions.append(kmeans.inertia_)
    kneedle = KneeLocator(K, distortions, curve='convex', direction='decreasing')
    optimal_clusters = kneedle.elbow if kneedle.elbow else 1
    return max(min(min_clusters, len(data)), optimal_clusters)


def _create_clustered_rects(rects: List[Rectangle], labels) -> List[Rectangle]:
    """Assign cluster labels to rectangles."""
    cluster_counts = np.bincount(labels)
    for rect, label in zip(rects, labels):
        if cluster_counts[label] > 1:
            rect.set_cluster(label)
    return rects
