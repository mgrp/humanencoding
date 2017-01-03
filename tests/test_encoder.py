import unittest
import humanencoding


class TestEncoder(unittest.TestCase):

    def test_wordlist_size(self):
        humanencoding.encoder.lazily_load_wordlist()
        self.assertEqual(len(humanencoding.encoder.wordlist),
                         65536)

    def test_invalid_wordlist_version(self):
        humanencoding.encoder.wordlist = []
        try:
            humanencoding.encoder.lazily_load_wordlist(version=0)
            raised_invalid_wordlist_error = False
        except humanencoding.HumanEncodingError:
            raised_invalid_wordlist_error = True
        self.assertTrue(raised_invalid_wordlist_error)

    def test_encode(self):
        test_input = b'test'
        expected_output = 'handset interview'
        self.assertEqual(humanencoding.encode(test_input),
                         expected_output)

    def test_encode_list(self):
        test_input = b'test'
        expected_output = ['handset', 'interview']
        self.assertEqual(humanencoding.encode(test_input, return_string=False),
                         expected_output)

    def test_decode(self):
        test_input = 'handset interview'
        expected_output = b'test'
        self.assertEqual(humanencoding.decode(test_input),
                         expected_output)

    def test_decode_list(self):
        test_input = ['handset', 'interview']
        expected_output = b'test'
        self.assertEqual(humanencoding.decode(test_input),
                         expected_output)

    def test_encode_padding(self):
        test_input = b'testa'
        expected_output = 'handset interview abilene null'
        self.assertEqual(humanencoding.encode(test_input),
                         expected_output)

    def test_decode_padding(self):
        test_input = 'handset interview abilene null'
        expected_output = b'testa'
        self.assertEqual(humanencoding.decode(test_input),
                         expected_output)

    def test_encode_checksum(self):
        test_input = b'test'
        expected_output = 'handset interview check laughingly sterility'
        self.assertEqual(humanencoding.encode(test_input, checksum=True),
                         expected_output)

    def test_encode_checksum(self):
        test_input = 'handset interview check laughingly sterility'
        expected_output = b'test'
        self.assertEqual(humanencoding.decode(test_input),
                         expected_output)

    def test_invalid_checksum(self):
        test_input = 'handset interview check laughingly test'
        try:
            humanencoding.decode(test_input)
            raised_checksum_error = False
        except humanencoding.HumanEncodingError:
            raised_checksum_error = True
        self.assertTrue(raised_checksum_error)

    def test_encode_max_size(self):
        test_input = b'test'
        max_bytes = len(test_input) - 1
        try:
            humanencoding.encode(test_input, max_bytes=max_bytes)
            raised_max_size_error = False
        except humanencoding.HumanEncodingError:
            raised_max_size_error = True
        self.assertTrue(raised_max_size_error)

    def test_decode_max_size(self):
        test_input = ['handset', 'interview']
        max_words = len(test_input) - 1
        try:
            humanencoding.decode(test_input, max_words=max_words)
            raised_max_size_error = False
        except humanencoding.HumanEncodingError:
            raised_max_size_error = True
        self.assertTrue(raised_max_size_error)


if __name__ == '__main__':
    unittest.main()