import os
import math
import time
import json
import codecs
import requests
import collections
import datetime as dt
import pandas as pd
pd.options.mode.chained_assignment = None
# this enables us for rewriting dataframe to previous variable

from twitterscraper import query_tweets
from datetime import datetime
from argparse import Namespace


args = Namespace(
    keyword="COVID-19 (#COVID-19) (@@realDonaldTrump)",
    since="2020-03-01",
    until="2020-06-01",
    limit=0,
    saved_file="COVID19 realDonaldTrump 0301_0531.csv",
)


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()
        elif isinstance(obj, collections.abc.Iterable):
            return list(obj)
        elif isinstance(obj, dt.datetime):
            return obj.isoformat()
        elif hasattr(obj, '__getitem__') and hasattr(obj, 'keys'):
            return dict(obj)
        elif hasattr(obj, '__dict__'):
            # save all key value pairs
            # return {member: getattr(obj, member)
            #         for member in dir(obj)
            #         if not member.startswith('_') and
            #         not hasattr(getattr(obj, member), '__call__')}
            return {
                member: getattr(obj, member) for member in [
                    'username', 'user_id', 'timestamp', 'text'
                ]
            }

        return json.JSONEncoder.default(self, obj)


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield (start_date + dt.timedelta(n), start_date + dt.timedelta(n + 1))


if __name__ == '__main__':
    start_date = datetime.strptime(args.since, '%Y-%m-%d').date()
    end_date = datetime.strptime(args.until, '%Y-%m-%d').date()
    for begindate, enddate in daterange(start_date, end_date):
        print(begindate.strftime("%Y-%m-%d"), enddate.strftime("%Y-%m-%d"))

        start = time.time()
        # Retrieved tweets to file:
        tweets = query_tweets(query=args.keyword,
                              limit=args.limit,
                              begindate=begindate,
                              enddate=enddate,
                              poolsize=20,
                              lang='en')
        print(f'{time.time()-start} s')

        if len(tweets) != 0:
            json_tweets = json.dumps(tweets, cls=JSONEncoder)
            pd_tweets = pd.read_json(json_tweets).drop_duplicates()
            unique_user = pd_tweets.groupby(
                pd_tweets.user_id.tolist(), as_index=False).size()

            tweets_count = len(pd_tweets)
            unique_user_count = len(unique_user)
            influence_score = (tweets_count / (unique_user_count + 1)) * \
                math.log10(tweets_count + 1)
        else:
            tweets_count = 0
            unique_user_count = 0
            influence_score = 0

        data = {
            'date': [begindate.strftime("%Y-%m-%d")],
            'tweets_count': [tweets_count],
            'unique_user_count': [unique_user_count],
            'influence_score': [influence_score],
        }
        results = pd.DataFrame.from_dict(data)
        results.to_csv(
            args.saved_file, mode='a',
            header=not os.path.exists(args.saved_file),
            index=False, encoding='utf-8'
        )
