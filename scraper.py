#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import urllib3

#Had some security issues. Had to disable it. Be careful!
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Need to disable verifying ssl.Be careful!
r = requests.get('https://us.soccerway.com/teams/england/tottenham-hotspur-football-club/675/matches/',verify=False)
soup = BeautifulSoup(r.text, 'lxml')

matches = soup.find('table',{'class':'matches'}).find('tbody')

i = 0
for row in matches.find_all('tr'):
    #For first ten result
    if i == 10:
        break
    else:
        i +=1

    data = row.find_all('td')
    home_team = data[3].text.strip()
    match_result = data[4].text.strip()
    match_result_class = data[4].find('a').attrs['class'][0]
    away_team = data[5].text.strip()

    output = str.format('Home team : {0}, Away team : {1}, Match Result Class :{2}',home_team,away_team,match_result_class)
    print(output)