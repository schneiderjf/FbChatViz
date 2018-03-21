#### This script parses the HTML files in the messages folder into one csv file ####
print("The html files are parsed...")
print("This may take a few seconds.")

import numpy as np
import pandas as pd
import re
import os, os.path

i = 0
# delete /n
with open('messages/'+str(i)+'.html', 'r') as f:
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
    with open('messages/'+str(i)+'.html', 'r') as f:
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

# Export to CSV
fb_database.to_csv('fb_data.csv')