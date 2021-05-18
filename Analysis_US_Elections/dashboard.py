from flask import Flask
from flask import render_template, request
from flask_pymongo import PyMongo
from datetime import timezone
import pandas as pd
import datetime
import re
from pandas.io.json import json_normalize
import t_r_full_j
from t_r_full_j import *


app = Flask(__name__)

# connect to twitter database
mongo1 = PyMongo(app, uri="mongodb://localhost:27017/finalproject")

# connect to reddit database on the same host
mongo2 = PyMongo(app, uri="mongodb://localhost:27017/finalproject")


@app.route("/")
def homepage():
    return render_template('home.html')


@app.route("/analysis2_chart")
def input2():
    return render_template('chart2.html')


@app.route("/analysis2_chart", methods=['POST'])
def chart2():
    
    # Date parameter in YYYY-MM-DD format
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    
    # Fetching twitter data from mongodb database
    twitter_data = mongo1.db.fptwitter.find({"data.created_at": {'$gte': start_date, '$lt': end_date}},
                                                            {'data.text': 1})
    
    twitter_list_cur = list(twitter_data)
   
    pd.set_option('display.max_rows', None)
    
    pd.set_option('display.max_columns', None)
    
    pd.set_option('display.width', None)
    
    #pd.set_option('display.max_colwidth', None)
    
    twitter_df = pd.DataFrame.from_dict(json_normalize(twitter_list_cur), orient='columns')
    # print(twitter_df)
 
    twitter_df['data.text'] = twitter_df['data.text'].apply(lambda x: clean_tweets(x))
    # print(twitter_df)

    # Parsing date parameter to unix timestamp for querying reddit data
    dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    unix_start_utc = int(dt.replace(tzinfo=timezone.utc).timestamp())
    # print("StartTime:", unix_start_utc)
    dt1 = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    unix_end_utc = int(dt1.replace(tzinfo=timezone.utc).timestamp())
    # print("EndTime:", unix_end_utc)
   
    # Fetching reddit data from mongodb database
    reddit_data = mongo2.db.fpreddit.find({"data.created_utc": {'$gte': unix_start_utc, '$lt': unix_end_utc}})
    
    # Creating sample data for biden's tweets/posts filteration
    bidenhashtagsnkeywords = ['#joebiden', '#biden2020', '#biden', 'joe biden', 'biden', 'joebiden']
    twitter_bidencount = 0

    # Creating sample data for trump's tweets/posts filteration
    trumphashtagsnkeywords = ['#donaldtrump', '#trump2020', '#trump', 'donald trump', 'trump', 'donaldtrump']
    twitter_trumpcount = 0
   
    # Iterating over twitter's pandas dataframe
    for twitter_row in twitter_df.itertuples():
        twitter_text = twitter_row[2]
        res1 = any(ele in twitter_text.lower() for ele in bidenhashtagsnkeywords)
        if res1:
            twitter_bidencount = twitter_bidencount + 1
        res2 = any(ele in twitter_text.lower() for ele in trumphashtagsnkeywords)
        if res2:
            twitter_trumpcount = twitter_trumpcount + 1

    print("Popularity of Joe Biden in tweets after Election's result were out: " + str(twitter_bidencount))
    print("Popularity of Donald Trump in tweets after Election's result were out: " + str(twitter_trumpcount))

    if twitter_bidencount > twitter_trumpcount:
         print("Joe Biden is more popular in public talks than Donald Trump since Election result were out on twitter.")
    else:
         print("Donald Trump is more popular in public talks than Joe Biden since Election result were out on twitter.")

    reddit_bidencount = 0
    reddit_trumpcount = 0
   
    # Iterating over reddit's cursor object
    for row in reddit_data:
        for post_comment in row['post_comments']:
            # for post titles
            if any(b in row['data']['title'].lower() for b in bidenhashtagsnkeywords):
                reddit_bidencount += 1

            if any(b in row['data']['title'].lower() for b in trumphashtagsnkeywords):
                reddit_trumpcount += 1

        # for comments
        if 'body' in post_comment.keys():
            if any(b in post_comment['body'].lower() for b in bidenhashtagsnkeywords):
                reddit_bidencount += 1

            if any(b in post_comment['body'].lower() for b in trumphashtagsnkeywords):
                reddit_trumpcount += 1

            # one level depth into each comment to get replies of depth one
            if post_comment['replies'] != '':
                if 'body' in post_comment['replies']['data']['children'][0]['data'].keys():
                    if any(b in post_comment['replies']['data']['children'][0]['data']['body'].lower() for b in
                           bidenhashtagsnkeywords):
                        reddit_bidencount += 1

                    if any(b in post_comment['replies']['data']['children'][0]['data']['body'].lower() for b in
                           trumphashtagsnkeywords):
                        reddit_trumpcount += 1

    print("Popularity of Joe Biden in reddit posts after Election's result were out: " + str(reddit_bidencount))
    print("Popularity of Donald Trump in reddit posts after Election's result were out: " + str(reddit_trumpcount))

    if reddit_bidencount > reddit_trumpcount:
         print("Joe Biden is more popular in public talks than Donald Trump since Election result were out on reddit.")
    else:
         print("Donald Trump is more popular in public talks than Joe Biden since Election result were out on reddit.")

    return render_template('chart2.html', t1=twitter_trumpcount, t2=twitter_bidencount, r1=reddit_trumpcount,
                           r2=reddit_bidencount)


# Data cleaning for performing analysis on twitter text
def clean_tweets(text):
    text = re.sub("RT @[\w]*:", "", text)
    text = re.sub("@[\w]*", "", text)
    text = re.sub("https?://[A-Za-z0-9./]*", "", text)
    text = re.sub("\n", "", text)
    return text


@app.route('/analysis1_chart')
def input1():
    return render_template('chart1.html')


@app.route('/analysis1_chart', methods=['POST'])
def chart1():
    if request.method=='POST':
        key_list_biden=request.form.getlist('bidenword')
        key_list_trump=request.form.getlist('trumpword')
        key_list_recount=request.form.getlist('recountword')
        get_keywords_from_user(key_list_biden,key_list_trump,key_list_recount)
        run_twitter_analysis()
        run_reddit_analysis()

        return render_template('chart1.html', tb=t_r_full_j.twitter_biden_recount_percent, tt=t_r_full_j.twitter_trump_recount_percent,
                               rb=t_r_full_j.reddit_biden_recount_percent, rt=t_r_full_j.reddit_trump_recount_percent)


if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=False, port=5000)
