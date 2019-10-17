# Copyright(C) 2019 Hajime Nakagami <nakagami@gmail.com>
# Licensed under any of LGPL2.1 or BSD License.

import os
from functools import lru_cache

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.pair cimport pair


__all__ = ["MeCabDictionary"]


cdef extern from "darts/darts.h" namespace "Darts":
    cdef cppclass DoubleArray:
        DoubleArray()
        int set_array(void *)


cdef extern from "mecab_struct.h":
    cdef struct Token:
        unsigned short lcAttr   # Left Attribte ID
        unsigned short rcAttr   # Right Attribute ID
        unsigned short posid    # Part of Speech ID
        short wcost             # Word Cost
        unsigned int feature
        unsigned int compound   # 0

    cdef struct CharInfo:
        unsigned int type
        unsigned int default_type
        unsigned int length
        unsigned int  group
        unsigned int invoke


cdef extern from "dic.h":
    cdef struct LookupToken:
        unsigned short lcAttr
        unsigned short rcAttr
        unsigned short posid
        short wcost
        unsigned int length
        unsigned int idx

    cdef void *_mmap_fd(int, size_t)
    cdef int _munmap(void *, size_t)
    cdef short _get_short(void *) nogil
    cdef int _exact_match_search(DoubleArray *da, char *s) nogil
    cdef vector[pair[int, size_t]] _common_prefix_search(DoubleArray *da, char *s) nogil
    cdef CharInfo _get_char_info(void *, size_t, unsigned int) nogil
    cdef pair[Token, string] _get_token(void *token, void *feature, unsigned int index) nogil
    cdef vector[LookupToken] _lookup(DoubleArray *da, void *token, char *s) nogil
    cdef int _get_trans_cost(void *m, int id1, int id2, int matrix_lsize)


cdef class CharProperty:
    cdef void *mmap
    cdef int offset, size
    cdef public object category_names

    def __init__(self, path):
        cdef int fd = os.open(path, os.O_RDONLY)
        self.category_names = []
        num_categories = int.from_bytes(os.read(fd, 4), byteorder='little')
        for i in range(num_categories):
            name = os.read(fd, 32)
            self.category_names.append(
                name[:name.find(b'\x00')].decode('ascii')
            )
        self.offset = 4 + num_categories * 32
        self.size = self.offset + 0xFFFF * 4
        self.mmap = _mmap_fd(fd, self.size)
        os.close(fd)

    def __del__(self):
        _munmap(self.mmap, self.size)

    def char_info(self, code_point):
        return _get_char_info(self.mmap, self.offset, code_point)


cdef class DicFileMap:
    cdef void *mmap
    cdef void *token, *feature
    cdef size_t size
    cdef int version, dictype, lexsize, lsize, rsize
    cdef object charset
    cdef DoubleArray *da

    def __init__(self, path):
        cdef int fd = os.open(path, os.O_RDONLY)
        self.size = int.from_bytes(os.read(fd, 4), byteorder='little') ^ 0xef718f77
        self.mmap = _mmap_fd(fd, self.size)

        self.version = int.from_bytes(os.read(fd, 4), byteorder='little')
        self.dictype = int.from_bytes(os.read(fd, 4), byteorder='little')
        self.lexsize = int.from_bytes(os.read(fd, 4), byteorder='little')
        self.lsize = int.from_bytes(os.read(fd, 4), byteorder='little')
        self.rsize = int.from_bytes(os.read(fd, 4), byteorder='little')
        cdef size_t dsize = int.from_bytes(os.read(fd, 4), byteorder='little')
        cdef size_t tsize = int.from_bytes(os.read(fd, 4), byteorder='little')
        cdef size_t fsize = int.from_bytes(os.read(fd, 4), byteorder='little')
        assert int.from_bytes(os.read(fd, 4), byteorder='little') == 0   # dummy
        charset = os.read(fd, 32)
        self.charset = charset[:charset.find(b'\x00')].decode('ascii')
        os.close(fd)

        self.da = new DoubleArray()
        self.da.set_array(self.mmap + 72)

        self.token = self.mmap + 72 + dsize
        self.feature = self.token + tsize

    cpdef get_token_by_index(self, idx):
        t, f = _get_token(self.token, self.feature, idx)
        return (t, f.decode('utf-8'))

    cpdef get_tokens(self, result):
        index = result >> 8
        count = result & 0xFF
        results = []
        return [self.get_token_by_index(i) for i in range(index, index + count)]

    cpdef exactMatchSearch(self, s):
        return _exact_match_search(self.da, s)

    cpdef commonPrefixSearch(self, s):
        return _common_prefix_search(self.da, s)

    cpdef lookup(self, s):
        return _lookup(self.da, self.token, s)

    def __del__(self):
        _munmap(self.mmap, self.size)


cdef class MeCabDictionary:
    cdef public object dicdir, char_property, sys_dic, unk_dic
    cdef public object char_categories, unknowns
    cdef void *matrix_mmap
    cdef public int matrix_lsize, matrix_rsize
    cdef size_t matrix_size

    def __init__(self, dicdir=None):
        if dicdir is None:
            with open('/etc/mecabrc', 'r') as f:
                for s in f.readlines():
                    kv = s.split('=')
                    if kv[0].strip() == 'dicdir':
                        dicdir = kv[1].strip()
        if dicdir is None:
            raise ValueError("Can't find dicdir")
        self.dicdir = dicdir

        self.char_property = CharProperty(os.path.join(self.dicdir, "char.bin"))
        self.sys_dic = DicFileMap(os.path.join(self.dicdir, "sys.dic"))
        self.unk_dic = DicFileMap(os.path.join(self.dicdir, "unk.dic"))

        # matrix
        cdef int fd = os.open(os.path.join(self.dicdir, "matrix.bin"), os.O_RDONLY)
        self.matrix_lsize = int.from_bytes(os.read(fd, 2), byteorder='little')
        self.matrix_rsize = int.from_bytes(os.read(fd, 2), byteorder='little')
        self.matrix_size = self.matrix_lsize * self.matrix_rsize * 2 + 4
        self.matrix_mmap = _mmap_fd(fd, self.matrix_size)
        os.close(fd)

        # build char_categories from 'char.bin'.
        self.char_categories = {}
        for i in range(0xFFFF):
            char_info = self.char_property.char_info(i)
            name = self.char_property.category_names[char_info['default_type']]
            self.char_categories[name] = {
                'LENGTH': char_info['length'],
                'GROUP': bool(char_info['group']),
                'INVOKE': bool(char_info['invoke']),
            }

        # build unknowns
        self.unknowns = {}
        for category_name in self.char_property.category_names:
            entries = []
            result = self.unk_dic.exactMatchSearch(category_name.encode('utf-8'))
            for t, f in self.unk_dic.get_tokens(result):
                entries.append(
                    (t['lcAttr'], t['rcAttr'], t['wcost'], ','.join(f.split(',')[:4]))
                )
            self.unknowns[category_name] = entries

    def get_trans_cost(self, id1, id2):
        return _get_trans_cost(self.matrix_mmap, id1, id2, self.matrix_lsize)

    @lru_cache(maxsize=1024)
    def get_char_categories(self, c):
        char_info = self.char_property.char_info(ord(c))
        category_names = self.char_property.category_names

        r = {category_names[char_info['default_type']]: []}
        for i in range(len(category_names)):
            if i != char_info['default_type'] and char_info['type'] & (1 << i):
                r[category_names[char_info['default_type']]].append(category_names[i])
        return r

    def unknown_invoked_always(self, cate):
        if cate in self.char_property.category_names:
            return self.char_categories[cate]['INVOKE']
        return False

    def unknown_grouping(self, cate):
        if cate in self.char_property.category_names:
            return self.char_categories[cate]['GROUP']
        return False

    def unknown_length(self, cate):
        if cate in self.char_property.category_names:
            return self.char_categories[cate]['LENGTH']
        return -1

    def lookup(self, s):
        return [
            (r['idx'], s[:r['length']].decode('utf-8'), r['lcAttr'], r['rcAttr'], r['wcost'])
            for r in self.sys_dic.lookup(s)
        ]

    def lookup_extra(self, idx):
        _, f = self.sys_dic.get_token_by_index(idx)
        f = f.split(',')
        return ','.join(f[:4]), f[4], f[5], f[6], f[7], f[8]
