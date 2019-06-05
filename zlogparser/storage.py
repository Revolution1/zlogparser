import errno
import logging
import os
import sqlite3
from contextlib import contextmanager

from tokenizer import tokenize
from utils import cached_property

LOG = logging.getLogger()

SQL_CREATE_TABLE = '''
CREATE TABLE IF NOT EXISTS log (
id              INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
level           CHAR(8)  NOT NULL,
tid             INTEGER  NOT NULL,
puttime         CHAR(21) NOT NULL,
fileline        CHAR(20),
function        CHAR(20) NOT NULL,
message         TEXT
)
'''

SQL_CREATE_TABLE_ITEMS = '''
CREATE TABLE IF NOT EXISTS items (
    field TEXT    NOT NULL,
    value TEXT    NOT NULL,
    PRIMARY KEY (field, value)
)
'''

# type: 0 - message; 1 - fileline
SQL_CREATE_TABLE_INVERTED_INDEX = '''
CREATE TABLE IF NOT EXISTS invidx (
    word TEXT    NOT NULL,
    id   INTEGER NOT NULL,
    type INTEGER NOT NULL,
    PRIMARY KEY (word, id)
)
'''

SQL_CREATE_INDEX_LVL = 'CREATE INDEX IF NOT EXISTS log_level ON  log (level)'
SQL_CREATE_INDEX_TID = 'CREATE INDEX IF NOT EXISTS log_tid ON  log (tid)'
SQL_CREATE_INDEX_TME = 'CREATE INDEX IF NOT EXISTS log_puttime ON log (puttime)'
SQL_CREATE_INDEX_FUN = 'CREATE INDEX IF NOT EXISTS log_function ON log (function)'
SQL_CREATE_INDEX_FIL = 'CREATE INDEX IF NOT EXISTS log_fileline ON log (fileline)'


class LogStorage(object):
    def __init__(self, node, storage_dir):
        self.node = node
        self.storage_dir = storage_dir
        self.path = os.path.join(storage_dir, node + '.sqlite3')

    @cached_property
    def con(self):
        return sqlite3.connect(self.path)

    def close(self):
        self.con.commit()
        return self.con.close()

    def __del__(self):
        self.close()

    def init(self):
        if not os.path.exists(self.storage_dir):
            LOG.info('creating index storage dir: %s' % self.storage_dir)
            try:
                os.makedirs(self.storage_dir)
            except OSError as e:
                # be happy if someone already created the path
                if e.errno != errno.EEXIST:
                    raise
        elif not os.path.isdir(self.storage_dir):
            raise RuntimeError('%s exists but is not a directory' % self.storage_dir)
        self.con.execute('PRAGMA synchronous = OFF')
        self.con.execute("PRAGMA read_uncommitted = true")
        self.con.execute("PRAGMA cache_size = -40000")
        self.con.execute("PRAGMA journal_mode = MEMORY")
        # self.con.execute("PRAGMA journal_mode = OFF")

    def create_log_table(self):
        self.con.execute(SQL_CREATE_TABLE)
        self.con.execute(SQL_CREATE_TABLE_ITEMS)

    def put_log(self, log):
        return self.con.execute(
            'INSERT INTO log (level, tid, puttime, fileline, function, message) VALUES (?,?,?,?,?,?)',
            log
        )

    def put_log_many(self, logs):
        return self.con.executemany(
            'INSERT INTO log (level, tid, puttime, fileline, function, message) VALUES (?,?,?,?,?,?)',
            logs
        )

    def create_index(self):  # create index after insertion can improve performance
        # self.con.execute(SQL_CREATE_INDEX_LVL)
        self.con.execute(SQL_CREATE_INDEX_TID)
        self.con.execute(SQL_CREATE_INDEX_TME)
        self.con.execute(SQL_CREATE_INDEX_FUN)
        self.con.execute(SQL_CREATE_INDEX_FIL)

    def is_fts(self):
        return self.con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ftsidx'").fetchone()

    def create_fulltext_index_fts(self):
        # https://www.sqlite.org/fts3.html#section_3
        self.con.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS ftsidx USING fts4(content='log', message, tokenize=porter)"
        )
        self.con.execute("INSERT INTO ftsidx(docid, message) SELECT id, message FROM log")

    def search(self, q):
        return self.con.execute("select * from log where id in (select docid from ftsidx where message match ?)", (q,))

    def create_fulltext_index_py(self):
        self.con.execute(SQL_CREATE_TABLE_INVERTED_INDEX)
        cur = self.con.execute("SELECT id, fileline, message FROM log")
        for lid, fileline, message in cur:
            if message in ('BEG', 'END'):
                continue
            tokens = tokenize(message)
            words = ((w,) for w in tokens)
            self.con.executemany("INSERT INTO invidx (word, id, type) VALUES (?, %s, 0)" % lid, words)
        self.con.execute('CREATE INDEX IF NOT EXISTS inv_word ON invidx (word)')

    @contextmanager
    def transaction_context(self):
        self.con.execute("BEGIN TRANSACTION")
        yield
        self.con.commit()

    def gen_items(self):
        # for filed in ('level', 'tid', 'fileline', 'function'):
        for filed in ('level', 'tid'):
            self.con.execute("INSERT INTO items (field, value) SELECT DISTINCT '{f}', {f} FROM log".format(f=filed))


if __name__ == '__main__':
    from preprocess import LogStream
    import time

    LOG.addHandler(logging.StreamHandler())

    logfile = 'logs/community-lookup-0.txt'

    size = os.stat(logfile).st_size
    t1 = time.time()

    stream = LogStream(logfile)
    store = LogStorage(stream.node, './log-cache')
    store.init()
    store.create_log_table()
    bulk_size = 100
    buf = []
    for l in stream:
        buf.append(l)
        if len(buf) == bulk_size:
            try:
                store.put_log_many(buf)
            except sqlite3.OperationalError:
                for b in buf:
                    if len(b) < 6:
                        print(b)
                raise
            buf = []
    if buf:
        store.put_log_many(buf)
    store.gen_items()
    store.create_index()
    dur = time.time() - t1
    # print 'workers: ', workers
    print('duration: %.2f sec' % dur)
    print('speed: %.2f Mb/s' % (size / dur / 1024 / 1024))

    print('create full-text index')
    t1 = time.time()
    store.create_fulltext_index_fts()
    dur = time.time() - t1
    print('duration: %.2f sec' % dur)
    print(store.search('epoch').fetchone())
    print(store.search('epo*').fetchone())
    print(store.search('epo').fetchone())
