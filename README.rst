=================
janomecabdic
=================

This is an add-on package for janome https://mocobeta.github.io/janome/ .

Janome can use compiled dictionaries for MeCab https://taku910.github.io/mecab/
via janomecabdic.

Requirements
-------------------------

- MeCab and MeCab dictionary (utf-8 encoded)
- Python 3.5+
- Cython and C++ (optional)
- janome

Instration
-------------------------

Install MeCab and MeCab dictionary.
(e.g.: Ubuntu/Debian)

::

    sudo apt install mecab mecab-ipadic-utf8

Install C++ compiler and Cython
(e.g.: Ubuntu/Debian),
as you like.

::

    sudo apt install build-essential
    pip install cython

Install janome and janomecabdic.

::

    pip install janome janomecabdic


Example (use /etc/mecabrc defined dictionary)
------------------------------------------------------------

Sample code
+++++++++++++++

::

    >>> from janome.tokenizer import Tokenizer
    >>> from janomecabdic import MeCabDictionary
    >>> t = Tokenizer()
    >>> t.sys_dic = MeCabDictionary()
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


Neologd example (tokenize with a specific dictionary)
--------------------------------------------------------------------

Install Neologd (e.g. Ubuntu/Debian)
+++++++++++++++++++++++++++++++++++++++++

::

   sudo apt install mecab mecab-ipadic-utf8 libmecab-dev
   git clone --depth 1 git@github.com:neologd/mecab-ipadic-neologd.git
   cd mecab-ipadic-neologd
   echo `mecab-config --dicdir`"/mecab-ipadic-neologd"
   ./bin/install-mecab-ipadic-neologd -n



Sample code
+++++++++++++++

::

   >>> from janome.tokenizer import Tokenizer
   >>> from janomecabdic import MeCabDictionary
   >>> t = Tokenizer()
   >>> t.sys_dic = MeCabDictionary('/usr/lib/mecab/dic/mecab-ipadic-neologd')
   >>> for token in t.tokenize('8月3日に放送された「中居正広の金曜日のスマイルたちへ」(TBS系)で、1日たった5分でぽっこりおなかを解消するというダイエット方法を紹介。キンタロー。のダイエットにも密着'):
   ...     print(token)
   ...
   8月3日  名詞,固有名詞,一般,*,*,*,8月3日,ハチガツミッカ,ハチガツミッカ
   に      助詞,格助詞,一般,*,*,*,に,ニ,ニ
   放送    名詞,サ変接続,*,*,*,*,放送,ホウソウ,ホーソー
   さ      動詞,自立,*,*,サ変・スル,未然レル接続,する,サ,サ
   れ      動詞,接尾,*,*,一段,連用形,れる,レ,レ
   た      助動詞,*,*,*,特殊・タ,基本形,た,タ,タ
   「      記号,括弧開,*,*,*,*,「,「,「
   中居正広の金曜日のスマイルたちへ        名詞,固有名詞,一般,*,*,*,中居正広の金曜日のスマイルたちへ,ナカイマサヒロノキンヨウビノスマイルタチヘ,ナカイマサヒロノキンヨービノスマイルタチヘ
   」(     記号,一般,*,*,*,*,」(,*,*
   TBS     名詞,固有名詞,一般,*,*,*,TBS,ティービーエス,ティービーエス
   系      名詞,接尾,一般,*,*,*,系,ケイ,ケイ
   )       記号,一般,*,*,*,*,),*,*
   で      助動詞,*,*,*,特殊・ダ,連用形,だ,デ,デ
   、      記号,読点,*,*,*,*,、,、,、
   1日     名詞,固有名詞,一般,*,*,*,1日,ツイタチ,ツイタチ
   たった  副詞,助詞類接続,*,*,*,*,たった,タッタ,タッタ
   5分     名詞,固有名詞,一般,*,*,*,5分,ゴフン,ゴフン
   で      助詞,格助詞,一般,*,*,*,で,デ,デ
   ぽっこりおなか  名詞,固有名詞,一般,*,*,*,ぽっこりおなか,ポッコリオナカ,ポッコリオナカ
   を      助詞,格助詞,一般,*,*,*,を,ヲ,ヲ
   解消    名詞,サ変接続,*,*,*,*,解消,カイショウ,カイショー
   する    動詞,自立,*,*,サ変・スル,基本形,する,スル,スル
   という  助詞,格助詞,連語,*,*,*,という,トイウ,トユウ
   ダイエット方法  名詞,固有名詞,一般,*,*,*,ダイエット方法,ダイエットホウホウ,ダイエットホウホー
   を      助詞,格助詞,一般,*,*,*,を,ヲ,ヲ
   紹介    名詞,サ変接続,*,*,*,*,紹介,ショウカイ,ショーカイ
   。      記号,句点,*,*,*,*,。,。,。
   キンタロー。    名詞,固有名詞,一般,*,*,*,キンタロー。,キンタロー,キンタロー
   の      助詞,連体化,*,*,*,*,の,ノ,ノ
   ダイエット      名詞,サ変接続,*,*,*,*,ダイエット,ダイエット,ダイエット
   に      助詞,格助詞,一般,*,*,*,に,ニ,ニ
   も      助詞,係助詞,*,*,*,*,も,モ,モ
   密着    名詞,サ変接続,*,*,*,*,密着,ミッチャク,ミッチャク
