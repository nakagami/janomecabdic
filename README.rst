=================
janomecabdic
=================

This is an add-on package for janome https://mocobeta.github.io/janome/ .

Janome can use compiled dictionaries for Mecab https://taku910.github.io/mecab/ 
via janomecabdic.

Example
-------------------------

::

    >>> from janome.tokenizer import Tokenizer
    >>> from janomecabdic import MecabDictionary
    >>> t = Tokenizer()
    >>> t.sys_dic = MecabDictionary()
    >>> for token in t.tokenize('すもももももももものうち'):
    ...     print(token)
    ...
    すもも  名詞,一般,*,*,*,*,すもも,スモモ,スモモ
    も      助詞,係助詞,*,*,*,*,も,モ,モ
    もも    名詞,一般,*,*,*,*,もも,モモ,モモ
    も      助詞,係助詞,*,*,*,*,も,モ,モ
    もも    名詞,一般,*,*,*,*,もも,モモ,モモ
    の      助詞,連体化,*,*,*,*,の,ノ,ノ
    うち    名詞,非自立,副詞可能,*,*,*,うち,ウチ,ウチ


Requirements
-------------------------

- MeCab + MeCab dictionary (utf-8 encoded)
- Python 3.5+
- Cython (with C++ compiler)
- janome

Instration
-------------------------

Install Mecab and Mecab dictionary.
(e.g.: Ubuntu/Debian)

::

    sudo apt install mecab mecab-ipadic-utf8

Install C++ compiler and Cython.
(e.g.: Ubuntu/Debian)

::

    sudo apt install build-essential
    pip intall cython

Install janome and janomecabdic.

::

    pip install janome janomecabdic

