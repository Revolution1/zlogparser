from __future__ import print_function

import argparse
import glob
import logging
import os
import sys
import time

from preprocess import LogStream
from storage import LogStorage

level = os.getenv('LOG_LEVEL') or logging.INFO
LOG_FORMAT = '[%(levelname)-5s] %(message)s'
# LOG_FORMAT = '[%(levelname)-5s][%(name)-32s][%(process)-5d] %(message)s'
console_handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(LOG_FORMAT)
console_handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)
root_logger.setLevel(level)

LOG = root_logger

INDEX_STORAGE = './log-cache'


def index_file(filepath):
    LOG = logging.getLogger()
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(logging.Formatter('[%(levelname)-5s][%(name)-32s][%(process)-5d] %(message)s'))
    LOG.handlers = [console_handler]
    LOG.name = 'indexer:%s' % filepath.split('/')[-1]
    try:
        stream = LogStream(filepath)
        LOG.info('indexing: ' + stream.node)
        storage = LogStorage(stream.node, './log-cache')
        bulk_size = 100
        buf = []
        for l in stream:
            buf.append(l)
            if len(buf) == bulk_size:
                storage.put_log_many(buf)
                buf = []
        if buf:
            storage.put_log_many(buf)
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


def list_cmd(field, node=None):
    if field == 'node':
        if not os.path.isdir(INDEX_STORAGE):
            LOG.error('index dir %s not exists or is not a dir.' % INDEX_STORAGE)
        nodes = [os.path.split(p)[-1].rpartition('.')[0] for p in glob.glob(os.path.join(INDEX_STORAGE, '*.sqlite3'))]
        # print('Indexed Nodes:')
        print('\n'.join(sorted(nodes)))
    else:
        if not node:
            LOG.error('node not provided')
            sys.exit(1)

def range_cmd():
    pass


def query_cmd():
    pass


def search_cmd():
    pass


def callstack_cmd():
    pass


commands = {
    'index': index_cmd,
    'list': list_cmd,
    'range': range_cmd,
    'query': query_cmd,
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
    parser = argparse.ArgumentParser(description='Zilliqa Log Analyzer')

    sub = parser.add_subparsers(dest='command')

    cmd_index = sub.add_parser('index', description='Index log file[s] for further analyze')
    cmd_index.add_argument(
        'file', nargs='+', help='the log Zilliqa files to index')

    cmd_list = sub.add_parser('list', description='List items of indexed logs')
    cmd_list.add_argument('node', nargs='?', help='get unique filed in particular node, optional when filed=node')
    cmd_list.add_argument(
        'field', help='the field to list, one of (node|fields|tid|function)')

    cmd_range = sub.add_parser('range', description='Get logs of particular time range')
    cmd_range.add_argument('start', help='the start datetime to query')
    cmd_range.add_argument('end', nargs='?', help='the end datetime to query, default to now')

    cmd_query = sub.add_parser('query', description='Query the logs by SQL')
    cmd_query.add_argument('node', help='the node to query log from')
    cmd_query.add_argument('query_string', help='the query string to execute (sqlite3 WHERE clause)')

    cmd_search = sub.add_parser('search', description='Do a full-text search over log message')
    cmd_search.add_argument('node', nargs='?', help='the node to search log from')
    cmd_search.add_argument('keyword', help='the keyword to search')

    cmd_callstack = sub.add_parser('callstack', description='Get callstack of particular task')
    cmd_callstack.add_argument('node', help='the node to get log from')
    cmd_callstack.add_argument('tid', type=int, help='the thread ID of the task')
    cmd_callstack.add_argument('task', help='the task(function) name to search')

    kwargs = vars(parser.parse_args())
    # LOG.info(kwargs)

    command = kwargs.pop('command')

    func = commands[command]
    if command == 'index':
        return func(*kwargs['file'])
    else:
        return func(**kwargs)


if __name__ == '__main__':
    main()
