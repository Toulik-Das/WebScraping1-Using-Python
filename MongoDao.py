from pymongo import MongoClient
from logger_impl import *


client = None

def __initClient():
    global client # this line will prevent ERROR: local variable 'client' referenced before assignment
    if client == None:
        client = MongoClient("mongodb://player_user:scrA9in9cr1cpL0YeZ@54.164.104.49:23016/player_data_db")
        logger.info("Connected to MongoDB Client")



def insertToPlayerStats(jsonObj):
    if client == None:
        __initClient()

    playerDataDb = client.player_data_db
    playerMatchStats = playerDataDb.player_match_stats
    playerMatchStats.insert_one(jsonObj)


def insertToProcessedUrls(url):
    if client == None:
        __initClient()

    playerDataDb = client.player_data_db
    processedMatchUrls = playerDataDb.processed_match_urls
    dataJson = {"url": url }
    processedMatchUrls.insert_one(dataJson)
    logger.info("match url inserted successfully: " + url)