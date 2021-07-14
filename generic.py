#
# Generic - Operate on files and data in a generic way
# HanishKVC, 2021
#


import datetime


def init_csv(CSVDataFile):
    CSVDataFile['Generic'] = {
        'import_header': _import_header_skip,
        'import_record': _import_generic_record,
        'delim': ',',
        'fieldProtectors': [ '"', "'" ],
        'skipLinesAtBegin': 0,
        }


def _import_generic_record(csvDF, l, la):
    ra = []
    for c in la:
        try:
            f = float(c.replace(",",""))
            ra.append(f)
        except:
            ra.append(c)
    return ra


def _import_header_skip(csvDF, f, csvType):
    for i in range(csvDF[csvType]['skipLinesAtBegin']):
        f.readline()


def list(npa, fieldTypes=None):
    """
    List the contents of the 2D array passed to this function.
    fieldTypes:
        if not None, it should be a string of chars,
        which specify the type of each field in the row.
            S: string field
            F: float field
            O: query field value to find the field type
        if None, then query field value to find the field type
    """
    for cR in npa:
        iF = -1
        for cC in cR:
            iF += 1
            if fieldTypes == None:
                cT = type(cC)
            else:
                if fieldTypes[iF] == 'S':
                    cT = str
                elif fieldTypes[iF] == 'F':
                    cT = float
                elif fieldTypes[iF] == 'O':
                    cT = type(cC)
            if cT == str:
                print("{:48}".format(cC), end=" ")
            elif cT == float:
                print("{:13.2f}".format(cC), end=" ")
            elif cT == datetime.datetime:
                print("{:13}".format(cC.strftime("%Y%m%dT%H%M")), end=" ")
            else:
                print("{:13}".format(cC), end=" ")
        print("\n")


