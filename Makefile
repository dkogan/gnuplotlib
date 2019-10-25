all: README README.org

# a multiple-target pattern rule means that a single invocation of the command
# builds all the targets, which is what I want here
%EADME %EADME.org: gnuplotlib.py README.footer.org extract_README.py
	python3 extract_README.py gnuplotlib

# make distribution tarball
dist:
	python3 setup.py sdist
.PHONY: dist

# make and upload the distribution tarball
dist_upload:
	python3 setup.py sdist upload
.PHONY: dist_upload

clean:
	rm -f README.org README
.PHONY: clean

