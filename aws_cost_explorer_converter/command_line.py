import boto3
from datetime import timedelta, date
from pprint import pprint

import aws_cost_explorer_converter

def main():
    client = boto3.client('ce', region_name='us-east-1')
    converted = aws_cost_explorer_converter.CostExplorerConverter(
            client,
            start = date.today() - timedelta(days = 5),
            #start = date.today().replace(day = 1),
            granularity = 'DAILY') \
                    .to_df(filter={ 'Tags': { 'Key': 'AppID', 'Values': [ '01036F7B-C158-426D-ABDD-86609A262CBA' ] } })

    print('Converted:')
    pprint(converted)

