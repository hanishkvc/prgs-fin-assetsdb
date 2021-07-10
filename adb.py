#
# adb - manage the assets db
# HanishKVC, 2021
# GPL
#


import datetime
import numpy


IDBSTOCK = {
    'NAME': 0,
    'BTRANSDATE': 1,
    'BPRICE': 2,
    'BQTY': 3,
    'BTRANSVALUE': 4,
    'STRANSDATE': 5,
    'SPRICE': 6,
    'SQTY': 7,
    'STRANSVALUE': 8
    }

gbSpaceOutListing = True


def _import_buy(db, ci):
    iDT = IDB['BTRANSDATE']
    iRow = -1
    for cr in db:
        iRow += 1
        if cr[iDT].timestamp() < ci[iDT].timestamp():
            continue
        db = numpy.insert(db, iRow, numpy.array([ci[0],ci[1],ci[2],ci[3],ci[4],0,0,0,0]), 0)
        return db


def import_da(db, da, daType="BUYSELL"):
    if type(db) == type(None): # Assuming its a BUY for now
        db = numpy.array([[da[0], da[1], da[2], da[3], da[4], 0, 0, 0, 0]], dtype=object)
        return db
    for ci in da:
        if ci[IDB['QTY']] > 0:
            db = _import_buy(db, ci)
        else:
            db = _import_sell(db, ci)
    return db


def list_stocknames(da, bPrint=True):
    """
    Retrieve and optionally print the name of stocks in the da.
    da: the da containing the stocks data.
    """
    stockNames = numpy.unique(da[:,IDBSTOCK['NAME']])
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


def list_stocks(da, filterStocks=[], bDetails=False):
    """
    List the data about specified stocks in the da.
    da: the da containing data about stocks
    filterStocks: a list of stock names or empty list.
    """
    totalSum = numpy.sum(da[:,IDBSTOCK['TRANSVALUE']])
    totalQty = numpy.sum(da[:,IDBSTOCK['QTY']])
    stocksSummaryList = []
    stockNames = list_stocknames(da, False)
    print("GrandSummary: NumOfCompanies={:8}, NumOfStocks={:8}, TotalValue={:16.2f}".format(len(stockNames), totalQty, totalSum))
    for sn in stockNames:
        if (len(filterStocks) > 0) and (sn not in filterStocks):
            continue
        stocks = da[da[:,IDBSTOCK['NAME']] == sn]
        stockSum, [ stockBuyAvg, stockBuyQty], [stockSellAvg, stockSellQty] = _stock_summary(stocks)
        if bDetails:
            for s in stocks:
                t = s.copy()
                t[IDBSTOCK['TRANSDATE']] = t[IDBSTOCK['TRANSDATE']].strftime("%Y%m%dIST%H%M")
                print(t)
        stocksSummaryList.append([ sn, stockBuyAvg, stockBuyQty, stockSellAvg, stockSellQty, stockSum ])
        print("{:48} : {:10.2f} x {:8} : {:10.2f} x {:8} : {:16.2f}".format(sn, stockBuyAvg, stockBuyQty, stockSellAvg, stockSellQty, stockSum))
        if gbSpaceOutListing:
            print("")
    return stocksSummaryList


