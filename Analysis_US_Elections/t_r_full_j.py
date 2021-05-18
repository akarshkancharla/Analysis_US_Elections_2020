from pymongo import MongoClient
from textblob import TextBlob
import numpy as np


biden_words=[]
trump_words=[]
recount_words=[]


twitter_biden_recount_percent=0
twitter_trump_recount_percent=0

reddit_biden_recount_percent=0
reddit_trump_recount_percent=0


def get_keywords_from_user(keylist_biden,keylist_trump,keylist_recount):
    global biden_words
    biden_words=keylist_biden
    print(biden_words)
    global trump_words
    trump_words=keylist_trump
    print(trump_words)
    global recount_words
    recount_words=keylist_recount
    print(recount_words)
   

def run_twitter_analysis():
    #Twitter
    client = MongoClient(port=27017)
    db = client['finalproject']
    coll2 = db['fptwitter']

    cur=coll2.find({})

    biden_tweet_count=0
    biden_recount=0
    trump_tweet_count=0
    trump_recount=0
    
    
    biden_sentiment=[]
    trump_sentiment=[]
    
    biden_subjectivity=[]
    trump_subjectivity=[]
    

    for row in cur:
        if 'entities' in row['data'].keys():
            if 'annotations' in row['data']['entities'].keys():
                if row['data']['entities']['annotations'][0]['normalized_text'].lower() in biden_words:
                    biden_tweet_count+=1
                    if any(b in row['data']['text'].lower() for b in recount_words):
                        biden_recount+=1
                        biden_sentiment.append(TextBlob(row['data']['text']).sentiment.polarity)
                        biden_subjectivity.append(TextBlob(row['data']['text']).sentiment.subjectivity)
                        
                        
                if row['data']['entities']['annotations'][0]['normalized_text'].lower() in trump_words:
                    trump_tweet_count+=1
                    if any(b in row['data']['text'].lower() for b in recount_words):
                        trump_recount+=1
                        trump_sentiment.append(TextBlob(row['data']['text']).sentiment.polarity)
                        trump_subjectivity.append(TextBlob(row['data']['text']).sentiment.subjectivity)
               
    print(biden_tweet_count)
    print(biden_recount)
    global twitter_biden_recount_percent
    twitter_biden_recount_percent=(biden_recount/biden_tweet_count)*100
    print("biden:",twitter_biden_recount_percent)
    twitter_biden_avg_sentiment=np.average(np.array(biden_sentiment))
    print("biden supporter sentiment: ",twitter_biden_avg_sentiment)
    twitter_biden_avg_subjectivity=np.average(np.array(biden_subjectivity))
    print("biden supporter subjectivity: ",twitter_biden_avg_subjectivity)
    print(trump_tweet_count)
    print(trump_recount)
    global twitter_trump_recount_percent
    twitter_trump_recount_percent=(trump_recount/trump_tweet_count)*100
    print("trump:",twitter_trump_recount_percent)
    twitter_trump_avg_sentiment=np.average(np.array(trump_sentiment))
    print("trump supporter sentiment: ",twitter_trump_avg_sentiment)
    twitter_trump_avg_subjectivity=np.average(np.array(trump_subjectivity))
    print("trump supporter subjectivity: ",twitter_trump_avg_subjectivity)
    


      

def run_reddit_analysis():
    
    client = MongoClient(port=27017)
    db = client['finalproject']
    coll2 = db['fpreddit']
    cur=coll2.find({})

    biden_tweet_count=0
    biden_recount=0
    trump_tweet_count=0
    trump_recount=0
    
    biden_sentiment=[]
    trump_sentiment=[]
    biden_subjectivity=[]
    trump_subjectivity=[]
    
    
    for row in cur:
        count=0
        for post_comment in row['post_comments']:
            #for post titles
            if count==0:
                count+=1
                if any(b in row['data']['title'].lower() for b in biden_words):
                    biden_tweet_count+=1
                    if any(b in row['data']['title'].lower() for b in recount_words):
                        biden_recount+=1
                        biden_sentiment.append(TextBlob(row['data']['title']).sentiment.polarity)
                        biden_subjectivity.append(TextBlob(row['data']['title']).sentiment.subjectivity)
                        
                if any(b in row['data']['title'].lower() for b in trump_words):
                    trump_tweet_count+=1
                    if any(b in row['data']['title'].lower() for b in recount_words):
                        trump_recount+=1
                        trump_sentiment.append(TextBlob(row['data']['title']).sentiment.polarity)
                        trump_subjectivity.append(TextBlob(row['data']['title']).sentiment.subjectivity)
                        
                        
            #for comments
            if 'body' in post_comment.keys():
                if any(b in post_comment['body'].lower() for b in biden_words):
                    biden_tweet_count+=1
                    if any(b in post_comment['body'].lower() for b in recount_words):
                        biden_recount+=1 
                        biden_sentiment.append(TextBlob(post_comment['body']).sentiment.polarity)
                        biden_subjectivity.append(TextBlob(post_comment['body']).sentiment.subjectivity)
                        
                if any(b in post_comment['body'].lower() for b in trump_words):
                    trump_tweet_count+=1
                    if any(b in post_comment['body'].lower() for b in recount_words):
                        trump_recount+=1 
                        trump_sentiment.append(TextBlob(post_comment['body']).sentiment.polarity)
                        trump_subjectivity.append(TextBlob(post_comment['body']).sentiment.subjectivity)
                
                #one level depth into each comment to get replies of depth one
                if post_comment['replies']!='':
                    if 'body' in post_comment['replies']['data']['children'][0]['data'].keys():
                        if any(b in post_comment['replies']['data']['children'][0]['data']['body'].lower() for b in biden_words):
                            biden_tweet_count+=1
                            if any(b in post_comment['replies']['data']['children'][0]['data']['body'].lower() for b in recount_words):
                                biden_recount+=1
                                biden_sentiment.append(TextBlob(post_comment['replies']['data']['children'][0]['data']['body']).sentiment.polarity)
                                biden_subjectivity.append(TextBlob(post_comment['replies']['data']['children'][0]['data']['body']).sentiment.subjectivity)
                                
                        if any(b in post_comment['replies']['data']['children'][0]['data']['body'].lower() for b in trump_words):
                            trump_tweet_count+=1
                            if any(b in post_comment['replies']['data']['children'][0]['data']['body'].lower() for b in recount_words):
                                trump_recount+=1
                                trump_sentiment.append(TextBlob(post_comment['replies']['data']['children'][0]['data']['body']).sentiment.polarity)
                                trump_subjectivity.append(TextBlob(post_comment['replies']['data']['children'][0]['data']['body']).sentiment.subjectivity)
                                
                                
    print(biden_tweet_count)
    print(biden_recount)
    global reddit_biden_recount_percent
    reddit_biden_recount_percent=(biden_recount/biden_tweet_count)*100
    print("biden:",reddit_biden_recount_percent)
    reddit_biden_avg_sentiment=np.average(np.array(biden_sentiment))
    print("biden supporter sentiment: ",reddit_biden_avg_sentiment)
    reddit_biden_avg_subjectivity=np.average(np.array(biden_subjectivity))
    print("biden supporter subjectivity: ",reddit_biden_avg_subjectivity)
    print(trump_tweet_count)
    print(trump_recount)
    global reddit_trump_recount_percent
    reddit_trump_recount_percent=(trump_recount/trump_tweet_count)*100
    print("trump:",reddit_trump_recount_percent)
    reddit_trump_avg_sentiment=np.average(np.array(trump_sentiment))
    print("trump supporter sentiment: ",reddit_trump_avg_sentiment)
    reddit_trump_avg_subjectivity=np.average(np.array(trump_subjectivity))
    print("trump supporter subjectivity: ",reddit_trump_avg_subjectivity)