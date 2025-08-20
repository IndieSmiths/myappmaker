
### standard library imports

from collections import defaultdict

from operator import itemgetter

from math import log

from contextlib import suppress


### third-party imports

from shapely import LineString, hausdorff_distance

from shapely.affinity import translate, scale


### local imports
from ..prefsmgmt import PREFERENCES, PreferencesKeys



STROKES_MAP = defaultdict(dict)

get_first_item = itemgetter(0)


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
    offset_union_linestring = get_offset_union_line_string(union_of_strokes)

    ### get size of line string bounding box
    size = get_linestring_size(offset_union_linestring)

    ###
    STROKES_MAP[no_of_strokes][widget_key] = (ratios_logs, offset_union_linestring, size)

def get_linestring_size(linestring):
    """Return size of linestring bounding box."""
    left, top, right, bottom = linestring.bounds
    return (right - left, bottom - top)

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


def get_offset_union_line_string(union_of_strokes):
    """Return offset union so 1st point in 1st stroke is at origin.

    It is returned as a LineString.
    """
    x, y = union_of_strokes[0]
    return translate(LineString(union_of_strokes), xoff=-x, yoff=-y)


def get_stroke_matches_data(strokes, always_filter=False):

    match_data = {}
    match_data['menu_items'] = match_data['chosen_widget_key'] = ''

    no_of_strokes = len(strokes)

    possible_matches = STROKES_MAP[no_of_strokes]

    if possible_matches:

        union_of_strokes = sum(strokes, [])

        match_data['union_bounding_box'] = LineString(union_of_strokes).bounds

        your_ratios_logs = get_strokes_ratios_logs(union_of_strokes, strokes)

        your_union_ls = get_offset_union_line_string(union_of_strokes)

        your_union_ls_size = get_linestring_size(your_union_ls)

        ### if the 'always_filter' flag is off, we check whether
        ### the user asked us to show a widget menu after drawing;
        ###
        ### if so, it is the same as asking us to not filter the results,
        ### that is, to list all rather than only matching the best one

        ignore_filtering = always_filter or PREFERENCES[
          PreferencesKeys.SHOW_WIDGET_MENU_AFTER_DRAWING.value
        ]

        ratio_tolerance = (
            PREFERENCES[PreferencesKeys.RATIO_LOG_DIFF_TOLERANCE.value]
        )

        hdist_widget_key_pairs = sorted(

            (

                ### item

                (

                    ## symmetric Hausdorff distance

                    get_scaled_symmetric_hausdorff(
                        your_union_ls,
                        your_union_ls_size,
                        widget_union_ls,
                        widget_union_ls_size,
                    ),

                    ## widget key
                    widget_key,

                )

                ### source

                for widget_key, (widget_ratios_logs, widget_union_ls, widget_union_ls_size)
                in possible_matches.items()

                ## filtering (or not)

                if ignore_filtering or not any(

                    abs(ratio_log_a - ratio_log_b) > ratio_tolerance

                    for ratio_log_a, ratio_log_b
                    in zip(your_ratios_logs, widget_ratios_logs)

                )

            ),

            ## sorting key
            key=get_first_item,

        )

        if ignore_filtering:

            ### generate menu items
            match_data['menu_items'] = hdist_widget_key_pairs
            report = "Didn't filter matches."

        else:

            # default report
            report = "Possible matches weren't similar enough."

            # check whether distances of best strokes are within
            # tolerable distance

            if hdist_widget_key_pairs:

                sym_hausdorff_dist, chosen_widget_key = hdist_widget_key_pairs[0]
                match_data['no_of_widgets'] = len(possible_matches)

                hausdorff_tolerance = PREFERENCES[
                    PreferencesKeys.MAXIMUM_TOLERABLE_HAUSDORFF_DISTANCE.value
                ]

                if sym_hausdorff_dist < hausdorff_tolerance:

                    report = 'match'

                    match_data['chosen_widget_key'] = chosen_widget_key
                    match_data['sym_hausdorff_dist'] = sym_hausdorff_dist

                else:
                    report += " (hausdorff distance too large)"

            else:
                report += " (proportions didn't match)"

    else:
        report = "No widget with this stroke count"

    match_data['report'] = report

    return match_data


def get_scaled_symmetric_hausdorff(
    your_ls,
    your_ls_size,
    widget_ls,
    widget_ls_size,
):
    """Return symmetric Hausdorff of linestrings after resizing first one.

    That is, after resizing the first one to match the size of the second one.
    """

    your_width, your_height = your_ls_size
    widget_width, widget_height = widget_ls_size

    your_to_widget_width_factor = widget_width / your_width 
    your_to_widget_height_factor = widget_height / your_height

    your_resized_ls = scale(
        your_ls,
        xfact=your_to_widget_width_factor,
        yfact=your_to_widget_height_factor,
        origin=(0, 0), # see comment below
    )

    # origin of scale is always (0, 0) because both linestrings are
    # offset so their first point is at (0, 0) coordinates (that is,
    # the linestrings are aligned at that point)

    return float(max(
        hausdorff_distance(your_resized_ls, widget_ls),
        hausdorff_distance(widget_ls, your_resized_ls),
    ))
