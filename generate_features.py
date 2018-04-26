import numpy as np
import pandas as pd
import re
import os, os.path
from datetime import datetime, timedelta


import nltk
from nltk.classify.textcat import TextCat
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('crubadan')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('vader_lexicon')


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
    try: 
        t = datetime.strptime(s, '%d %B %Y %H:%M %Z')
    except: 
        t = parse(s)
    return t


def response_time(fb):
    #sort by ID 
    fb = fb.sort_values(by=['conversation_id', 'timestamp'])
    
    #for every entry: check previous entry of id; if id is different, enter 9999
    array = fb[['conversation_id','timestamp']].as_matrix()
    # replytime in dd:hh:mm
    conversation_id = None
    results = []
    for i in range(len(array)): 
        if array[i,0] == conversation_id: 
            #calculate time difference
            response_time = array[i,1] - array[i-1,1]
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

def emoji_count(m):
    m = str(m)
    if re.findall(r'[\U0001f600-\U0001f650]', m):
        return len(re.findall(r'[\U0001f600-\U0001f650]', m))
    else: 
        return 0


def sentiment_analysis(m):
    '''
    returns the sentiment score between -1 and 1 
    '''
    try:
        first_text_list = nltk.word_tokenize(m)
        cleaned = [word for word in first_text_list if word.lower() not in stopwords]
        cleaned = str(' '.join(cleaned))    
        
        sid = SentimentIntensityAnalyzer()
        return sid.polarity_scores(cleaned)['compound']
    except:
        return 0

def detect_language(x):
    tc = TextCat()
    lemm = WordNetLemmatizer()

    tok = nltk.word_tokenize(x)
    lemmatized = [lemm.lemmatize(word) for word in tok]
    sentence = [sent for sent in lemmatized if sent.isalpha()]

    text = ' '.join(sentence[:10])

    lang = tc.guess_language(text)
    
    return lang


def top_word_freq(wordlist, n):
    
    wordfreq = [wordlist.count(p) for p in wordlist]
    freqdict = dict(zip(wordlist, wordfreq))
    
    aux = [(freqdict[key], key) for key in freqdict]
    aux.sort()
    aux.reverse()
    
    return aux[:n]


def topics_analysis(x, n_top_words):
    
    text, n_top_words = list(x), n_top_words
    lemm = WordNetLemmatizer()
    class LemmaCountVectorizer(CountVectorizer):
    
        def build_analyzer(self):
        
            analyzer = super(LemmaCountVectorizer, self).build_analyzer()
            return lambda doc: (lemm.lemmatize(w) for w in analyzer(doc))
    
    tf_vectorizer = LemmaCountVectorizer(max_df = 0.95, min_df = 2, stop_words = 'english', decode_error = 'ignore')

    tf = tf_vectorizer.fit_transform(text)
    
    lda = LatentDirichletAllocation(n_components = 11, max_iter = 5,
                                    learning_method = 'online', learning_offset = 50., random_state = 0)
    lda.fit(tf)
    
    tf_feature_names = tf_vectorizer.get_feature_names()
    
    first_topic = lda.components_[0]
    second_topic = lda.components_[1]
    third_topic = lda.components_[2]
    fourth_topic = lda.components_[3]
    
    first_topic_words = [tf_feature_names[i] for i in first_topic.argsort()[:-n_top_words - 1 :-1]]
    second_topic_words = [tf_feature_names[i] for i in second_topic.argsort()[:-n_top_words - 1 :-1]]
    third_topic_words = [tf_feature_names[i] for i in third_topic.argsort()[:-n_top_words - 1 :-1]]
    fourth_topic_words = [tf_feature_names[i] for i in fourth_topic.argsort()[:-n_top_words - 1 :-1]]
    
    return first_topic_words



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
facebook['emoji_count'] = facebook.text.apply(lambda m: emoji_count(m))

# The NLTK Vader libaray needs to be present
facebook['msg_sentiment'] = facebook.text.apply(lambda m: sentiment_analysis(m))
facebook['language'] = facebook.text.apply(lambda m: detect_language(m))


#### export data ####

facebook.to_csv('fb_data_features.csv', index=False)

print('Done! -> fb_data_features.csv generated') 