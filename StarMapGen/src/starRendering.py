P2MM = 0.26458333333

def get_params2(sp_type):
    return {
        500: [0.75, ["#5579ff", "#1345ff", "#9cb2ff"]],
        510: [0.75, ["#5579ff", "#1345ff", "#9cb2ff"]],
        520: [0.5, ["#688bff", "#2256ff", "#b9c9ff"]],

        330: [0.75, ["#9cb2ff", "#607aff", "#e0e4ff"]],
        340: [0.75, ["#fffcb6", "#fffa72", "#fff8fc"]],
        350: [0.75, ["#ffc58d", "#ff9228", "#ffeedd"]],
        360: [0.75, ["#ff9f41", "#ff7e00", "#ffc38b"]],
        370: [0.75, ["#ff6040", "#ff4000", "#ff8030"]],

        130: [1, ["#9cb2ff", "#607aff", "#e0e4ff"]],
        140: [1, ["#fffcb6", "#fffa72", "#fff8fc"]],
        150: [1, ["#ffc58d", "#ff9228", "#ffeedd"]],
        160: [1, ["#ff9f41", "#ff7e00", "#ffc38b"]],
        170: [1, ["#ff6040", "#ff4000", "#ff8030"]],

        530: [0.5, ["#9cb2ff", "#607aff", "#e0e4ff"]],
        540: [0.5, ["#fffcb6", "#fffa72", "#fff8fc"]],
        550: [0.5, ["#ffc58d", "#ff9228", "#ffeedd"]],
        560: [0.25, ["#ff9f41", "#ff7e00", "#ffc38b"]],
        570: [0.20, ["#ff6040", "#ff4000", "#ff8030"]],

        580: [0.20, ["#ff26b0", "#ff4000", "#ff64c8"]],
        600: [0.25, ["#5579ff", "#1345ff", "#9cb2ff"]],
        700: [0.375, ["#c86400", "#804000", "#ff8000"]],
        800: [0.375, ["#0000ff", "#ff0000", "#000000"]],
    }.get(
        sp_type,
        [0.25, ["rgM0a", "rgM0b", "rgM0c"]],
    )


def spec_type_to_value(sp):
    if sp == "BD":
        return 580

    if sp == "WD":
        return 600

    if sp == "NS":
        return 700

    if sp == "BH":
        return 800

    spec_order = [
        "O",
        "B",
        "A",
        "F",
        "G",
        "K",
        "M",
    ]

    value = (
            10 * spec_order.index(
        sp[0:1]
    )
    )

    value += int(
        sp[1:2]
    )

    sp_class = sp[2:]

    if sp_class == "":
        return value + 500

    if sp_class == "III":
        return value + 300

    if sp_class == "I":
        return value + 100

    if sp_class == "II":
        return value + 200

    if sp_class == "IV":
        return value + 400


def get_size(sp_val):
    value = (
            sp_val // 10 * 10
    )

    params = get_params2(
        value
    )

    return params[0]


def get_bracket_values(sp_val):
    if sp_val >= 570:
        return (
            sp_val,
            sp_val,
        )

    low = (
            int(sp_val)
            // 10
            * 10
    )

    return (
        low,
        low + 10,
    )


def sort_spec_type_for_display(sp_type):
    if sp_type == "BD":
        return 2000

    if sp_type == "WD":
        return 1000

    return spec_type_to_value(
        sp_type
    )

def interpolate_colors(
        spectral_type,
        index,
):
    spectral_value = spec_type_to_value(
        spectral_type
    )

    low, high = get_bracket_values(
        spectral_value
    )

    value = spectral_value % 10

    low_params = get_params2(
        low
    )

    high_params = get_params2(
        high
    )

    color1 = low_params[1][index]
    color2 = high_params[1][index]

    red1 = int(
        color1[1:3],
        16,
    )

    red2 = int(
        color2[1:3],
        16,
    )

    green1 = int(
        color1[3:5],
        16,
    )

    green2 = int(
        color2[3:5],
        16,
    )

    blue1 = int(
        color1[5:7],
        16,
    )

    blue2 = int(
        color2[5:7],
        16,
    )

    red = (
            red1
            + (red2 - red1)
            // 10
            * value
    )

    green = (
            green1
            + (green2 - green1)
            // 10
            * value
    )

    blue = (
            blue1
            + (blue2 - blue1)
            // 10
            * value
    )

    return (
        f"#{red:02x}"
        f"{green:02x}"
        f"{blue:02x}"
    )

def create_def(sp_type, star_data, d_dict):
    """Create the gradient definitions for the star symbols

    Each star symbol consists of three components that each is
    a unique color and gradient.  The colors are based on the
    spectral type of the star but the gradients are the same
    regardless of spectral type.  This function creates the gradient
    information and returns the gradient names to be used.

    To help minimize the size of the resultant SVG file, gradients
    are only generated for the spectral types that will be on the
    map.  The gradients are stored in a dictionary, indexed by
    an ID based on the spectral type of the star.  This dictionary
    is passed in as one of the parameters and if the requested
    gradient is already there, the function simply returns the list
    of gradients to use for the specified star.

    Inputs:
     - spType - The spectral type of the star
     - starData - A list containing information about the size of
                  the star symbol and the colors to be used
     - dDict - the definition dictionary that will hold the
               definition information

    Outputs:
     - gList - a list of the three gradients needed for the
               specified star.
    """
    g1 = "rg" + sp_type + "a"
    g2 = "rg" + sp_type + "b"
    g3 = "rg" + sp_type + "c"

    gList = [g1, g2, g3]
    if g1 not in d_dict:
        color = interpolate_colors(sp_type, 0)
        #		print ("Adding " + g1 + " definition")
        r1 = 100 * star_data[0]
        s1 = '  <radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="%f">\n' % (g1, r1)
        s1 += '   <stop stop-color="%s" offset="0"/>\n' % (color)
        s1 += '   <stop stop-color="%s" stop-opacity="0" offset="1"/>\n' % (color)
        s1 += '  </radialGradient>\n'
        d_dict[g1] = s1

    if g2 not in d_dict:
        color = interpolate_colors(sp_type, 1)
        #		print ("Adding " + g2 + " definition")
        r2 = 56.25 * star_data[0]
        s2 = '  <radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="%f">\n' % (g2, r2)
        s2 += '   <stop stop-color="%s" offset="0"/>\n' % (color)
        s2 += '   <stop stop-color="%s" offset="0.54545"/>\n' % (color)
        s2 += '   <stop stop-color="%s" stop-opacity="0" offset="1"/>\n' % (color)
        s2 += '  </radialGradient>\n'
        d_dict[g2] = s2

    if g3 not in d_dict:
        color = interpolate_colors(sp_type, 2)
        #		print ("Adding " + g3 + " definition")
        r3 = 50 * star_data[0]
        s3 = '  <radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="%f">\n' % (g3, r3)
        s3 += '   <stop stop-color="%s" offset="0"/>\n' % (color)
        s3 += '   <stop stop-color="%s" stop-opacity=".86432" offset="0.5"/>\n' % (color)
        s3 += '   <stop stop-color="%s" stop-opacity="0" offset="1"/>\n' % (color)
        s3 += '  </radialGradient>\n'
        d_dict[g3] = s3

    return gList

def create_symbol(p, sp_type, pos, d_dict):
    scale = p['scale'] * P2MM
    sp_val = spec_type_to_value(sp_type)
    star_data = get_params2(sp_val)
    star_data[0] = get_size(sp_val)
    g_list = create_def(sp_type, star_data, d_dict)
    s = ' <g transform="matrix(%f,0,0,%f,%f,%f)">\n' % (scale, scale, star_data[0] * pos[0] * scale,
                                                        star_data[0] * pos[1] * scale)
    if ("NS" == sp_type or "BH" == sp_type):
        s += '  <path style="fill:#ffffff;" d="m -4,-40 a 6.35,54.2 0 0 1 7,-7.5 l -2.8,48.5 z" transform="matrix(-0.8,0.6,-0.6,-0.8,0,0)" />'
        scale = 1
    s += '  <circle r="%f" fill="black"/>\n' % (star_data[0] * 55.)
    s += '  <circle r="%f" fill="url(#%s)"/>\n' % (star_data[0] * 100., g_list[0])
    s += '  <circle r="%f" fill="url(#%s)"/>\n' % (star_data[0] * 75., g_list[1])
    s += '  <circle r="%f" fill="url(#%s)"/>\n' % (star_data[0] * 50., g_list[2])
    if ("NS" == sp_type or "BH" == sp_type):
        s += '  <path style="fill:#ffffff;" d="m -4,-40 a 6.35,54.2 0 0 1 7,-7.5 l -2.8,48.5 z" transform="matrix(0.8,-0.6,0.6,0.8,0,0)" />'
    s += ' </g>\n'
    return s


def get_tweak_offset(s_list):
    offset = (0, 0)
    large_star_count = 0
    for s in s_list:
        if (sort_spec_type_for_display(s) < 560):
            large_star_count = large_star_count + 1
    n_stars = len(s_list)
    t1 = (get_star_offset_list(n_stars))[0]
    temp = (0.5 * t1[0], 0.5 * t1[1])

    if (1 == large_star_count and n_stars < 5):
        offset = (-temp[0], -temp[1])

    if (2 == large_star_count and (3 == n_stars or 4 == n_stars)):
        offset = (0, -temp[1])

    if (3 == large_star_count and (5 == n_stars or 4 == n_stars)):
        offset = (0, -temp[1])

    if (4 == n_stars and large_star_count < 3):
        offset = (-0.5 * temp[0], -0.5 * temp[1])

    if (n_stars > 5 and 1 == large_star_count):
        offset = (-0.5 * temp[0], -0.5 * temp[1])

    if (n_stars > 7 and (2 == large_star_count or 4 == large_star_count or 5 == large_star_count)):
        offset = (-0.5 * temp[0], -0.5 * temp[1])

    if ((6 == n_stars or 7 == n_stars) and 2 == large_star_count):
        offset = (0, -0.5 * temp[1])

    if ((6 == n_stars or 7 == n_stars) and 3 == large_star_count):
        offset = (temp[0], -0.5 * temp[1])

    if ((6 == n_stars or 7 == n_stars) and (4 == large_star_count or 5 == large_star_count)):
        offset = (temp[0], 0)

    if (n_stars > 7 and 3 == large_star_count):
        offset = (temp[0], -0.5 * temp[1])

    if (n_stars > 7 and (6 == large_star_count or 7 == large_star_count)):
        offset = (-0.5 * temp[0], 0)

    return offset


def get_star_offset_list(n):
    """Offsets for stars in a system

    This method returns a list of tuples based on the number of stars
    in the system.  Each tuple represents the x,y offset of the star
    from the system center for drawing purposes.

    Input: n - the number of stars in the system

    Output: a list of x,y pairs, one for each star in the system
    """
    if (2 == n):
        return [(-24, -24), (24, 24)]
    if (3 == n):
        return [(-36, -36), (36, -20), (-12, 36)]
    if (4 == n):
        print("4 stars")
        return [(-36, -36), (36, -36), (-36, 36), (36, 36)]
    if (5 == n):
        print("5 stars")
        return [(-44, -20), (0, -48), (44, -20), (28, 32), (-28, 32)]
    if (6 == n):
        print("6 stars")
        return [(-28, -48), (28, -48), (56, 0), (28, 48), (-28, 48), (-56, 0)]
    if (7 == n):
        print("7 stars")
        return [(-28, -48), (28, -48), (56, 0), (28, 48), (-28, 48), (-56, 0), (0, 0)]
    if (8 == n):
        print("8 stars")
        return [(-42, -42), (0, -60), (42, -42), (60, 0), (42, 42), (0, 60), (-42, 42), (-60, 0)]
    if (9 == n):
        print("9 stars")
        return [(-42, -42), (0, -60), (42, -42), (60, 0), (42, 42), (0, 60), (-42, 42), (-60, 0), (0, 0)]
    if (10 == n):
        print("10 stars")
        return [(-42, -42), (0, -60), (42, -42), (60, 0), (42, 42), (0, 60), (-42, 42), (-60, 0), (20, -20), (-20, 20)]
    else:
        return [(0, 0) * n]

