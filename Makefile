all:

src-index: zsources.txt
	python gen-src-index.py

zsources.txt:
	find  Zilliqa -name '*.h' -o -name '*.hpp' -o -name '*.c' -o -name '*.cpp' > zsources.txt

clean-src-idx:
	rm -f zsources.txt zourcesdump.pickle
