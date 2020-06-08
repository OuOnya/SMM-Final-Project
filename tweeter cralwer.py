import os
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
    since="2020-05-14",
    until="2020-05-15",
    limit=0,
    saved_file="COVID19 realDonaldTrump 0514_0515.csv",
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


if __name__ == '__main__':
    # Save the retrieved tweets to file:
    start = time.time()
    tweets = query_tweets(query=args.keyword,
                          limit=args.limit,
                          begindate=datetime.strptime(
                              args.since, '%Y-%m-%d').date(),
                          enddate=datetime.strptime(
                              args.until, '%Y-%m-%d').date(),
                          poolsize=20,
                          lang='en')
    json_tweets = json.dumps(tweets, cls=JSONEncoder)
    pd_tweets = pd.read_json(json_tweets).drop_duplicates()
    pd_tweets.to_csv(args.saved_file, index=False, encoding='utf-8')
    print(f'{time.time()-start} s')

    # start = time.time()
    # os.system(
    #     f'twitterscraper "{args.keyword}" -bd {args.since} -ed {args.until} --lang en -o tweets.json -ow')
    # print(time.time() - start)

    pd_tweets = pd.read_csv(args.saved_file)
    print(pd_tweets)
    unique_user_count = pd_tweets.groupby(
        pd_tweets.user_id.tolist(), as_index=False).size()
    print(unique_user_count)
