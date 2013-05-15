#!/usr/bin/env python2
import sys
from pdfminer.pdfparser import PDFDocument, PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfinterp import process_pdf
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
from pdfminer.image import ImageWriter


# main
def main(argv):
    import getopt

    def usage():
        print ('usage: %s [-d] [-p pagenos] [-m maxpages] '
               '[-P password] [-o output] [-C] '
               '[-n] [-A] [-V] [-M char_margin] [-L line_margin] '
               '[-W word_margin] [-F boxes_flow] '
               '[-Y layout_mode] [-O output_dir] [-t text|html|xml|tag] '
               '[-c codec] [-s scale] file ...' % argv[0])
        return 100

    def checkOption(argv):
        try:
            optFormat = 'dp:m:P:o:CnAVM:L:W:F:Y:O:t:c:s:'
            (opts, args) = getopt.getopt(argv[1:], optFormat)
        except getopt.GetoptError:
            return (None, None, True)
        if not args:
            return (None, None, True)

        return (opts, args, False)

    def initOptionVal():
        optVal = {}
        # debug option
        optVal['debug'] = 0
        # input option
        optVal['password'] = ''
        optVal['pagenos'] = set()
        optVal['maxpages'] = 0
        # output option
        optVal['outfile'] = None
        optVal['outtype'] = None
        optVal['imagewriter'] = None
        optVal['layoutmode'] = 'normal'
        optVal['codec'] = 'utf-8'
        optVal['scale'] = 1
        optVal['caching'] = True
        optVal['laparams'] = LAParams()
        return optVal

    def readOption(opts, optVal):
        for (key, value) in opts:
            if key == '-d':
                optVal['debug'] += 1
            elif key == '-p':
                optVal['pagenos'].update(int(x)-1 for x in value.split(','))
            elif key == '-m':
                optVal['maxpages'] = int(value)
            elif key == '-P':
                optVal['password'] = value
            elif key == '-o':
                optVal['outfile'] = value
            elif key == '-C':
                optVal['caching'] = False
            elif key == '-n':
                optVal['laparams'] = None
            elif key == '-A':
                optVal['laparams'].all_texts = True
            elif key == '-V':
                optVal['laparams'].detect_vertical = True
            elif key == '-M':
                optVal['laparams'].char_margin = float(value)
            elif key == '-L':
                optVal['laparams'].line_margin = float(value)
            elif key == '-W':
                optVal['laparams'].word_margin = float(value)
            elif key == '-F':
                optVal['laparams'].boxes_flow = float(value)
            elif key == '-Y':
                optVal['layoutmode'] = value
            elif key == '-O':
                optVal['imagewriter'] = ImageWriter(value)
            elif key == '-t':
                optVal['outtype'] = value
            elif key == '-c':
                optVal['codec'] = value
            elif key == '-s':
                optVal['scale'] = float(value)
        return optVal

    def getValFromOptionVal(optVal):
        vals = []
        for key, val in optVal.iteritems():
            vals.append(val)
        return vals

    (opts, args, showUsage) = checkOption(argv)
    if showUsage:
        return usage()

    # Read optiaon
    optionVal = initOptionVal()
    optionVal = readOption(opts, optionVal)
    (scale, layoutmode, laparams, outfile, outtype,
     pagenos, caching, codec, debug, password, imagewriter,
     maxpages, ) = getValFromOptionVal(optionVal)

    PDFDocument.debug = debug
    PDFParser.debug = debug
    CMapDB.debug = debug
    PDFResourceManager.debug = debug
    PDFPageInterpreter.debug = debug
    PDFDevice.debug = debug
    #
    rsrcmgr = PDFResourceManager(caching=caching)
    if not outtype:
        outtype = 'text'
        if outfile:
            if outfile.endswith('.htm') or outfile.endswith('.html'):
                outtype = 'html'
            elif outfile.endswith('.xml'):
                outtype = 'xml'
            elif outfile.endswith('.tag'):
                outtype = 'tag'
    if outfile:
        outfp = file(outfile, 'w')
    else:
        outfp = sys.stdout
    if outtype == 'text':
        device = TextConverter(rsrcmgr, outfp, codec=codec, laparams=laparams,
                               imagewriter=imagewriter)
    elif outtype == 'xml':
        device = XMLConverter(rsrcmgr, outfp, codec=codec, laparams=laparams,
                              imagewriter=imagewriter)
    elif outtype == 'html':
        device = HTMLConverter(rsrcmgr, outfp, codec=codec, scale=scale,
                               layoutmode=layoutmode, laparams=laparams,
                               imagewriter=imagewriter)
    elif outtype == 'tag':
        device = TagExtractor(rsrcmgr, outfp, codec=codec)
    else:
        return usage()
    for fname in args:
        fp = file(fname, 'rb')
        process_pdf(rsrcmgr, device, fp, pagenos,
                    maxpages=maxpages, password=password,
                    caching=caching, check_extractable=True)
        fp.close()
    device.close()
    outfp.close()
    return

if __name__ == '__main__':
    sys.exit(main(sys.argv))
