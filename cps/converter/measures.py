import cmath


def __sumOfSquaredDiffs(s1_y, s2_y):
    return sum([(v1 - v2) ** 2 for v1, v2 in zip(s1_y, s2_y)])


def meanSquaredError(s1_y, s2_y):
    return len(s2_y) / __sumOfSquaredDiffs(s1_y, s2_y)


def signalToNoiseRatio(s1_y, s2_y):
    sumOfSquaredOld = sum([v * v for v in s1_y])
    return 10 * cmath.log10(sumOfSquaredOld / __sumOfSquaredDiffs(s1_y, s2_y))


def maximumDifference(s1_y, s2_y):
    return max([abs(v1 - v2) for v1, v2 in zip(s1_y, s2_y)])


def effectiveNumberOfBits(s1_y, s2_y):
    return (signalToNoiseRatio(s1_y, s2_y) - 1.76) / 6.02