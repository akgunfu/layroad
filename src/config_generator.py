import itertools

from image_processing import ENHANCE_CONTRAST, BLUR, EDGE_DETECTION, THRESHOLD, UPSCALE

FAVORITES_ = [[UPSCALE, THRESHOLD, UPSCALE, ENHANCE_CONTRAST, EDGE_DETECTION],
              [ENHANCE_CONTRAST, UPSCALE, THRESHOLD, BLUR, UPSCALE, EDGE_DETECTION],
              [ENHANCE_CONTRAST, UPSCALE, THRESHOLD, UPSCALE, BLUR, EDGE_DETECTION],
              [UPSCALE, THRESHOLD, ENHANCE_CONTRAST, UPSCALE, BLUR, EDGE_DETECTION]]


def generate_configs(use_favorites=True):
    if use_favorites:
        return [{'steps': config} for config in FAVORITES_]
    else:
        return [{'steps': config} for config in _get_combinatorial_configs()]


def _get_combinatorial_configs():
    configs = []
    for ec_count in range(1, 3):
        for us_count in range(1, 3):
            for bl_count in range(2):
                step_counts = {'EC': ec_count, 'US': us_count, 'BL': bl_count, 'TH': 1}
                all_steps = (
                        [ENHANCE_CONTRAST] * step_counts['EC'] +
                        [UPSCALE] * step_counts['US'] +
                        [BLUR] * step_counts['BL'] +
                        [THRESHOLD]
                )
                for perm in itertools.permutations(all_steps):
                    if any(perm[i] == perm[i + 1] for i in range(len(perm) - 1)):
                        continue
                    if perm[0] in [THRESHOLD, BLUR]:
                        continue
                    perm_with_ed = list(perm) + [EDGE_DETECTION]
                    if perm_with_ed not in configs:
                        configs.append(perm_with_ed)
    filtered_configs = [
        config for config in configs
        if max(config.count(step) for step in set(config)) <= 2
           and list(config.count(step) for step in set(config)).count(2) <= 1
    ]
    return filtered_configs
