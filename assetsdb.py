#!/usr/bin/env python3
# Store Assets data
# HanishKVC, 2021
# GPL


import sys
import time
import numpy
import readline


DELIMITER = ','
TOKENPROTECTORS = [ "'", '"' ]

IDBSTOCKNAME = 1


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
    if (tTotal != (tValue*tQty)):
        print("DBUG:ImportCSVO1:TotalValue mismatch", la)
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
            print("ERRR:ImportCSVO1:", la)
            print(sys.exc_info())
    return db


def list_stocknames(db):
    """
    List the name of stocks in the db.
    db: the db containing the stocks data.
    """
    stockNames = numpy.unique(db[:,IDBSTOCKNAME])
    for sn in stockNames:
        print(sn)
    return stockNames


def list_stocks(db, filterStocks=[]):
    """
    List the data about specified stocks in the db.
    db: the db containing data about stocks
    filterStocks: a list of stock names or empty list.
    """
    stockNames = list_stocknames(db)
    for sn in stockNames:
        stocks = db[db[:,1] == sn]
        for s in stocks:
            if (len(filterStocks) > 0) and (s not in filterStocks):
                continue
            print(s)


while True:
    try:
        exec(input("$"))
    except:
        if (sys.exc_info()[0] == SystemExit):
            break;
        print("ERRR:", sys.exc_info())

