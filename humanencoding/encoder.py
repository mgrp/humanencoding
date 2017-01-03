'''

    humanencoding, binary data to dictionary words encoder and decoder
    Copyright (C) 2017 M GRP Limited <https://m.pr/>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''


import importlib
from binascii import crc32, hexlify
from struct import pack, unpack


DEFAULT_WORDLIST_VERSION = 1
CHECKSUM_WORD = 'check'
PADDING_WORD = 'null'
WORDLIST_SIZE = 65536


class HumanEncodingError(Exception):

    pass


_wordlist = []


def lazily_load_wordlist(version):
    global _wordlist
    version = int(version)
    if _wordlist:
        return _wordlist
    wordlist_module_name = '.wordlist_v{}'.format(version)
    try:
        wordlist_module = importlib.import_module(wordlist_module_name,
                                                  package='humanencoding')
    except Exception as e:
        err = 'Invalid word list module: {} ({})'
        raise HumanEncodingError(err.format(wordlist_module_name, e))
    words = getattr(wordlist_module, 'words', None)
    if not words:
        raise HumanEncodingError('Word list module has no words attribute')
    elif len(words) != WORDLIST_SIZE:
        err = 'Word list is in invalid size, found {} and expected {} words'
        raise HumanEncodingError(err.format(len(words), WORDLIST_SIZE))
    _wordlist = words
    return _wordlist


def _bytes_to_int(b):
    return unpack('<H', b)[0]


def _chunk_to_word(chunk, wordlist):
    try:
        return wordlist[_bytes_to_int(chunk)]
    except IndexError:
        err = 'Invalid chunk, is the wordlist the correct size?'
        raise HumanEncodingError(err.format(word))


def _int_to_bytes(i):
    return pack('<H', i)


def _word_to_chunk(word, wordlist):
    try:
        return _int_to_bytes(wordlist.index(word))
    except ValueError:
        err = 'Invalid word: {} (word not in wordlist)'
        raise HumanEncodingError(err.format(word))


def encode(binary_data, version=DEFAULT_WORDLIST_VERSION, checksum=False,
           return_string=True):
    wordlist = lazily_load_wordlist(version=version)
    data_len = len(binary_data)
    padded = data_len % 2 == 1
    if padded:
        binary_data += '\0'
        data_len += 1
    encoded_output = []
    for i in range(0, data_len, 2):
        chunk = binary_data[i: i + 2]
        encoded_output.append(_chunk_to_word(chunk, wordlist))
    if padded:
        encoded_output.append(PADDING_WORD)
    if checksum:
        encoded_output.append(CHECKSUM_WORD)
        checksum_int = crc32(binary_data[:-1] if padded else binary_data)
        checksum_bytes = pack('<i', checksum_int)
        encoded_output.append(_chunk_to_word(checksum_bytes[0:2], wordlist))
        encoded_output.append(_chunk_to_word(checksum_bytes[2:4], wordlist))
    return ' '.join(encoded_output) if string else encoded_output


def decode(words, version=DEFAULT_WORDLIST_VERSION):
    wordlist = lazily_load_wordlist(version=version)
    if isinstance(words, str):
        words = words.split()
    words = [str(w).lower() for w in words]
    checksum_words = []
    if len(words) > 3 and words[-3] == CHECKSUM_WORD:
        checksum_words = words[-2:]
        words = words[:-3]
    is_padded = False
    if words[-1] == PADDING_WORD:
        is_padded = True
        words = words[:-1]
    output = b''
    for word in words:
        output += _word_to_chunk(word, wordlist)
    if is_padded:
        output = output[:-1]
    if checksum_words:
        checksum_packed = _word_to_chunk(checksum_words[0], wordlist)
        checksum_packed += _word_to_chunk(checksum_words[1], wordlist)
        checksum_unpacked = unpack('<i', checksum_packed)[0]
        if checksum_unpacked != crc32(output):
            raise HumanEncodingError('Invalid CRC32 checksum')
    return output
