import requests
import json 
from pprint import pprint
import random

class DotaClient():
    
    # static variable declaring base url for API calls 
    base_url = "https://api.opendota.com/api/"

    def __init__(self, api_key=None):
        self.api_key = api_key 
        self.api_url = '/?api_key='+api_key
        

    def get_match_by_id(self, match_id: int):
        """Function to fetch a match data from a specific match specified by match_id.

        Args:
            match_id (int): Integer corresponding to the match id value in OpenDota.

            show (bool): Whether to print results as well as returning results.

        Returns:
            json: Dictionary/Json describing match details
        """        
        if type(match_id)!=int:
            raise ValueError("")
        url = (DotaClient.base_url + 'matches/{}' + self.api_url).format(match_id)
        content = requests.get(url).content
        data = json.loads(content)      
        return data   


    def get_matches_by_player(self, player_id: int, limit: int=0):
        
        if type(player_id)!=int: 
            raise ValueError("player_id must be type Int")
        if type(limit)!=int:
            raise ValueError("limit must be type Int")

        url = (DotaClient.base_url + 'players/{}/matches' + self.api_url).format(player_id)
        content = requests.get(url).content
        data = json.loads(content)
        return data[-1*(limit):]
        
    
    def get_random_match_sample(self, limit: int=100):

        if type(limit)!=int:
            raise ValueError("limit must be type Int") 

        url = (DotaClient.base_url + 'publicMatches' + self.api_url)
        
        # save match_ids to ensure repeated sampling does not occur
        match_ids = []
        data = []

        while (len(data)<limit) & True:
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
    def win_rate(data: list):

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
    
    def get_hero_data(self):
        url = DotaClient.base_url + 'heroes' + self.api_url
        content = requests.get(url).content
        data = json.loads(content)
        return data
    
    def get_hero_from_id(self,hero_id: int):
        if type(hero_id)!=int: 
            raise ValueError("hero_id must be type Int")

        url = DotaClient.base_url + 'heroes' + self.api_url
        content = requests.get(url).content
        data = json.loads(content)
        hero = "".join([i['name'] for i in data if i['id']==hero_id])
        return hero 

    def get_id_from_hero(self, hero: str):
        if type(hero)!=str:
            raise ValueError("hero must be type str")

        hero = hero.strip().lower()
        url = DotaClient.base_url + 'heroes' + self.api_url
        content = requests.get(url).content
        data = json.loads(content)
        hero_id = "".join([i['id'] for i in data if i['name'].lower() == hero])
        return hero_id








