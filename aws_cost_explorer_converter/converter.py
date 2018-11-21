import boto3
from datetime import timedelta, date
import logging
import pandas
from pprint import pprint

class CostExplorerConverter:
    def __init__(self, client, start = None, end = None, granularity = 'DAILY', metrics = [ 'UnblendedCost' ], group_by = None, filter = None):
        self.client = client

        # Ensure default time range
        if not end:
            end = date.today()
        if not start:
            start = end - timedelta(days = 1)

        self.common_args = self._do_args({}, start, end, granularity, metrics, group_by, filter)

    def _do_args(self, args, start, end, granularity, metrics, group_by, filter):
        if start and not end:
            end = date.today()
        elif end and not start:
            start = end - timedelta(days = 1)

        if start and end:
            args['TimePeriod'] = {
                    'Start': start.isoformat(),
                    'End': end.isoformat()
                    #'Start': start.replace(microsecond=0).isoformat() + 'Z',
                    #'End': end.replace(microsecond=0).isoformat() + 'Z'
                    }

        if granularity:
            args['Granularity'] = granularity

        if metrics:
            args['Metrics'] = metrics

        if group_by:
            args['GroupBy'] = filter

        if filter:
            args['Filter'] = filter

        return args

    def to_array(self, start = None, end = None, granularity = None, metrics = None, group_by = None, filter = None):
        args = self._do_args(self.common_args.copy(), start, end, granularity, metrics, group_by, filter)

        records = []

        done = False
        while not done:
            print('Calling with:')
            pprint(args)
            print('')
            response = self.client.get_cost_and_usage(**args)

            if not response:
                raise Exception('No response recieved from AWS get_cost_and_usage')

            print('Response:')
            pprint(response)
            print('')

            records.extend(response['ResultsByTime'])

            if 'nextToken' in response:
                ## TODO: test looping
                args['NextPageToken'] = response['nextToken']
            else:
                done = True

        rows = []
        for record in records:
            row = {
                    'estimated':    record['Estimated'],
                    'start':        record['TimePeriod']['Start'],
                    'end':          record['TimePeriod']['End'],
                    'amount':       record['Total']['UnblendedCost']['Amount']
                    }
            rows.append(row)

        return rows

    def to_df(self, start = None, end = None, granularity = None, metrics = None, group_by = None, filter = None):
        rows = self.to_array(start, end, granularity, metrics, group_by, filter)
        df = pandas.DataFrame(rows)
        return df

