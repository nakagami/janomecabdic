// Copyright(C) 2019 Hajime Nakagami <nakagami@gmail.com>
// Licensed under any of LGPL2.1 or BSD License.

#include <string>
#include <algorithm>
#include <sys/mman.h>
#include "darts/darts.h"
#include "mecab_struct.h"

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


inline std::pair<int, size_t> _exact_match_search(Darts::DoubleArray *da, char *s)
{
    Darts::DoubleArray::result_pair_type  result_pair;
    result_pair = da->exactMatchSearch<Darts::DoubleArray::result_pair_type>(s);
    return std::make_pair(result_pair.value, result_pair.length);
}


inline std::vector<std::pair<int, size_t> > _common_prefix_search(Darts::DoubleArray *da, char *s)
{
    const long unsigned int RESULT_SIZE = 1024;
    std::vector<std::pair<int, size_t> > r;
    Darts::DoubleArray::result_pair_type  result_pair[RESULT_SIZE];
    size_t num = da->commonPrefixSearch(s, result_pair, sizeof(result_pair));
    for (size_t i = 0; i < std::min(num, RESULT_SIZE); ++i) {
        r.push_back(std::make_pair(result_pair[i].value, result_pair[i].length));
    }
    return r;
}


inline CharInfo _get_char_info(void *m, size_t offset, unsigned short code_point)
{
    return reinterpret_cast<CharInfo *>(m + offset)[code_point];
}


inline std::vector<std::pair<Entry, std::string> >_get_entries(void *entry, void *feature, unsigned int index, unsigned int count)
{
    std::vector<std::pair<Entry, std::string> > results;
    for (unsigned int i = 0; i< count; ++i) {
        Entry e = reinterpret_cast<Entry *>(entry)[index+i];
        std::string s(reinterpret_cast<char *>(feature) + e.feature);
        results.push_back(std::make_pair(e, s));
    }
    return results;
}


inline std::string _get_feature(void *entry, void *feature, unsigned int index)
{
    Entry e = reinterpret_cast<Entry *>(entry)[index];
    std::string s(reinterpret_cast<char *>(feature) + e.feature);
    return s;
}


inline std::vector<std::vector<int> > _lookup(Darts::DoubleArray *da, void *entry, char *s)
{
    std::vector<std::vector<int> > results;

    Darts::DoubleArray::result_pair_type  result_pair[1024];
    size_t num = da->commonPrefixSearch(s, result_pair, sizeof(result_pair));
    for (size_t i = 0; i < num; ++i) {
        unsigned int idx = result_pair[i].value >> 8;
        int count = result_pair[i].value & 0xFF;
        for (int j = 0; j < count; ++j) {
            Entry e = reinterpret_cast<Entry *>(entry)[idx + j];
            std::vector<int> v;
            v.push_back(e.lcAttr);
            v.push_back(e.rcAttr);
            v.push_back(e.posid);
            v.push_back(e.wcost);
            v.push_back(result_pair[i].length);
            v.push_back(idx + j);
            results.push_back(v);
        }
    }
    return results;
}


inline short _get_trans_cost(void *m, int id1, int id2, int matrix_lsize)
{
    int i = (id2 * matrix_lsize + id1) * 2 + 4;
    return *reinterpret_cast<short *>(m + i);
}
