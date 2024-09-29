import cv2
import numpy as np
import math
from frames import *


def get_tickers(video, frames):
    sample_count = len(frames)

    difference_sum = np.sum(
        [frames_gray(abs(frames[i] - frames[i + 1])) for i in range(sample_count - 1)],
        axis=0,
    )
    difference_sum /= sample_count - 1

    threshold = np.amax(difference_sum) * 0.95
    _, text_pixels = cv2.threshold(difference_sum, threshold, 1.0, cv2.THRESH_BINARY)

    nonzero_coords = np.transpose(np.nonzero(text_pixels))

    miny, minx = np.min(nonzero_coords, axis=0)
    maxy, maxx = np.max(nonzero_coords, axis=0)

    expand_threshold = threshold * 0.5
    expand_threshold_up = threshold * 0.15

    tickers = expand_tickers(
        video,
        miny,
        minx,
        maxy,
        maxx,
        expand_threshold,
        expand_threshold_up,
        difference_sum,
    )

    return tickers


def expand_tickers(
    video, miny, minx, maxy, maxx, expand_threshold, expand_threshold_up, difference_sum
):
    while True:
        expanded = False

        if (
            minx > 0
            and difference_sum[miny : maxy + 1, minx - 1].mean() > expand_threshold
        ):
            minx -= 1
            expanded = True

        if (
            maxx < video.width - 1
            and difference_sum[miny : maxy + 1, maxx + 1].mean() > expand_threshold
        ):
            maxx += 1
            expanded = True

        if (
            miny > 0
            and difference_sum[miny - 1, minx : maxx + 1].mean() > expand_threshold_up
        ):
            miny -= 1
            expanded = True

        if (
            maxy < video.height - 1
            and difference_sum[maxy + 1, minx : maxx + 1].mean() > expand_threshold
        ):
            maxy += 1
            expanded = True

        if not expanded:
            break

    h = maxy - miny + 1
    w = maxx - minx + 1

    miny -= math.floor(h * 1 / 3 + 1)
    maxy += math.floor(h * 1 / 3 + 1)

    tickers = np.array([[[miny, maxy], [minx, maxx]]], dtype=np.int32)

    tickers = np.maximum(tickers, 0)
    tickers = np.minimum(
        tickers, np.array([[[video.height - 1], [video.width - 1]]], dtype=np.int32)
    )

    return (tickers, h, w)
