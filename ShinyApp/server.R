# Facebook Analysis Tool
library(shiny)
library(DT)

shinyServer(function(input, output, session) {
  source('init.R')
  #source("analysis/ticketpool_html.R"

  observeEvent(input$fb_filepath,{
    output$loading <- renderPrint('Loading Data - this may take a few minutes')
  })
  
  observeEvent(input$fb_filepath,{

    filepath <- input$fb_filepath
    fb_datapath <- filepath$datapath
    facebook <<- read.csv(fb_datapath, encoding = 'UTF-8')
    
    facebook$timestamp <- as.POSIXct(strptime(x = as.character(facebook$timestamp),
                                              format = "%Y-%m-%d %H:%M:%S"))
  
    # select top 50 friends 
    top_users <- facebook %>% filter(!is.na(user)& user != "" & user!= " ") %>% group_by(user) %>% 
      summarize(word_sum = sum(msg_word_count)) %>% 
      arrange(desc(word_sum))
    top_users <- head(top_users,50)
    top_users$Gender <- "unclassified"
    top_users$Friend_Group <- "unclassified"
    top_users$Relationship <- "unclassified"
    top_users <- subset(top_users, select = c("user","Gender", "Friend_Group","Relationship"))
    
    #render as table
    output$table <- renderRHandsontable({rhandsontable(top_users)
        })
    
    }) 
    
    #### Save the table and prepare Data for the plots#### 
    observeEvent(input$save, {
      
      #filepath <- input$fb_filepath
      #fb_datapath <- filepath$datapath
      #facebook <- read.csv(fb_datapath)
      
      facebook$timestamp <- as.POSIXct(strptime(x = as.character(facebook$timestamp),
                                                format = "%Y-%m-%d %H:%M:%S"))
      # filter outlier (erroneuos data)
      facebook <- facebook[facebook$timestamp > strptime(x = as.character('2005-01-01 01:00:00'), format = "%Y-%m-%d %H:%M:%S"),]
      facebook <- facebook %>% filter(!is.na(user)& user != "" & user!= " ") 
      
      top_users <- hot_to_r(input$table)
      facebook <- facebook %>% group_by(user) %>% left_join(top_users)
      
      #### Save as csv #### 
      
      write.csv(facebook, file = "fb_data_annotated.csv")
      
      #### Data Processing #### 
      facebook$msg_word_count <- as.numeric(facebook$msg_word_count)
      
      facebook$Gender <- factor(facebook$Gender)
      facebook$Friend_Group <- factor(facebook$Friend_Group)
      facebook$Relationship <- factor(facebook$Relationship)
      
      facebook[is.na(facebook)] <- "unclassified"
      
      sentiment.comparison <- facebook %>% filter(photo_sent==0) %>%
        mutate(date2=as.Date(timestamp))
      
      fb_others <- facebook %>% filter(user != input$name & Friend_Group != 'drop' & group_conversation == 0 & sticket_sent == 0)
      fb_others$year = floor_date(fb_others$timestamp, "year")
      
      levels(fb_others$Gender) <- c('Female','Male', 'Uncategorized')
      
      fb_me <- facebook %>% filter(user == input$name & Friend_Group != 'drop')
      
      years <- sort(unique(substring(fb_others$year,1,4)))
      
      updateSelectInput(session, "plot1_year", choices = years)
      updateSelectInput(session, "plot3_convers", choices = head((top_users %>% filter( user != input$name & Friend_Group != 'drop'))$user,10))
      
      fb_me$conversation_init <- as.integer(fb_me$conversation_init)
      fb_me$question_flag <- as.numeric(fb_me$question_flag)
      fb_me$Gender <- as.numeric(fb_me$Gender)
     
    
    #### Make the plots ####
      
    output$plot1 <- reactivePlot(function() {
      
      # check for the input variable
      inputyear = as.character(input$plot1_year)
      year_filter = as.Date(paste(inputyear, "-01-01", sep = "", "%Y-%m-%d"))
      
      inputcat = as.character(input$plot1_cat)
      if (inputcat == "Gender") {
        myColors1 <- brewer.pal(3,"Set1")
        names(myColors1) <- levels(fb_others$Gender)
        colScale <- scale_colour_manual(name = "Gender",values = myColors1)
      }
      if( inputcat == "Friend Group"){
        myColors1 <- brewer.pal(9,"Set1")
        names(myColors1) <- levels(fb_others$Friend_Group)
        colScale <- scale_colour_manual(name = "Friend_Group",values = myColors1)
        inputcat <- "Friend_Group"
      }
      if( inputcat == "Relationship"){
        myColors1 <- brewer.pal(9,"Set1")
        names(myColors1) <- levels(fb_others$Relationship)
        colScale <- scale_colour_manual(name = "Relationship",values = myColors1)
      }
      
      s = fb_others %>%  filter(year == year_filter) %>%group_by(user) %>% summarize(count = n())  %>% arrange(desc(count))
      x = head(s$user,25)
      
      
      p <- fb_others %>% filter(year == year_filter) %>% group_by(user) %>%
        filter(user %in% x)  %>%
        ggplot(aes(x=reorder(user,user, FUN=length), fill = eval(parse(text=inputcat)))) +
        geom_bar(stat="count") +
        coord_flip()+
        ggtitle(paste('Top Users in ',inputyear))+
        labs(fill = inputcat)+
        xlab('Name')+
        ylab('Number of messages')+
        colScale
      print(p)
      
    })
  

    #### Make Plot 2 ####
    plot2_df <- fb_me %>% group_by(month=floor_date(timestamp, "month")) %>%
      summarize(word_count_avg = mean(msg_word_count),
                questions_rate = mean(question_flag),
                initialized_rate = mean(conversation_init),
                emojis_rate = sum(emoji_count)/ sum(msg_word_count), 
                group_conversation_rate = mean(group_conversation),
                no_photos = sum(photo_sent))
    
    output$plot2 <- reactivePlot(function() {
    # check for the input variable
    input2cat_raw = as.character(input$plot2_cat)
    input2cat = gsub(" ","_",input2cat_raw)
    
    p2 <- plot2_df %>%
      ggplot(aes(month, eval(parse(text=input2cat)))) +
          geom_bar(stat='identity') + 
          geom_smooth()+
          ggtitle(input2cat)+
          xlab('Time')+
          ylab(input2cat_raw)
    print(p2)
    })
  
    #### Make Plot 3 ####
    
    output$plot3 <- reactivePlot(function() {
  
      p3 <- ggplot(sentiment.comparison %>% filter(conversation_name==gsub(" ", "_", input$plot3_convers)), aes(x=date2, y=msg_sentiment ,color=user)) + 
        geom_point(alpha=.5) +
        geom_smooth(span=0.01) +
        ggtitle("Trend in Positivity") +
        xlab('Time')+
        ylab('Positivity of the message')
      print(p3)
    })
  
    })
})




