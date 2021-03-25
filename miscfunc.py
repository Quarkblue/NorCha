import random
import string


def create_id():
    """
    Creates a 24 char Hex string to be used as an ObjectID
    :return:
    """
    x = string.hexdigits
    strng = ''
    id = strng.join(random.choice(x) for _ in range(24))
    return id
