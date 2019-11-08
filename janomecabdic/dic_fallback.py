# Copyright(C) 2019 Hajime Nakagami <nakagami@gmail.com>
# Licensed under any of LGPL2.1 or BSD License.

import os
import mmap
import struct
from functools import lru_cache

__all__ = ["MeCabDictionary"]


class CharProperty:
    def __init__(self, path):
        with open(path, 'rb') as f:
            self.category_names = []
            num_categories = int.from_bytes(f.read(4), byteorder='little')
            for i in range(num_categories):
                name = f.read(32)
                self.category_names.append(
                    name[:name.find(b'\x00')].decode('ascii')
                )
            self.offset = 4 + num_categories * 32
            self.size = self.offset + 0xFFFF * 4
            self.mmap = mmap.mmap(f.fileno(), 0, mmap.MAP_PRIVATE, mmap.PROT_READ)

    def char_info(self, code_point):
        i = self.offset + code_point * 4
        data = self.mmap[i:i+4]
        v = data[0] + (data[1] << 8) + (data[2] << 16) + (data[3] << 24)
        return {
            'type': v & 0b111111111111111111,
            'default_type': (v >> 18) & 0b11111111,
            'length': (v >> 26) & 0b1111,
            'group': (v >> 30) & 0b1,
            'invoke': (v >> 31) & 0b1,
        }


class DicFileMap:

    def __init__(self, path):
        with open(path, 'rb') as f:
            self.size = int.from_bytes(f.read(4), byteorder='little') ^ 0xef718f77

            self.version = int.from_bytes(f.read(4), byteorder='little')
            self.dictype = int.from_bytes(f.read(4), byteorder='little')
            self.lexsize = int.from_bytes(f.read(4), byteorder='little')
            self.lsize = int.from_bytes(f.read(4), byteorder='little')
            self.rsize = int.from_bytes(f.read(4), byteorder='little')
            dsize = int.from_bytes(f.read(4), byteorder='little')
            tsize = int.from_bytes(f.read(4), byteorder='little')
            fsize = int.from_bytes(f.read(4), byteorder='little')
            assert int.from_bytes(f.read(4), byteorder='little') == 0   # dummy
            charset = f.read(32)
            self.charset = charset[:charset.find(b'\x00')].decode('ascii')

            self.mmap = mmap.mmap(f.fileno(), 0, mmap.MAP_PRIVATE, mmap.PROT_READ)
            self.da_offset = 72
            self.token_offset = 72 + dsize
            self.feature_offset = self.token_offset + tsize

    @lru_cache(maxsize=1024)
    def get_entries_by_index(self, idx, count):
        mmap = self.mmap
        feature_offset = self.feature_offset

        results = []
        i = self.token_offset + idx * 16
        data = mmap[i:i + count * 16]
        for i in range(count):
            lcAttr, rcAttr, posid, wcost, feature, compound = struct.unpack(
                'HHHhII', data[i*16: (i+1)*16]
            )
            k = j = feature_offset + feature
            while mmap[k]:
                k += 1
            results.append(
                (lcAttr, rcAttr, posid, wcost, mmap[j:k].decode('utf-8'))
            )
        return results

    def get_entries(self, result):
        index = result >> 8
        count = result & 0xFF
        return self.get_entries_by_index(index, count)

    @lru_cache(maxsize=1024)
    def _get_base_check(self, idx):
        i = self.da_offset + idx * 8
        return struct.unpack('iI', self.mmap[i:i+8])

    def exactMatchSearch(self, s):
        v = -1
        b, _ = self._get_base_check(0)
        for i in range(len(s)):
            p = b +s[i] + 1
            base, check = self._get_base_check(p)
            if b == check:
                b = base
            else:
                return v

        p = b
        n, check = self._get_base_check(p)
        if b == check and n < 0:
            v = -n-1

        return v

    def commonPrefixSearch(self, s):
        results = []
        b, _ = self._get_base_check(0)
        for i in range(len(s)):
            p = b
            n, check = self._get_base_check(p)
            if b == check and n < 0:
                results.append((-n-1, i))
            p = b + s[i] + 1
            base, check = self._get_base_check(p)
            if b == check:
                b = base
            else:
                return results

        p = b
        n, check = self._get_base_check(p)
        if b == check and n < 0:
            results.append((-n-1, len(s)))
        return results

    def lookup(self, s):
        results = []
        for value, length in self.commonPrefixSearch(s):
            idx = value >> 8
            count = value & 0xff
            entries = self.get_entries_by_index(idx, count)
            for i in range(len(entries)):
                l, r, p, w, _ = entries[i]
                results.append((l, r, p, w, length, idx + i))
        return results

    def get_feature(self, idx):
        mmap = self.mmap
        i = self.token_offset + idx * 16 + 8
        k = j = self.feature_offset + struct.unpack('I', mmap[i:i + 4])[0]
        while mmap[k]:
            k += 1
        return mmap[j:k]


class MeCabDictionary:

    def __init__(self, dicdir=None):
        if dicdir is None:
            rcpath = os.path.join(os.path.expanduser('~'), 'mecabrc')
            if not os.access(rcpath, os.R_OK):
                rcpath = '/etc/mecabrc'
            with open(rcpath, 'r') as f:
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
        with open(os.path.join(self.dicdir, "matrix.bin"), 'rb') as f:
            self.matrix_lsize = int.from_bytes(f.read(2), byteorder='little')
            self.matrix_rsize = int.from_bytes(f.read(2), byteorder='little')
            self.matrix_size = self.matrix_lsize * self.matrix_rsize * 2 + 4
            self.matrix_mmap = mmap.mmap(f.fileno(), 0, mmap.MAP_PRIVATE, mmap.PROT_READ)

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
            for l, r, p, w, f in self.unk_dic.get_entries(result):
                entries.append(
                    (l, r, w, ','.join(f.split(',')[:4]))
                )
            self.unknowns[category_name] = entries

    @lru_cache(maxsize=1024)
    def get_trans_cost(self, id1, id2):
        i = (id2 * self.matrix_lsize + id1) * 2 + 4
        return struct.unpack('h', self.matrix_mmap[i:i+2])[0]

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
            (idx, s[:length].decode('utf-8'), l, r, w)
            for l, r, p, w, length, idx in self.sys_dic.lookup(s)
        ]

    @lru_cache(maxsize=1024)
    def lookup_extra(self, idx):
        f = self.sys_dic.get_feature(idx).decode('utf-8').split(',')
        return ','.join(f[:4]), f[4], f[5], f[6], f[7], f[8]
