import os
import argparse
import json
import pandas as pd
import numpy as np

MENTION_INPUT_FILE = 'mention_influence.csv'
REPLY_INPUT_FILE = 'reply_influence {}.csv'

MENTION_OUTPUT_FILE = '{}_mention.json'
REPLY_OUTPUT_FILE = '{}_reply.json'


def mention_csv2json(users, nation, input_file=MENTION_INPUT_FILE, output_file=MENTION_OUTPUT_FILE):
    output_file = output_file.format(nation)

    try:
        # read csv file and square the original score
        pd_data = pd.read_csv(input_file, index_col='date').T
        pd_data **= 2

        json_data = json.loads(pd_data.to_json(orient='split'))
        json_data = [
            {
                'name': users[user],
                'data': data
            }
            for user, data in zip(json_data['index'], json_data['data'])
        ]

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)

        print(f'Successfully converted {input_file} to {output_file}.')

    except Exception as e:
        print(e)


def reply_csv2json(users, nation, input_file=REPLY_INPUT_FILE, output_file=REPLY_OUTPUT_FILE):
    output_file = REPLY_OUTPUT_FILE.format(nation)

    json_data = []
    for user, screen_name in users.items():
        try:
            ifile = input_file.format(user)
            pd_data = pd.read_csv(ifile, index_col='date')

            # To normalize the data: log(Total Reply Counts + 1) ^ 2
            json_data.append({
                'name': screen_name,
                'data': (np.log10(pd_data[user] + 1) ** 2).tolist()
            })
        except Exception as e:
            print(e)
            print(f'Cannot convert {screen_name} data.')

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

    print(f'Successfully converted all reply_influence.csv to {output_file}.')


if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=__doc__
    )

    arg_parser.add_argument(
        "-map",
        "--name_map",
        type=str,
        default="ID2name.json",
        help="Input file with user figures. Defalut: ID2name.json"
    )

    arg_parser.add_argument(
        "-d",
        "--source_dir",
        type=str,
        default=".",
        help="The folder path of the source CSV file. Defalut: . (current working directory)"
    )

    arg_parser.add_argument(
        "-m",
        "--convert_mention",
        action="store_true",
        help="If specified, the script will convert mention_influence.csv to Nation_mention.json",
    )

    arg_parser.add_argument(
        "-r",
        "--convert_reply",
        action="store_true",
        help="If specified, the script will convert all reply_influence {user}.csv to Nation_reply.json",
    )

    arg_parser.add_argument(
        "-n",
        "--nation",
        type=str,
        default="US",
        help="Set the 2-letter country abbreviation code. You can choose from:\n"
             "JP (Japan)\n"
             "FR (France)\n"
             "TH (Thailand)\n"
             "ID (Indonesia)\n"
             "US (United States)\n"
             "UK (United Kingdom)\n"
             "Default: US\n"
    )

    args = arg_parser.parse_args()

    try:
        with open(args.name_map, 'r', encoding='utf-8') as f:
            USERS = json.load(f)
    except Exception as e:
        print(e)
        exit(1)

    if args.convert_mention:
        mention_csv2json(
            USERS,
            args.nation.upper(),
            os.path.join(args.source_dir, MENTION_INPUT_FILE)
        )

    if args.convert_reply:
        reply_csv2json(
            USERS,
            args.nation.upper(),
            os.path.join(args.source_dir, REPLY_INPUT_FILE)
        )
