from __future__ import print_function

import argparse
import glob
import logging
import os
import sys
import time

import recovery
from preprocess import LogStream
from storage import LogStorage
from utils import indent_block
from utils import parse_puttime
from utils import shorten_time

LOG_LEVEL = os.getenv('LOG_LEVEL') or logging.INFO
LOG_FORMAT = '[%(levelname)-5s] %(message)s'
# LOG_FORMAT = '[%(levelname)-5s][%(name)-32s][%(process)-5d] %(message)s'
console_handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(LOG_FORMAT)
console_handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)
root_logger.setLevel(LOG_LEVEL)

LOG = root_logger

INDEX_STORAGE = './log-cache'


def index_file(filepath):
    LOG = logging.getLogger()
    console_handler.setFormatter(logging.Formatter('[%(levelname)-5s][%(name)-32s][%(process)-5d] %(message)s'))
    LOG.name = 'indexer:%s' % filepath.split('/')[-1]
    try:
        stream = LogStream(filepath)
        LOG.info('indexing: ' + stream.node)
        store = LogStorage(stream.node, './log-cache')
        if os.path.isfile(store.path):
            LOG.error('log index file %s already exists' % store.path)
        store.init()
        store.create_log_table()
        bulk_size = 256
        buf = []
        # with storage.transaction_context():
        for l in stream:
            buf.append(l)
            if len(buf) == bulk_size:
                store.put_log_many(buf)
                buf = []
        if buf:
            store.put_log_many(buf)
        store.gen_items()
        store.create_index()
        store.create_fulltext_index_fts()
        LOG.info('done indexing: ' + stream.node)
    except:
        LOG.exception('error wile index file: ' + filepath)


def index_cmd(*files):
    for f in files:
        if not os.path.isfile(f):
            raise AttributeError('%s not exists or is not a file' % f)

    from multiprocessing import Pool, cpu_count

    workers = cpu_count()
    pool = Pool(workers)

    size = sum(os.stat(i).st_size for i in files)
    t = time.time()
    pool.map(index_file, files)
    dur = time.time() - t

    print('workers:  %s' % workers)
    print('files:    %s' % len(files))
    print('duration: %s %s' % ('%.1f' % dur, 'sec'))
    print('speed:    %s %s' % ('%.1f' % (size / dur / 1024 / 1024), 'Mb/s'))


def indexed_nodes():
    if not os.path.isdir(INDEX_STORAGE):
        LOG.error('index dir %s not exists or is not a dir.' % INDEX_STORAGE)
        sys.exit(1)
    return [os.path.split(p)[-1].rpartition('.')[0] for p in glob.glob(os.path.join(INDEX_STORAGE, '*.sqlite3'))]


def get_node_storage(node):
    if node not in indexed_nodes():
        LOG.error('node index not exists')
        sys.exit(1)
    return LogStorage(node, INDEX_STORAGE)


def list_cmd(item, node=None, recover=False):
    if item == 'node':
        print('\n'.join(sorted(indexed_nodes())))
    elif item == 'field':
        print('\n'.join((
            'Fields of the Log:',
            'level     -   log level',
            'tid       -   thread ID',
            'puttime   -   datetime of the log (YYYY-MM-DD HH:MM:SS.sss)',
            'fileline  -   filepath:lineno (filepath is left truncated)',
            'function  -   right truncated function name of the log',
            'message   -   log message'
        )))
    else:
        if not node:
            LOG.error('node not provided')
            sys.exit(1)
        if item == 'function':
            store = get_node_storage(node)
            cur = store.con.execute("SELECT DISTINCT function, fileline from log WHERE message='BEG'")
            for function, fileline in cur:
                if recover:
                    function, filepath, lineno = recovery.recover(function, fileline)
                    if len(function) > 20:
                        function = '%s[%s]' % (function[:20], function[20:])
                    fileline = '%s:%s' % (filepath, lineno)
                print('%-55s  %s' % (function, fileline))
        else:
            store = get_node_storage(node)
            cur = store.con.execute('SELECT value from items WHERE field=?', (item,))
            print('\n'.join(sorted(i[0] for i in cur)))


def print_rows(cur, recover):
    for l in cur:
        _, level, tid, puttime, fileline, function, message = l
        if recover:
            function, filepath, lineno = recovery.recover(function, fileline)
            function = '%-40s' % function
            fileline = '%-50s:%-4s' % (filepath, lineno)
        print('  '.join([level, '{:5}'.format(tid), puttime, fileline, function, message]))


def range_cmd(node, start, end, recover=False):
    store = get_node_storage(node)
    cur = store.con.execute(
        'SELECT * from log WHERE puttime BETWEEN DATETIME(?) AND DATETIME(?)',
        (start, end))
    print_rows(cur, recover)


def query_cmd(node, query_string, recover=False):
    store = get_node_storage(node)
    cur = store.con.execute('SELECT * from log WHERE ' + query_string)
    print_rows(cur, recover)


def full_text_index_cmd():
    pass


def search_cmd(node, keywords, recover=False):
    store = get_node_storage(node)
    cur = store.search(keywords)
    print_rows(cur, recover)


def callstack_cmd(node, tid, puttime, task, strict=False, show_msg=False):
    """
    BEGIN function() [xxx.cpp:123]
    """

    store = get_node_storage(node)
    cur = store.con.execute(
        "SELECT * FROM log WHERE tid=? AND function=? and message='BEG' "
        "order by abs(julianday(puttime) - julianday(?)) limit 1",
        (tid, task[:20], puttime)
    )
    # TODO: uniq
    start = cur.fetchone()
    if not start:
        LOG.error("Stack entry not found")
        sys.exit(1)
    lid, lvl, tid, put, fl, fun, msg = start
    cur = store.con.execute("SELECT * FROM log WHERE id>=? AND tid=?", (lid, tid,))
    fun, fi, ln = recovery.recover(fun, fl)
    stack = []
    print("Displaying Call Stack of %s() in thread %s" % (fun, tid))
    for lid, lvl, tid, put, fl, fun, msg in cur:
        fun, fi, ln = recovery.recover(fun, fl)
        if msg == 'BEG':
            stack.append(('BEG', fun, fi, ln, put))
            print(
                indent_block('BEGIN  %s        [%s]  [%s:%s]' % (fun + '()', shorten_time(put), fi, ln), len(stack) - 1)
            )
        elif msg == 'END':
            top = stack[-1]
            duration = (parse_puttime(put) - parse_puttime(top[4])).total_seconds()
            if top[1] == fun and top[2] == fi:
                print(
                    indent_block(
                        'END  %s        [duration:%.2fs  %s]  [%s:%s]' % (
                            fun + '()', duration, shorten_time(put), fi, ln),
                        len(stack) - 1
                    )
                )
                stack.pop()
            elif strict:
                LOG.error(
                    "Unmatched function end:\n"
                    'END  %s        [duration:%.2fs  %s]  [%s:%s]' % (fun + '()', duration, shorten_time(put), fi, ln)
                )
                sys.exit(1)
            else:
                print(
                    indent_block(
                        "Unmatched function end:\n"
                        'END  %s        [duration:%.2fs  %s]  [%s:%s]' % (
                            fun + '()', duration, shorten_time(put), fi, ln),
                        len(stack)
                    )
                )
            if not stack:
                break
        else:
            if show_msg:
                msg = '\n' + indent_block(msg, len(stack))
            else:
                msg = ''
            print(
                indent_block(
                    '[%s]  %s        [%s]  [%s:%s]' % (lvl, fun + '()', shorten_time(put), fi, ln)
                    + msg,
                    len(stack)
                )
            )


commands = {
    'index': index_cmd,
    'ls': list_cmd,
    'range': range_cmd,
    'query': query_cmd,
    'full-text-index': full_text_index_cmd,
    'search': search_cmd,
    'callstack': callstack_cmd
}


# - See what every node is doing at a particular moment or time range
# - Filter the logs based on some keywords or fields
# - Get the call stack of a particular task being conducted by one of the thread
# - Other views you think it's good to have
def main():
    """
    Usage:
        zlogparser index PATH
                   list node | FIELD
                   range START [END]
                   query NODE QUERY_STRING
                   search KEYWORD
                   callstack NODE TID TASK
    """
    parser = argparse.ArgumentParser(prog='zlogparser', description='Zilliqa Log Analyzer')
    sub = parser.add_subparsers(title='commands', dest='command')

    # index
    cmd_index = sub.add_parser('index', description='Index log file[s] for further analysis')
    cmd_index.add_argument(
        'file', nargs='+', help='the log Zilliqa files to index')

    # ls
    cmd_list = sub.add_parser('ls', description='List items of indexed logs')
    cmd_list.add_argument('-r', '--recover', dest='recover', action='store_true', required=False,
                          help='try to recover the full filepath and function name')
    cmd_list.add_argument('node', nargs='?', help='get unique filed in particular node, optional when filed=node')
    cmd_list.add_argument(
        'item', help='the field to list, one of (node|field|level|tid|function)',

        choices=('node', 'field', 'level', 'tid', 'function'))

    # range
    cmd_range = sub.add_parser('range', description='Get logs of particular time range')
    cmd_range.add_argument('node', help='the node to query log from')
    cmd_range.add_argument('-s', '--start', dest='start', default='1970-01-01', required=False,
                           help='the start datetime to query, default to unix-epoch')
    cmd_range.add_argument('-e', '--end', dest='end', default='now', required=False,
                           help='the end datetime to query, default to now')
    cmd_range.add_argument('-r', '--recover', dest='recover', action='store_true', required=False,
                           help='try to recover the full filepath and function name')

    # query
    cmd_query = sub.add_parser('query', description='Query the logs by SQL')
    cmd_query.add_argument('-r', '--recover', dest='recover', action='store_true', required=False,
                           help='try to recover the full filepath and function name')
    cmd_query.add_argument('node', help='the node to query log from')
    cmd_query.add_argument('query_string', help='the query string to execute (sqlite3 WHERE clause)')

    # search index
    # sub.add_parser('full-text-index', description='do full text indexing for "search" command')
    # search
    cmd_search = sub.add_parser('search', description='Do a full-text search over log message')
    cmd_search.add_argument('node', help='the node to search log from')
    cmd_search.add_argument('keywords', help="the keywords of the message to search, "
                                             "support '*' as wildcard, "
                                             "support logical operator (AND|OR|NOT)")
    cmd_search.add_argument('-r', '--recover', dest='recover', action='store_true', required=False,
                            help='try to recover the full filepath and function name')

    # callstack
    cmd_callstack = sub.add_parser('callstack', description='Get callstack of particular task')
    cmd_callstack.add_argument('node', help='the node to get log from')
    cmd_callstack.add_argument('tid', type=int, help='the thread ID of the task')
    cmd_callstack.add_argument('task', help='the task(function) name to search')
    cmd_callstack.add_argument('-t', '--puttime', dest='puttime', default='now',
                               help='find the task "BEG" call nearest to the puttime, default to now')
    cmd_callstack.add_argument('-s', '--strict', dest='strict', action='store_true',
                               help='raise error when callstack mismatched')
    cmd_callstack.add_argument('-m', '--show-msg', dest='show_msg', action='store_true',
                               help='show message in printed stack')

    kwargs = vars(parser.parse_args())
    # LOG.info(kwargs)

    command = kwargs.pop('command')
    if not command:
        parser.print_usage()
        print('zlogparser: error: too few arguments')
        sys.exit(2)
    func = commands[command]
    if command == 'index':
        return func(*kwargs['file'])
    else:
        return func(**kwargs)


if __name__ == '__main__':
    main()
