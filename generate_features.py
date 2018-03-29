import numpy as np
import pandas as pd
import re
import os, os.path
from datetime import datetime, timedelta

print('The features are created...') 
print('This may take a few seconds.') 

#### Define Util functions #### 
def msg_word_count(x):
    x = str(x)
    x = x.split(" ")
    return(len(x))
        
def question_flag(x):
    x = str(x)
    if '?' in x:
        return 1
    else:
        return 0

def is_in(m,l):
    if m in list(l):
        return 1
    else: 
        return 0
    
def group_conversation(fb_database):
    conv = fb_database.groupby(['conversation_id']).user.nunique()
    idx = conv[conv > 2].index
    fb_database['group_conversation'] = fb_database['conversation_id'].apply(lambda m: is_in(m,idx))
    return fb_database

def sticker_sent(x): 
    x = str(x)
    matchobj = re.search(r'<p><img src="messages/stickers/',x)
    if matchobj: 
        return 1
    else:
        return 0
    
def photo_sent(x):
    x = str(x)
    matchobj = re.match(r'<p><img src="messages/photos/',x)
    if matchobj: 
        return 1
    else:
        return 0

def timestamp(x,y):
    s = x +" "+ y 
    t = datetime.strptime(s, '%d %B %Y %H:%M %Z')
    return t


def response_time(fb):
    #sort by ID 
    fb = fb.sort_values('conversation_id')
    
    #for every entry: check previous entry of id; if id is different, enter 9999
    array = fb[['conversation_id','timestamp']].as_matrix()
    # replytime in dd:hh:mm
    conversation_id = None
    results = []
    for i in range(len(array)): 
        if array[i,0] == conversation_id: 
            #calculate time difference
            response_time = array[i-1,1] - array[i,1]
            results.append(response_time)
        else: 
            conversation_id = array[i,0]
            results.append('New')
    fb['response_time'] = results
    return fb

def conversation_init(response_time):
    """
    if message starts with a greeting or last message longer than a day 
    """
    #m = re.match(r'(Hey|Hello|Hi|Hallo|Hay|Ola|Hola)',message)
    #if m: 
    #    return 1
    if response_time == 'New':
        return 1
    elif response_time > timedelta(days=1):
        return 1
    else: 
        return 0
"""
def reply_time(x)
    pass

def conversation_initiated(x)
    pass

def sentiment(x):
    pass

def no_emojis(x):
    pass

def topic_by_day(x):
    pass

def topic_by_month(x):
    pass

def topic(x):
    pass

def language(x):
    pass

"""

#### load the data ####
facebook = pd.read_csv('fb_data.csv', lineterminator='\n')

#### generate features ####

facebook['msg_word_count'] = facebook.text.apply(lambda m: msg_word_count(m))
facebook['question_flag'] = facebook.text.apply(lambda m: question_flag(m))
facebook = group_conversation(facebook)
facebook['photo_sent'] = facebook.text.apply(lambda m: photo_sent(m))
facebook['sticket_sent'] = facebook.text.apply(lambda m: sticker_sent(m))
facebook['timestamp'] = facebook[['date','time']].apply(lambda t: timestamp(*t), axis=1)
facebook = response_time(facebook)
facebook['conversation_init'] = facebook['response_time'].apply(lambda t: conversation_init(t))

"""
facebook['group_conversation'] = None
facebook['reply_time'] = facebook.text.apply(lambda m: question_flag(m)) 
facebook['conversation_initiated'] = facebook.text.apply(lambda m: question_flag(m))
facebook['sentiment'] = facebook.text.apply(lambda m: question_flag(m))
facebook['no_emojis'] = facebook.text.apply(lambda m: question_flag(m))
facebook['topic'] = facebook.text.apply(lambda m: question_flag(m))
""" 

#### export data ####

facebook.to_csv('fb_data_features.csv', index=False)

print('Done! -> fb_data_features.csv generated') 