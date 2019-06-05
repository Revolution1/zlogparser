# Zilliqa Node Log Parser


- Written in python 2.7 (for maximum compatibility)

- Zero non-standard-lib depends

## Install

```
make install

# or

python ./setup.py install
```

## Usage

```
usage: zlogparser [-h] {index,ls,range,query,full-text-index,search,callstack} ...

Zilliqa Log Analyzer

optional arguments:
  -h, --help            show this help message and exit

commands:
  {index,ls,range,query,full-text-index,search,callstack}
```

## Commands

### index

```
usage: zlogparser index [-h] file [file ...]

Index log file[s] for further analysis

positional arguments:
  file        the log Zilliqa files to index

optional arguments:
  -h, --help            show this help message and exit
```

### ls

```
usage: zlogparser ls [-h] [-r] [node] {node,field,level,tid,function}

List items of indexed logs

positional arguments:
  node                  get unique filed in particular node, optional when
                        filed=node
  {node,field,level,tid,function}
                        the field to list, one of
                        (node|field|level|tid|function)

optional arguments:
  -h, --help            show this help message and exit
  -r, --recover         try to recover the full filepath and function name
```

### range

```
usage: zlogparser range [-h] [-s START] [-e END] [-r] node

Get logs of particular time range

positional arguments:
  node                  the node to query log from

optional arguments:
  -h, --help            show this help message and exit
  -s START, --start START
                        the start datetime to query, default to unix-epoch
  -e END, --end END     the end datetime to query, default to now
  -r, --recover         try to recover the full filepath and function name
```

### query

```
usage: zlogparser query [-h] [-r] node query_string

Query the logs by SQL

positional arguments:
  node           the node to query log from
  query_string   the query string to execute (sqlite3 WHERE clause)

optional arguments:
  -h, --help     show this help message and exit
  -r, --recover  try to recover the full filepath and function name
```

### search

```
usage: zlogparser search [-h] [-r] node keywords

Do a full-text search over log message

positional arguments:
  node           the node to search log from
  keywords       the keywords of the message to search, support '*' as
                 wildcard, support logical operator (AND|OR|NOT)

optional arguments:
  -h, --help     show this help message and exit
  -r, --recover  try to recover the full filepath and function name
```

### callstack

```
usage: zlogparser callstack [-h] [-t PUTTIME] [-s] [-m] node tid task

Get callstack of particular task

positional arguments:
  node                  the node to get log from
  tid                   the thread ID of the task
  task                  the task(function) name to search

optional arguments:
  -h, --help            show this help message and exit
  -t PUTTIME, --puttime PUTTIME
                        find the task "BEG" call nearest to the puttime,
                        default to now
  -s, --strict          raise error when callstack mismatched
  -m, --show-msg        show log message in printed stack
```
