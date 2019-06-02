import os
import sqlite3

from utils import cached_property

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

SQL_CREATE_INDEX_TID = 'CREATE INDEX IF NOT EXISTS log_tid ON  log (tid)'
SQL_CREATE_INDEX_TME = 'CREATE INDEX IF NOT EXISTS log_time ON log (puttime)'

STORAGE_PATH = './log-cache'


class LogStorage(object):
    def __init__(self, node):
        self.node = node
        self.path = os.path.join(STORAGE_PATH, node + '.sqlite3')
        self.init()

    @cached_property
    def con(self):
        if not os.path.exists(STORAGE_PATH):
            os.mkdir(STORAGE_PATH)
        return sqlite3.connect(self.path)

    def close(self):
        self.con.commit()
        return self.con.close()

    def __del__(self):
        self.close()

    def init(self):
        self.con.execute(SQL_CREATE_TABLE)
        self.con.execute(SQL_CREATE_INDEX_TID)
        self.con.execute(SQL_CREATE_INDEX_TME)
        self.con.execute('PRAGMA synchronous = OFF')

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


if __name__ == '__main__':
    from preprocess import LogStream
    import time

    logfile = 'logs/community-lookup-0.txt'

    size = os.stat(logfile).st_size
    t1 = time.time()

    stream = LogStream(logfile)
    storage = LogStorage(stream.node)
    bulk_size = 100
    buf = []
    for l in stream:
        buf.append(l)
        if len(buf) == bulk_size:
            try:
                storage.put_log_many(buf)
            except sqlite3.OperationalError:
                for b in buf:
                    if len(b) < 6:
                        print b
                raise
            buf = []
    if buf:
        storage.put_log_many(buf)
    dur = time.time() - t1
    # print 'workers: ', workers
    print 'duration:', dur, 'sec'
    print 'speed:   ', size / dur / 1024 / 1024, 'Mb/s'
