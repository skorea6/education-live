import string
import random


def make_random(length):
    string_pool = string.ascii_lowercase + string.digits
    result = ""
    for i in range(length):
        result += random.choice(string_pool)
    return result


def six_number_random():
    return random.randint(100000, 999999)
