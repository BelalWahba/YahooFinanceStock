import json
import urllib.parse
import boto3
import pandas as pd
import io

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    # try:
    obj = s3.get_object(Bucket=bucket, Key=key)
    newobj = obj['Body'].read().decode('utf-8')
    print(newobj)
    df = pd.DataFrame()
    for count in range(newobj.count("records")):
        slice = newobj.split("}]}")[count]
        newdictttt = slice + "}]}"
        newdictttt
        data = json.loads(newdictttt)
        for i in range(len(data["records"])):
            record = data["records"][i]
            df = df.append(record,ignore_index=True)
    print(df)
    outputjson = df.to_parquet()
    bucket_name = "transformed-stock-data"
    s3_path = key+'.parquet'
    s3 = boto3.resource("s3")
    s3.Bucket(bucket_name).put_object(Key=s3_path, Body=outputjson)
    return
    # except Exception as e:
    #     print(e)
    #     print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
    #     raise e
