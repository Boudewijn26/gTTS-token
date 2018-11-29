# -*- coding: utf-8 -*-
import calendar
import math
import time
import requests
import re


class Token:
    """ Token (Google Translate Token)
    Generate the current token key and allows generation of tokens (tk) with it
    Python version of `token-script.js` itself from translate.google.com

    :param proxies: dict Proxies to use with requests module for connecting translator service
    """

    SALT_1 = "+-a^+6"
    SALT_2 = "+-3^+b+-f"

    def __init__(self, proxies=None):
        self.token_key = None
        self.proxies = proxies

    def calculate_token(self, text, seed=None, proxies=None):
        """ Calculate the request token (`tk`) of a string
        :param text: str The text to calculate a token for
        :param seed: str The seed to use. By default this is the number of hours since epoch
        :param proxies: dict Proxies to use with requests module for connecting translator service, overrides existing proxies for 1 request
        """

        if seed is None:
            seed = self._get_token_key(proxies or self.proxies)

        [first_seed, second_seed] = seed.split(".")

        try:
            d = bytearray(text.encode('UTF-8'))
        except UnicodeDecodeError:
            # This will probably only occur when d is actually a str containing UTF-8 chars, which means we don't need
            # to encode.
            d = bytearray(text)

        a = int(first_seed)
        for value in d:
            a += value
            a = self._work_token(a, self.SALT_1)
        a = self._work_token(a, self.SALT_2)
        a ^= int(second_seed)
        if 0 > a:
            a = (a & 2147483647) + 2147483648
        a %= 1E6
        a = int(a)
        return str(a) + "." + str(a ^ int(first_seed))

    def _get_token_key(self, proxies):
        if self.token_key is not None:
            return self.token_key

        response = requests.get(
            "https://translate.google.com/", proxies=proxies)
        tkk_expr = re.search("(tkk:.*?),", response.text)
        if not tkk_expr:
            raise ValueError(
                "Unable to find token seed! Did https://translate.google.com change?"
            )

        tkk_expr = tkk_expr.group(1)
        try:
            # Grab the token directly if already generated by function call
            result = re.search("\d{6}\.[0-9]+", tkk_expr).group(0)
        except AttributeError:
            # Generate the token using algorithm
            timestamp = calendar.timegm(time.gmtime())
            hours = int(math.floor(timestamp / 3600))
            a = re.search("a\\\\x3d(-?\d+);", tkk_expr).group(1)
            b = re.search("b\\\\x3d(-?\d+);", tkk_expr).group(1)

            result = str(hours) + "." + str(int(a) + int(b))

        self.token_key = result
        return result

    """ Functions used by the token calculation algorithm """
    def _rshift(self, val, n):
        return val >> n if val >= 0 else (val + 0x100000000) >> n

    def _work_token(self, a, seed):
        for i in range(0, len(seed) - 2, 3):
            char = seed[i + 2]
            d = ord(char[0]) - 87 if char >= "a" else int(char)
            d = self._rshift(a, d) if seed[i + 1] == "+" else a << d
            a = a + d & 4294967295 if seed[i] == "+" else a ^ d
        return a
