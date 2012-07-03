"""
  This file specifies the view methods

  Necessary actions for extending for new currency:
    - add new entry to url-dictionary with the proper url
    - create a model in models.py with the same name as the entry
      in the url dictionary
    - add new currency to imports in this file
    - syncdb
    - call currencyRates/update or click the update button in 
      the index-view
"""
from django.template import Context, loader
from django.http import HttpResponse
from django.db import transaction,connection
from django.shortcuts import render_to_response
from currencyRates.models import EuroToUSD,EuroToGBP
import datetime
import urllib
import re
import json

#data source urls
url = dict()
url['EuroToUSD'] = "http://www.bundesbank.de/cae/servlet/CsvDownload?tsId=BBK01.WT5636&its_csvFormat=de&mode=its"
url['EuroToGBP'] = "http://www.bundesbank.de/cae/servlet/CsvDownload?tsId=BBK01.WT5627&its_csvFormat=de&mode=its"

#pattern to filter out all lines that do not start with a date
dp = re.compile('[1-9][0-9]{3}\-[0-9]{2}\-[0-9]{2}')

#return template with currencies
def index(request):
    currencies = dict()
    currencies['currencyList'] = url.keys()
    return render_to_response('currencyRates/index.html',currencies)

#for performance: use of transactions
@transaction.commit_manually
def update(request):

    for currency,link in url.iteritems():
        latest_date = datetime.date(1970, 1, 1)

        table = globals()[currency];

        #get latest data entry for update - if non exists, keep it at 1970-01-01
        if len(table.objects.all()) > 0:
            latest_date = table.objects.all().order_by('-date')[0].date

        #load data
        data = urllib.urlopen(link).read().split("\n")

        #loop through usd data - set gbp to 0 for now
        for line in data:
            entry = line.split(";")
            #skip lines that do not match date pattern, that do not contain a value and those that already exist in the database
            #for performance reasons it is not checked against the database whether the specific entry already exists
            if dp.match(entry[0]) and entry[1] != "." and parseDate(entry[0]) > latest_date:
                table.objects.create(date = entry[0], rate = entry[1].replace(",","."))


    transaction.commit()

    return HttpResponse("Done")

def loaddata(request):

    data = list()

    #get the currency from get parameter or set first as default
    for cur,link in url.iteritems():
        if request.GET.get('currency') is not None and cur.upper() == request.GET.get('currency').upper():
            currency = cur
            break
    else:
        currency = url.keys()[0]

    #tablename/modelname
    table = globals()[currency]

    #get start and enddate - set default to today and 30days before startdate if not set
    if request.GET.get('enddate'):
        enddate = parseDate(request.GET.get('enddate'))
    else:
        enddate = table.objects.all().order_by('-date')[0].date

    if request.GET.get('startdate'):
        startdate = parseDate(request.GET.get('startdate'))
    else:
         startdate = enddate + datetime.timedelta(-30)

    #cursor for raw query execution
    cursor = connection.cursor()

    #month
    if request.GET.get('interval') is not None and request.GET.get('interval') == "m":
        cursor.execute("""SELECT strftime('%%Y-%%m-%%d',date) AS date, 
                                 avg(rate) AS rate 
                          FROM currencyRates_"""+currency+"""
                          WHERE date >= %s AND date <= %s 
                          GROUP BY strftime('%%Y-%%m', date) 
                          ORDER BY date;""",[startdate,enddate])
        for element in cursor.fetchall():
            data.append([str(element[0]),
                         float(element[1])])
    #week
    elif request.GET.get('interval') is not None and request.GET.get('interval') == "w":
        cursor.execute("""SELECT strftime('%%Y-%%m-%%d',date) AS date, 
                                 avg(rate) AS rate
                          FROM currencyRates_"""+currency+"""
                          WHERE date >= %s AND date <= %s 
                          GROUP BY strftime('%%Y-%%W', date) 
                          ORDER BY date;""",[startdate,enddate])
        for element in cursor.fetchall():
            data.append([str(element[0]),
                         float(element[1])])
    #day - default
    else:
        for element in table.objects.all().extra(where=["date >= '" + str(startdate) + "' AND date <= '" + str(enddate) + "'"]).order_by('date'):
            data.append([str(element.date), 
                         float(element.rate)])

    return HttpResponse(json.dumps(data), mimetype="application/json")

#simple helper method for easier date comparison in update method
def parseDate(date_str):
    date_list = date_str.split("-")
    return datetime.date(int(date_list[0]),int(date_list[1]),int(date_list[2]))
