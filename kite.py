#
# Kite - Operate on Kite related files and data
# HanishKVC, 2021
#


import time
import numpy

from hlpr import *


CSVDataFile = None


def init(inCSVDataFile):
    global CSVDataFile
    CSVDataFile = inCSVDataFile
    CSVDataFile['KiteTrades'] = {
        'import_header': _import_kite_header,
        'import_record': _import_kite_trades_record,
        'delim': ',',
        'fieldProtectors': [ '"', "'" ],
        'skipLinesAtBegin': 1,
        }
    CSVDataFile['KiteOpenOrders'] = {
        'import_header': _import_kite_header,
        'import_record': _import_kite_openorders_record,
        'delim': ',',
        'fieldProtectors': [ '"', "'" ],
        'skipLinesAtBegin': 1,
        }
    CSVDataFile['KiteHoldings'] = {
        'import_header': _import_kite_header,
        'import_record': _import_kite_holdings_record,
        'delim': ',',
        'fieldProtectors': [ '"', "'" ],
        'skipLinesAtBegin': 1,
        }


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
    tSymbol = fix_symbol(la[fi['INSTRUMENT']])
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
    tSymbol = fix_symbol(la[fi['INSTRUMENT']])
    tQty = int(la[fi['QTY']].split('/')[1].replace(",", ""))*tType
    tUnitPrice = float(la[fi['PRICE']].replace(",", ""))
    tLTP = float(la[fi['LTP']].replace(",", ""))
    tTotal = tUnitPrice*tQty
    return [ tDate, tSymbol, tUnitPrice, tQty, tTotal, tLTP, round(tUnitPrice/tLTP,4) ]


def _list_kite_openorders(db):
    tSum = 0
    for x in db:
        tSum += x[4]
        print("{:32} {:8} {:8.2f} {:8.2f} {:8.2f}".format(x[1], x[3], x[2], x[5], (x[6]-1)*100), end="\n\n")
    print("{:16} : {}".format("TotalValue", tSum))
    print("{:16} : {}".format("TotalBuy", numpy.sum(db[db[:,4]>0,4])))
    print("{:16} : {}".format("TotalSell", numpy.sum(db[db[:,4]<0,4])))


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
        elif la[i].find("AVG. COST") != -1:
            fi['AVGPRICE'] = i
        elif la[i].find("CUR. VAL") != -1:
            fi['CURVALUE'] = i
        elif la[i].startswith("LTP"):
            fi['LTP'] = i
        elif la[i].find("TIME") != -1:
            fi['TIME'] = i
        elif la[i].find("NET CHG") != -1:
            fi['NETCHG'] = i
        elif la[i].find("DAY CHG") != -1:
            fi['DAYCHG'] = i
    CSVDataFile[csvType]['FieldIndex'] = fi


def _import_kite_holdings_record(l, la):
    """
    Import the csv file generated when exporting holdings from kite
    """
    if len(la) != 8:
        input("WARN:ImportKiteHoldings: CSV file format might have changed...")
        return None
    fi = CSVDataFile['KiteHoldings']['FieldIndex']
    tSymbol = fix_symbol(la[fi['INSTRUMENT']])
    tQty = int(la[fi['QTY']].replace(",", ""))
    tAvgPrice = float(la[fi['AVGPRICE']].replace(",", ""))
    tLTP = float(la[fi['LTP']].replace(",", ""))
    tCurValue = float(la[fi['CURVALUE']].replace(",", ""))
    tNetChg = float(la[fi['NETCHG']].replace(",", ""))
    tDayChg = float(la[fi['DAYCHG']].replace(",", ""))
    tCheck = tLTP*tQty
    if (abs(tCurValue - tCheck) > 0.001):
        input("DBUG:ImportKiteHoldings:CurValue mismatch:{}:{}".format(la, tCheck))
    tCheck = round(((tLTP/tAvgPrice)-1)*100,2)
    if (abs(tNetChg - tCheck) > 0.1):
        input("DBUG:ImportKiteHoldings:NetChg mismatch:{}:{}".format(la, tCheck))
    return [ tSymbol, tLTP, tAvgPrice, tQty, tCurValue, tNetChg, tDayChg ]


def _list_kite_holdings(db, sortBy=-2, mayBeAdj=0.98):
    theFormat = "{:32} {:8.2f} {:8.2f} {:8} {:8.2f} {:8.2f} {:8.2f} {:8.2f}"
    dbN = db[numpy.argsort(db[:,sortBy])]
    theHFormat = theFormat.replace(".2f","")
    print(theHFormat.format("Symbol", "LTP", "AvgPrice", "Qty", "CurVal", "NetChg", "DayChg", "MayBe"), end="\n\n")
    for x in dbN:
        tMayBe = x[1]*mayBeAdj
        print(theFormat.format(x[0], x[1], x[2], x[3], x[4], x[5], x[6], tMayBe), end="\n\n")


