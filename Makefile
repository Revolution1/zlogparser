all:

install:
	python setup.py install

ctags.txt: Zilliqa
	ctags -R -x --languages=c++ Zilliqa | grep function > ctags.txt
