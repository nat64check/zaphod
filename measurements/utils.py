import base64
import io
from collections import defaultdict

import skimage.io
from django.utils.safestring import mark_safe
from skimage.measure import compare_ssim


# noinspection PyTypeChecker
def compare_base64_images(img1_b64, img2_b64):
    img1_bytes = base64.decodebytes(img1_b64.encode('ascii'))
    img1 = skimage.io.imread(io.BytesIO(img1_bytes))

    img2_bytes = base64.decodebytes(img2_b64.encode('ascii'))
    img2 = skimage.io.imread(io.BytesIO(img2_bytes))

    return compare_ssim(img1, img2, multichannel=True)


def get_resource_stats(resources):
    stats = defaultdict(lambda: {
        'ok': 0,
        'fail': 0
    })

    for resource in resources:
        resource_type = resource['request']['resource_type']
        category = resource['success'] and 'ok' or 'fail'
        stats[resource_type][category] += 1
        stats['total'][category] += 1

    return stats


def colored_score(score, precision=2):
    if score is None:
        return '-'
    elif score < 0.8:
        color = "#d10003"
    elif score < 0.95:
        color = "#b3a100"
    else:
        color = "#1d803b"

    return mark_safe(('<span style="color: {}">{:.' + str(precision) + 'f}</span>').format(color, score))
