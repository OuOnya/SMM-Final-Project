# SMM-Final-Project

This version use [twint](https://github.com/twintproject/twint).

So you need to install twint first:

``pip install twint``


## How to use?
1. Set the time zone of your country if you want. The crawler will search based on the time zone.
2. Set the keywords you want to search. Ex: ``COVID-19 OR coronavirus``
3. Set the language you want to crawl.
3. Select users you want to search for. Please use the same name as their Twitter ID.
4. Run it :)


## Convert CSV files to JSON files
If you run the above code, it will output *mention_influence.csv* file and several *reply_influence __USER__.csv* files.

To convert these CSV files to standard JSON format.

First, you need to write your *ID2name.json* file to match the Twitter ID with the real name.

Then specify the abbreviated code of your country, for example ***US***. Use the following command:

```python
python csv2json.py -m -r -n US
```

You can use ``python export_analyse.py --help`` to see a list of 2-letter country abbreviation code and more details.

If you have saved CSV files in another directory, for example ***./content/drive/mention_influence.csv***.
You can use the following command:

```python
python csv2json.py -m -n US -d "./content/drive"
```


## Features:
- Save all statistics to one file "mention_influence.csv".
- ``mention_influence`` support to continue crawling if "mention_influence.csv" exists.
- ``reply_influence`` function can work now. But it often sleeps so it is very slow. Currently each user saves to a different file.
- ``reply_influence`` also support to continue crawling if "reply_influence {user}.csv" exists.

**If you have any questions please contact me.**
