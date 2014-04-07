# pyPdfCompare

pyPdfCompare allows you to *visually* compare two PDF files, page by page. Visually meaning the text isn't analyzed, but rather each page is rasterized and compared.

## Design

pyPdfCompare takes two PDF files and converts each page to a single image file. The resolution of the images can be configured. Next, images files are compared sequentially and differences are highlighted. These modified images (showing the changes) are then used to create a new PDF file, again converting each image back to PDF and merging them to a single file.

Because pyPdfCompare uses the `io` module, intermediate binary streams are never written to disk but kept in memory, thus eliminating expensive I/O operations.

### Configuration

These options can be specified when starting a new comparison:

 - *Resolution* — this is the resolution used when converting the individual PDF pages to an image. The higher the resolution, the more precise the comparison will be, but the slower the overall process will be. Remember that pyPdfCompare performs all operations up to the final merging to the resulting PDF in memory, so higher resolutions will require more RAM.
 - *All pages or only differences* — the resulting PDF can either contain all pages, or only the pages that are identified as different.
 - *Pages to compare* — for each of the PDF files to be compared, the list of pages — as well as the order — can be specified independently. Thus, you could compare page 1, 5 and 3 of PDF *x* with page 1, 2 and 4 of PDF *y*.

## Requirements

pyPdfCompare was created using CPython 3.3.5 in a Windows environment. Although untested, it should work in all OS'es that support the requirements.

### 3rd-party Python libraries

 - [docopt](http://docopt.org/) 0.6.1
 - [PyPDF2](http://mstamy2.github.com/PyPDF2) 1.20
 - [Wand](http://wand-py.org/) 0.3.7
 - [Pillow](http://python-imaging.github.io) 2.4.0

### Non-Python dependencies

 - [ImageMagick](http://www.imagemagick.org) (make sure to install the development libraries!)
 - [Ghostscript](http://www.ghostscript.com)
 
## Credits

I owe quite a lot to StackOverflow for providing me a wealth of information. More specifically, following questions (and their answers) helped a lot during development of pyPdfCompare:

 - [Improve quality of Wand conversion](http://stackoverflow.com/questions/17314382/improve-quality-of-wand-conversion)
 - [Color in red diffrencies between two pictures](http://stackoverflow.com/questions/18341754/color-in-red-diffrencies-between-two-pictures)