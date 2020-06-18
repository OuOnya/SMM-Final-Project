import os
import math
import time
import json
import twint
import requests
import datetime as dt
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None
# this enables us for rewriting dataframe to previous variable

from datetime import datetime
from argparse import Namespace

os.environ['TZ'] = 'US/Eastern'

args = Namespace(
    keyword='COVID-19 OR coronavirus OR virus OR #COVID-19',
    since='2020-03-01',
    until='2020-06-01',
    date_format='%Y-%m-%d',
    lang='en',
)

users = [
    'BarackObama',
    'BernieSanders',
    'HillaryClinton',
    'JoeBiden',
    'KingJames',
    'NYGovCuomo',
    'RandPaul',
    'realDonaldTrump',
    'rudygobert27',
    'tomhanks',
    'KDTrey5',
    'iamcardib',

    'GovernorKayIvey',
    'GovInslee',
    'GovHolcomb',
    'GovInslee',
    'SenGillibrand',
    'dougducey',
    'SenSchumer',
    'KimReynoldsIA',
    'Mike_Pence',
]


def daterange(str_start_date, str_end_date, date_format):
    start_date = datetime.strptime(str_start_date, date_format).date()
    end_date = datetime.strptime(str_end_date, date_format).date()

    for n in range(int((end_date - start_date).days)):
        yield ((start_date + dt.timedelta(n)).strftime(date_format),
               (start_date + dt.timedelta(n + 1)).strftime(date_format))


def continue_date(user, filename):
    try:
        data = pd.read_csv(filename, index_col='date')
        last_date = data[data[user] != 0].index[-1]
        last_date = datetime.strptime(last_date, args.date_format).date()
        return (last_date + dt.timedelta(1)).strftime(args.date_format)
    except Exception as e:
        pass

    return args.since


def store_data(append_data, filename):
    try:
        data = pd.read_csv(filename, index_col='date')
        append_data = append_data.combine(data, np.maximum, fill_value=0)
    except:
        pass

    append_data.to_csv(filename)


def mention_influence(user, filename='mention_influence.csv'):
    c = twint.Config()

    c.Filter_retweets = True
    c.Backoff_exponent = 2
    c.Retries_count = 20
    c.Lang = args.lang
    c.Hide_output = True
    c.Pandas = True

    str_start_date = continue_date(user, filename)
    for begindate, enddate in daterange(str_start_date, args.until, args.date_format):
        print('----------------------------------------------')
        print(f'Advanced search : "{args.keyword} (@{user})" on {begindate}.')
        start = time.time()

        # Set config
        c.Search = f'{args.keyword} (@{user})'
        c.Since = begindate
        c.Until = enddate

        # Retrieved tweets
        twint.run.Search(c)
        print(f'Search time: {time.time() - start} s.')

        pd_tweets = twint.storage.panda.Tweets_df
        if len(pd_tweets) != 0:
            pd_unique_user = pd_tweets.groupby('user_id').size()

            tweet_count = len(pd_tweets)
            unique_user_count = len(pd_unique_user)
            influence_score = ((0.9 ** (pd_unique_user - 1)).sum() /
                               (unique_user_count)) * math.log10(tweet_count + 1)
        else:
            tweet_count = 0
            unique_user_count = 0
            influence_score = 0

        data = {
            'date': [begindate],
            user: [influence_score],
        }
        append_data = pd.DataFrame.from_dict(data)
        append_data.set_index('date', inplace=True)
        print('----------------------------------------------')
        print(append_data)
        store_data(append_data, filename=filename)


def reply_influence(user, filename='reply_influence.csv'):
    id_list = []

    original_post_conf = twint.Config()
    original_post_conf.Username = user
    original_post_conf.Search = args.keyword
    original_post_conf.Lang = args.lang
    original_post_conf.Pandas = True
    original_post_conf.Proxy_host = 'tor'

    reply_conf = twint.Config()
    reply_conf.To = user
    reply_conf.Filter_retweets = True
    reply_conf.Backoff_exponent = 2
    reply_conf.Retries_count = 20
    reply_conf.Hide_output = True
    reply_conf.Lang = args.lang
    reply_conf.Pandas = True
    reply_conf.Proxy_host = 'tor'

    str_start_date = continue_date(user, filename)
    for begindate, enddate in daterange(str_start_date, args.until, args.date_format):
        print('----------------------------------------------')
        print(f'Advanced search : "{args.keyword}" on {begindate}.')
        start = time.time()

        original_post_conf.Search = args.keyword
        original_post_conf.Since = begindate
        original_post_conf.Until = enddate

        twint.run.Search(original_post_conf)
        print(f'Search time: {time.time() - start} s.')

        pd_tweets = twint.storage.panda.Tweets_df
        if len(pd_tweets) != 0:
            id_list.append(*pd_tweets['id'].tolist())

        print('id_list: ', len(id_list))
        print(id_list)

        reply_list = []
        reply_count_list = []
        unique_user_count = []
        user_weight_list = []
        influence_score_list = []
        if len(id_list) != 0:
            print('----------------------------------------------')
            print(f'Searching reply posts to {user}.')
            start = time.time()

            reply_conf.Since = begindate
            reply_conf.Until = enddate

            twint.run.Search(reply_conf)
            print(f'Search time: {time.time() - start} s.')

            pd_all_reply_tweets = twint.storage.panda.Tweets_df
            # id: current post id
            # conversation_id: original post id, i.e. the post id that is replied

            # pd_reply_tweets = pd_all_reply_tweets[
            #     pd_all_reply_tweets['conversation_id'].isin(id_list)
            # ]
            # reply_list = pd_reply_tweets.groupby(
            #     'conversation_id').size().to_list()

            pd_reply_tweets_list = [
                pd_all_reply_tweets[
                    pd_all_reply_tweets['conversation_id'] == id
                ]
                for id in id_list
            ]

            pd_unique_user_list = [
                pd_reply_tweets.groupby('user_id').size()
                for pd_reply_tweets in pd_reply_tweets_list
            ]

            reply_count_list = [
                len(pd_reply_tweets)
                for pd_reply_tweets in pd_reply_tweets_list
            ]

            unique_user_count = [
                len(pd_unique_user)
                for pd_unique_user in pd_unique_user_list
            ]

            user_weight_list = [
                0 if len(pd_unique_user) == 0 else
                (0.9 ** (pd_unique_user - 1)).sum() / len(pd_unique_user)
                for pd_unique_user in pd_unique_user_list
            ]

            influence_score_list = [
                0 if reply_count == 0 else
                user_weight * math.log10(reply_count + 1)
                for user_weight, reply_count in zip(user_weight_list, reply_count_list)
            ]

        data = {
            'date': [begindate],
            'id': [id_list],
            'reply_count_list': [reply_count_list],
            'unique_user_count': [unique_user_count],
            'user_weight_list': [user_weight_list],
            'influence_score_list': [influence_score_list],
            user: [sum(reply_count_list)],
        }
        append_data = pd.DataFrame.from_dict(data)
        append_data.set_index('date', inplace=True)
        print('----------------------------------------------')
        print(append_data)

        append_data.to_csv(
            f'reply_influence {user}.csv', mode='a',
            header=not os.path.exists(f'reply_influence {user}.csv')
        )


if __name__ == '__main__':
    for user in users:
        mention_influence(user)
        # reply_influence(user)
