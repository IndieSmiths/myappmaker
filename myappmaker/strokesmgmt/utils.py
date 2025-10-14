"""Facility for general utilities."""

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
    """Update strokes map using given data and extra data obtained from it."""

    ### delete entry for given widget key if it exists

    for inner_map in STROKES_MAP.values():

        with suppress(KeyError):
            del inner_map[widget_key]

    ### grab quantity of strokes
    no_of_strokes = len(strokes)

    ### obtain the sum of all strokes, which works as a union
    union_of_strokes = sum(strokes, [])

    ### calculate the ln of the width:height ratio for the union and each
    ### individual stroke
    ###
    ### further adjustments of the underlying values may be performed during
    ### calculations to produce ratios that are easier to compare with other
    ### ratios
    ratios_logs = get_logs_of_width_height_ratios(union_of_strokes, strokes)

    ### get copy of union offset so that its first point is at the origin;
    ### such copy is actually an instance of the LineString class
    offset_union_linestring = get_offset_union_line_string(union_of_strokes)

    ### get size of line string bounding box
    size = get_linestring_size(offset_union_linestring)

    ### finally update the strokes map with the given and produced data

    STROKES_MAP[no_of_strokes][widget_key] = (

        ratios_logs,
        offset_union_linestring,
        size,

    )

def get_linestring_size(linestring):
    """Return size of linestring bounding box."""
    left, top, right, bottom = linestring.bounds
    return (right - left, bottom - top)

def get_logs_of_width_height_ratios(union_of_strokes, strokes):
    """Return tuple w/ ln of width:height ratios.

    That is, width:height ratio of union of strokes and of each stroke
    individually.

    Further adjustments of the underlying values may be performed during
    calculations to produce ratios that are easier to compare with other
    ratios. Such adjustments are explained in comments near the spots
    where they are applied.
    """

    ### create list to store ratios's logs
    ratios_logs = []

    ### calculate the log for the width:height ratio of the union of
    ### strokes and each individual stroke

    for points in (union_of_strokes, *strokes):

        ## calculate width and height of given stroke or union of strokes
        ##
        ## whenever width or height is 0 (when the stroke or union of strokes
        ## forms a perfect horizontal or vertical line), we use 1 instead,
        ## which is a close enough value that prevents math errors further
        ## down (namely, division by 0 or math.log(0))

        # grab all xs and ys of the points forming the given
        # stroke or union of strokes
        xs, ys = zip(*points)

        # calculate width; if it is 0, use 1 instead

        left = min(xs)
        right = max(xs)

        width = (right - left) or 1

        # calculate height; if it is 0, use 1 instead

        top = min(ys)
        bottom = max(ys)

        height = (bottom - top) or 1


        ## it is difficult to produce accurate ratios for cases in which one
        ## dimension is much smaller in comparison to the other one
        ##
        ## this happens when the stroke is almost a perfect horizontal or
        ## vertical line;
        ##
        ## the reason is that since the ratio is given by width divided by
        ## height, the tiniest variation in the smaller dimension can change
        ## the ratio significantly;
        ##
        ## for instance, if width is 200 and height is 2, the resulting ratio
        ## is 100, but if the user performs a stroke of height 1 or 3 instead,
        ## the ratio now dramatically changes to either 200 or 66.66...: much
        ## different than the original 100; even when alleviated by math.log()
        ## these differences may still be considerable;
        ##
        ## because of that, we alleviate such different ratios further by
        ## by pretending that all dimensions that are more than 10 times
        ## smaller than the other are exactly 10 times smaller, that is,
        ## we generalize them; after, all we are not interested in the
        ## absolute number anyway, just that the ratios are similar

        ## XXX further research might improve the measure explained above
        ## (and employed below);
        ##
        ## for now, manual tests indicates its results are satisfactory,
        ## specially since they apply solely to corner cases (the measure
        ## doesn't apply to most strokes expected to be used)

        if (width * 10) < height:
            width = height / 10

        elif (height * 10) < width:
            height = width / 10

        ## with the width and height now calculated (and adjusted as needed),
        ## append the log of their ratio
        ratios_logs.append(log(width/height))


    ### finally return the list with all ratios's logs
    return tuple(ratios_logs)


def get_offset_union_line_string(union_of_strokes):
    """Return offset union so 1st point in 1st stroke is at origin.

    It is returned as a LineString.
    """
    x, y = union_of_strokes[0]
    return translate(LineString(union_of_strokes), xoff=-x, yoff=-y)


def get_stroke_matches_data(strokes, always_filter=False):
    """Return data on how much given strokes match with existing ones."""

    ### create dictionary to hold the match data
    match_data = {}

    ### create placeholder keys for menu items and a chosen widget key
    ###
    ### whether these keys will be updated or not depends on the result of
    ### the matching
    match_data['menu_items'] = match_data['chosen_widget_key'] = ''

    ### let's start by determining the quantity of strokes and use it to
    ### decrease the number of possible matches right off the bat

    no_of_strokes = len(strokes)

    possible_matches = STROKES_MAP[no_of_strokes]

    ### if there are possible matches with that quantity of strokes, we keep
    ### measuring whether these possible matches are good enough/actual
    ### matches

    if possible_matches:

        ### obtain the sum of all strokes, which works as a union
        union_of_strokes = sum(strokes, [])

        ### store the bounding box of the union in our match data
        match_data['union_bounding_box'] = LineString(union_of_strokes).bounds

        ### calculate the logs for the width:height ratios of the union of
        ### strokes and each individual stroke

        your_ratios_logs = (
            get_logs_of_width_height_ratios(union_of_strokes, strokes)
        )

        ### get copy of union offset so that its first point is at the origin;
        ### such copy is actually an instance of the LineString class
        your_union_ls = get_offset_union_line_string(union_of_strokes)

        ### get size of line string bounding box
        your_union_ls_size = get_linestring_size(your_union_ls)

        ### determine whether we should ignore filtering results or not;
        ###
        ### this is the case if...
        ###
        ### - the always_filter is on; or
        ### - we were asked to show a menu with all matches (widget menu)
        ###
        ### if so, instead of filtering the results to get only the
        ### best match (if that), we list all

        ignore_filtering = always_filter or PREFERENCES[
          PreferencesKeys.SHOW_WIDGET_MENU_AFTER_DRAWING.value
        ]

        ### grab the tolerable difference between ratios's logs; a measure
        ### set by the user

        ratio_diff_tolerance = (
            PREFERENCES[PreferencesKeys.RATIO_LOG_DIFF_TOLERANCE.value]
        )

        ### here we create the list of data representing widgets that match
        ### the given drawing (strokes), if any, depending on a series of
        ### factors

        hdist_widget_key_pairs = sorted(

            ### items to be gathered (if any) and sorted

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

                ### filtering (or not)

                if (

                    ## if this is on, we accept the item without performing the
                    ## filter right below ("not any")
                    ignore_filtering

                    ## otherwise, this item is only accepted with not a single
                    ## one of differences between the ratios's logs is above
                    ## the tolerance (which is set by the user)

                    or not any(

                        abs(ratio_log_a - ratio_log_b) > ratio_diff_tolerance

                        for ratio_log_a, ratio_log_b
                        in zip(your_ratios_logs, widget_ratios_logs)

                    )
                )

            ),

            ### items are sorted by their first component, which is the
            ### symmetric Hausdorff distance; since this distance is a
            ### measure of dissimilarity, the best matches have the lowest
            ### values and are listed first
            key=get_first_item,

        )

        ### below we further populate the match_data dict depending on
        ### whether we ignored filtering or not

        ## if we did ignore filtering, it means we approved all possible
        ## matches;
        ##
        ## they are stored for usage in the widget menu to be presented
        ## to users (best matches first), so they can pick whichever they
        ## want

        if ignore_filtering:

            ### store matches
            match_data['menu_items'] = hdist_widget_key_pairs

            ### create message to serve as report
            report = "Didn't filter matches."

        ## if filtering wasn't ignored, there are more steps involved, since
        ## the list of matches may be empty, if no possible matches survived
        ## the filter;
        ##
        ## on top of that, not ignoring the filters means the user is only
        ## interested in the best match possible; this means even if the list
        ## is not empty we'll only keep its first item;
        ##
        ## and there's more: this best match will still be submitted to an
        ## extra filter (whether its symmetric Hausdorff distance is within
        ## another tolerance measure set by the user)

        else:

            ### create default report for when no matches were similar enough
            ###
            ### at this point we don't know if we'll use it yet
            no_matches_report = "Possible matches weren't similar enough."

            ### if the list of matches is not empty, we check whether the
            ### symmetric Hausdorff distance of its first item (the only one
            ### that interests us) is within a tolerable distance set by the
            ### user

            if hdist_widget_key_pairs:

                ### regardless of whether we end up with a best match, store
                ### the number of initial possible matches
                match_data['no_of_widgets'] = len(possible_matches)

                ### grab maximum tolerable (symmetric) Hausdorff distance
                ### set by user

                hausdorff_tolerance = PREFERENCES[
                    PreferencesKeys.MAXIMUM_TOLERABLE_HAUSDORFF_DISTANCE.value
                ]

                ### grab symmetric Hausdorff distance and widget key of best
                ### match in the list (although the widget key will only be
                ### used with distance is tolerable
                sym_hausdorff_dist, widget_key = hdist_widget_key_pairs[0]

                ### if distance is tolerable, store widget key and symmetric
                ### Hausdorff distance in our match data

                if sym_hausdorff_dist < hausdorff_tolerance:

                    match_data['chosen_widget_key'] = widget_key
                    match_data['sym_hausdorff_dist'] = sym_hausdorff_dist

                    ## use a simple report just to mean we found a best match
                    report = 'match'

                ### if distance is not tolerable though, we create message to
                ### report our lack of matches due to Hausdorff distance being
                ### too large

                else:

                    report = (
                        no_matches_report
                        + " (hausdorff distance too large)"
                    )

            ### if the list of matches is empty, it means none survived the
            ### ratios's logs filter applied, so we create message to report
            ### the problem

            else:
                report = no_matches_report + " (proportions didn't match)"

    ### if there aren't possible matches with that quantity of strokes,
    ### create a message to serve as a report

    else:
        report = "No widget with this stroke count"


    ### finally store the report produced and return the match data

    match_data['report'] = report

    return match_data


def get_scaled_symmetric_hausdorff(
    your_ls,
    your_ls_size,
    widget_ls,
    widget_ls_size,
):
    """Return symmetric Hausdorff of line strings after resizing first one.

    That is, after resizing the first one to match the size of the second one.

    A line string is an object that represents various points forming line
    segments, although here we are only considering the points for our
    calculations, as further explained/commented in the relevant section of
    the code.
    """

    ### grab width and height of each line string

    your_width, your_height = your_ls_size
    widget_width, widget_height = widget_ls_size

    ### calculate scaling factor between widths and heights

    your_to_widget_width_factor = widget_width / your_width 
    your_to_widget_height_factor = widget_height / your_height

    ### scale first line string to match size of second one using
    ### the scaling factors calculated

    your_resized_ls = scale(
        your_ls,
        xfact=your_to_widget_width_factor,
        yfact=your_to_widget_height_factor,
        origin=(0, 0), # see comment below
    )

    # origin of scale is always (0, 0) because both linestrings are
    # offset so their first point is at (0, 0) coordinates (that is,
    # the linestrings are aligned at that point)

    ### finally calculate and return the symmetric Hausdorff distance between
    ### the line strings, as a float;
    ###
    ### the function used to calculated the Hausdorff distance could further
    ### divide those segments if desired with its "densify" parameter, but
    ### doing so would be a mistake here, since these line strings are
    ### formed by uniting strokes, so there are no points between those
    ### strokes; thus, it would be conceptually wrong to use "densify" here;

    return float(

        ## the symmetric Hausdorff distance is either the Hausdorff distance
        ## from the first line string to the second one, or the distance from
        ## the second one to the first one: whichever is the largest
        ##
        ## that is, since the Hausdorff distance is a measure of
        ## dissimilarity, the symmetric Hausdorff distance seems to assume it
        ## is more accurate to consider the highest dissimilarity between the
        ## 02 set of points (represented here by line string objects)

        max(
            hausdorff_distance(your_resized_ls, widget_ls),
            hausdorff_distance(widget_ls, your_resized_ls),
        )

    )
