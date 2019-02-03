import csv
from difflib import SequenceMatcher
import re
import string
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
from googlesearch import search
from collections import OrderedDict
#import unidecode
'''
['Twenty20 Internationals', 'One-Day Internationals', 'Twenty20','Tests 1st Innings','Tests 2nd Innings' ,
                                     'minor tour','tour','Youth One-Day Internationals','Other Twenty20 matches','Other one-day/limited-overs matches',
                                     'Women\'s Twenty20 Internationals','Women\'s One-Day Internationals','List A','First-class','Other matches']:
'''



def handleSubs(commentry,playerDict_n,teamKeys):
    name = ''
    if commentry.strip().startswith("run out "):
        name = ''.join(x for x in commentry if x in string.printable)
        name = name.split('[')[1].split(']')[0]
    else:
        name = ''.join(x for x in commentry if x in string.printable)
        try:
            name = name.split('(')[1].split(')')[0]
        except:
            print('web error',name)
            return None
            
##              print('-',name)
    playerInfo = {}
    search_url = ''
    url = ''
##    page = ''
##    soup = ''
##    pees = ''
##    try:
##        for url in search(name + ' ESPN cricket',tld = 'co.in',lang = 'en', num = 1,stop = 1):
##            search_url = url
##            break
##    except Exception as e:
##        print(e)
##        exit()
    for url in search(name + ' ESPN cricket',tld = 'com', num = 1,stop = 1):
            search_url = url
            break

    page = urllib.request.urlopen(search_url,timeout = 60)
##    opener = urllib.build_opener()
##    opener.addheaders = [('User-agent','Mozilla/5.0')]
##    response = opener.open(search_url)
##    page = response.read()
    soup = BeautifulSoup(page,'html.parser')
    pees = soup.find_all('p',class_='ciPlayerinformationtxt')
    val = []
    key = []
    
    for pee in pees:
        key.append(pee.find('b').get_text())
        val.append(pee.find('span').get_text())
       # print('url : '+search_url+'name : '+name)
       # print(key,val)
    playerInfo['short_name'] = name
    playerInfo['player_cric_info_link'] = search_url
    playerInfo['team'] = teamKeys
    cricInfoBatsmanId = str(search_url).split('/')[-1].replace('.html', '')
    playerInfo['_id'] = cricInfoBatsmanId + '-' + playerDict_n['match_id']
    playerInfo['TeamID'] = playerDict_n['OpponentID']
    playerInfo['OpponentID'] = playerDict_n['TeamID']
    playerInfo['run_scored'] = '-'
    playerInfo['balls_faced'] = '-'
    playerInfo['M'] = '-'
    playerInfo['4s'] = '-'
    playerInfo['6s'] = '-'
    playerInfo['strike_rate'] = '-'
    playerInfo['MatchURL'] = playerDict_n['MatchURL']
    playerInfo['match_id'] = playerDict_n['match_id']
    playerInfo['Match_start_Date'] = playerDict_n['Match_start_Date']
    playerInfo['Venue'] = playerDict_n['Venue']
    playerInfo['innings'] = playerDict_n['innings']
    playerInfo['commentry'] = '-'
    playerInfo['match_type_text'] = playerDict_n['match_type_text']
    if "Full name" in key:
        playerInfo['Player_Full_Name'] = val[key.index("Full name")]
    else:
        playerInfo['Player_Full_Name'] = '-'
    if 'Born' in key:
        playerInfo['date,place_of_birth'] = val[key.index('Born')].replace('\n','').strip()
    else:
        playerInfo['date,place_of_birth'] = '-'
    if 'Nickname' in key:
        playerInfo['Player_Nickname'] = val[key.index('Nickname')]
    else:
        playerInfo['Player_Nickname'] = '-'
    if not 'run_scored' in playerInfo:
        playerInfo['run_scored'] = "-"
    if not 'balls_faced' in playerInfo:
        playerInfo['balls_faced'] = "-"
    if not 'strike_rate' in playerInfo:
        playerInfo['strike_rate'] = "-"
    if not 'balls_bowled' in playerInfo:
        playerInfo['balls_bowled'] = "-"
    if not 'maiden_overs' in playerInfo:
        playerInfo['maiden_overs'] = "-"
    if not 'runs_given' in playerInfo:
        playerInfo['runs_given'] = "-"
    if not 'wicket' in playerInfo:
        playerInfo['wicket'] = "-"
    if not 'econ' in playerInfo:
        playerInfo['econ'] = "-"
    if not 'wide_balls' in playerInfo:
        playerInfo['wide_balls'] = "-"
    if not 'no_balls' in playerInfo:
        playerInfo['no_balls'] = "-"
    
    return playerInfo
#csv_file = "D:\\temp\\player_match_stats_29Nov2018.csv"
def Process_CSV(year): 
    csv_file = year+".csv"
    df = pd.read_csv(csv_file)
    types = set(x.strip() for x in df['match_type_text'])
    matchId_playersDict = {}

    def addCommentryField(playerName, shortName, playersDict_1, field):
        if " " in playerName:
            if SequenceMatcher(None, playerName, shortName).ratio() >= 0.7:
                if field in playersDict_1:
                    catches = playersDict_1[field]
                    catches += 1
                    playersDict_1[field] = catches
                else:
                    playersDict_1[field] = 1
        else:
            shortNameArr = shortName.split(" ")
            for sName in shortNameArr:
                sName = sName.strip()
                if len(sName) > 2:
                    if SequenceMatcher(None, playerName, sName).ratio() >= 0.9:
                        if field in playersDict_1:
                            catches = playersDict_1[field]
                            catches += 1
                            playersDict_1[field] = catches
                        else:
                            playersDict_1[field] = 1


    # below creating a match wise players dict
    with open(csv_file, 'r') as csvfile:
        csvReader = csv.DictReader(csvfile)
        
        for row in csvReader:
            matchType = row['match_type_text']
            if matchType.strip() in types:
                matchId = row['match_id']
                if matchId in matchId_playersDict:
                    playersDict = matchId_playersDict[matchId]
                    playerId = row['cric_info_id']
                    playersDict[playerId] = row
                else:
                    playersDict = {}
                    playerId = row['cric_info_id']
                    playersDict[playerId] = row
                    matchId_playersDict[matchId] = playersDict

                
    print("matchId_playersDict length: ", len(matchId_playersDict))
    #print("870881 length: ", len(matchId_playersDict['870881']))
    #print("870881 values: ", matchId_playersDict['870881'])

    with open(year+'_1.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(("PlayerID", "TeamID", "MatchID", "OpponentID", "PlayerProfileURL",
                         "MatchURL", "MatchFormat", "MatchStartDate", "MatchVenue",'innings', "TeamName", "PlayerName", "PlayerFullName",
                         "Player Date,Place of Birth", "PlayerNickName", "B_Bat", "R_Bat", "4s", "6s",
                         "SR_Bat", "BallsBowled","RunsGiven", "MaidenOvers", "W_Bow", "ER_Bow", "Wide_Bow",
                         "No_Bow",'commentry' ,"catches", "stumped","run_out"))


        for matchId, players in matchId_playersDict.items():

            teamDict = {}

            for playerId, playerDict in players.items():
                team = playerDict['team']
                if team in teamDict:
                    teamPlayers = teamDict[team]
                    teamPlayers.append(playerDict)
                else:
                    teamPlayers = []
                    teamPlayers.append(playerDict)
                    teamDict[team] = teamPlayers

            print("teamDict length: ", len(teamDict))

            teamKeys = list(teamDict.keys())

            print("teamKeys: ", teamKeys)

            teamPlayers_0 = teamDict[teamKeys[0]]
            teamPlayers_1 = teamDict[teamKeys[1]]
            
            for playerDict_0 in teamPlayers_0:
                commentry = str(playerDict_0['commentry'])
                if ' sub ' in commentry or '(sub ' in commentry:
                    handle = handleSubs(commentry,playerDict_0,teamKeys[1])
                    if handle == None:
                        continue
                    Flag = True
                    for i in range(0,len(teamPlayers_1)):
                        if handle['short_name'] == teamPlayers_1[i]['short_name']:
                            print(handle['short_name'],teamPlayers_1[i]['short_name'])
                            Flag = False
                            break
                    if Flag:
                        teamPlayers_1.append(handle)
                    #commentry = commentry.replace('sub','').replace('(','').replace(')','').replace('[',' ').replace(']',' ')

                 #print("commentry: ", commentry)
                if commentry.strip().startswith("c "):
                    # catch
                    #commentry = unidecode.unidecode(commentry)
                    if ' sub ' in commentry:
                        commentry = commentry.replace('(','').replace(')','').replace(' sub ',' ')
                    commentry = ''.join(x for x in commentry if x in string.printable)

                    playerNameMatch = re.match(r"c ([\w\s'-]+) b ", commentry.strip())
##                    print(playerNameMatch)
                    try:
                        playerName = playerNameMatch.group(1)

                    except:
                        print("commentry 0c: ", commentry)
                        playerNameMatch = re.match(r"c & b ([\w\s'-]+)", commentry.strip())
                        playerName = playerNameMatch.group(1)

                    #playerName = unidecode.unidecode(playerName)
                    for playersDict_1 in teamPlayers_1:
                        shortName = playersDict_1['short_name']
                        #shortName = unidecode.unidecode(shortName)
                        shortName = ''.join(x for x in shortName if x in string.printable)
                        playerName = playerName.strip()
                        addCommentryField(playerName, shortName, playersDict_1, 'catches')

                elif commentry.strip().startswith("st "):
                    # stump
                    #commentry = unidecode.unidecode(commentry)
                    if ' sub ' in commentry:
                        commentry = commentry.replace('(','').replace(')','').replace(' sub ',' ')
                    commentry = ''.join(x for x in commentry if x in string.printable)
                    playerNameMatch = re.match(r"st ([\w\s'-]+) b ", commentry.strip())
                    try:
                        playerName = playerNameMatch.group(1)

                    except:
                        print("commentry 0st: ", commentry)
                    #playerName = unidecode.unidecode(playerName)
                    for playersDict_1 in teamPlayers_1:
                        shortName = playersDict_1['short_name']
                        #shortName = unidecode.unidecode(shortName)
                        shortName = ''.join(x for x in shortName if x in string.printable)
                        playerName = playerName.strip()
                        addCommentryField(playerName, shortName, playersDict_1, 'stumped')


                elif commentry.strip().startswith("run out "):
                    if 'sub' in commentry:
##                        # if substitute in commentry, then ignore, as he will not be found in players list
##                        continue
                        commentry = commentry.replace('[','').replace(']','').replace(' sub ','')

                    #commentry = unidecode.unidecode(commentry)
                    commentry = ''.join(x for x in commentry if x in string.printable)
                    try:
                        playerNameMatch = re.match(r"run out \(([\w\s'/-]+)", commentry.strip())
                        playerName = playerNameMatch.group(1)
                    except:
                        print('commentry 0ro: ',commentry)
                        

                    playerNames = []
                    if '/' in playerName:
                        playerNames = playerName.split('/')

                    for playersDict_1 in teamPlayers_1:
                        shortName = playersDict_1['short_name']
                        #shortName = unidecode.unidecode(shortName)
                        shortName = ''.join(x for x in shortName if x in string.printable)
                        playerName = playerName.strip()
                        if len(playerNames) > 0:
                            for player in playerNames:
                                player = player.strip()
                                addCommentryField(player, shortName, playersDict_1, 'run_out')

                        else:
                            addCommentryField(playerName, shortName, playersDict_1, 'run_out')



            for playerDict_1 in teamPlayers_1:
                commentry = str(playerDict_1['commentry'])
                if ' sub ' in commentry or '(sub ' in commentry:
                    handle = handleSubs(commentry,playerDict_1,teamKeys[0])
                    if handle == None:
                        continue
                    Flag = True
                    for i in range(0,len(teamPlayers_0)):
                        if handle['short_name'] == teamPlayers_0[i]['short_name']:
                            print(handle['short_name'],teamPlayers_0[i]['short_name'])
                            Flag = False
                            break
                    if Flag:
                        teamPlayers_0.append(handle)
                    #commentry = commentry.replace('sub','').replace('(','').replace(')','').replace('[','').replace(']','')

                if commentry.strip().startswith("c "):
                    # catch
                    #commentry = unidecode.unidecode(commentry)
                    commentry = ''.join(x for x in commentry if x in string.printable)
                    #print("commentry: ", commentry)
                    if ' sub ' in commentry:
                        commentry = commentry.replace('(','').replace(')','').replace(' sub ',' ')

                    playerNameMatch = re.match(r"c ([\w\s'-]+) b ", commentry.strip())
                    try:
                        playerName = playerNameMatch.group(1)
                    except:
                        playerNameMatch = re.match(r"c & b ([\w\s'-]+)", commentry.strip())
                        playerName = playerNameMatch.group(1)

                    #playerName = unidecode.unidecode(playerName)
                    for playersDict_0 in teamPlayers_0:
                        shortName = playersDict_0['short_name']
                        #shortName = unidecode.unidecode(shortName)
                        shortName = ''.join(x for x in shortName if x in string.printable)
                        playerName = playerName.strip()
                        addCommentryField(playerName, shortName, playersDict_0, 'catches')


                elif commentry.strip().startswith("st "):
                    # stump
                    #commentry = unidecode.unidecode(commentry)
                    if ' sub ' in commentry:
                        commentry = commentry.replace('(','').replace(')','').replace(' sub ',' ')
                    commentry = ''.join(x for x in commentry if x in string.printable)
                    playerNameMatch = re.match(r"st ([\w\s'-]+) b ", commentry.strip())
                    try:
                        playerName = playerNameMatch.group(1)

                    except:
                        print("commentry 1st: ", commentry)
                    #playerName = unidecode.unidecode(playerName)
                    for playersDict_0 in teamPlayers_0:
                        shortName = playersDict_0['short_name']
                        #shortName = unidecode.unidecode(shortName)
                        shortName = ''.join(x for x in shortName if x in string.printable)
                        playerName = playerName.strip()
                        addCommentryField(playerName, shortName, playersDict_0, 'stumped')


                elif commentry.strip().startswith("run out "):
                    if 'sub' in commentry:
##                        # if substitute in commentry, then ignore, as he will not be found in players list
##                        continue
                        commentry = commentry.replace('[','').replace(']','').replace(' sub ','')

                    #commentry = unidecode.unidecode(commentry)
                    commentry = ''.join(x for x in commentry if x in string.printable)
                    playerNameMatch = re.match(r"run out \(([\w\s'/-]+)", commentry.strip())
                    try:
                        playerName = playerNameMatch.group(1)

                    except:
                        print("commentry 1rt: ", commentry)
                    playerNames = []
                    if '/' in playerName:
                        playerNames = playerName.split('/')

                    for playersDict_0 in teamPlayers_0:
                        shortName = playersDict_0['short_name']
                        #shortName = unidecode.unidecode(shortName)
                        shortName = ''.join(x for x in shortName if x in string.printable)
                        playerName = playerName.strip()
                        if len(playerNames) > 0:
                            for player in playerNames:
                                player = player.strip()
                                addCommentryField(player, shortName, playersDict_0, 'run_out')
                        else:
                            addCommentryField(playerName, shortName, playersDict_0, 'run_out')

            for playerDict_0 in teamPlayers_0:
                if not 'catches' in playerDict_0:
                    playerDict_0['catches'] = "0"
                if not 'stumped' in playerDict_0:
                    playerDict_0['stumped'] = "0"
                if not 'run_out' in playerDict_0:
                    playerDict_0['run_out'] = "0"
            

                writer.writerow((playerDict_0["_id"],playerDict_0["TeamID"],playerDict_0["match_id"], playerDict_0["OpponentID"], playerDict_0["player_cric_info_link"],
                    playerDict_0["MatchURL"], playerDict_0["match_type_text"], playerDict_0["Match_start_Date"],
                    playerDict_0["Venue"], playerDict_0["innings"],playerDict_0["team"], playerDict_0["short_name"], playerDict_0["Player_Full_Name"],
                    playerDict_0["date,place_of_birth"], playerDict_0["Player_Nickname"], playerDict_0["balls_faced"],
                    playerDict_0["run_scored"], playerDict_0["4s"], playerDict_0["6s"], playerDict_0["strike_rate"],
                    playerDict_0["balls_bowled"], playerDict_0["runs_given"], playerDict_0["maiden_overs"],
                    playerDict_0["wicket"], playerDict_0["econ"], playerDict_0["wide_balls"], playerDict_0["no_balls"],playerDict_0["commentry"],
                    playerDict_0["catches"], playerDict_0["stumped"], playerDict_0["run_out"]))

            for playerDict_1 in teamPlayers_1:
                if not 'catches' in playerDict_1:
                    playerDict_1['catches'] = "0"
                if not 'stumped' in playerDict_1:
                    playerDict_1['stumped'] = "0"
                if not 'run_out' in playerDict_1:
                    playerDict_1['run_out'] = "0"


                writer.writerow((playerDict_1["_id"],playerDict_1["TeamID"],playerDict_1["match_id"], playerDict_1["OpponentID"], playerDict_1["player_cric_info_link"],
                    playerDict_1["MatchURL"], playerDict_1["match_type_text"], playerDict_1["Match_start_Date"],
                    playerDict_1["Venue"],playerDict_1["innings"] ,playerDict_1["team"], playerDict_1["short_name"], playerDict_1["Player_Full_Name"],
                    playerDict_1["date,place_of_birth"], playerDict_1["Player_Nickname"], playerDict_1["balls_faced"],
                    playerDict_1["run_scored"], playerDict_1["4s"], playerDict_1["6s"], playerDict_1["strike_rate"],
                    playerDict_1["balls_bowled"], playerDict_1["runs_given"], playerDict_1["maiden_overs"],
                    playerDict_1["wicket"], playerDict_1["econ"], playerDict_1["wide_balls"], playerDict_1["no_balls"],playerDict_1["commentry"],
                    playerDict_1["catches"], playerDict_1["stumped"], playerDict_1["run_out"]))

##                writer.writerow((playerDict_1["_id"], playerDict_1["short_name"], playerDict_1["player_cric_info_link"],
##                     playerDict_1["team"], playerDict_1["commentry"], playerDict_1["run_scored"],
##                     playerDict_1["balls_faced"], playerDict_1["M"], playerDict_1["4s"], playerDict_1["6s"],
##                     playerDict_1["balls_bowled"], playerDict_1["maiden_overs"], playerDict_1["runs_given"],
##                     playerDict_1["wicket"], playerDict_1["econ"], playerDict_1["dot_delivery"],
##                     playerDict_1["four_delivery"],
##                     playerDict_1["six_delivery"], playerDict_1["wide_balls"], playerDict_1["no_balls"],
##                     playerDict_1["Position"], playerDict_1["match_id"], playerDict_1["match_desc"],
##                     playerDict_1["url_match_type"],
##                     playerDict_1["match_type_text"], playerDict_1["season"], playerDict_1["strike_rate"],
##                     playerDict_1["cric_info_id"], playerDict_1["catches"], playerDict_1["stumped"], playerDict_1["run_out"]))


####for year in ['2011','2012','2013','2014','2015','2016','2017','2018']:
##Process_CSV('2018')

