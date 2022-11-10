# YahooFinanceStock

# *Overview*

- Aquiring data by webscraping stocks from yahoo finance using lambda function and cleaning them .
- Push the data into Kinesis Data Dtreams so that
	- It can be batched using Kinesis Firehose and dumped into an S3 bucket.
	- it triggers lambda functiont to write the data into InfluxDB and activate the SES alert function.
- Running AWS Glue crawler to standarize the schema and query the data on AWS Athena.
- Visualize the resluts on both AWS Quicksight for historical data and Grafana for time series data.
- Created a Cloudformation template to all the services used in the project.

<p align="center">
    <img src="https://github.com/BelalWahba/YahooFinanceStockIngesion/blob/main/Sources/fsdfsdfsdfsd.png">
</p>

# *Extraction and Transformation*

For data acquisition there was no suitable free stockapi with decent number of requests/day, so
instead another approach was webscraping 5 different stocks from yahoo finance using request_html
library and its async function alongside with async function definition, a lambda function triggered by
EventBridge that runs every minute to run the webscraping code.
The acquired data had to enter another process for cleaning and transforming it into a manner that
is well suited for loading it into kinesis data streams.
Once the records are ready they are loaded into kinesis data stream service which is suitable to the project as it was
the cheapest and reliable.


# *Load*

The data in kinesis would trigger two things, one of them is to send the raw records to kinesis firehose to
batch all the records and store them in an S3 bucket which would trigger a lambda function to change the batched object
format into Parquet file as it's a columnar storage format that is optimized for fast retrieval of data to analyze then put
it on another S3 bucket. And the other is loading the live records into InfluxDB on an EC2 instance
and it was favored on the InfluxDB cloud as using it on an ec2 was free so it wouln't cost anything, and this was done by
triggering a lambda function by kinesis.


# *Analysis*

For this part AWS Glue crawler was found reasonable as if there were any anomalies in the schema of the data
it can always fix it and analyse the data in Athena service using sql and use the results to visualise.


# *Visualisasion*

-After analyzing the data quicksight was used to visualize the results of the historical data into charts and graphs readable to the client
to get a useful insight from these stocks.

<p align="center">
    <img src="https://github.com/BelalWahba/YahooFinanceStockIngesion/blob/main/Sources/QuickSight.gif">
</p>

-And creating a live dashboard representing every change in the stock by connecting the live data in InfluxDB as a source to Grafana
to do time series analysis on and create the live dashboard.

<p align="center">
    <img src="https://github.com/BelalWahba/YahooFinanceStockIngesion/blob/main/Sources/Grafana.gif">
</p>

# *Alerting System*

Added an alerting function to the lambda triggered by kinesis data stream to send an email using SES once a certain condition is met.

<p align="center">
    <img src="https://github.com/BelalWahba/YahooFinanceStockIngesion/blob/main/Sources/SES.png">
</p>

# *Infrastructure as a Code (IAC)*

Created a Cloudformation template to all the services used in the project so it can be launched in any region any account just by using it.
