#Ticket Analysis Tool
library(shiny)
library(DT)
library(shinyjs)
library(rhandsontable)

options(shiny.maxRequestSize=100*1024^2)

years <- c('2000')

fluidPage(
  title = 'Facebook Analysis Tool',
  fluidRow(
    column(1,''),
    column(10, h1('Facebook Analysis Tool'))
  ),
  fluidRow(
    column(1,''),
    column(10, h6('by Jan-Felix Schneider, Yuriy Loukachev, Brian Allen - Data Science Institute Columbia University'))
  ),
  hr(),
  fluidRow(
    column(1,''),
    column(10, p('This tool should provide you a way to analyze your own facebook data. 
                 Who are you chatting with the most? 
                 How did your chatting behaivor change? 
                 How has your conversation with certain friends evolve? 
                 Find out by just following the steps below... '))
    ),
  fluidRow(
    column(1,''),
    column(5,h4("Step 1: Load your data"))
  ),
  fluidRow(
    column(1,''),
    column(10,p("Bevore loading your data you should prepare it for this tool. For this just following the following github tutorial https://github.com/J-FSchneider/FbChatViz so that you have the 'fb_data_features.csv' file present. Once you selected the file, it will take a few seconds to loead the data into the tool...  "))
  ),

  fluidRow(
    column(1,''),
    column(3, fileInput('fb_filepath',"Select your data", accept = c(
      "text/csv",
      "text/comma-separated-values, text/plain",
      ".csv"))),
    column(3, textInput('name', 'Type in your Facebook name' )),
    column(3, conditionalPanel(condition="$('html').hasClass('shiny-busy')",
                               tags$div("     Your Data is being loaded... Please wait a few seconds")))
  ),
  fluidRow(
    column(1,''),
    column(10,h4("Step 2: Annotate your Data"))
  ),
  fluidRow(
    column(1,''),
    column(10,p("In this step we will be enriching your data a little bit. The following table shows the top 50 people you chatted the most with. You can edit the table, so please type in some more information about them. 
                Gender: 0 for male and 1 for female
                Friend Group: try to choose 3-5 groups you want to classify your friends by (for example: work, university, high-school, hometown, etc. )
                Relationship: Try to castegorize your friends into 3-5 relationship groups (for example: love interest, best friend, co-worker,...)
                You do not have to tag all people, but the more the nicer your graphs will be... ;-) "))
  ),
  fluidRow(
    column(1,''),
    column(10, rHandsontableOutput("table"))
  ),
  hr(),
  fluidRow(
    column(1,''),
    column(10,p("Once you're done just hit save! The new annotated dataset will be stored at 'fb_data_features_annotated.csv' "))
    ),
  fluidRow(
    column(1,''),
    column(3, actionButton('save', 'Save Annotations')),
    column(3, conditionalPanel(condition="$('html').hasClass('shiny-busy')",
                               tags$div("     Your Data is being processed... Please wait a few seconds")))
  ),
  hr(),
  fluidRow(
    column(1,h3('')),
    column(10,h4('Step 3: Who are you chatting with?'))
  ),
  fluidRow(
    column(1,''),
    column(5, selectInput('plot1_cat', 'Category', c("Gender", "Friend Group", "Relationship"))),
    column(5, selectInput('plot1_year', 'Year', years))
    ),
  fluidRow(
    column(1,''),
    column(10, p('In this graph you can check who you are checking with the most? It shows the top 25 users you chatted with in the selected year. '))
  ),
  fluidRow(
    column(1,''),
    column(10, plotOutput('plot1'))
  ),
  hr(),
  fluidRow(
    column(1,h3('')),
    column(10,h4('Step 4: Look at your behavior over time!'))
  ),
  fluidRow(
    column(1,''),
    column(5, selectInput('plot2_cat', 'Category', c("emojis rate","group conversation rate", "questions rate", "word count avg", "initialized rate", "no photos")))
  ),
  fluidRow(
    column(1,''),
    column(10, p('In this graph you can see how your behavior on FB changed over time...'))
  ),
  fluidRow(
    column(1,''),
    column(10, plotOutput('plot2'))
  ),
  hr(),
  fluidRow(
    column(1,h3('')),
    column(10,h4('Step 5: How are your relationships?'))
  ),
  fluidRow(
    column(1,''),
    column(10, p('In this graph you can check how your relationships have developed over time with the people you chatted the most with.  
                 Every point represents a message and the location shows the sentiment of your message. The line shows the running average of yours and the selected friends positiveness in your conversation. Note that if no line is shown, there is unfortunately not enought data to plot it... '))
  ),
  fluidRow(
    column(1,''),
    column(5, selectInput('plot3_convers', 'Conversation', choices=c('Friend1','Friend2')))
  ),
  fluidRow(
    column(1,''),
    column(10, plotOutput('plot3'))
  ),
  hr()
)
