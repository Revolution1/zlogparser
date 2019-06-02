import cPickle

index = {}

with open('zsources.txt') as f:
    for l in f:  # readline
        index[l[-16:]] = l

DUMP_FILE='zourcesdump.pickle'
with open(DUMP_FILE, 'w') as w:
    cPickle.dump(index, w, protocol=2)

print("wrote %s indexes to %s" % (len(index), DUMP_FILE))
