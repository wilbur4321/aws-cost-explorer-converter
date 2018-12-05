import boto3
from datetime import timedelta, date
import logging
import pandas
from pprint import pprint
import re

class CostExplorerConverter:
    def __init__(self, client, start = None, end = None, granularity = 'DAILY', metrics = [ 'UnblendedCost' ], group_by = None, filter = None):
        self.client = client

        # Ensure default time range
        if not end:
            end = date.today()
        if not start:
            start = end - timedelta(days = 1)

        self.common_args = self._do_args({}, start, end, granularity, metrics, group_by, filter)

    @staticmethod
    def _camel_to_snake(name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def _do_args(self, args, start, end, granularity, metrics, group_by, filter):
        if start and not end:
            end = date.today()
        elif end and not start:
            # TODO: this doesn't work if end is passed in as a string
            start = end - timedelta(days = 1)

        if start and end:
            try:
                start = start.isoformat()
            except:
                pass

            try:
                end = end.isoformat()
            except:
                pass

            args['TimePeriod'] = {
                    'Start': start,
                    'End': end
                    #'Start': start.replace(microsecond=0).isoformat() + 'Z',
                    #'End': end.replace(microsecond=0).isoformat() + 'Z'
                    }

        if granularity:
            args['Granularity'] = granularity

        if metrics:
            args['Metrics'] = metrics

        if group_by:
            args['GroupBy'] = group_by

        if filter:
            args['Filter'] = filter

        return args

    def to_array(self, start = None, end = None, granularity = None, metrics = None, group_by = None, filter = None):
        args = self._do_args(self.common_args.copy(), start, end, granularity, metrics, group_by, filter)

        if 'GroupBy' in args:
            group_names = []
            for group in args['GroupBy']:
                if group['Type'] == 'TAG':
                    # TODO: more thorough cleaning
                    group_names.append('tag_' + group['Key'].lower().replace('-', '_'))
                else:
                    group_names.append(group['Key'].lower())

        records = []

        done = False
        while not done:
            print('Calling with:')
            pprint(args)
            print('')
            response = self.client.get_cost_and_usage(**args)

            if not response:
                raise Exception('No response recieved from AWS get_cost_and_usage')

            #print('Response:')
            #pprint(response)
            #print('')

            records.extend(response['ResultsByTime'])

            if 'NextPageToken' in response:
                ## TODO: test looping
                args['NextPageToken'] = response['NextPageToken']
            else:
                done = True

        rows = []
        for record in records:
            #pprint(record)
            row = {
                    'estimated':    record['Estimated'],
                    'start':        record['TimePeriod']['Start'],
                    'end':          record['TimePeriod']['End']
                    }

            groups = record['Groups']
            if not groups:
                for metric in args['Metrics']:
                    row[CostExplorerConverter._camel_to_snake(metric)] = record['Total'][metric]['Amount']
                rows.append(row)
            else:
                for group in groups:
                    r = row.copy()
                    keys = group['Keys']
                    for i in range(len(group_names)):
                        r[group_names[i]] = keys[i]
                    for metric in args['Metrics']:
                        r[CostExplorerConverter._camel_to_snake(metric)] = group['Metrics'][metric]['Amount']
                    rows.append(r)

        return rows

    def to_df(self, start = None, end = None, granularity = None, metrics = None, group_by = None, filter = None):
        rows = self.to_array(start, end, granularity, metrics, group_by, filter)
        df = pandas.DataFrame(rows)
        return df

