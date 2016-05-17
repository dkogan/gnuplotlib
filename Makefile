all: README README.org

# a multiple-target pattern rule means that a single invocation of the command
# builds all the targets, which is what I want here
%EADME %EADME.org: gnuplotlib.py README.footer.org extract_README.py
	python extract_README.py gnuplotlib
clean:
	rm -f README.org README
.PHONY: clean

