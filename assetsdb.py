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


HISTORYFILE="./.assetsdb.history"

DELIMITER = ','
FIELDPROTECTORS = [ "'", '"' ]

IDBSTOCK = { 'TRANSDATE': 0, 'NAME': 1, 'VALUE': 2, 'QTY': 3, 'TRANSVALUE': 4 }

gbSpaceOutListing = True


def csv2list(inL, delim=DELIMITER, fieldProtectors = FIELDPROTECTORS):
    """
    Convert a csv line into a python list.
    delim: the character used to delimit the fields
    fieldProtectors: characters that could be used to protect fields having delim char in them.
    """
    tA = []
    curToken = ""
    bProtectedToken = False
    inL = inL.strip()
    if not inL.endswith(delim):
        inL += delim
    for c in inL:
        if (not bProtectedToken) and (c == delim):
            tA.append(curToken)
            curToken = ""
            continue
        if c in fieldProtectors:
            bProtectedToken = not bProtectedToken
            continue
        curToken += c
    return tA


def _handle_asset_csv_o1(la):
    tDate = time.strptime(la[1], "%Y%m%dIST%H%M")
    tSymbol = la[2]
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


def _import_kite_trades_record(l, la):
    """
    Import the csv file generated when exporting trades from kite
    """
    if len(la) != 7:
        input("WARN:ImportKiteTrades: CSV file format might have changed...")
        return None
    fi = CSVDataFile['KiteTrades']['FieldIndex']
    tDate = time.strptime(la[fi['TIME']], "%Y-%m-%d %H:%M:%S")
    tType = 1 if (la[fi['TYPE']] == 'BUY') else -1
    tSymbol = la[fi['INSTRUMENT']]
    tQty = int(la[fi['QTY']].replace(",", ""))*tType
    tUnitPrice = float(la[fi['PRICE']].replace(",", ""))
    tTotal = tUnitPrice*tQty
    return [ tDate, tSymbol, tUnitPrice, tQty, tTotal ]


def _import_kite_openorders_record(l, la):
    """
    Import the csv file generated when exporting open orders from kite
    NOTE: Assumes that the open orders have not been partially fullfilled.
    """
    if len(la) != 8:
        input("WARN:ImportKiteOpenOrders: CSV file format might have changed...")
        return None
    fi = CSVDataFile['KiteOpenOrders']['FieldIndex']
    tDate = time.strptime(la[fi['TIME']], "%Y-%m-%d %H:%M:%S")
    tType = 1 if (la[fi['TYPE']] == 'BUY') else -1
    tSymbol = la[fi['INSTRUMENT']]
    tQty = int(la[fi['QTY']].split('/')[1].replace(",", ""))*tType
    tUnitPrice = float(la[fi['PRICE']].replace(",", ""))
    tLTP = float(la[fi['LTP']].replace(",", ""))
    tTotal = tUnitPrice*tQty
    return [ tDate, tSymbol, tUnitPrice, tQty, tTotal, tLTP, round(tUnitPrice/tLTP,4) ]


def _list_kite_openorders(db):
    [ print("{:32} {:8} {:8.2f} {:8.2f} {:8.2f}".format(x[1], x[3], x[2], x[5], (x[6]-1)*100), end="\n\n") for x in db ]


def _import_kite_header(f, csvType):
    global CSVDataFile
    l = f.readline()
    l = l.upper()
    la = csv2list(l, CSVDataFile[csvType]['delim'], CSVDataFile[csvType]['fieldProtectors'])
    fi = {}
    for i in range(len(la)):
        if la[i].startswith("QTY"):
            fi['QTY'] = i
        elif la[i].startswith("INSTRUMENT"):
            fi['INSTRUMENT'] = i
        elif la[i].startswith("TYPE"):
            fi['TYPE'] = i
        elif la[i].find("PRICE") != -1:
            fi['PRICE'] = i
        elif la[i].startswith("LTP"):
            fi['LTP'] = i
        elif la[i].find("TIME") != -1:
            fi['TIME'] = i
    CSVDataFile[csvType]['FieldIndex'] = fi


def _import_header_skip(f, csvType):
    for i in range(CSVDataFile[csvType]['skipLinesAtBegin']):
        f.readline()


CSVDataFile = {
    'O1': {
        'import_header': _import_header_skip,
        'import_record': _import_o1_record,
        'delim': ',',
        'fieldProtectors': [ '"', "'" ],
        'skipLinesAtBegin': 1,
        },
    'KiteTrades': {
        'import_header': _import_kite_header,
        'import_record': _import_kite_trades_record,
        'delim': ',',
        'fieldProtectors': [ '"', "'" ],
        'skipLinesAtBegin': 1,
        },
    'KiteOpenOrders': {
        'import_header': _import_kite_header,
        'import_record': _import_kite_openorders_record,
        'delim': ',',
        'fieldProtectors': [ '"', "'" ],
        'skipLinesAtBegin': 1,
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
            print("INFO:ImportCSV:", la)
            if (type(db) == type(None)):
                db = numpy.array(la)
            else:
                db = numpy.vstack((db, la))
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


def runme():
    load_history(HISTORYFILE)
    while True:
        try:
            exec(input("$"))
        except:
            if (sys.exc_info()[0] == SystemExit):
                break;
            #print("ERRR:", sys.exc_info())
            traceback.print_exc()
    save_history(HISTORYFILE)


startup()
runme()

