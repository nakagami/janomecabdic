// Copyright(C) 2019 Hajime Nakagami <nakagami@gmail.com>
// Licensed under any of LGPL2.1 or BSD License.

#include <string>
#include <sys/mman.h>
#include "darts/darts.h"
#include "mecab_struct.h"

struct LookupToken {
    unsigned short lcAttr;
    unsigned short rcAttr;
    unsigned short posid;
    short wcost;
    unsigned int   length;
    unsigned int   idx;
};



inline void *_mmap_fd(int fd, size_t size)
{
    return mmap(0, size, PROT_READ, MAP_PRIVATE, fd, 0);
}


inline int _munmap(void *m, size_t size)
{
    return munmap(m, size);
}

inline short _get_short(void *m)
{
    return *reinterpret_cast<short *>(m);
}


inline int _exact_match_search(Darts::DoubleArray *da, char *s)
{
    return da->exactMatchSearch<Darts::DoubleArray::result_type>(s);
}


inline std::vector<std::pair<int, size_t> > _common_prefix_search(Darts::DoubleArray *da, char *s)
{
    std::vector<std::pair<int, size_t> > r;
    Darts::DoubleArray::result_pair_type  result_pair[1024];
    size_t num = da->commonPrefixSearch(s, result_pair, sizeof(result_pair));
    for (size_t i = 0; i < num; ++i) {
        r.push_back(std::make_pair(result_pair[i].value, result_pair[i].length));
    }
    return r;
}


inline CharInfo _get_char_info(void *m, size_t offset, unsigned short code_point)
{
    return reinterpret_cast<CharInfo *>(m + offset)[code_point];
}


inline std::pair<Token, std::string> _get_token(void *token, void *feature, unsigned int index)
{
    Token t = reinterpret_cast<Token *>(token)[index];
    std::string s(reinterpret_cast<char *>(feature) + t.feature);
    return std::make_pair(t, s);
}


inline std::vector<LookupToken> _lookup(Darts::DoubleArray *da, void *token, char *s)
{
    std::vector<LookupToken> results;

    Darts::DoubleArray::result_pair_type  result_pair[1024];
    size_t num = da->commonPrefixSearch(s, result_pair, sizeof(result_pair));
    for (size_t i = 0; i < num; ++i) {
        unsigned int idx = result_pair[i].value >> 8;
        int count = result_pair[i].value & 0xFF;
        for (int j = 0; j < count; ++j) {
            LookupToken t = reinterpret_cast<LookupToken *>(token)[idx + j];
            t.idx = idx + j;
            t.length = result_pair[i].length;
            results.push_back(t);
        }
    }
    return results;
}


inline short _get_trans_cost(void *m, int id1, int id2, int matrix_lsize)
{
    int i = (id2 * matrix_lsize + id1) * 2 + 4;
    return *reinterpret_cast<short *>(m + i);
}
