import requests
from bs4 import BeautifulSoup
from logger_impl import *
import scrap_players
import time
import re
import pandas as pd
import process_csv
#import process_csv as pc

payload = {'key': 'ac9e8cf2dec81949d9ee1235ed6ae3fb', 'url':
'https://httpbin.org/ip'}

def Generic(season):
    pageUrl = "http://www.espncricinfo.com/ci/engine/series/index.html?season="+season+";view=season"
    page = requests.get(pageUrl, params = payload).text
    soup = BeautifulSoup(page, 'html.parser')
    print('Starting for season : ' + season)
    #print("page html: ", soup.prettify())
    matchSectionDiv = soup.find('div', class_='match-section-head')
    ##print(matchSectionDiv.prettify())
    scorecardCtr = 1
    doneTest = 0
    mainDF = []
    while True:

        matchTypeText = ""
        try:
            #print(matchSectionDiv.prettify())
            matchTypeText = matchSectionDiv.find('h2').get_text()
            logger.info("matchTypeText: " + str(matchTypeText))

            if "Tests" == matchTypeText and doneTest:
                # next Div of Match Section Head, like Test, ODI International
                matchSectionDiv = matchSectionDiv.findNext('div', class_="match-section-head")
                continue

           
            seriesSummarySection = matchSectionDiv.findNext('section', class_="series-summary-wrap")
            allSeriesSections = seriesSummarySection.find_all('section', class_="series-summary-block")
            
            for seriesSection in allSeriesSections:
                seriesFullUrl = ""
                try:
                    seriesUrl = seriesSection['data-summary-url']
                    seriesFullUrl = "http://www.espncricinfo.com" + seriesUrl
                    
                    # seriesFullUrl = http://www.espncricinfo.com/ci/engine/match/index/series.html?series=10233
                    seriesPage = requests.get(seriesFullUrl, params = payload).text
                    seriesSoup = BeautifulSoup(seriesPage, 'html.parser')
                    Date = seriesSoup.find('span',class_ = 'bold').get_text()
                    venue = seriesSoup.find('span',class_='match-no').get_text()
                    venue = venue.strip().split(' ')[3:]
                    venue = ' '.join(venue)
                    scorecardElements = seriesSoup.find_all(text="Scorecard")

          
                    for scorecardElement in scorecardElements:
                        scorecardUrl = ""
                        try:                           
                            scorecardParent = scorecardElement.parent
                            scorecardUrl = scorecardParent['href']

                            logger.info("scorecardCtr: " + str(scorecardCtr))
                            scorecardCtr += 1
                            scorecardPage = requests.get(scorecardUrl,params = payload).text
                            scorecardSoup = BeautifulSoup(scorecardPage, 'html.parser')
                            accordianDivs = scorecardSoup.find_all('div', class_="accordion-header")

                            isTest1stInning = False
                            for accordianDiv in accordianDivs:
                                value = accordianDiv.find(text=re.compile('1st Innings'))
                                logger.info("accordianDiv: " + str(accordianDiv))
                                logger.info("accordianDiv value: " + str(value))
                                if value != None and '1st Innings' in value:
                                    isTest1stInning = True

                            
                            scorecardUrlArr = scorecardUrl.split('/')
                            urlMatchId = scorecardUrlArr[len(scorecardUrlArr) - 2]
                            urlMatchDesc = scorecardUrlArr[len(scorecardUrlArr) - 1]
                            logger.info("urlMatchDesc: " + str(urlMatchDesc))
                            # checking if match is Test or Other
##                            if 'test' in urlMatchDesc and isTest1stInning and not doneTest:
##                                logger.info("this is TEST match: " + str(scorecardUrl))
##                                #time.sleep(70)
##                                doneTest = True
##                                df = scrap_players_odi.scrapData(scorecardSoup, urlMatchId, 
##                                    urlMatchDesc, matchTypeText, scorecardUrl, season, Date, venue)
##
##                                df = df.transpose()
##                                mainDF.append(df)
##                                #print('main DF List length in Test : ',len(mainDF))
##                               
##                            else:
##                                logger.info("this is ODI or T20 match: " + str(scorecardUrl))
##
##                                df = scrap_players_odi.scrapData(scorecardSoup, urlMatchId, 
##                                    urlMatchDesc, matchTypeText, scorecardUrl, season, Date, venue)
##                                df = df.transpose()
##                                mainDF.append(df)

                            
##                            if doneTest == 4 and matchTypeText == 'Tests': #for sample data
##                                continue
##                            doneTest+=1#for sample data

                            df = scrap_players.scrapData(scorecardSoup, urlMatchId, 
                                 urlMatchDesc, matchTypeText, scorecardUrl, season, Date, venue)

                            df = df.transpose()
                            mainDF.append(df)
                            print('DFs collected for '+season +' so far : ',len(mainDF))
##                            if len(mainDF) == 6: #for sample data
##                                return mainDF

                            
                        except Exception as scoreCardEx:
                            logger.error("Exception for Scorecard URL: " + str(scorecardUrl))
                            logger.exception:("message")
            
                            print('scorecard : '+str(scoreCardEx)+'url : '+str(scorecardUrl))
                            time.sleep(10)


                except Exception as seriesEx:
                    logger.error("Exception for seriesFullUrl: " + str(seriesFullUrl))
                    logger.exception("message")
                    print('series :'+str(seriesEx))
                    #print("Exception for seriesFullUrl: " + str(seriesFullUrl))
                    time.sleep(10)

        except Exception as matchTypeEx:
            logger.error("Exception for matchTypeText: " + str(matchTypeText))
            logger.exception("message")
            print('outer : '+str(matchTypeEx))
            #print("Exception for matchTypeText: " + str(matchTypeText))
            time.sleep(10)

        # next Div of Match Section Head, like Test, ODI International

        matchSectionDiv = matchSectionDiv.findNext('div', class_="match-section-head")
        if matchSectionDiv == None:
            break

            
    return mainDF
    #print(mainDFD.head(10))
##    reorder_ = ["PlayerID", "TeamID", "MatchID", "OpponentID", "PlayerProfileURL",
##                         "MatchURL", "MatchFormat", "MatchStartDate", "MatchVenue", "TeamName", "PlayerName", "PlayerFullName",
##                         "Player Date,Place of Birth", "PlayerNickName", "B_Bat", "R_Bat", "4s", "6s",
##                         "SR_Bat", "BallsBowled","RunsGiven", "MaidenOvers", "W_Bow", "ER_Bow", "Wide_Bow",
##                         "No_Bow", "catches", "stumped","run_out"]
##    mainDFD = mainDFD[reorder_]


##seasons = [str(val) for val in range(2017,2008,-1)]
##print(seasons)
seasons = ['2018/19']
#df = pd.DataFrame()#complete 10 years
for season in seasons:
    file = season
    l = Generic(season)
    local = pd.DataFrame()#for particular year
    for d in l:
        #print(d.head(3)['match_type_text'])
       # df = df.append(d)
        local = local.append(d)
    local.fillna('-',inplace = True)
    local.to_csv(season+'.csv')
    #process_csv.Process_CSV(season)

    
#df.fillna('-',inplace = True)
#df.to_csv('10yrs.csv')
#process_csv.Process_CSV('10yrs')
##df = pd.DataFrame()
##for file in seasons:
##    d = pd.read_csv(file+'.csv')
##    df = df.append(d)
##df.to_csv('10yrsSample.csv')
##

    
