#! /usr/bin/env python3
# getShedule.py - Returns a list of a baseball teams schedule as datetime objects.

import requests, bs4, html5lib, datetime, re, time

months = {"JAN" : 1, "FEB" : 2, "MAR" : 3, "APR" : 4, "MAY" : 5, "JUN" : 6, \
    "JUL" : 7, "AUG" : 8, "SEP" : 9, "OCT" : 10, "NOV" : 11, "DEC" : 12} 

def getShedule(url):
    dates_and_times = []

    res = requests.get(url)
    res.raise_for_status() # Check to see if we downloaded the page successfully.
    soup = bs4.BeautifulSoup(res.text, 'html5lib')

    dateObjs = soup.select('main > div div.TableBaseWrapper:nth-of-type(2) span.CellGameDate')
    timeObjs = soup.select('main > div div.TableBaseWrapper:nth-of-type(2) div > a[href]')

    dates = [i.text.strip().upper() for i in dateObjs] # Month Day, Year ... (AUG 3, 2020)
    times = [i.text.strip().upper() for i in timeObjs] # Times are in EST ... (9:10 pm)

    dateRegex = re.compile(r'([a-zA-Z]{3}) (\d+), (\d{4})')
    timeRegex = re.compile(r'(\d+):(\d+) ([a-zA-Z]{2})')

    for i in range(0, len(dates)):
        dateMatch = dateRegex.search(dates[i])
        timeMatch = timeRegex.search(times[i])

        if dateMatch:
            month_ = months[dateMatch.group(1)]
            day_ = int(dateMatch.group(2))
            year_ = int(dateMatch.group(3))
        else:
            month_ = months[0]
            day_ = 0
            year_ = 0
        
        if timeMatch:
            hour_ = int(timeMatch.group(1)) - 3 # Convert time to PST
            minute_ = int(timeMatch.group(2))
            is_pm = timeMatch.group(3)
        else:
            hour_ = 0
            minute_ = 0
            is_pm = None

        if is_pm == 'PM':
            hour_ = hour_ + 12 # datetime.hour is in range(24)

        temp = datetime.datetime(year = year_, month = month_, day = day_, hour = hour_, minute = minute_)
        dates_and_times.append(temp)

    return dates_and_times