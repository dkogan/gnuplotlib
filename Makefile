# reroute the main POD into a separate README.pod if requested. This is here
# purely to generate a README.pod for the github front page
README.org: gnuplotlib.py
	perl -ne "if( /'''(.*)/) { if(\$$started) { exit; } else { \$$started = 1; } \$$_ = \$$1 } \
                  print if \$$started;" < $^ > $@

clean:
	rm -f README.org
.PHONY: clean

