from influxdb import InfluxDBClient
import json
import base64
from datetime import datetime
import os
import boto3

def retreive_data(event):
    for record in event['Records']:
        payload = base64.b64decode(record['kinesis']['data'])
        deserialize_payload = json.loads(payload)
        print(deserialize_payload)
    return deserialize_payload

def payload(records):
    newrecord = {}
    for k,v in records.items():
        if k != 'Stock':
            if k != 'DateTime':
                newrecord[k] = float(v)
            else:
                newrecord[k] = v

    json_payload = []
    data = {
        "measurement": "Stocks",
        "tags": {
            "Stock": list(records.values())[0] 
            },
        "time": datetime.now(),
        "fields": newrecord}
    json_payload.append(data)
    return json_payload

def ses(stock,date):
    ses = boto3.client('ses')
    body = """
	    Warning!!!!!!!
	
	    Regardsing this stock -- {0}
	    
	    Its market price dropped just now
	    {1}
    """
    
    ses.send_email(Source = os.getenv("EMAIL"),Destination = {'ToAddresses': [os.getenv("EMAIL")]},
    Message = {'Subject': {
			    'Data': 'StockApi',
			    'Charset': 'UTF-8'},
		    'Body': {
			    'Text':{
				    'Data': body.format(stock, date),
				    'Charset': 'UTF-8'}}})
    return {'statusCode': 200,'body': json.dumps('Successfully sent email from Lambda using Amazon SES')}
    
def lambda_handler(event, context):
    records =  retreive_data(event)
    for count in range(len(records["records"])):
        record = records["records"][count]
        if record["RegularMarketPrice"] < record["DaysRangeLower"] or record["RegularMarketPrice"] == record["DaysRangeLower"]:
            ses(record["Stock"],record["DateTime"])
        lastrec = payload(record)
        print(lastrec)
        client = InfluxDBClient(os.getenv("IP"), 8086, os.getenv("USER"), os.getenv("PASS"), os.getenv("DATA"))
        client.get_list_database()
        client.switch_database('StockData')
        client.write_points(lastrec)
        print(client.write_points(lastrec))
