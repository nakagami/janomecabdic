import unittest

from janome.tokenizer import Tokenizer
import janomecabdic


class TestDic(unittest.TestCase):
    def setUp(self):
        self.tokenizer = Tokenizer()
        self.mecab_dic = janomecabdic.MeCabDictionary()

    def test_get_trans_cost(self):
        # trans cost
        for i in range(self.mecab_dic.matrix_lsize):
            for j in range(self.mecab_dic.matrix_rsize):
                self.assertEqual(
                    self.mecab_dic.get_trans_cost(i, j),
                    self.tokenizer.sys_dic.get_trans_cost(i, j)
                )

    def test_get_char_categories(self):
        self.assertEqual(
            self.tokenizer.sys_dic.char_categories,
            self.mecab_dic.char_categories
        )

    def test_char_info(self):
        # code_point -> [type, default_type, length, group, invoke]
        self.assertEqual(
            self.mecab_dic.char_property.char_info(0),
            {"type": 1, "default_type": 0, "length": 0, "group": 1, "invoke": 0}
        )
        self.assertEqual(
            self.mecab_dic.char_property.char_info(0x20),
            {"type": 2, "default_type": 1, "length": 0, "group": 1, "invoke": 0}
        )
        self.assertEqual(
            self.mecab_dic.char_property.char_info(ord('\t')),
            {"type": 2, "default_type": 1, "length": 0, "group": 1, "invoke": 0}
        )
        self.assertEqual(
            self.mecab_dic.char_property.char_info(ord('1')),
            {"type": 16, "default_type": 4, "length": 0, "group": 1, "invoke": 1}
        )
        self.assertEqual(
            self.mecab_dic.char_property.char_info(ord('あ')),
            {"type": 64, "default_type": 6, "length": 2, "group": 1, "invoke": 0}
        )
        self.assertEqual(
            self.mecab_dic.char_property.char_info(ord('漢')),
            {"type": 4, "default_type": 2, "length": 2, "group": 0, "invoke": 0}
        )
        self.assertEqual(
            self.mecab_dic.char_property.char_info(0x4e00),
            {"type": 260, "default_type": 8, "length": 0, "group": 1, "invoke": 1}
        )
        self.assertEqual(
            self.mecab_dic.char_property.char_info(0x3007),
            {"type": 264, "default_type": 3, "length": 0, "group": 1, "invoke": 1}
        )

    def test_get_char_categories(self):
        for i in range(0xFFFF):
            d1 = self.mecab_dic.get_char_categories(chr(i))
            d2 = self.tokenizer.sys_dic.get_char_categories(chr(i))
            for k in d1:
                self.assertEqual(d1[k], d2[k])
            # A bit difference, less results than janome's get_char_categories().
            #if d1 != d2:
            #    print()
            #    print(hex(i))
            #    print(d1)
            #    print(d2)

    def test_exact_match_search(self):
        self.assertEqual(self.mecab_dic.unk_dic.exactMatchSearch(b"SPACE"), 9729)
        self.assertEqual(self.mecab_dic.unk_dic.exactMatchSearch(b"DEFAULT"), 2817)
        self.assertEqual(self.mecab_dic.unk_dic.exactMatchSearch(b"SYMBOL"), 9985)
        self.assertEqual(self.mecab_dic.unk_dic.exactMatchSearch(b"BADCATEGORY"), -1)

    def test_common_prefix_search(self):
        self.assertEqual(
            self.mecab_dic.sys_dic.commonPrefixSearch("すもももももももものうち".encode('utf-8')),
            [(8849415, 3), (9258497, 6), (9259009, 9)]
        )

    def test_get_tokens(self):
        result = self.mecab_dic.unk_dic.exactMatchSearch(b"CYRILLIC")
        self.assertEqual(result, 1541)
        self.assertEqual(len(self.mecab_dic.unk_dic.get_tokens(result)), 5)

    def test_unknowns(self):
        self.assertEqual(self.mecab_dic.unknowns, self.tokenizer.sys_dic.unknowns)

    def test_lookup(self):
        s = "すもももももももものうち".encode('utf-8')

        r1 = self.tokenizer.sys_dic.lookup(s)
        r2 = self.mecab_dic.lookup(s)
        self.assertEqual(len(r1), len(r2))

        s1 = set()
        for r in r1:
            s1.add((r[1], r[2], r[3], r[4]))
        s2 = set()
        for r in r2:
            s2.add((r[1], r[2], r[3], r[4]))
        self.assertEqual(s1, s2)

        s1 = set()
        for r in r1:
            s1.add(self.tokenizer.sys_dic.lookup_extra(r[0]))
        s2 = set()
        for r in r2:
            s2.add(self.mecab_dic.lookup_extra(r[0]))
        self.assertEqual(s1, s2)

    def test_tokenizer(self):
        s = 'すもももももももものうち'
        t = Tokenizer()
        t.sys_dic = janomecabdic.MeCabDictionary()
        self.assertEqual(
            [str(token) for token in t.tokenize(s)],
            [str(token) for token in self.tokenizer.tokenize(s)]
        )


if __name__ == "__main__":
    unittest.main()

