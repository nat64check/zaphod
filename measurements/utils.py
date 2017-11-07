from django.utils.crypto import get_random_string


def generate_random_token():
    return get_random_string(length=50)
