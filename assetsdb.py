#!/usr/bin/env python3
# Store Assets data
# HanishKVC, 2021
# GPL


import sys
import os
import time
import numpy
import readline
import rlcompleter
import traceback

from hlpr import *
import kite


HISTORYFILE="./.assetsdb.history"

IDBSTOCK = { 'TRANSDATE': 0, 'NAME': 1, 'VALUE': 2, 'QTY': 3, 'TRANSVALUE': 4 }

gbSpaceOutListing = True


def _handle_asset_csv_o1(la):
    tDate = time.strptime(la[1], "%Y%m%dIST%H%M")
    tSymbol = fix_symbol(la[2])
    tTotal = float(la[3].replace(",",""))
    tValue = float(la[4].replace(",", ""))
    tQty = int(la[5].replace(",", ""))
    tCheck = tValue*tQty
    if (abs(tTotal - tCheck) > 0.001):
        input("DBUG:ImportCSVO1:TotalValue mismatch:{}".format(la), tCheck)
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


def _import_generic_record(l, la):
    ra = []
    for c in la:
        try:
            f = float(c.replace(",",""))
            ra.append(f)
        except:
            ra.append(c)
    return ra


def _import_header_skip(f, csvType):
    for i in range(CSVDataFile[csvType]['skipLinesAtBegin']):
        f.readline()


CSVDataFile = {
    'Generic': {
        'import_header': _import_header_skip,
        'import_record': _import_generic_record,
        'delim': ',',
        'fieldProtectors': [ '"', "'" ],
        'skipLinesAtBegin': 0,
        },
    'O1': {
        'import_header': _import_header_skip,
        'import_record': _import_o1_record,
        'delim': ',',
        'fieldProtectors': [ '"', "'" ],
        'skipLinesAtBegin': 1,
        },
    'Funds': {
        'import_header': _import_header_skip,
        'import_record': _import_funds_record,
        'delim': ',',
        'fieldProtectors': [ '"', "'" ],
        'skipLinesAtBegin': 1,
        'FieldIndex': { 'TIME': 0, 'AMOUNT': 1 },
        },
    }
def import_csv(csvType, sFile, db=None):
    """
    Import csv file main flow
    csvType: Specifies the type of csv file to import, which is used to get details like
        the delimiter of the fields,
        the fieldProtectors (Used to allow delimiter to be present within a fields value)
        the number of lines to skip, if any at the begining.
        the function used to infer the data in each line of the csv file.
    sFile: the file to import
    db: optional db to load the data into. If None, then a new db is created.
    """
    f = open(sFile)
    CSVDataFile[csvType]['import_header'](f, csvType)
    #breakpoint()
    for l in f:
        la = csv2list(l, CSVDataFile[csvType]['delim'], CSVDataFile[csvType]['fieldProtectors'])
        #print("DBUG:ImportCSV:CurLine:", l, la)
        try:
            la = CSVDataFile[csvType]['import_record'](l, la)
            if (type(la) == type(None)):
                continue
            dprint("INFO:ImportCSV:{}".format(la), gDEBUGLVLINFO)
            if (type(db) == type(None)):
                db = numpy.array(la, dtype=object)
            else:
                db = numpy.vstack((db, numpy.array(la, dtype=object)))
        except:
            print(sys.exc_info())
            input("ERRR:ImportCSV:{}".format(la))
    return db


def list_stocknames(db, bPrint=True):
    """
    Retrieve and optionally print the name of stocks in the db.
    db: the db containing the stocks data.
    """
    stockNames = numpy.unique(db[:,IDBSTOCK['NAME']])
    for i in range(len(stockNames)):
        sn = stockNames[i]
        if (bPrint):
            print("{:4}: {}".format(i,sn))
    return stockNames


def _stock_summary(stocks):
    stocksBuy = stocks[stocks[:,IDBSTOCK['QTY']] > 0]
    stocksSell = stocks[stocks[:,IDBSTOCK['QTY']] < 0]
    stockSum = numpy.sum(stocks[:,IDBSTOCK['TRANSVALUE']])
    stockBuyQty = numpy.sum(stocksBuy[:,IDBSTOCK['QTY']])
    stockBuyAvg = numpy.sum((stocksBuy[:,IDBSTOCK['VALUE']]*stocksBuy[:,IDBSTOCK['QTY']])/stockBuyQty)
    stockSellQty = numpy.sum(stocksSell[:,IDBSTOCK['QTY']])
    stockSellAvg = numpy.sum((stocksSell[:,IDBSTOCK['VALUE']]*stocksSell[:,IDBSTOCK['QTY']])/stockSellQty)
    return stockSum, [stockBuyAvg, stockBuyQty], [stockSellAvg, stockSellQty]


def list_stocks(db, filterStocks=[], bDetails=False):
    """
    List the data about specified stocks in the db.
    db: the db containing data about stocks
    filterStocks: a list of stock names or empty list.
    """
    totalSum = numpy.sum(db[:,IDBSTOCK['TRANSVALUE']])
    totalQty = numpy.sum(db[:,IDBSTOCK['QTY']])
    stockNames = list_stocknames(db, False)
    print("GrandSummary: NumOfCompanies={:8}, NumOfStocks={:8}, TotalValue={:16.2f}".format(len(stockNames), totalQty, totalSum))
    for sn in stockNames:
        if (len(filterStocks) > 0) and (sn not in filterStocks):
            continue
        stocks = db[db[:,IDBSTOCK['NAME']] == sn]
        stockSum, [ stockBuyAvg, stockBuyQty], [stockSellAvg, stockSellQty] = _stock_summary(stocks)
        if bDetails:
            for s in stocks:
                t = s.copy()
                t[IDBSTOCK['TRANSDATE']] = time.strftime("%Y%m%dIST%H%M", t[IDBSTOCK['TRANSDATE']])
                print(t)
        print("{:48} : {:10.2f} x {:8} : {:10.2f} x {:8} : {:16.2f}".format(sn, stockBuyAvg, stockBuyQty, stockSellAvg, stockSellQty, stockSum))
        if gbSpaceOutListing:
            print("")


def startup_message():
    print("INFO: AssetsDB")
    print("NOTE: exit() to quit")


def startup():
    kite.init(CSVDataFile)
    readline.parse_and_bind("tab: complete")
    startup_message()


def load_history(histFile):
    if os.path.exists(histFile):
        readline.read_history_file(histFile)
    else:
        f = open(histFile, mode="wt")
        f.close()


def save_history(histFile):
    readline.write_history_file(histFile)


def init_scripts(srcFiles):
    for srcFile in srcFiles:
        f = open(srcFile)
        src = f.read()
        f.close()
        exec(src, globals())


def runme():
    init_scripts(sys.argv[1:])
    load_history(HISTORYFILE)
    while True:
        try:
            bDoExec = False
            try:
                toRun = input("$")
                res = eval(toRun)
            except SyntaxError:
                bDoExec = True
            if bDoExec:
                res = exec(toRun)
            if(type(res) != type(None)):
                print(res)
        except:
            if (sys.exc_info()[0] == SystemExit):
                break;
            #print("ERRR:", sys.exc_info())
            traceback.print_exc()
    save_history(HISTORYFILE)


startup()
runme()

