PI = 3.1415926535897932384626433832795
HALF_PI = 1.5707963267948966192313216916398
TWO_PI = 6.283185307179586476925286766559


def NormalizeDeg180(theta):
    while theta < -180:
        theta += 360
    while theta > 180:
        theta -= 360
    return theta


def GapDeg(deg1, deg2):
    diff = abs(deg1 - deg2) % 360
    if diff > 180:
        diff = 360 - diff
    return diff


def clip(value, lower, upper):
    return max(min(value, upper), lower)
