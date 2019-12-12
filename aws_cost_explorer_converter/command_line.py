import boto3
import argparse
import json
from datetime import timedelta, date
from pprint import pprint

import aws_cost_explorer_converter

def parse_args():
    parser = argparse.ArgumentParser(
            description='Fetch cost explorer data from AWS and display and/or save it',
            usage='%(prog)s [options]',
            epilog='Standard environment variables for AWS connection information are supported'
            )

    global args
    parser.add_argument('--start', help='Start date; if a negative number, is taken as a delta from today; if zero, then as the start of the current month')
    parser.add_argument('--end', help='End date')
    parser.add_argument('--granularity', default='DAILY', help='Granularity, MONTHLY, DAILY or HOURLY (untested)')
    parser.add_argument('--filter', type=json.loads, help='JSON filter expression (see AWS documentation)')
    parser.add_argument('--metrics', type=json.loads, default=['UnblendedCost'], help='JSON metrics expression, eg \'[ "UnblendedCost", "NetUnblendedCost"]\'')
    parser.add_argument('--group-by', type=json.loads, help='JSON group_by expression (see AWS documentation)')
    parser.add_argument('--display', action='store_true', help='Display (truncated) output table')
    parser.add_argument('--out', help='File to store CSV in (not stored if not specified')

    args = parser.parse_args()

    # Handle special cases of start
    try:
        x = int(args.start)
        if x == 0:
            args.start = date.today().replace(day = 1)
        elif x < 0:
            args.start = date.today() + timedelta(days = x)
    except:
        pass

    return args

def main():
    args = parse_args()

    if not args.display and not args.out:
        raise Exception('Not showing or saving output, no reason to run')

    client = boto3.client('ce', region_name='us-east-1')
    converted = aws_cost_explorer_converter.CostExplorerConverter(
            client,
            start = args.start,
            end = args.end,
            granularity = args.granularity,
            filter = args.filter,
            group_by = args.group_by,
            metrics = args.metrics
        ).to_df()

    if args.display:
        print('Converted:')
        pprint(converted)
        print('')

    if args.out:
        converted.to_csv(path_or_buf = args.out, index = False, encoding = 'utf-8')
        print('Wrote csv to %s' % (args.out))

