#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from optparse import OptionParser

from . import converter
from . import __version__


def _parse_options():
    """Parses md2slides's command line options"""

    parser = OptionParser(
        usage="%prog [options] input.md ...",
        description="Convert Markdown to LaTex beamer",
        epilog="Note: PDF output needs the `pdflatex`",
        version="%prog " + __version__)

    parser.add_option(
            "-t", "--theme",
            dest="theme",
            help="use theme (default: Warsaw)",
            default='Warsaw')

    parser.add_option(
        "-o", "--output_file",
        dest="output_file",
        help="path to the tex/pdf file: .tex/.pdf",
        metavar="FILE",
        default='slides.tex')


    (options, args) = parser.parse_args()

    if not args:
        parser.print_help()
        sys.exit(1)

    return options, args[0]


def log(message, type):
    """Log notices to stdout and errors to stderr"""

    (sys.stdout if type == 'notice' else sys.stderr).write(message + "\n")


def run(input_file, options):
    """Runs the Converter using parsed options."""

    options.logger = log
    converter.Converter(input_file, **options.__dict__).execute()

def show_info():

    print '########################################'
    print '######   md2slides               #######'
    print '######    markdown -> slides     #######'
    print '######     To make life easy     #######'
    print '######      for HEP scientists!  #######'
    print '########################################'

def main():
    """Main program entry point"""

    show_info()

    options, input_file = _parse_options()

    try:
        run(input_file, options)
    except Exception as e:
        sys.stderr.write("Error: %s\n" % e)
        sys.exit(1)


if __name__ == '__main__':
    main()
