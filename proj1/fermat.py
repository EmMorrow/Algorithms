import random
import math

# returns whether the given number is prime, composite, or carmichael.
# k fermat tests are run
def prime_test(N, k):
    if N == 2:
        return 'prime'

    for x in range(k):
        a = random.randint(2, N-1)
        if mod_exp(a, N - 1, N) != 1:
            return 'composite'
        if is_carmichael(N, a):
            return 'carmichael'

    return 'prime'


# returns x^y mod N
def mod_exp(x, y, N):
    if y == 0:
        return 1
    z = mod_exp(x, math.floor(y/2), N)

    if y % 2 == 0:
        return z ** 2 % N
    else:
        return (x * z ** 2) % N

# returns the probability of the algorithm correctly saying that a number is prime
def probability(k):
    prob = 1 / (2 ** k)
    prob = 100 - prob
    return prob


# checks to see if a number is carmichael by taking a^N-1 and seeing if it's
# equivalent to 1 (mod N), -1 (mod N), or a number greater than 1 (mod N)
# if it's not carmichael then it will equal -1 (mod N) first and can return false
# otherwise if it hits a number > 1 (mod N) before it hits -1 (mod N) then it's
# carmichael and returns true
def is_carmichael(N, a):
    x = N - 1

    # checks what the mod is until the exponent is odd
    while x % 2 != 1:
        mod = mod_exp(a, x, N)
        if mod > 1:
            if mod - N == -1:
                return False
            else:
                return True
        x = x / 2

    return False

