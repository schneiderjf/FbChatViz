import numpy as np
import pandas as pd
import re
import os, os.path

##### GENERATE A DATA FRAME FROM THE HTML FILES #####

print('The HTML files are being parsed...')
print('This may take a few seconds. ')

i = 0
# delete /n
with open('messages/'+str(i)+'.html', 'r', encoding="utf-8") as f:
    data=f.read().replace('\n', '')
    
# get conversation title
x = re.search('<title>(.*)</title>', data, re.S)
name = x.group(1)

# get conversation name
x = re.search('Conversation with (.*)', name)
person = x.group(1)
filename = person.replace(' ','_')

# split into rows
conversation = data.split('<div class="message"><div class="message_header">')[1:]
fb_database = pd.DataFrame(conversation)

# add meta data
fb_database['conversation_id'] = i
fb_database['conversation_name'] = filename
fb_database['plattform'] = 'Facebook'

# iterate through the messages
no_files = len(os.listdir('messages/')) - 8 
for i in range(no_files):
    with open('messages/'+str(i)+'.html', 'r', encoding="utf-8") as f:
        data=f.read().replace('\n', '')
    x = re.search('<title>(.*)</title>', data, re.S)
    name = x.group(1)
    x = re.search('Conversation with (.*)', name)
    person = x.group(1)
    filename = person.replace(' ','_')
    conversation = data.split('<div class="message"><div class="message_header">')[1:]
    conversation = pd.DataFrame(conversation)
    conversation['conversation_id'] = i
    conversation['conversation_name'] = str(filename)
    conversation['plattform'] = 'Facebook'
    fb_database = pd.concat([fb_database,conversation])

##### PARSE THE HTML FILE #####

def get_user(x):
    matchobj = re.search(r'<span class="user">(.*?)</span>',x)
    if matchobj:
        y = matchobj.group(1)
    else: 
        y = None
    return y

def get_text(x):
    matchobj = re.search(r'</div></div><p>(.*?)</p>',x)
    if matchobj:
        y = matchobj.group(1)
    else: 
        y = None
    return y

def get_day(x):
    matchobj = re.search(r'class="meta">(.*?),',x)
    if matchobj:
        y = matchobj.group(1)
    else: 
        y = None
    return y

def get_time(x):
    matchobj = re.search(r'at(.*?)</span>',x)
    if matchobj:
        y = matchobj.group(1)
    else: 
        y = None
    return y

def get_date(x):
    matchobj = re.search(r'class="meta">.*?, (.*?) at',x)
    if matchobj:
        y = matchobj.group(1)
    else: 
        y = None
    return y

# parse the features

fb_database['user'] = fb_database[0].apply(lambda x: get_user(x))
fb_database['text'] = fb_database[0].apply(lambda x: get_text(x))
fb_database['day'] = fb_database[0].apply(lambda x: get_day(x))
fb_database['date'] = fb_database[0].apply(lambda x: get_date(x))
fb_database['time'] = fb_database[0].apply(lambda x: get_time(x))

fb_database = fb_database.reset_index().drop([0,'index'], axis=1)
fb_database.index.name = 'message_id'

##### EXPORT THE RESULTS #####

fb_database.to_csv('fb_data.csv')
print('Done! -> File at fb_data.csv')