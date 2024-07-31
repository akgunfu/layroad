import numpy as np
from kneed import KneeLocator
from sklearn.cluster import KMeans


def cluster_rectangles(rectangles, mode='size'):
    """Cluster rectangles by size or distance."""
    if not rectangles or len(rectangles) <= 1:
        return [(x, y, w, h, 0) for (x, y, w, h) in rectangles]

    rectangles = _remove_outliers(rectangles)

    if mode == 'size':
        return _cluster_by_size(rectangles)
    elif mode == 'distance':
        return _cluster_by_distance(rectangles)
    else:
        raise ValueError("Invalid mode. Choose either 'size' or 'distance'.")


def _remove_outliers(rectangles):
    """Remove outlier rectangles based on size."""
    sizes = np.array([w * h for (x, y, w, h) in rectangles])
    mean_size = np.mean(sizes)
    std_size = np.std(sizes)
    return [(x, y, w, h) for (x, y, w, h) in rectangles if
            (mean_size - 2 * std_size) <= (w * h) <= (mean_size + 2 * std_size)]


def _cluster_by_size(rectangles):
    """Cluster rectangles by their size."""
    sizes = np.array([(w * h) for (x, y, w, h) in rectangles]).reshape(-1, 1)
    num_clusters = _determine_optimal_clusters(sizes)
    kmeans = KMeans(n_clusters=num_clusters)
    labels = kmeans.fit_predict(sizes)
    return _create_clustered_rectangles(rectangles, labels)


def _cluster_by_distance(rectangles):
    """Cluster rectangles by their proximity."""
    centers = np.array([(x + w / 2, y + h / 2) for (x, y, w, h) in rectangles])
    num_clusters = _determine_optimal_clusters(centers)
    kmeans = KMeans(n_clusters=num_clusters)
    labels = kmeans.fit_predict(centers)
    return _create_clustered_rectangles(rectangles, labels)


def _determine_optimal_clusters(data, max_clusters=15, min_clusters=3):
    """Determine the optimal number of clusters using the elbow method."""
    distortions = []
    K = range(1, max_clusters + 1)
    for k in K:
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(data)
        distortions.append(kmeans.inertia_)
    kneedle = KneeLocator(K, distortions, curve='convex', direction='decreasing')
    optimal_clusters = kneedle.elbow if kneedle.elbow else 1
    return max(min(min_clusters, len(data)), optimal_clusters)


def _create_clustered_rectangles(rectangles, labels):
    """Assign cluster labels to rectangles."""
    clustered_rectangles = [(x, y, w, h, labels[i]) for i, (x, y, w, h) in enumerate(rectangles)]
    cluster_counts = np.bincount(labels)
    return [(x, y, w, h, label) for (x, y, w, h, label) in clustered_rectangles if cluster_counts[label] > 1]


def filter_contained_rectangles(rectangles):
    """Filter out rectangles contained within others."""
    filtered_rectangles = []
    for rect in rectangles:
        x, y, w, h = rect
        contained = False
        for other in rectangles:
            if rect == other:
                continue
            ox, oy, ow, oh = other
            if x >= ox and y >= oy and x + w <= ox + ow and y + h <= oy + oh:
                contained = True
                break
        if not contained:
            filtered_rectangles.append(rect)
    return filtered_rectangles
