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
    """
    Insert the given sell transaction into the db, by matching it with related
    buy transactions (going from oldest to latest buy transactions).
    """
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
    input("WARN:ImportSell:OpenShortedAssetNotSupported:", ci)


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
    assetNames = numpy.unique(db[:,IDB['NAME']])
    for i in range(len(assetNames)):
        an = assetNames[i]
        if (bPrint):
            print("{:4}: {}".format(i,an))
    return assetNames


def _asset_summary_bsda(da):
    daBuys = da[da[:,IBS['QTY']] > 0]
    daSells = da[da[:,IBS['QTY']] < 0]
    daSum = numpy.sum(da[:,IBS['TRANSVALUE']])
    daBuysQty = numpy.sum(daBuys[:,IBS['QTY']])
    daBuysAvg = numpy.sum((daBuys[:,IBS['PRICE']]*daBuys[:,IBS['QTY']])/daBuysQty)
    daSellsQty = numpy.sum(daSells[:,IBS['QTY']])
    daSellsAvg = numpy.sum((daSells[:,IBS['PRICE']]*daSells[:,IBS['QTY']])/daSellsQty)
    return daSum, [daBuysAvg, daBuysQty], [daSellsAvg, daSellsQty]


def list_assets_bsda(da, filterAssets=[], bDetails=False):
    """
    List the data about specified assets in the da.
    da: the da containing data about assets
    filterAssets: a list of asset names or empty list.
    """
    totalSum = numpy.sum(da[:,IBS['TRANSVALUE']])
    totalQty = numpy.sum(da[:,IBS['QTY']])
    assetsSummaryList = []
    assetNames = list_assetnames(da, False)
    print("GrandSummary: UniqAssetsCnt={:8}, NumOfAssets={:8}, TotalValue={:16.2f}".format(len(assetNames), totalQty, totalSum))
    for an in assetNames:
        if (len(filterAssets) > 0) and (an not in filterAssets):
            continue
        assets = da[da[:,IBS['NAME']] == an]
        assetSum, [ assetBuyAvg, assetBuyQty], [assetSellAvg, assetSellQty] = _asset_summary_bsda(assets)
        if bDetails:
            for s in assets:
                t = s.copy()
                t[IBS['TRANSDATE']] = t[IBS['TRANSDATE']].strftime("%Y%m%dIST%H%M")
                print(t)
        assetsSummaryList.append([ an, assetBuyAvg, assetBuyQty, assetSellAvg, assetSellQty, assetSum ])
        print("{:48} : {:10.2f} x {:8} : {:10.2f} x {:8} : {:16.2f}".format(an, assetBuyAvg, assetBuyQty, assetSellAvg, assetSellQty, assetSum))
        if gbSpaceOutListing:
            print("")
    return assetsSummaryList


def _dba_summary(dba):
    bSum = numpy.sum(dba[:,IDB['BTRANSVALUE']])
    bQty = numpy.sum(dba[:,IDB['BQTY']])
    if (bQty == 0):
        if (bSum == 0):
            bAvg = 0
        else:
            bAvg = numpy.nan
            input("WARN:DBASummary:BuySum {} without BuyQty {}".format(bSum, bQty))
    else:
        bAvg = bSum/bQty
    sSum = numpy.sum(dba[:,IDB['STRANSVALUE']])
    sQty = numpy.sum(dba[:,IDB['SQTY']])
    if (sQty == 0):
        if (sSum == 0):
            sAvg = 0
        else:
            sAvg = numpy.nan
            input("WARN:DBASummary:SellSum {} without SellQty {}".format(sSum, sQty))
    else:
        sAvg = sSum/sQty
    return [bAvg, bQty, bSum], [sAvg, sQty, sSum]


def list_assets(db, filterAssets=[], bDetails=False):
    """
    List the data about specified assets in the db.
    db: the db containing data about assets
    filterAssets: a list of asset names or empty list.
    """
    dba = db
    dbaInHand = dba[dba[:,IDB['SQTY']] == 0]
    atAssetNames = list_assetnames(dba, False)
    ihAssetNames = list_assetnames(dbaInHand, False)
    ihUniqAssetsCnt = len(ihAssetNames)
    [ihTBAvg, ihTBQty, ihTBSum], [ihTSAvg, ihTSQty, ihTSSum] = _dba_summary(dbaInHand)  # In hand totals
    print("GrandSummary:InHand: UniqAssets={:8}, TotalQtys={:8}, TotalInvestedValue={:16.2f}".format(ihUniqAssetsCnt, ihTBQty, ihTBSum))
    assetsSummaryList = []
    totalProfitLoss = 0
    for an in atAssetNames:
        if (len(filterAssets) > 0) and (an not in filterAssets):
            continue
        atAssets = dba[dba[:,IDB['NAME']] == an]                # All total of a asset
        ihAssets = dbaInHand[dbaInHand[:,IDB['NAME']] == an]    # In hand of a asset
        prevAssets = atAssets[atAssets[:,IDB['SQTY']] > 0]
        curAssetProfitLoss = numpy.sum(prevAssets[:,IDB['STRANSVALUE']] - prevAssets[:,IDB['BTRANSVALUE']])
        totalProfitLoss += curAssetProfitLoss
        [atBAvg, atBQty, atBSum], [atSAvg, atSQty, atSSum] = _dba_summary(atAssets)
        [ihBAvg, ihBQty, ihBSum], [ihSAvg, ihSQty, ihSSum] = _dba_summary(ihAssets)
        if bDetails:
            for s in atAssets:
                t = s.copy()
                #t[IBS['TRANSDATE']] = t[IBS['TRANSDATE']].strftime("%Y%m%dIST%H%M")
                print(t)
        assetsSummaryList.append([ an, ihBAvg, ihBQty, ihBSum, atBAvg, atBQty, atSAvg, atSQty, curAssetProfitLoss ])
        print("{:48} :c: {:10.2f} x {:8} = {:16.2f} :b: {:10.2f} x {:8} :s: {:10.2f} x {:8} :PL: {:10.2f}".format(an, ihBAvg, ihBQty, ihBSum, atBAvg, atBQty, atSAvg, atSQty, curAssetProfitLoss))
        if gbSpaceOutListing:
            print("")
    print("GrandSummary:InHand: UniqAssets={:8}, TotalQtys={:8}, TotalInvestedValue={:16.2f} :ProfitLoss:{:16.2f}".format(ihUniqAssetsCnt, ihTBQty, ihTBSum, totalProfitLoss))
    return assetsSummaryList


