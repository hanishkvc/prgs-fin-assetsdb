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


def handle_asset(la):
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
    Assume that the specified file is a csv file following my previous google sheets assets csv exports
    Skip the 1st line
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
            la = handle_asset(la)
            print("INFO:ImportCSVO1:", la)
            if (db == None):
                db = numpy.array(la)
            else:
                db = numpy.vstack((db, la))
        except:
            print("ERRR:ImportCSVO1:", la)
            print(sys.exc_info())
    return db


while True:
    try:
        exec(input("$"))
    except:
        print("ERRR:", sys.exc_info())

