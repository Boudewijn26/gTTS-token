# coding=UTF-8

import unittest

from gtts_token import gtts_token


class TestToken(unittest.TestCase):
    """Test gToken"""

    def setUp(self):
        self.tokenizer = gtts_token.Token()

    def test_token(self):
        text = 'Hello person'
        self.assertEqual('654469.1039188', self.tokenizer.calculate_token(text, seed=403409))

    def test_work_token(self):
        token_key = 403404
        seed = '+-a^+6'
        self.assertEqual(415744659, self.tokenizer._work_token(token_key, seed))

    def test_token_accentuated(self):
        text = u'Hé'
        self.assertEqual('63792.446860', self.tokenizer.calculate_token(text, seed=403644))

    def test_token_special_char(self):
        text = u'€Hé'
        self.assertEqual('535990.918794', self.tokenizer.calculate_token(text, seed=403644))

    def test_token_very_special_char(self):
        text = u"◐"
        self.assertEqual('457487.54195', self.tokenizer.calculate_token(text, seed=403644))

    def test_token_longer(self):
        text = u'¿ya estás volviendo a casa?'
        self.assertEqual('518335.115040', self.tokenizer.calculate_token(text, seed=403935))

    def test_bytes_input(self):
        text = "è"
        self.assertEqual('554589.941173', self.tokenizer.calculate_token(text, seed=404008))
if __name__ == '__main__':
    unittest.main()
