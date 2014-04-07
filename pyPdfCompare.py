__author__ = 'Kristof Speeckaert'

import PyPDF2
import logging
from wand.image import Image as wandImage
from PIL import Image, ImageChops
from io import BufferedRandom, BytesIO


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def split_pdf(src_filename, pdf_res,  page_list=None, img_format='png'):

    pdf_source = PyPDF2.PdfFileReader(open(src_filename, 'rb'))

    logging.debug('Source PDF {} contains {} pages'.format(src_filename, pdf_source.getNumPages()))
    pages = []

    if not page_list:
        log.debug('Extracting all pages from PDF')
        # no pages defined, so create a list of all page numbers
        page_list = list(range(pdf_source.getNumPages()))
    else:
        log.debug('Extracting {} page(s) from PDF'.format(len(page_list)))

    for page_nr in page_list:

        log.debug('Processing page {}'.format(page_nr))
        page = pdf_source.getPage(page_nr)

        log.debug('Extracting page from source PDF')
        # extract single page and save it to a temporary stream
        pdf_writer = PyPDF2.PdfFileWriter()
        pdf_writer.addPage(page)
        pdf_page_stream = BufferedRandom(BytesIO())
        pdf_writer.write(pdf_page_stream)
        # reset the binary stream's position to the beginning
        pdf_page_stream.seek(0)

        log.debug('Converting PDF page to image ({})'.format(img_format))
        # Define the resolution when opening the intermediate PDF for better quality converted PNGs
        # http://stackoverflow.com/questions/17314382/improve-quality-of-wand-conversion
        with wandImage(file=pdf_page_stream, resolution=pdf_res) as pdf_page:
            image_page = pdf_page.convert(img_format)
            image_page_stream = BufferedRandom(BytesIO())
            image_page.save(file=image_page_stream)
            pages.append(image_page_stream)

    return pages


def compare(pages_x, pages_y, img_format='png', all_pages=False):

    # create a list of tuples from corresponding pages of both sources
    # we assume here that the order in which to compare them is the list order
    pages = list(zip(pages_x, pages_y))
    differences = []
    diff_cnt = 0

    for page_x, page_y in pages:

        # reset binary stream position
        page_x.seek(0)
        page_y.seek(0)

        # open the image and convert to RGBA mode
        img_x = Image.open(page_x).convert('RGBA')
        img_y = Image.open(page_y).convert('RGBA')

        diff_xy = ImageChops.difference(img_x, img_y)

        # check if the images are identical; if so, getbbox() will return None
        # http://effbot.org/zone/pil-comparing-images.htm
        if diff_xy.getbbox():
            log.debug('Difference found')
            diff_cnt += 1

            # http://stackoverflow.com/questions/18341754/color-in-red-diffrencies-between-two-pictures
            red_layer = Image.new(diff_xy.mode, diff_xy.size, 'red') # Make a red layer the same size
            diff_red = ImageChops.multiply(red_layer, diff_xy)
            comp_xy = ImageChops.blend(diff_red, img_y, 0.7)
            diff_stream = BufferedRandom(BytesIO())
            comp_xy.save(diff_stream, format=img_format)
            differences.append(diff_stream)

        elif all_pages:
            log.debug('Pages are identical')
            # no difference detected between the 2 images; just save one of the originals
            diff_stream = BufferedRandom(BytesIO())
            img_x.save(diff_stream, format=img_format)
            differences.append(diff_stream)

    if all_pages and len(pages_x) != len(pages_y):
        log.debug('Adding remaining pages (nothing to compare to)')
        # we need to return a complete set of pages, and both sets contain a different number of pages
        shortest, longest = (pages_x, pages_y) if len(pages_x) < len(pages_y) else (pages_y, pages_x)
        remaining = longest[len(shortest):]
        for page in remaining:
            page.seek(0)
            img = Image.open(page).convert('RGBA')
            diff_stream = BufferedRandom(BytesIO())
            img.save(diff_stream, format=img_format)
            differences.append(diff_stream)

    log.debug('{} differences found'.format(diff_cnt))
    return differences


def merge_pdf(pages, target_pdf, img_format='png'):

    merged_pdf = PyPDF2.PdfFileWriter()
    log.debug('Merging {} into one PDF document'.format(len(pages)))

    for page in pages:
        # reset binary stream position
        page.seek(0)
        pdf_page_stream = BufferedRandom(BytesIO())

        log.debug('Converting image to PDF')
        with wandImage(file=page, format=img_format) as image:
            img_converted = image.convert('pdf')
            img_converted.save(file=pdf_page_stream)
            img_converted.close()

        log.debug('Adding PDF page to merged document')
        pdf_page_stream.seek(0)
        merged_pdf.addPage(PyPDF2.PdfFileReader(pdf_page_stream).getPage(0))

    merged_pdf.write(open(target_pdf, 'wb'))


def main(pdf_x, pdf_y, pdf_merged, pdf_res=150, extract_pages_x=None, extract_pages_y=None, all_pages=True):

    # if the page list is passed as a string, we need to split it, convert it to integer and rebase it to 0
    page_list_x = [int(x)-1 for x in extract_pages_x.split(',')] if isinstance(extract_pages_x, str) else extract_pages_x
    page_list_y = [int(y)-1 for y in extract_pages_y.split(',')] if isinstance(extract_pages_y, str) else extract_pages_y

    # convert the resolution to integer as we may receive this as a string
    if pdf_res:
        pdf_res = int(pdf_res)

    log.info('Splitting first PDF')
    pdf_pages_x = split_pdf(src_filename=pdf_x, page_list=page_list_x, pdf_res=pdf_res)

    log.info('Splitting second PDF')
    pdf_pages_y = split_pdf(src_filename=pdf_y, page_list=page_list_y, pdf_res=pdf_res)

    log.info('Determining differences')
    differences = compare(pdf_pages_x, pdf_pages_y, all_pages=all_pages)

    log.info('Creating new PDF')
    merge_pdf(differences, pdf_merged)

    log.info('Finished analyzing differences')
