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
TOKENPROTECTORS = [ "'", '"' ]

IDBSTOCK = { 'TRANSDATE': 0, 'NAME': 1, 'VALUE': 2, 'QTY': 3, 'TRANSVALUE': 4 }

gbSpaceOutListing = True


def csv2list(inL, delim=DELIMITER, tokenProtectors = TOKENPROTECTORS):
    """
    Convert a csv line into a python list.
    delim: the character used to delimit the fields
    tokenProtectors: characters that could be used to protect fields having delim char in them.
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
        if c in tokenProtectors:
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


def import_csv_o1(sFile, db=None):
    """
    Import csv file which follows my previous google sheets based assets csv exports.
    sFile: the file to import
    db: optional db to load the data into. If None, then a new db is created.
    Note:
        Skip the 1st line, of the specified file.
    """
    f = open(sFile)
    f.readline()
    #breakpoint()
    for l in f:
        la = csv2list(l)
        #print("DBUG:ImportCSVO1:CurLine:", la)
        if len(la) < 4:
            continue
        if len(la[1]) < 8:
            continue
        if not la[1][0].isnumeric():
            continue
        try:
            if la[2][0].strip().startswith("#"):
                continue
            la = _handle_asset_csv_o1(la)
            print("INFO:ImportCSVO1:", la)
            if (type(db) == type(None)):
                db = numpy.array(la)
            else:
                db = numpy.vstack((db, la))
        except:
            print(sys.exc_info())
            input("ERRR:ImportCSVO1:{}".format(la))
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
    print("NOTE: sys.exit() to quit")


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

