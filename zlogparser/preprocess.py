import logging
import os

LOG = logging.getLogger()

INFO = 'INFO'
DEBUG = 'DEBUG'
WARNING = 'WARNING'
FATAL = 'FATAL'

# lp = r'\('
# rp = r'\)'
# lb = r'\['
# rb = r'\]'
#
# lbp = lb + lp
# rbp = rb + rp
#
# LOG_LEVEL = r'[A-Z]+'
# LOG_TID = r'\d+'
# LOG_TIME = r'.*'
# LOG_FILE_LINE = r'.*:\d+'
# LOG_FUNC_NAME = r'\w+'
# LOG_MSG = r'.*'
#
# LOG_START = re.compile(r'^' + LOG_LEVEL + lb)
# LOG_FIELD = re.compile(
#     lbp + LOG_LEVEL + rbp +
#     lb + r'\s*' + lp + LOG_TID + rbp +
#     lbp + LOG_TIME + rbp +
#     lbp + LOG_FILE_LINE + rbp +
#     lbp + LOG_FUNC_NAME + rp + r'\W*' + rb +
#     '\s*' + LOG_MSG
# )


LOG_FIELDS = [
    ('level', None),
    ('tid', lambda x: int(x)),
    # ('time', lambda x: datetime.datetime.strptime(x, '%y-%m-%dT%H:%M:%S.%f')),
    ('time', lambda x: '20' + x.replace('T', ' ')),
    ('fileline', None),
    ('function', None),
    ('msg', None)
]


class LogStream(object):
    def __init__(self, filename):
        self.filename = filename
        self.node = os.path.split(filename)[-1].rpartition('.')[0]
        self._fp = None
        self._msg_pending = False
        self._msg_buf = []
        self._log_buf = []
        self.open()

    def open(self):
        if not self._fp or self._fp.closed:
            self._fp = open(self.filename, 'rb')

    def reload(self):
        self.open()
        self.close()

    def close(self):
        self._fp.close()

    def __del__(self):
        self._fp.close()

    def __iter__(self):
        for line in self._fp:
            if not line:
                continue
            if line[0] == '[':
                if self._log_buf:
                    msg = '\n'.join(self._msg_buf)
                    log = self._log_buf
                    log.append(msg)
                    self._log_buf = []
                    self._msg_buf = []
                    self._msg_pending = False
                    yield log
                fields = line.split(']', 5)
                if len(fields) < 5:
                    LOG.error("Unparsed line: " + line)
                    continue
                for name, formatter in LOG_FIELDS:
                    f = fields.pop(0).lstrip('[').strip()
                    if formatter:
                        try:
                            f = formatter(f)
                        except Exception as e:
                            self._log_buf = []
                            self._msg_buf = []
                            self._msg_pending = False
                            LOG.error("Error: %s\n" % e + "Unparsed line: " + line)
                            continue
                    if name == 'msg':
                        self._msg_buf = [f]
                    else:
                        self._log_buf.append(f)
                self._msg_pending = True
            else:
                if not self._log_buf or not self._msg_pending:
                    LOG.error("Unparsed line: " + line)
                    continue
                self._msg_buf.append(line)
        if self._log_buf:
            self._log_buf.append('\n'.join(self._msg_buf))
            yield self._log_buf


def __process(l):
    try:
        stream = LogStream(l)
        print('processing:', stream.node)
        msg_len = 0
        for i in stream:
            msg_len = max(msg_len, len(i[-1]))
        print('done processing:', stream.node, 'max_msg:', msg_len)
    except:
        LOG.exception('error')


if __name__ == '__main__':
    import time
    import glob
    from multiprocessing import Pool, cpu_count

    workers = cpu_count()
    pool = Pool(workers)

    files = glob.glob('logs/*.txt')
    size = sum(os.stat(i).st_size for i in files)
    t = time.time()
    pool.map(__process, files)
    dur = time.time() - t
    print('workers: ', workers)
    print('count:   ', len(files))
    print('duration:', dur, 'sec')
    print('speed:   ', size / dur / 1024 / 1024, 'Mb/s')
