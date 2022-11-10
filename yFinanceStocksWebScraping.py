from bs4 import BeautifulSoup
import re
import boto3
import json
from requests_html import AsyncHTMLSession
import nest_asyncio
import asyncio
from datetime import datetime

async def get_EURUSD():
    asession = AsyncHTMLSession()
    r = await asession.get('https://finance.yahoo.com/quote/EURUSD%3DX?p=EURUSD%3DX')
    records= await test(r)
    return records

async def get_JPYUSD():
    asession = AsyncHTMLSession()
    r = await asession.get('https://finance.yahoo.com/quote/JPY%3DX?p=JPY%3DX')
    records= await test(r)
    return records
    
async def get_GBPUSD():
    asession = AsyncHTMLSession()
    r = await asession.get('https://finance.yahoo.com/quote/GBPUSD%3DX?p=GBPUSD%3DX')
    records= await test(r)
    return records
    
async def get_CMCCrypto():
    asession = AsyncHTMLSession()
    r = await asession.get('https://finance.yahoo.com/quote/%5ECMC200?p=%5ECMC200')
    records= await test(r)
    return records

async def get_GoldDec():
    asession = AsyncHTMLSession()
    r = await asession.get('https://finance.yahoo.com/quote/GC%3DF?p=GC%3DF')
    records= await test(r)
    return records

async def scraping101(dictionary,r):
    soup = BeautifulSoup(r.content, 'html.parser')
    name = soup.h1.text
    results = soup.find('div', {'class': 'D(ib) Mend(20px)'})
    regularMarketPrice = results.find('fin-streamer', {'data-field': 'regularMarketPrice'}).text
    regularMarketChangeDemo = results.find('fin-streamer', {'data-field': 'regularMarketChange'}).text
    regularMarketChange = re.findall(r"[-]?(?:\d*\.\d+|\d+)", regularMarketChangeDemo)[0]
    regularMarketChangePercentDemo = results.find('fin-streamer', {'data-field': 'regularMarketChangePercent'}).text
    regularMarketChangePercent = re.findall(r"[-]?(?:\d*\.\d+|\d+)", regularMarketChangePercentDemo)[0]
    quoteSummary = soup.find('div', {'id': 'quote-summary'})
    rightbracket = quoteSummary.find('table', {'class': 'W(100%) M(0) Bdcl(c)'})
    try:
        leftbracket = quoteSummary.find('table', {'class': 'W(100%)'})
        bid = leftbracket.find('td', {'data-test': 'BID-value'}).text
    except:
        pass
    date = datetime.now()
    date = date.strftime("%m/%d/%Y, %H:%M:%S")
    dictionary['Stock'] = name
    dictionary['DateTime'] = date
    dictionary['RegularMarketPrice'] = regularMarketPrice
    dictionary['RegularMarketChange'] = regularMarketChange
    dictionary['RegularMarketChangePercent'] = regularMarketChangePercent
    try:
        dictionary['Bid'] = bid
    except:
        pass
    return rightbracket, dictionary

async def extractQuoteSummary(rightbracket):
    l2= []
    for tr in rightbracket.find_all('tr'):
        for td in tr.find_all('td'):
            l2.append(td.text)
    return l2

def Convert(lst,dic):
    res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
    return dic.update(res_dct)

async def transform(dictionary):
    substring = ' - '
    lastdict = {}
    for k,v in dictionary.items():
        newk = k.replace(" ", "")
        newk = newk.replace("'", "")
        newv = v.replace(",", "")
        if substring in v:
            lastdict[newk+'Lower'] = dictionary[k].split('-')[0].replace(",", "")
            lastdict[newk+'Upper'] = dictionary[k].split('-')[1].replace(",", "")
            continue
        lastdict[newk] = newv
    return lastdict

async def test(r):
    dictionary = {}
    rightbracket, dictionary = asyncio.run(scraping101(dictionary,r))
    rightbracket = await extractQuoteSummary(rightbracket)
    Convert(rightbracket,dictionary)
    lastdict = await transform(dictionary)
    return lastdict

async def fakemain():
    asession = AsyncHTMLSession()
    array = {}
    records= asession.run(get_EURUSD, get_JPYUSD, get_GBPUSD,get_CMCCrypto,get_GoldDec)
    array["records"] = records
    records = json.dumps(array)
    return records

def generate(stream_name, kinesis_client,results): 
    respone = kinesis_client.put_record(
    StreamName=stream_name,
    Data=results,
    PartitionKey='user1')
    print (respone,results)

if __name__ == '__main__':
    nest_asyncio.apply()
    records = asyncio.run(fakemain())
    STREAM_NAME = "StockApi"
    generate(STREAM_NAME, boto3.client('kinesis'),records)
