from DBInit import DBInit
from loguru import logger
import requests
from bs4 import BeautifulSoup
import re

class Search:
     
     def __init__(self): 
          pass
     
     @staticmethod
     def contains_digit(url):
          # 使用正则表达式检查URL中是否包含数字
          if re.search(r'\d', url):
               return True
          else:
               return False
                    
     def search_player(self):
          self.db = DBInit(table_name="players").db
          sql = "SELECT * FROM players where player_url is null and player_image_url is null"
          result = self.db.find(sql, to_json=True)

          wiki_prefix = "https://wikipedia.org"
          for index in range(len(result)):
               try:
                    ID = result[index]["ID"]
                    FULL_NAME = result[index]['FULL_NAME']
                    full_name_search = FULL_NAME.replace(" ", "+")
                    response = requests.get('https://wikipedia.org/w/index.php?search=' \
                         + full_name_search \
                              + '+football+player')
                    soup = BeautifulSoup(response.text, 'html.parser')  
                    PLAYER_URL = wiki_prefix \
                         + soup.find(class_="mw-search-result mw-search-result-ns-0").find('a')["href"]
                    PLAYER_IMAGE_URL = "https:" \
                         + soup.find(class_="mw-search-result mw-search-result-ns-0").find("img")["src"]
                    sql = f"UPDATE players SET player_url = '{PLAYER_URL}', " \
                         f"player_image_url = '{PLAYER_IMAGE_URL}' WHERE ID = {ID}"
                    
                    logger.info(sql)
                    self.db.update(sql)
               except Exception as e:
                    try: 
                         logger.error(f"Lack of player_image_url for ID: '{ID}'")
                         ID = result[index]["ID"]
                         FULL_NAME = result[index]['FULL_NAME']
                         full_name_search = FULL_NAME.replace(" ", "+")
                         response = requests.get('https://wikipedia.org/w/index.php?search=' \
                              + full_name_search \
                                   + '+football+player')
                         soup = BeautifulSoup(response.text, 'html.parser')  
                         PLAYER_URL = wiki_prefix \
                              + soup.find(class_="mw-search-result mw-search-result-ns-0").find('a')["href"]
                         sql = f"UPDATE players SET player_url = '{PLAYER_URL}'" \
                              f"WHERE ID = {ID}"
                         
                         logger.info(sql)
                         self.db.update(sql)
                    except Exception as e:
                         logger.error(f"Error Occured: {e}")
                         logger.error(f"Error ID: '{ID}'")
     
     def search_referee(self):
          self.db = DBInit(table_name="referee").db
          sql = "SELECT * FROM referee where referee_url is null and referee_image_url is null"
          result = self.db.find(sql, to_json=True)

          wiki_prefix = "https://wikipedia.org"
          for index in range(len(result)):
               try:
                    ID = result[index]["ID"]
                    DETECTED_NAME = result[index]['DETECTED_NAME']
                    name_search = DETECTED_NAME.replace(" ", "+")
                    response = requests.get('https://wikipedia.org/w/index.php?search=' \
                         + name_search \
                              + '+referee')
                    soup = BeautifulSoup(response.text, 'html.parser')  
                    REFEREE_URL = wiki_prefix \
                         + soup.find(class_="mw-search-result mw-search-result-ns-0").find('a')["href"]
                    if self.contains_digit(REFEREE_URL):
                         continue
                    REFEREE_IMAGE_URL = "https:" \
                         + soup.find(class_="mw-search-result mw-search-result-ns-0").find("img")["src"] 
                    sql = f"UPDATE referee SET referee_url = '{REFEREE_URL}', " \
                         f"referee_image_url = '{REFEREE_IMAGE_URL}' WHERE ID = {ID}"
                    
                    logger.info(sql)
                    self.db.update(sql)
               except Exception as e:
                    try: 
                         logger.error(f"Lack of referee_image_url for ID: '{ID}'")
                         ID = result[index]["ID"]
                         DETECTED_NAME = result[index]['DETECTED_NAME']
                         name_search = DETECTED_NAME.replace(" ", "+")
                         response = requests.get('https://wikipedia.org/w/index.php?search=' \
                              + name_search \
                                   + '+referee')
                         soup = BeautifulSoup(response.text, 'html.parser')  
                         REFEREE_URL = wiki_prefix \
                              + soup.find(class_="mw-search-result mw-search-result-ns-0").find('a')["href"]
                         sql = f"UPDATE referee SET referee_url = '{REFEREE_URL}'" \
                              f"WHERE ID = {ID}"
                         
                         logger.info(sql)
                         self.db.update(sql)
                    except Exception as e:
                         logger.error(f"Error Occured: {e}")
                         logger.error(f"Error ID: '{ID}'")
     
     
     def search_team(self):
          self.db = DBInit(table_name="team").db
          sql = "SELECT * FROM team where team_url is null and team_image_url is null"
          result = self.db.find(sql, to_json=True)

          wiki_prefix = "https://wikipedia.org"
          for index in range(len(result)):
               try:
                    ID = result[index]["ID"]
                    TEAM = result[index]['TEAM']
                    name_search = TEAM.replace(" ", "+")
                    response = requests.get('https://wikipedia.org/w/index.php?search=' \
                         + name_search \
                              + '+football+club' \
                                   + '&title=Special:Search&profile=advanced&fulltext=1&ns0=1')
                    soup = BeautifulSoup(response.text, 'html.parser')  
                    TEAM_URL = wiki_prefix \
                         + soup.find(class_="mw-search-result mw-search-result-ns-0").find('a')["href"]
                    if self.contains_digit(TEAM_URL):
                         continue
                    TEAM_IMAGE_URL = "https:" \
                         + soup.find(class_="mw-search-result mw-search-result-ns-0").find("img")["src"] 
                    sql = f"UPDATE team SET team_url = '{TEAM_URL}', " \
                         f"team_image_url = '{TEAM_IMAGE_URL}' WHERE ID = {ID}"
                    
                    logger.info(sql)
                    self.db.update(sql)
               except Exception as e:
                    try: 
                         logger.error(f"Lack of team_image_url for ID: '{ID}'")
                         ID = result[index]["ID"]
                         TEAM = result[index]['TEAM']
                         name_search = TEAM.replace(" ", "+")
                         response = requests.get('https://wikipedia.org/w/index.php?search=' \
                              + name_search \
                                   + '+football+club')
                         soup = BeautifulSoup(response.text, 'html.parser')  
                         TEAM_URL = wiki_prefix \
                              + soup.find(class_="mw-search-result mw-search-result-ns-0").find('a')["href"]
                         sql = f"UPDATE team SET team_url = '{TEAM_URL}'" \
                              f"WHERE ID = {ID}"
                         
                         logger.info(sql)
                         self.db.update(sql)
                    except Exception as e:
                         logger.error(f"Error Occured: {e}")
                         logger.error(f"Error ID: '{ID}'")
  
     
     def search_venue(self):
          self.db = DBInit(table_name="venue").db
          sql = "SELECT * FROM venue where venue_url is null and venue_image_url is null"
          result = self.db.find(sql, to_json=True)

          wiki_prefix = "https://wikipedia.org"
          for index in range(len(result)):
               try:
                    ID = result[index]["ID"]
                    VENUE = result[index]['VENUE']
                    name_search = VENUE.replace(" ", "+")
                    response = requests.get("https://wikipedia.org/w/index.php?search=" \
                         + f"{name_search}" \
                              + "&title=Special:Search&profile=advanced&fulltext=1&ns0=1")
                    logger.info(response.url)
                    soup = BeautifulSoup(response.text, 'html.parser')  
                    VENUE_URL = wiki_prefix \
                         + soup.find(class_="mw-search-result mw-search-result-ns-0").find('a')["href"]
                    VENUE_IMAGE_URL = "https:" \
                         + soup.find(class_="mw-search-result mw-search-result-ns-0").find("img")["src"] 
                    sql = f"UPDATE venue SET venue_url = '{VENUE_URL}', " \
                         f"venue_image_url = '{VENUE_IMAGE_URL}' WHERE ID = {ID}"
                    
                    logger.info(sql)
                    self.db.update(sql)
               except Exception as e:
                    try: 
                         logger.error(f"Lack of venue_image_url for ID: '{ID}'")
                         ID = result[index]["ID"]
                         VENUE = result[index]['VENUE']
                         name_search = VENUE.replace(" ", "+")
                         response = requests.get('https://wikipedia.org/w/index.php?search=' \
                              + name_search)
                         soup = BeautifulSoup(response.text, 'html.parser')  
                         VENUE_URL = wiki_prefix \
                              + soup.find(class_="mw-search-result mw-search-result-ns-0").find('a')["href"]
                         sql = f"UPDATE venue SET venue_url = '{VENUE_URL}'" \
                              f"WHERE ID = {ID}"
                         
                         logger.info(sql)
                         self.db.update(sql)
                    except Exception as e:
                         logger.error(f"Error Occured: {e}")
                         logger.error(f"Error ID: '{ID}'")
  
     
     
     def run(self, keyword):
          if keyword == "players":
               self.search_player()
          elif keyword == "referee":
               self.search_referee()
          elif keyword == "team":
               self.search_team()
          elif keyword == "venue":
               self.search_venue()