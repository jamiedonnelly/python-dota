import requests
import json 
from pprint import pprint
import random
import matplotlib.pyplot as plt
from datetime import datetime 
import numpy as np 
import mysql.connector
import time 


class DotaClient():
    # static variable declaring base url for API calls 
    base_url = "https://api.opendota.com/api/"  

    @staticmethod
    def get_hero_data():
        url = DotaClient.base_url + 'heroes' 
        content = requests.get(url).content
        data = json.loads(content)
        return data 

    def __init__(self, api_key: str):
        self.api_key = api_key 
        self.api_url = '/?api_key='+api_key
        self.heroes_data = DotaClient.get_hero_data()

    def get_match_by_id(self, match_id: int):
        """Function to fetch a match data from a specific match specified by match_id.

        Args:
            match_id (int): Integer corresponding to the match id value in OpenDota.

            show (bool): Whether to print results as well as returning results.

        Returns:
            json: Dictionary/Json describing match details
        """        
        if type(match_id)!=int:
            raise ValueError("match_id must be type Int")
        url = (DotaClient.base_url + 'matches/{}' + self.api_url).format(match_id)
        content = requests.get(url).content
        data = json.loads(content)      
        return data   


    def get_matches_by_player(self, player_id: int, limit: int=None):
        
        if type(player_id)!=int: 
            raise ValueError("player_id must be type Int")
        url = (DotaClient.base_url + 'players/{}/matches' + self.api_url).format(player_id)
        content = requests.get(url).content
        data = json.loads(content)
        if limit:    
            if type(limit)!=int:
                raise ValueError("limit must be type Int")
            else:
                return data[:limit]
        else:
            return data
        
    
    def get_random_match_sample(self, limit: int=100):

        if type(limit)!=int:
            raise ValueError("limit must be type Int") 

        url = (DotaClient.base_url + 'publicMatches' + self.api_url)
        
        # save match_ids to ensure repeated sampling does not occur
        match_ids = []
        data = []

        while (len(data)<limit):
            content = requests.get(url).content
            call = json.loads(content)
            for i in call:
                if len(data)<limit:
                    if i['match_id'] not in match_ids:
                        data.append(i)
                        match_ids.append(i['match_id'])
                    else:
                        pass
                else:
                    break
        return data
        
    def get_random_match_sample_by_player(self, player_id: int, limit: int=100):
        
        if type(player_id)!=int: 
            raise ValueError("player_id must be type Int")
        if type(limit)!=int:
            raise ValueError("limit must be type Int")

        data = self.get_matches_by_player(player_id,limit=0)
        random_sample = random.sample(data,limit)
        
        return random_sample

    @staticmethod
    def winrate(data: list):

        if type(data)!=list:
            raise ValueError("data must be submitted as a list type")
        
        win_count = 0

        for i in data:
            if (i['player_slot'] >=0) & (i['player_slot']<=127):
                if i['radiant_win']==True:
                    win_count +=1 
                else:
                    pass
            else:
                if i['radiant_win']==False:
                    win_count +=1 
                else:
                    pass
        return win_count/len(data)

    @staticmethod 
    def random_match_id():
        # Define lower limit and upper limit to sample match ids from
        lower_limit, upper_limit = 6, 6.5
        return int(round(np.random.uniform(lower_limit,upper_limit),9)*1e9)

    def get_player_name_from_id(self, player_id):
        
        if type(player_id)!=int:
            raise ValueError("player_id must be type int")

        url = (DotaClient.base_url + 'players/{}' + self.api_url).format(player_id)
        content = requests.get(url).content
        data = json.loads(content)
        return data['profile']['personaname']

    def get_player_winrate(self, player_id: int, limit: int=100):

        if type(player_id)!=int: 
            raise ValueError("player_id must be type Int")
        if type(limit)!=int:
            raise ValueError("limit must be type Int")
        
        name = self.get_player_name_from_id(player_id)
        data = self.get_matches_by_player(player_id, limit)
        wr = DotaClient.win_rate(data)

        print("{}'s win rate over the latest {} games is {}%.".format(name, limit, wr*100))
        return wr 

    def plot_player_winrate(self, player_id: int, interval: int=25):
        if type(player_id)!=int: 
            raise ValueError("player_id must be type Int")
        if type(interval)!=int:
            raise ValueError("limit must be type Int")
        
        # load player's entire match history
        data = self.get_matches_by_player(player_id)
        data = data[::-1]
        wr = []
        intervals = [i for i in range(0,len(data),interval)]
        for i in range(1,len(intervals)):
            wr.append(DotaClient.winrate(data[intervals[i-1]:intervals[i]]))
        plt.figure(figsize=(7,4))
        plt.plot(wr)
        plt.ylabel("{}-game winrate".format(interval))
        plt.title("{} {}-game winrate over time.".format(self.get_player_name_from_id(player_id),interval))
        plt.xticks([],[])
        plt.show()

    def get_hero_from_id(self, hero_id: int):
        if type(hero_id)!=int: 
            raise ValueError("hero_id must be type Int")
        hero = [i['localized_name'] for i in self.heroes_data if i['id']==hero_id][0]
        return hero 

    def get_id_from_hero(self, hero: str):
        if type(hero)!=str:
            raise ValueError("hero must be type str")
        hero = hero.strip().lower()
        hero_id = [i['id'] for i in self.heroes_data if i['localized_name'].lower() == hero][0]
        return hero_id

    def get_current_patch(self):
        match_id = self.get_random_match_sample(1)[0]['match_id']
        match_data = self.get_match_by_id(match_id)
        return match_data['patch']
    
    @staticmethod
    def get_draft(data):
        radiant = []
        dire = []
        for i in data['players']:
            if (i['player_slot']>=0) & (i['player_slot']<=127):
                radiant.append(i['hero_id'])
            else:
                dire.append(i['hero_id'])
        return radiant, dire 

    
## Function included to help populate MYSQL database with basic information about games.   
  
def db_insert(db, cursor, data, dota_client) -> None:
    insert_cmd = "INSERT INTO matches (match_id, result, rad1, rad2, rad3, rad4, rad5, dire1, dire2, dire3, dire4, dire5, patch) values ({},{},{},{},{},{},{},{},{},{},{},{},{});"
    if len(data)!=1:
        try:
            if data['lobby_type'] in [5,6,7]:
                try:
                    matchid = data['match_id']
                    radiant, dire = dota_client.get_draft(data)
                    if data['radiant_win']==True:
                        result = 1
                    else:
                        result = 0
                    patch = data['patch']
                    print(insert_cmd.format(matchid,result,radiant[0],radiant[1],radiant[2],radiant[3],radiant[4],dire[0],dire[1],dire[2],dire[3],dire[4],patch))
                    cursor.execute(insert_cmd.format(matchid,result,radiant[0],radiant[1],radiant[2],radiant[3],radiant[4],dire[0],dire[1],dire[2],dire[3],dire[4],patch))
                except:
                    pass
            else:
                pass
        except:
            pass
    else:
        pass
    db.commit()
