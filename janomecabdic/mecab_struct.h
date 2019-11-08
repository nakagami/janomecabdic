//  MeCab -- Yet Another Part-of-Speech and Morphological Analyzer
//
//  Copyright(C) 2001-2006 Taku Kudo <taku@chasen.org>
//  Copyright(C) 2004-2006 Nippon Telegraph and Telephone Corporation
#ifndef MECAB_STRUCT_H_
#define MECAB_STRUCT_H_

struct Entry {
  unsigned short lcAttr;
  unsigned short rcAttr;
  unsigned short posid;
  short wcost;
  unsigned int   feature;
  unsigned int   compound;
};


struct CharInfo {
  unsigned int type:         18;
  unsigned int default_type: 8;
  unsigned int length:       4;
  unsigned int group:        1;
  unsigned int invoke:       1;
  CharInfo() : type(0), default_type(0), length(0), group(0), invoke(0) {}
  bool isKindOf(CharInfo c) const { return type & c.type; }
};

#endif   // MECAB_STRUCT_H_
