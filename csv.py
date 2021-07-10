#
# CSV - Module to handle csv files
# HanishKVC, 2021
# GPL
#


def import_csv(csvType, sFile, da=None):
    """
    Import csv file main flow
    csvType: Specifies the type of csv file to import, which is used to get details like
        the delimiter of the fields,
        the fieldProtectors (Used to allow delimiter to be present within a fields value)
        the number of lines to skip, if any at the begining.
        the function used to infer the data in each line of the csv file.
    sFile: the file to import
    da: optional da to load the data into. If None, then a new da is created.
    """
    f = open(sFile)
    CSVDataFile[csvType]['import_header'](CSVDataFile, f, csvType)
    #breakpoint()
    for l in f:
        la = csv2list(l, CSVDataFile[csvType]['delim'], CSVDataFile[csvType]['fieldProtectors'])
        #print("DBUG:ImportCSV:CurLine:", l, la)
        try:
            la = CSVDataFile[csvType]['import_record'](CSVDataFile, l, la)
            if (type(la) == type(None)):
                continue
            dprint("INFO:ImportCSV:{}".format(la), gDEBUGLVLINFO)
            if (type(da) == type(None)):
                da = numpy.array(la, dtype=object)
            else:
                da = numpy.vstack((da, numpy.array(la, dtype=object)))
        except:
            #print(sys.exc_info())
            traceback.print_exc()
            input("ERRR:ImportCSV:{}".format(la))
    return da


