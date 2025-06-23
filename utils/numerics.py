def simpson_integral(f, a, b, n = 32):
    """
    Compute the definite integral of f from a to b using Simpson's Rule.

    Args:
        f (callable): Function to integrate.
        a (float): Lower bound.
        b (float): Upper bound.
        n (int): Number of intervals (will be made even if not).

    Returns:
        float: Approximate integral of f from a to b.
    """
    if n % 2:
        n += 1
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n, 2):
        s += 4*f(a+i*h)
    for i in range(2, n, 2):
        s += 2*f(a+i*h)
    return s*h/3