#
# adb - manage the assets db
# HanishKVC, 2021
# GPL
#

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
                t[IDBSTOCK['TRANSDATE']] = time.strftime("%Y%m%dIST%H%M", t[IDBSTOCK['TRANSDATE']])
                print(t)
        stocksSummaryList.append([ sn, stockBuyAvg, stockBuyQty, stockSellAvg, stockSellQty, stockSum ])
        print("{:48} : {:10.2f} x {:8} : {:10.2f} x {:8} : {:16.2f}".format(sn, stockBuyAvg, stockBuyQty, stockSellAvg, stockSellQty, stockSum))
        if gbSpaceOutListing:
            print("")
    return stocksSummaryList


