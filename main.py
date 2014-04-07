"""
pyPdfCompare - Visually compare PDF documents

Usage:
    pyPdfCompare <pdfX> <pdfY> <pdfOutput> [options]

Options:
    --pagesX=<pages>    Comma-separated list of page numbers to compare.
    --pagesY=<pages>    Comma-separated list of page numbers to compare.
    --resolution=<dpi>  DPI resolution used to perform the comparison [default: 150].
    -a --all-pages      Export all pages, not just differences.
    -d --debug          Enable debugging.
    -v --version        Shows pyWatch version.
    -h --help           Show this screen.
"""

__author__ = 'Kristof Speeckaert'

from pyPdfCompare import main
from docopt import docopt
import sys
import logging


if __name__ == '__main__':

    arguments = docopt(__doc__, version='pyPdfCompare 1.0')

    #Configure debugging level
    if arguments['--debug']:
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s: %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    logging.debug(arguments)

    main(pdf_x=arguments['<pdfX>'],
         pdf_y=arguments['<pdfY>'],
         pdf_merged=arguments['<pdfOutput>'],
         extract_pages_x=arguments['--pagesX'],
         extract_pages_y=arguments['--pagesY'],
         all_pages=arguments['--all-pages'],
         pdf_res=arguments['--resolution'])
    sys.exit(0)