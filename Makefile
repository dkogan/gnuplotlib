all: README README.org

# a multiple-target pattern rule means that a single invocation of the command
# builds all the targets, which is what I want here
%EADME %EADME.org: gnuplotlib.py README.footer.org extract_README.py
	python3 extract_README.py gnuplotlib

DIST_VERSION := $(or $(shell < gnuplotlib.py perl -ne "if(/__version__ = '(.*)'/) { print \$$1; exit}"), $(error "Couldn't parse the distribution version"))

DIST := dist/gnuplotlib-$(DIST_VERSION).tar.gz
$(DIST): README

# make distribution tarball
$(DIST):
	python3 setup.py sdist
.PHONY: $(DIST) # rebuild it unconditionally

dist: $(DIST)
.PHONY: dist


# make and upload the distribution tarball
dist_upload: $(DIST)
	twine upload --verbose $(DIST)
.PHONY: dist_upload


clean:
	rm -f README.org README
.PHONY: clean

