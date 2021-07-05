#
# h7 - Operate on files and data created by me
# HanishKVC, 2021
#


import time
import numpy

from hlpr import *


CSVDataFile = None


def init(inCSVDataFile):
    global CSVDataFile
    CSVDataFile = inCSVDataFile
    CSVDataFile['H7O1'] = {
        'import_header': _import_header_skip,
        'import_record': _import_o1_record,
        'delim': ',',
        'fieldProtectors': [ '"', "'" ],
        'skipLinesAtBegin': 1,
        }
    CSVDataFile['H7Funds'] = {
        'import_header': _import_header_skip,
        'import_record': _import_funds_record,
        'delim': ',',
        'fieldProtectors': [ '"', "'" ],
        'skipLinesAtBegin': 1,
        'FieldIndex': { 'TIME': 0, 'AMOUNT': 1 },
        }


def _handle_asset_csv_o1(la):
    tDate = time.strptime(la[1], "%Y%m%dIST%H%M")
    tSymbol = fix_symbol(la[2])
    tTotal = float(la[3].replace(",",""))
    tValue = float(la[4].replace(",", ""))
    tQty = int(la[5].replace(",", ""))
    tCheck = tValue*tQty
    if (abs(tTotal - tCheck) > 0.001):
        input("DBUG:ImportCSVO1:TotalValue mismatch:{}:{}".format(la, tCheck))
    return [ tDate, tSymbol, tValue, tQty, tTotal ]



def _import_o1_record(l, la):
    """
    Import a csv file record, which follows my previous google sheets based assets csv exports.
    """
    if len(la) < 4:
        return None
    if len(la[1]) < 8:
        return None
    if not la[1][0].isnumeric():
        return None
    if la[2][0].strip().startswith("#"):
        return None
    la = _handle_asset_csv_o1(la)
    return la


def _import_funds_record(l, la):
    """
    Import the csv file manually created to contain the funds used for a specific type of asset.
    The csv file should consist of Time, Amount
    """
    if len(la) != 2:
        input("WARN:ImportFunds: CSV file format might have changed...")
        return None
    fi = CSVDataFile['Funds']['FieldIndex']
    tDate = time.strptime(la[fi['TIME']], "%Y%m%dIST%H%M")
    tAmount = float(la[fi['AMOUNT']].replace(",", ""))
    return [ tDate, tAmount ]


def _list_funds(db):
    tSum = 0
    for x in db:
        tSum += x[1]
        tDate = time.strftime("%Y%m%dIST%H%M", x[0])
        print("{:16} {:8.2f}".format(tDate, x[1]), end="\n\n")
    print("{:16} : {}".format("TotalValue", tSum))


