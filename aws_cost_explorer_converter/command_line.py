import boto3
from datetime import timedelta, date
from pprint import pprint

import aws_cost_explorer_converter

def main():
    client = boto3.client('ce', region_name='us-east-1')
    converted = aws_cost_explorer_converter.CostExplorerConverter(
            client,
            start = date(2018, 7, 5),
            #start = date.today() - timedelta(days = 2),
            #start = date.today().replace(day = 1),
            granularity = 'DAILY') \
                    .to_df(
                        filter=
#                            { 'And': [
                                { 'Tags': { 'Key': 'AppID', 'Values': [ '01036F7B-C158-426D-ABDD-86609A262CBA' ] } }
#                                , { 'Tags': { 'Key': 'Name',  'Values': [ 'dev1-dn-1a-0001', 'dev1-dn-1a-0001-xvdf' ] } }
#                            ] }
                        ,group_by=[
                            { 'Type': 'TAG', 'Key': 'Name' }
#                            , { 'Type': 'DIMENSION', 'Key': 'OPERATION' }
                            ]
                        )

    print('Converted:')
    pprint(converted)
    print('')

    path = '/tmp/costs.csv'
    converted.to_csv(path_or_buf = path, index = False)
    print('Wrote csv to %s' % (path))

