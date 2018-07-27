import base64
import io

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


def colored_score(score):
    if not score:
        return None
    elif score < 0.8:
        color = "#d10003"
    elif score < 0.95:
        color = "#b3a100"
    else:
        color = "#1d803b"

    return mark_safe('<span style="color: {}">{:.2f}</span>'.format(color, score))
