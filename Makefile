all:

ctags.txt: Zilliqa
	ctags -R -x --languages=c++ Zilliqa | grep function > ctags.txt
