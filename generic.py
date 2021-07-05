#
# Generic - Operate on files and data in a generic way
# HanishKVC, 2021
#


def init(CSVDataFile):
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


