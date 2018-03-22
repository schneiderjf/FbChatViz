# Tutorial: Getting started analyzing your Facebook chats - Step by Step 

Facebook knows a lot about us. In fact, all messages we have ever sent via messenger are sitting on the servers of the internet giant - as long as you have not deleted them. Every Facebook user can download their data and this tutorial should provide you with a step-by-step tutorial, to bring your data into an analyzable format, as well as helping you to create some first basic features for chat analysis. 

## 0, Install requirements

Please make sure you have the following requirements installed: 
* Python 3.x
* numpy 
* pandas

## 1, Download your data

To get your facebook data just follow the instructions of this link: https://www.facebook.com/help/302796099745838

In a nutshell: 
- Click the small arrow at the top right of any Facebook page and select Settings
- Click Download a copy of your Facebook data below your General Account Settings
- Click Start My Archive

Facebook needs to collect your data, so it might take a while. Once the folder with the data is present continue to step 2. 


## 2, Parse the HTML files into a csv file

Your Facebook Data comes as a folder with HTML files, which is very handy if you want to click through it, but unsuitable if you want to do statistical analysis with python or R and we would therefore like to have it in a cleaner format. The messages are stored in the folder “messages”. Just copy this folder into your working directory.

I’ve written you a short script that turns the HTML files into one single csv file. Just place the file 'html_to_csv.py' in the same directory of the message folder, go to your terminal and run:

```
python html_to_csv.py
```

It will take a few seconds and create the csv file as “fb_data.csv”. Now you have the data in as a csv file with the following variable names: 

* message_id
* conversation_id
* conversation_name 
* time
* date
* day
* plattform
* text

## 3, Generate basic features 

With this data one can already do some basic analysis, such as frequency per time, frequencies per friends, etc. 
However for more interesting analysis, it makes sense to generate some features for more in depth analysis of your relationships and their development over time. To generate a few more features, just run the second script. (Make sure the data set is present, and it has the right filename 'fb_data.csv'). The following features will be added: 

* word_count: number of words in a message
* question_asked: indicates, whether a question was asked
* group_conversation: flags if more than 2 people are in the conversation
* image_sent: flag if a message was an image
* sticker_sent: flag if a message was a sticker

###### Features work in progress 
* response_time: how much time (Work in progress, will be available soon)
* new_conversation: binary, 1 if the last conversation is more than 24 hours ago (Work in progress, will be available soon)
* sentiment: by using the NLTK library (Work in progress, will be available soon)
* topic: what topics does the message contain (Work in progress, will be available soon)

To create these features just run: 

```
python generate_features.py
```

The new csv file "fb_data_features.csv" will be added to the folder

## 4, Some basic questions 

When opening the file, you might need to specify the lineterminator to be '\n'. (E.g. pd.read_csv(fname, lineterminator='\n')). If you don't specify it, this might cause troubles... 

You can now use these features to answer some basic questions, by loading the data into your favored analytics environment. Here are some suggestions of analysis you may want to do: 
- Who are the people you have chatted the most with? 
- How did the people change over time you chatted with? 
- Who are you interested in, and who is more interested in you? (By looking at the number of questions asked) 
- ... 

Have fun exploring your social interactions - and let me know what you make out of it! 

I hope this tutorial helped you to reveal some insights from your chat histories. Because messenger data is only one source of your chat data and does not give a complete picture of your texting interaction, I am planning to also provide you with a tutorial with how you get your WhatsApp data and iMessage data and integrate it with your Facebook chats. Stay tuned... 

Note: Please cite this tutorial if you use it for a project. :-) 



