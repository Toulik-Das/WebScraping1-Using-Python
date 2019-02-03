import requests
from bs4 import BeautifulSoup
from logger_impl import *
import MongoDao
import pandas as pd
import time

payload = {'key': 'ac9e8cf2dec81949d9ee1235ed6ae3fb', 'url':
'https://httpbin.org/ip'}



def scrapData(scorecardSoup, matchId, matchDesc, matchTypeText, pageUrl, season, Date, venue):

    #pageUrl = "http://www.espncricinfo.com/series/11422/scorecard/858491/bangladesh-vs-pakistan-only-t20i-pakistan-tour-of-bangladesh-2015"
    try:
        """page = urllib.request.urlopen(pageUrl)

        ## get match-id and match-name from url
        pageUrlArr = pageUrl.split('/')
        matchId = pageUrlArr[len(pageUrlArr ) - 2]
        matchDesc = pageUrlArr[len(pageUrlArr ) - 1] """
        #soup = BeautifulSoup(page, 'html.parser')
        soup = scorecardSoup

        #print("page html: ", soup.prettify())
        scorecardDiv = soup.find_all('article', class_='sub-module scorecard')
        playerBatsmanDict = {}
        playerBowlerDict = {}
        batsmanScorecardParam = ['run_scored', 'balls_faced','M', '4s', '6s', 'strike_rate']
        bowlerScorecardParam = ['O', 'M', 'R', 'W', 'Econ', 'WD', 'NB']

        teamList = []
        teamIDList = []
        inningsTeam = []
##        print(len(scorecardDiv))
        #creating playing team list
        for scorecardVal in scorecardDiv:
            #print(scorecardVal)
            team = scorecardVal.find('h2').get_text()
            if matchTypeText == 'Tests':
                team = str(team).replace('1st Innings', '').replace('2nd Innings', '')
            else:
                team = str(team).replace('Innings', '')
            if team.strip() in teamList:
                break
            teamList.append(team.strip())
        count = {teamList[0]:0,teamList[1]:0}

        for team in teamList:
            word = team.split(' ')
            if len(word) == 1:
                id_ = team[:3]
                teamIDList.append(id_)
            else:
                id_ = ''
                for x in word:
                    id_ = id_ + x[0]
                teamIDList.append(id_)

        for scorecardVal in scorecardDiv:
            team = scorecardVal.find('h2').get_text()
            inn = ''
            if matchTypeText == 'Tests':
                inn = ' '.join(str(team).split(' ')[-2:])
                team = str(team).replace('1st Innings', '').replace('2nd Innings', '')
            else:
                team = str(team).replace('Innings', '')
            team = team.strip()
            count[team] += 1
##            print(count)
            logger.info("team: " + team)
            #print("batsman div: ", scorecardVal)
            batsmanList = scorecardVal.find_all('div', class_='wrap batsmen')
            batsmanListNotBatted = scorecardVal.find('div', class_='wrap dnb').find_all('a')
##            for bt in batsmanListNotBatted:
##                print(bt.get('href'))
##                print(bt.get_text())
            for batsman in batsmanList:
                batsmanDict = {}
                #print("batsman data: ", batsman)
                batsmanAnchor = batsman.find('div', class_="cell batsmen").find('a')
                batsmanLink = batsmanAnchor.get('href')
                batsmanName = batsmanAnchor.get_text()

                batsmanLinkArr = str(batsmanLink).split('/')
                cricInfoBatsmanId = batsmanLinkArr[len(batsmanLinkArr) - 1]
                cricInfoBatsmanId = str(cricInfoBatsmanId).replace('.html', '')
                #print("batsman Name: ", batsmanName, " batsmanId: ", cricInfoBatsmanId)
                batsmanDict['short_name'] = batsmanName
                batsmanDict['player_cric_info_link'] = batsmanLink
                batsmanDict['team'] = team
            

                #print("batsmanDiv: ", batsmanDiv.get_text())
                try:
                    commentry = batsman.find('div', class_="cell commentary").find('a').get_text()
                    batsmanDict['commentry'] = commentry
                except AttributeError as ae:
                    batsmanDict['commentry'] = ''

                #print("batsman commentry: ", commentry)
                #print("commentryDiv: ", commentryDiv.get_text())
                batsmanStatsList = batsman.find_all('div', class_="cell runs")
                ctr = 0
                tempList = []
                for batsmanStats in batsmanStatsList:
                    #print("anchor: ", batsmanStats.get_text())
                    #param = batsmanScorecardParam[ctr]
                    #ctr += 1
                    #batsmanDict[param] = batsmanStats.get_text()
                    tempList.append(batsmanStats.get_text())
                     
                if len(tempList) == 6:
                    batsmanDict['run_scored'] = tempList[0]
                    batsmanDict['balls_faced'] = tempList[1]
                    batsmanDict['M'] = tempList[2]
                    batsmanDict['4s'] = tempList[3]
                    batsmanDict['6s'] = tempList[4]
                    batsmanDict['strike_rate'] = tempList[5]
                else:
                    batsmanDict['run_scored'] = tempList[0]
                    batsmanDict['balls_faced'] = tempList[1]
                    batsmanDict['M'] = '-'
                    batsmanDict['4s'] = tempList[2]
                    batsmanDict['6s'] = tempList[3]
                    batsmanDict['strike_rate'] = tempList[4]

                
                
                batsmanDict['innings'] = inn
                key = cricInfoBatsmanId# + "_" + team
                if matchTypeText == 'Tests':
                    key = key + inn[0]
                playerBatsmanDict[key] = batsmanDict
            
                #break
##            print(batsmanListNotBatted)

            for batsmen in batsmanListNotBatted:
                    batsmanDict={}
                    batsmanLink = batsmen.get('href')
                    batsmanName = batsmen.get_text()
                    batsmanLinkArr = str(batsmanLink).split('/')
                    cricInfoBatsmanId = batsmanLinkArr[len(batsmanLinkArr) - 1]
                    cricInfoBatsmanId = str(cricInfoBatsmanId).replace('.html', '')
                    batsmanDict['short_name'] = batsmanName
                    batsmanDict['player_cric_info_link'] = batsmanLink
                    batsmanDict['team'] = team
                    batsmanDict['run_scored'] = '-'
                    batsmanDict['balls_faced'] = '-'
                    batsmanDict['M'] = '-'
                    batsmanDict['4s'] = '-'
                    batsmanDict['6s'] = '-'
                    batsmanDict['strike_rate'] = '-'
                    batsmanDict['innings'] = inn
                    key = cricInfoBatsmanId# + "_" + team
                    #print('id : ',cricInfoBatsmanId)
                    #print('key : ',key)
                    #print(batsmanDict)
                    if matchTypeText == 'Tests':
                        key = key+inn[0]
                    playerBatsmanDict[key] = batsmanDict
                    #print('Dict added : ',playerBatsmanDict[key])

            bowlersTR = scorecardVal.find('tbody').find_all('tr')
            #print("bowler section: ", bowlersTR)
            for bowlerRow in bowlersTR:
                bowlersTD = bowlerRow.find_all('td')
                bowlerAnchor = bowlersTD[0].find('a')
                bowlerLink = bowlerAnchor.get('href')
                bowlerName = bowlerAnchor.get_text()
                #print("bowler name: ", bowlerName, " link: ", bowlerLink)
                bowlerLinkArr = str(bowlerLink).split('/')
                cricInfoBowlerId = bowlerLinkArr[len(bowlerLinkArr) - 1]
                cricInfoBowlerId = str(cricInfoBowlerId).replace('.html', '')
                logger.info("bowlersTD: " + str(bowlersTD))
                logger.info("length bowlersTD: " + str(len(bowlersTD)))
                if len(bowlersTD) ==  13:
                    overs = bowlersTD[2].find(text=True)
                    maidens = bowlersTD[3].find(text=True)
                    runs = bowlersTD[4].find(text=True)
                    wickets = bowlersTD[5].find(text=True)
                    economy = bowlersTD[6].find(text=True)
                    dotBalls = bowlersTD[7].find(text=True)
                    ballerFours = bowlersTD[8].find(text=True)
                    ballerSixes = bowlersTD[9].find(text=True)
                    wideBalls = bowlersTD[10].find(text=True)
                    noBalls = bowlersTD[11].find(text=True)
           
                else:
                    overs = bowlersTD[2].find(text=True)
                    maidens = bowlersTD[3].find(text=True)
                    runs = bowlersTD[4].find(text=True)
                    wickets = bowlersTD[5].find(text=True)
                    economy = bowlersTD[6].find(text=True)
                    dotBalls = 0
                    ballerFours = 0
                    ballerSixes = 0
                    wideBalls = bowlersTD[7].find(text=True)
                    noBalls = bowlersTD[8].find(text=True)
                    
##                print('o'+overs)
##                print(maidens)
##                print(runs)
##                print(wickets)
##                print(economy)
##                print(dotBalls)
##                print(ballerFours)
##                print(ballerSixes)
##                print(wideBalls)
##                print(noBalls)        
                   
                
                #['O', 'M', 'R', 'W', 'Econ', 'WD', 'NB']
                bowlerDict = {}
                bowlerDict['short_name'] = bowlerName
                bowlerDict['player_cric_info_link'] = bowlerLink
                if '.' in overs:
                    oversArr = overs.split('.')
                    totalBalls: int = int(oversArr[0]) * 6
                    totalBalls += int(oversArr[1])
                else:
                    totalBalls: int = int(overs) * 6

                # getting the bowling team name
                if team == teamList[0]:
                    bowlingTeam = teamList[1]
                else:
                    bowlingTeam = teamList[0]

                bowlerDict['team'] = bowlingTeam
                bowlerDict['balls_bowled'] = totalBalls
                bowlerDict['maiden_overs'] = maidens
                bowlerDict['runs_given'] = runs
                bowlerDict['wicket'] = wickets
                bowlerDict['econ'] = economy
                bowlerDict['dot_delivery'] = dotBalls
                bowlerDict['four_delivery'] = ballerFours
                bowlerDict['six_delivery'] = ballerSixes
                bowlerDict['wide_balls'] = wideBalls
                bowlerDict['no_balls'] = noBalls
                bowlerDict['innings'] = inn
                #print(overs, maidens, runs, wickets, economy, wideBalls, noBalls)
                key = cricInfoBowlerId# + "_" + team
                if matchTypeText == 'Tests':
                    key = key+inn[0]
                playerBowlerDict[key] = bowlerDict

        #print("batsmanDict: ", playerBatsmanDict)
        #print("bowlerDict: ", playerBowlerDict)

        if matchTypeText == 'Tests' and ((count[teamList[0]] == 2 and count[teamList[1]] == 1) or (count[teamList[0]] == 1 and count[teamList[1]] == 2)):
            # if 
            missing = ''
            if count[teamList[0]] == 1:
                missing = teamList[0]
            elif count[teamList[1]] == 1:
                missing = teamList[1]

            for scorecardVal in scorecardDiv:
                team = scorecardVal.find('h2').get_text()
                inn = ' '.join(str(team).split(' ')[-2:])
                team = str(team).replace('1st Innings', '').replace('2nd Innings', '')
                team = team.strip()
                if team == missing:
                    batsmanList = scorecardVal.find_all('div', class_='wrap batsmen')
                    batsmanListNotBatted = scorecardVal.find('div', class_='wrap dnb').find_all('a')
                    for batsman in batsmanList:
                        batsmanDict = {}
                        batsmanAnchor = batsman.find('div', class_="cell batsmen").find('a')
                        batsmanLink = batsmanAnchor.get('href')
                        batsmanName = batsmanAnchor.get_text()
                        batsmanLinkArr = str(batsmanLink).split('/')
                        cricInfoBatsmanId = batsmanLinkArr[len(batsmanLinkArr) - 1]
                        cricInfoBatsmanId = str(cricInfoBatsmanId).replace('.html', '')
                        batsmanDict['short_name'] = batsmanName
                        batsmanDict['player_cric_info_link'] = batsmanLink
                        batsmanDict['team'] = team
                        batsmanDict['run_scored'] = '-'
                        batsmanDict['balls_faced'] = '-'
                        batsmanDict['M'] = '-'
                        batsmanDict['4s'] = '-'
                        batsmanDict['6s'] = '-'
                        batsmanDict['strike_rate'] = '-'
                        batsmanDict['innings'] = '2nd Innings'
##                      print(batsmanList)
                        key = cricInfoBatsmanId
                        batsmanDict['commentry'] = '-'
                        if matchTypeText == 'Tests':
                            key = key+'2'
                        playerBatsmanDict[key] = batsmanDict

                        for batsmen in batsmanListNotBatted:
                            batsmanLink = batsmen.get('href')
                            batsmanName = batsmen.get_text()
                            batsmanLinkArr = str(batsmanLink).split('/')
                            cricInfoBatsmanId = batsmanLinkArr[len(batsmanLinkArr) - 1]
                            cricInfoBatsmanId = str(cricInfoBatsmanId).replace('.html', '')
                            batsmanDict['short_name'] = batsmanName
                            batsmanDict['player_cric_info_link'] = batsmanLink
                            batsmanDict['team'] = team
                            batsmanDict['run_scored'] = '-'
                            batsmanDict['balls_faced'] = '-'
                            batsmanDict['M'] = '-'
                            batsmanDict['4s'] = '-'
                            batsmanDict['6s'] = '-'
                            batsmanDict['strike_rate'] = '-'
                            batsmanDict['innings'] = '2nd Innings'
                            key = cricInfoBatsmanId# + "_" + team
                            if matchTypeText == 'Tests':
                                key = key+'2'
                            playerBatsmanDict[key] = batsmanDict
                 
        # checking batsman in bowler map, if found add them in playerBatsmanDict
        if matchTypeText == 'Tests':
            for batsmanKey, batsmanValue in playerBatsmanDict.items():
                if batsmanKey in playerBowlerDict:
                    if playerBatsmanDict[batsmanKey]['innings'] == playerBowlerDict[batsmanKey]['innings']:
                        bowlerData = playerBowlerDict[batsmanKey]
                        fianlDict = {**batsmanValue, **bowlerData}
                        playerBatsmanDict[batsmanKey] = fianlDict
                        del playerBowlerDict[batsmanKey]
        else:                
            for batsmanKey, batsmanValue in playerBatsmanDict.items():
                if batsmanKey in playerBowlerDict:
                    bowlerData = playerBowlerDict[batsmanKey]
                    fianlDict = {**batsmanValue, **bowlerData}
                    playerBatsmanDict[batsmanKey] = fianlDict
                    del playerBowlerDict[batsmanKey]

##        print("after merging batsmanDict: ", playerBatsmanDict)
##        print("after merging bowlerDict: ", playerBowlerDict)
        playerFinalDict = {**playerBatsmanDict, **playerBowlerDict}

##        
##        print("Player final dict: ", playerFinalDict)
        
        ##TODO mark player as 'Batsman', 'Bowler', 'WicketKeeper', 'All rounder'
        pno = 0
        for playerKey, playerValue in playerFinalDict.items():
            flag = True
            while flag:
                try:
                    pno+=1
                    if pno <= 5:
                        shortName = playerValue['short_name']
                        playerDict = playerFinalDict[playerKey]              
                        if '†' in shortName:
                        #checking for WicketKeeper positio
                            playerDict['Position'] = "WK"
                        elif 'econ' in playerDict:
                            playerDict['Position'] = "Bowler"
                        else:
                            playerDict['Position'] = "Batsman"
                        #print('Pno : ' + str(pno))
                        playerDict['match_id'] = matchId + '_' + playerDict['innings'][:2]
                        playerDict['match_desc'] = matchDesc
                        playerDict['match_type_text'] = matchTypeText +' '+ playerDict['innings']
                        playerDict['season'] = season
                        playerDict['MatchURL'] = pageUrl
                        playerDict['Match_start_Date'] = Date
                        playerDict['Venue'] = venue
                        if playerDict['team'] == teamList[0]:
                            playerDict['TeamID'] = teamIDList[0]
                            playerDict['OpponentID'] = teamIDList[1]
                        else:
                            playerDict['TeamID'] = teamIDList[1]
                            playerDict['OpponentID'] = teamIDList[0]
                        url = playerDict['player_cric_info_link']
                        page = requests.get(url,params = payload).text
                        soup = BeautifulSoup(page,'html.parser')
                        pees = soup.find_all('p',class_='ciPlayerinformationtxt')
                        val = []
                        key = []
                        for pee in pees:
                            key.append(pee.find('b').get_text())
                            val.append(pee.find('span').get_text())
                            if "Full name" in key:
                                playerDict['Player_Full_Name'] = val[key.index("Full name")]
                            else:
                                playerDict['Player_Full_Name'] = '-'
                            if 'Born' in key:
                                playerDict['date,place_of_birth'] = val[key.index('Born')].replace('\n','').strip()
                            else:
                                playerDict['date,place_of_birth'] = '-'
                            if 'Nickname' in key:
                                playerDict['Player_Nickname'] = val[key.index('Nickname')]
                            else:
                                playerDict['Player_Nickname'] = '-'
                          
                                
                    ##            playerDict['Player_Full_Name'] = data[0]
                    ##            playerDict['data,place_of_birth'] = data[1][1:]
                    ##            if data[4] == None:
                    ##                playerDict['Player_Nickname'] = '-'
                    ##            else:
                    ##                playerDict['Player_Nickname'] = data[4]
                                    

                                #DOB_PlaceOB = soup.fin_next('p',class_='ciPlayerinformationtxt').find('span').get_text()
                               
                                    
                               
                                # below adding missed parameters in player's dict with default 0 value
                        if not 'run_scored' in playerDict:
                            playerDict['run_scored'] = "-"

                        if not 'balls_faced' in playerDict:
                            playerDict['balls_faced'] = "-"

                        if not 'strike_rate' in playerDict:
                            playerDict['strike_rate'] = "-"

                        if not 'balls_bowled' in playerDict:
                            playerDict['balls_bowled'] = "-"

                        if not 'maiden_overs' in playerDict:
                            playerDict['maiden_overs'] = "-"
                        if not 'runs_given' in playerDict:
                            playerDict['runs_given'] = "-"
                        if not 'wicket' in playerDict:
                            playerDict['wicket'] = "-"
                        if not 'econ' in playerDict:
                            playerDict['econ'] = "-"
                        if not 'wide_balls' in playerDict:
                            playerDict['wide_balls'] = "-"
                        if not 'no_balls' in playerDict:
                            playerDict['no_balls'] = "-"
                        flag = False
                    else:
                        pno = 0
                        time.sleep(10)
                    
                            
                except Exception as e:
                    print('pausing scrapping for 5 mins : '+str(e))
                    time.sleep(300)
                    flag = True
                    

 
       # print("Player final dict 2: ", playerFinalDict)

        for key, val in playerFinalDict.items():
            val['cric_info_id'] = key
            val['_id'] = key + "-" + matchId
            #print(key)
            #MongoDao.insertToPlayerStats(val)
        

        logger.info("players inserted successfully for url: " + pageUrl)
        #MongoDao.insertToProcessedUrls(pageUrl)
        #print(playerFinalDict.key())
        df = pd.DataFrame(playerFinalDict)
        return df

    except Exception as e:
        logger.error("ERROR while processing URL: " + pageUrl)
        logger.exception("message")
        print("Scrapping : "+str(e))
        #print(("ERROR while processing URL: " + pageUrl))



#scrapODI_T20Data('', '', '', "T20", '', '')
