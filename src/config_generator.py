import itertools

from edge_detection import EdgeDetection


def generate_configs(use_favorites=True):
    favs = [
        [EdgeDetection.US, EdgeDetection.TH, EdgeDetection.US, EdgeDetection.EC, EdgeDetection.ED],
        [EdgeDetection.EC, EdgeDetection.US, EdgeDetection.TH, EdgeDetection.BL, EdgeDetection.US, EdgeDetection.ED],
        [EdgeDetection.EC, EdgeDetection.US, EdgeDetection.TH, EdgeDetection.US, EdgeDetection.BL, EdgeDetection.ED],
        [EdgeDetection.US, EdgeDetection.TH, EdgeDetection.EC, EdgeDetection.US, EdgeDetection.BL, EdgeDetection.ED]
    ]

    if use_favorites:
        return [{'steps': config} for config in favs]
    else:
        return [{'steps': config} for config in get_combinatorial_configs()]


def get_combinatorial_configs():
    configs = []
    for ec_count in range(1, 3):
        for us_count in range(1, 3):
            for bl_count in range(2):
                step_counts = {'EC': ec_count, 'US': us_count, 'BL': bl_count, 'TH': 1}
                all_steps = (
                        [EdgeDetection.EC] * step_counts['EC'] +
                        [EdgeDetection.US] * step_counts['US'] +
                        [EdgeDetection.BL] * step_counts['BL'] +
                        [EdgeDetection.TH]
                )
                for perm in itertools.permutations(all_steps):
                    if any(perm[i] == perm[i + 1] for i in range(len(perm) - 1)):
                        continue
                    if perm[0] in [EdgeDetection.TH, EdgeDetection.BL]:
                        continue
                    perm_with_ed = list(perm) + [EdgeDetection.ED]
                    if perm_with_ed not in configs:
                        configs.append(perm_with_ed)
    filtered_configs = [
        config for config in configs
        if max(config.count(step) for step in set(config)) <= 2
           and list(config.count(step) for step in set(config)).count(2) <= 1
    ]
    return filtered_configs
