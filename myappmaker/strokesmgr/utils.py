
### standard library imports

from collections import defaultdict

from math import log

from contextlib import suppress


### third-party import
from numpy import array as numpy_array



STROKES_MAP = defaultdict(dict)


def update_strokes_map(widget_key, strokes):

    for inner_map in STROKES_MAP.values():

        with suppress(KeyError):
            del inner_map[widget_key]

    ### 
    no_of_strokes = len(strokes)

    ### union of strokes
    union_of_strokes = sum(strokes, [])

    ###
    ratios_logs = get_strokes_ratios_logs(union_of_strokes, strokes)

    ### get offset union for easier comparison
    offset_union_array = get_offset_union_array(union_of_strokes)

    ###
    STROKES_MAP[no_of_strokes][widget_key] = (ratios_logs, offset_union_array)


def get_strokes_ratios_logs(union_of_strokes, strokes):
    """Return tuple w/ ln of width:height ratios.

    That is, width:height ratio of union of strokes and of each stroke
    individually.
    """

    ratios_logs = []

    for points in (union_of_strokes, *strokes):

        xs, ys = zip(*points)

        left = min(xs)
        right = max(xs)

        width = (right - left) or 1

        top = min(ys)
        bottom = max(ys)

        height = (bottom - top) or 1

        # XXX further research might improve the measure explained and
        # employed below;
        #
        # for now, manual tests indicates its results are satisfactory,
        # specially since they apply solely to corner cases (the measure
        # doesn't apply to most strokes expected to be used)

        # cases in which one of the dimensions are much smaller in comparison
        # to the other dimension are difficult to produce accurate ratios;
        #
        # this happens when the stroke is almost perfect horizontal or vertical
        # line;
        #
        # the reason is that since the ratio is given by width/height, the
        # tiniest variation in the smaller dimention can change the ratio
        # significantly;
        #
        # for instance, if width is 200 and height is 2, the resulting ratio
        # is 100, but if the user performs a stroke of height 1 or 3 instead,
        # the ratio now dramatically changes to either 200 or 66.66..., much
        # different than the original 100; even when alleviated by math.log
        # these differences may still be considerable;
        #
        # because of that, we alleviate such different ratios further by
        # by pretending that all dimensions that are more than 10 times
        # smaller than the other are exactly 10 times smaller, that is,
        # we generalize them; after, all we are not interested in the
        # absolute number anyway, just that the ratios are similar

        if (width * 10) < height:
            width = height / 10

        elif (height * 10) < width:
            height = width / 10

        #
        ratios_logs.append(log(width/height))

    return tuple(ratios_logs)


def get_offset_union_array(union_of_strokes):
    """Yield offset strokes so 1st point in 1st stroke is at origin.

    Moved strokes are yielded as numpy arrays.
    """

    ### coordinates of first point from first stroke
    x_offset, y_offset = union_of_strokes[0]

    ### offset all points in all strokes ac

    return numpy_array(

        [
            (a - x_offset, b - y_offset)
            for a, b in union_of_strokes
        ]

    )


def are_ratios_logs_similar(ratios_logs_a, ratios_logs_b, tolerance):

    return not any(

        abs(ratio_log_a - ratio_log_b) > tolerance
        for ratio_log_a, ratio_log_b in zip(ratios_logs_a, ratios_logs_b)

    )
