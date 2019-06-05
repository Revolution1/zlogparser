import os

from stemmer import EnglishStemmer
import re
from string import punctuation
from string import lowercase
import itertools

stm = EnglishStemmer()

punctuation_set = frozenset(punctuation)

STOP_WORDS = frozenset(('a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'can',
                        'for', 'from', 'have', 'if', 'in', 'is', 'it', 'may',
                        'not', 'of', 'on', 'or', 'tbd', 'that', 'the', 'this',
                        'to', 'us', 'we', 'when', 'will', 'with', 'yet',
                        'you', 'your', 'beg', 'end'))

ADDR_REG = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+')

HEX_REG = re.compile(r'[0-9a-f]{2,}')

DELIMITER_REG = re.compile(r'[=,]+')

NON_WORD_REG = re.compile(r'\W')

MIN_TOKEN_SIZE = 3

def path_tokenize(p):
    return set(i for i in (stm.stem(i) for i in p.lower().replace('\\', '/').split('/')) if i)


def _tokenize_token(t):
    tokens = []
    buf = []
    for c in t:
        if c in punctuation_set and buf:
            tokens.append(''.join(buf))
            buf = []
        else:
            buf.append(c)
    if buf:
        tokens.append(''.join(buf))
    return (
        stm.stem(t) for t in tokens
        if t and
        len(t) >= MIN_TOKEN_SIZE and
        t not in STOP_WORDS
    )


def tokenize(s):
    s = s.lower()
    tokens = itertools.chain(*(DELIMITER_REG.split(t) for t in s.split()))  # split
    tokens = [t.strip(punctuation) for t in tokens]
    tokens = [
        t for t in tokens
        if t and
           len(t) >= MIN_TOKEN_SIZE and
           t not in STOP_WORDS
    ]
    tokens = [stm.stem(t) for t in tokens]
    result = set(tokens)
    for t in tokens:
        if not t.isalpha() and not t.isalnum() and not t.isdecimal():
            result.update(_tokenize_token(t))
        elif t.startswith('0x'):
            result.add(t[2:])
    return result


if __name__ == '__main__':
    import pprint

    pprint.pprint(path_tokenize('/Users/revol/firestack/code/zlogparser.txt'))

    line = '''\
Incoming broadcast <54.218.55.134:46667> (Len=798): 012200000318BEE23EACFB58B9E611D2296D3E522A2E9F8DACA91FD7F4BF...
FinalBlock 24460 state delta (Len=0):
State Delta hash received from finalblock is null, skip processing state delta
Storing TxBlock:
<TxBlock>

<BlockBase>

 m_blockHash = 9536a3d7f4a5e504f30fa882cd8d98b4994ae775e5bd1d1f43bf9bfdb3824d6f

 m_timestamp = 1549574226701924

<BlockHeaderBase>

 m_version       = 1

 m_committeeHash = a2e0e3cb0b76e232095c9f6c0ebf908ca8b9ce2da0a65fd46e327265c74c9e6b

 m_prevHash      = c4b27b30d771dea68b3efa33887de48c5326a8a53b9f2140a6b977228b38a5c0

<TxBlockHeader>

 m_gasLimit    = 200000

 m_gasUsed     = 0

 m_rewards     = 0

 m_blockNum    = 24460

 m_numTxs      = 0

 m_minerPubKey = 0x02081DCD3D93A4406E6D90241931A4D8A28553EC7BA28AB5B51D35D992CA2C7383

 m_dsBlockNum  = 245

<TxBlockHashSet>

 m_stateRootHash  = 573e4975096ebd6368963d5df85d22afae4611bbdd4b0d3d4fbcfc29ac3234c4

 m_stateDeltaHash = 0000000000000000000000000000000000000000000000000000000000000000

 m_mbInfoHash     = a55d0022b55f92d779ac470c3b2bad2f39862568323a257086125db2f24a4023

<MicroBlockInfo>

 t.m_microBlockHash = b72aa866f11452195c80406992187b7876493912991bf23761ce03f258ab0e3f

 t.m_txnRootHash    = 0000000000000000000000000000000000000000000000000000000000000000

 t.m_shardId        = 0

<MicroBlockInfo>

 t.m_microBlockHash = 9b72be629ec9a6a2be8a6a23243cb9f6c20fc410ba1e9581d4a682bef3ee5690

 t.m_txnRootHash    = 0000000000000000000000000000000000000000000000000000000000000000

 t.m_shardId        = 1

<MicroBlockInfo>

 t.m_microBlockHash = a074f7c60ebd739423da39203a9a9fe79649aaf4c88b46e46ae6e04ad0707aa8

 t.m_txnRootHash    = 0000000000000000000000000000000000000000000000000000000000000000

 t.m_shardId        = 2

<MicroBlockInfo>

 t.m_microBlockHash = 93bff6355fb8c6e024841e5332d35445f458b09a7290fa9f95559592b3104ecc

 t.m_txnRootHash    = 0000000000000000000000000000000000000000000000000000000000000000

 t.m_shardId        = 3
'''
    pprint.pprint(tokenize(line))
