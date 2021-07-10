#
# adb - manage the assets db
# HanishKVC, 2021
# GPL
#


import datetime
import numpy


IDB = {
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

IBS = {
    'NAME': 0,
    'TRANSDATE': 1,
    'PRICE': 2,
    'QTY': 3,
    'TRANSVALUE': 4,
    }

gbSpaceOutListing = True


def _import_buy(db, ci):
    iDT = IDB['BTRANSDATE']
    iRow = -1
    #print(type(db), db.shape, db)
    bBreak = False
    for cr in db:
        iRow += 1
        if cr[iDT].timestamp() <= ci[iDT].timestamp():
            continue
        bBreak = True
        break
    if not bBreak:
        iRow += 1
    db = numpy.insert(db, iRow, numpy.array([ci[0],ci[1],ci[2],ci[3],ci[4],0,0,0,0]), 0)
    return db


def _import_sell(db, ci):
    iRow = -1
    iRemaining = -1*ci[IBS['QTY']]
    for cr in db:
        iRow += 1
        if cr[IDB['NAME']] != ci[IBS['NAME']]:
            continue
        buyQty = cr[IDB['BQTY']]
        sellQty = cr[IDB['SQTY']]
        iDelta = buyQty - sellQty
        if (iDelta <= 0):
            continue
        iDelta = iDelta - iRemaining
        if iDelta == 0:
            cr[IDB['STRANSDATE']] = ci[IBS['TRANSDATE']]
            cr[IDB['SPRICE']] = ci[IBS['PRICE']]
            cr[IDB['SQTY']] = iRemaining
            cr[IDB['STRANSVALUE']] = ci[IBS['PRICE']]*cr[IDB['SQTY']]
            return db
        elif iDelta < 0:
            cr[IDB['STRANSDATE']] = ci[IBS['TRANSDATE']]
            cr[IDB['SPRICE']] = ci[IBS['PRICE']]
            cr[IDB['SQTY']] = cr[IDB['BQTY']]
            cr[IDB['STRANSVALUE']] = ci[IBS['PRICE']]*cr[IDB['SQTY']]
            iRemaining = -1*iDelta
        else:
            cr[IDB['BQTY']] = iRemaining
            cr[IDB['BTRANSVALUE']] = cr[IDB['BPRICE']]*cr[IDB['BQTY']]
            cr[IDB['STRANSDATE']] = ci[IBS['TRANSDATE']]
            cr[IDB['SPRICE']] = ci[IBS['PRICE']]
            cr[IDB['SQTY']] = iRemaining
            cr[IDB['STRANSVALUE']] = ci[IBS['PRICE']]*cr[IDB['SQTY']]
            iRemaining = 0
            db = numpy.insert(db, iRow, numpy.array([cr[0],cr[1],cr[2],iDelta,cr[2]*iDelta,0,0,0,0]), 0)
            return db


def import_da(db, da, daType="BUYSELL"):
    #breakpoint()
    if type(db) == type(None): # Assuming its a BUY for now
        print("WARN:ADB.ImportDB:Creating db...")
        db = numpy.array([[da[0,0], da[0,1], da[0,2], da[0,3], da[0,4], 0, 0, 0, 0]], dtype=object)
        da = da[1:]
    for ci in da:
        if ci[IDB['BQTY']] > 0:
            db = _import_buy(db, ci)
        else:
            db = _import_sell(db, ci)
    return db


def list_assetnames(db, bPrint=True):
    """
    Retrieve and optionally print the name of assets in the db.
    db: the db containing the assets data.
    """
    assetNames = numpy.unique(da[:,IDB['NAME']])
    for i in range(len(assetNames)):
        sn = assetNames[i]
        if (bPrint):
            print("{:4}: {}".format(i,sn))
    return assetNames


def _asset_summary(assets):
    assetsBuy = assets[assets[:,IDB['QTY']] > 0]
    assetsSell = assets[assets[:,IDB['QTY']] < 0]
    assetSum = numpy.sum(assets[:,IDB['TRANSVALUE']])
    assetBuyQty = numpy.sum(assetsBuy[:,IDB['QTY']])
    assetBuyAvg = numpy.sum((assetsBuy[:,IDB['VALUE']]*assetsBuy[:,IDB['QTY']])/assetBuyQty)
    assetSellQty = numpy.sum(assetsSell[:,IDB['QTY']])
    assetSellAvg = numpy.sum((assetsSell[:,IDB['VALUE']]*assetsSell[:,IDB['QTY']])/assetSellQty)
    return assetSum, [assetBuyAvg, assetBuyQty], [assetSellAvg, assetSellQty]


def list_assets(db, filterStocks=[], bDetails=False):
    """
    List the data about specified assets in the db.
    db: the db containing data about assets
    filterStocks: a list of asset names or empty list.
    """
    totalSum = numpy.sum(db[:,IDB['TRANSVALUE']])
    totalQty = numpy.sum(db[:,IDB['QTY']])
    assetsSummaryList = []
    assetNames = list_assetnames(db, False)
    print("GrandSummary: NumOfCompanies={:8}, NumOfStocks={:8}, TotalValue={:16.2f}".format(len(assetNames), totalQty, totalSum))
    for sn in assetNames:
        if (len(filterStocks) > 0) and (sn not in filterStocks):
            continue
        assets = db[db[:,IDB['NAME']] == sn]
        assetSum, [ assetBuyAvg, assetBuyQty], [assetSellAvg, assetSellQty] = _asset_summary(assets)
        if bDetails:
            for s in assets:
                t = s.copy()
                t[IDB['TRANSDATE']] = t[IDB['TRANSDATE']].strftime("%Y%m%dIST%H%M")
                print(t)
        assetsSummaryList.append([ sn, assetBuyAvg, assetBuyQty, assetSellAvg, assetSellQty, assetSum ])
        print("{:48} : {:10.2f} x {:8} : {:10.2f} x {:8} : {:16.2f}".format(sn, assetBuyAvg, assetBuyQty, assetSellAvg, assetSellQty, assetSum))
        if gbSpaceOutListing:
            print("")
    return assetsSummaryList


