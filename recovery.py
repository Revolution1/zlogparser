cache = {}


def recover(function, fileline, tags=None):
    global cache
    if not tags:
        import tagindex
        tags = tagindex.tags
        cache = tagindex.cache
    if (function, fileline) in cache:
        return cache[(function, fileline)]
    else:
        path, lineno = fileline.split(':')
        lineno = int(lineno)
        tag_match = []
        for t in tags:
            _f = function.rstrip('()')
            if t[0].startswith(_f):
                tag_match.append(t)
        if not tag_match:
            func, path, lineno = function, path, lineno
        elif len(tag_match) > 1:
            lineno_diff = []
            for i in tag_match:
                if not i[1].endswith(path):
                    continue
                lineno_diff.append((abs(lineno - i[2]), i))
            if not lineno_diff:
                func, path, lineno = function, path, lineno
            else:
                _, (func, path, _) = min(lineno_diff, key=lambda x: x[0])
        else:
            func, path, _ = tag_match[0]
        cache[(function, fileline)] = func, path, lineno
        return func, path, lineno


if __name__ == '__main__':
    print recover('ProcessStateDeltaFro', 'ckProcessing.cpp:788')
    print recover('ProcessStateDelta', 'ckProcessing.cpp:788')
    print recover('ProcessStateDelta', 'ckProcessing.cpp:787')
    print recover('P', 'ckProcessing.cpp:788')
    print recover('ProcessStateDelta', 'p:788')
    print recover('ProcessS', 'g.cpp:700')
