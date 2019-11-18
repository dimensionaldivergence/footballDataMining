#!/usr/bin/env python3
from datetime import datetime, timezone
import pytz
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.common.keys import Keys
import time
import copy
import json,csv
import os
from collections import OrderedDict
import pandas as pd

firefox_profile = webdriver.FirefoxProfile()
firefox_profile.set_preference('permissions.default.image', 2)
firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

potential_leagues = {'fr_ligue1': 'https://us.soccerway.com/national/france/ligue-1/20192020/regular-season/r53638/',
                     'fr_ligue2': 'https://us.soccerway.com/national/france/ligue-2/20192020/regular-season/r54072/',
                     'fr_national': 'https://us.soccerway.com/national/france/national/20192020/regular-season/r53268/',
                     'de_bundesliga': 'https://us.soccerway.com/national/germany/bundesliga/20192020/regular-season/r53499/',
                     'de_bundesliga2': 'https://us.soccerway.com/national/germany/2-bundesliga/20192020/regular-season/r53500/',
                     'de_bundesliga3': 'https://us.soccerway.com/national/germany/3-liga/20192020/regular-season/r53501/',
                     'en_premierleague': 'https://us.soccerway.com/national/england/premier-league/20192020/regular-season/r53145/',
                     'en_championship': 'https://us.soccerway.com/national/england/championship/20192020/regular-season/r53782/',
                     'en_leagueone': 'https://us.soccerway.com/national/england/league-one/20192020/regular-season/r53677/',
                     'it_serieA': 'https://us.soccerway.com/national/italy/serie-a/20192020/regular-season/r54890/',
                     'it_serieB': 'https://us.soccerway.com/national/italy/serie-b/20192020/regular-season/r54637/',
                     'pr_primeiraliga': 'https://us.soccerway.com/national/portugal/portuguese-liga-/20192020/regular-season/r53517/',
                     'pr_segundaliga': 'https://us.soccerway.com/national/portugal/liga-de-honra/20192020/regular-season/r53518/',
                     'nl_eredivisie': 'https://us.soccerway.com/national/netherlands/eredivisie/20192020/regular-season/r54058/',
                     'nl_eerstedivisie': 'https://us.soccerway.com/national/netherlands/eerste-divisie/20192020/regular-season/r52785/',
                     'es_laliga': 'https://us.soccerway.com/national/spain/primera-division/20192020/regular-season/r53502/',
                     'es_segundadivision': 'https://us.soccerway.com/national/spain/segunda-division/20192020/regular-season/r54950/',
                     'br_serieA': 'https://us.soccerway.com/national/brazil/serie-a/2019/regular-season/r51143/',
                     'br_serieB': 'https://us.soccerway.com/national/brazil/serie-b/2019/regular-season/r50954/',
                     'ar_superliga': 'https://us.soccerway.com/national/argentina/primera-division/20192020/regular-season/r52234/',
                     'ar_primeranacional': 'https://us.soccerway.com/national/argentina/prim-b-nacional/20192020/regular-season/r54679/',
                     'no_eliteserien': 'https://us.soccerway.com/national/norway/eliteserien/2019/regular-season/r50939/',
                     'no_1division': 'https://us.soccerway.com/national/norway/1-division/2019/regular-season/r51416/',
                     'pl_ekstraklasa': 'https://us.soccerway.com/national/poland/ekstraklasa/20192020/regular-season/r53505/',
                     'pl_iliga': 'https://us.soccerway.com/national/poland/i-liga/20192020/regular-season/r53507/',
                     'ro_ligai': 'https://us.soccerway.com/national/romania/liga-i/20192020/regular-season/r54245/',
                     'ro_ligaii': 'https://us.soccerway.com/national/romania/liga-ii/20192020/regular-season/r54197/',
                     'ru_premierleague': 'https://us.soccerway.com/national/russia/premier-league/20192020/regular-season/r53628/',
                     'ru_FNL': 'https://us.soccerway.com/national/russia/1-division/20192020/regular-season/r53625/',
                     'us_mls': 'https://us.soccerway.com/national/united-states/mls/2019/regular-season/r51257/',
                     'au_bundesliga': 'https://us.soccerway.com/national/austria/bundesliga/20192020/regular-season/r54164/',
                     'au_bundesliga2': 'https://us.soccerway.com/national/austria/1-liga/20192020/regular-season/r54328/',
                     'be_firstdivisionA': 'https://us.soccerway.com/national/belgium/pro-league/20192020/regular-season/r53516/',
                     'dn_superliga': 'https://us.soccerway.com/national/denmark/superliga/20192020/regular-season/r54285/',
                     'dn_1stdivision': 'https://us.soccerway.com/national/denmark/1st-division/20192020/regular-season/r53778/'}

matches_unclean_headers = ['league_id', 'match_time', 'match_url', 'home_team', 'away_team', 'full_time_score']
matches_clean_headers   = ['league_id', 'match_time', 'match_url', 'home_team', 'away_team', 'full_time_score', 'half_time_score',
                           'corners', 'offsides', 'shots_on_target', 'fouls']


def close_popup(webdriver):
    while True:
        try:
            consent_button = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//div[@id='qcCmpButtons']//button[@class='qc-cmp-button']")))
            consent_button.click()
            break
        except Exception as e:
            time_now = datetime.utcnow().replace(tzinfo=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
            print("{} - {}".format(time_now, repr(e)), file=open('scraper_error.log', 'a'))
            time.sleep(0.5)

def wait_for_page_refresh(very_first_match_date):
    while True:
        time_now = datetime.utcnow().replace(tzinfo=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
        try:
            last_10_matches = driver.find_elements_by_css_selector("tr[id^='page_team_1_block_team_matches_summary_7']")
            if very_first_match_date != last_10_matches[0].find_element_by_class_name("full-date").text:
                print("{} - New data present on page.".format(time_now), file=open('scraper_stdout.log'))
                very_first_match_date = last_10_matches[0].find_element_by_class_name("full-date").text
                return last_10_matches, very_first_match_date
            else:
                print("{} - Page hasn't refreshed yet.".format(time_now), file=open('scraper_stdout.log'))
                time.sleep(0.5)    
        except Exception as e:
            print("{} - {}".format(time_now, repr(e)), file=open('scraper_error.log', 'a'))

all_matches_unclean = {k: [] for k,v in potential_leagues.items()}
team_done = None
run_once = False
clean_csv = 'all_matches_clean.csv'
unclean_csv = 'all_matches_unclean.csv'

# Create unclean file if not existing
if not os.path.isfile(unclean_csv):
    with open(unclean_csv, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(matches_unclean_headers)
# Create clean file if not existing, otherwise pick up where we left off
if not os.path.isfile(clean_csv):
    with open(clean_csv, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(matches_clean_headers)    
elif pd.read_csv(clean_csv).size > 2:
    clean_unfinished_data = pd.read_csv(clean_csv)
    last_data = clean_unfinished_data.iloc[-1,3:5]
    last_data2 = clean_unfinished_data.iloc[-2,3:5]
    league = clean_unfinished_data.iloc[-1,0]     # All leagues before this are supposed to be ready.
    team_done = list(set(last_data) & set(last_data2))[0]
    # Remove already done leagues from the dict
    for league_id in list(potential_leagues.keys()):
        if league_id != league:
            del potential_leagues[league_id]
            time_now = datetime.utcnow().replace(tzinfo=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
            print("{} - Removed: {}".format(time_now, league_id), file=open('scraper_stdout.log'))
        else:
            break

# Start looping through the filtered (or original) league dict.
for league_id,league_url in potential_leagues.items():    
    #if league_id == 'fr_ligue2':
        #break
    driver = webdriver.Firefox(firefox_profile=firefox_profile)
    driver.get(league_url)
    
    # Closing pop-up about accepting cookies
    if not run_once:
        close_popup(driver)
        run_once = True

    # Remove already done teams from the list
    teams = driver.find_element_by_xpath("//div[@id='page_competition_1_block_competition_tables_7']").find_elements_by_class_name("team_rank")
    if team_done:
        for team in teams[:]:
            if team.find_element_by_class_name('team').text != team_done:
                teams.remove(team)
            else:
                break
    teams_urls = [team.find_element_by_class_name('team').find_element_by_tag_name('a').get_attribute('href') for team in teams]
    
    # Start iterating on the cleaned data
    for team_url in teams_urls:
        #if team_url == teams_urls[1]:
            #break
        driver.get(team_url)

        # Initialize some variables
        very_first_match_date = None
        first_match_reached = False
        
        while not first_match_reached:
            # Checking if new data present on page (either in the beginning or after button click)
            last_10_matches, very_first_match_date = wait_for_page_refresh(very_first_match_date)
            
            for element in last_10_matches:
                match_time_unchecked = element.find_element_by_class_name("full-date").text
                match_time_ms = int(datetime.strptime(match_time_unchecked, '%d/%m/%y').replace(tzinfo=timezone.utc).timestamp() * 1000)
                if match_time_ms < int(datetime(2017, 1, 1).replace(tzinfo=timezone.utc).timestamp() * 1000):
                    first_match_reached = True
                home_team = element.find_element_by_class_name("team-a").text
                away_team = element.find_element_by_class_name("team-b").text
                full_time_score = element.find_element_by_class_name("score-time").text
                if any(c in full_time_score for c in ["P", "E"]):
                    full_time_score = full_time_score.strip('EP')
                elif ":" in full_time_score:        # Future matches reached
                    break
                elif "PSTP" in full_time_score:   # Postponed match, skip
                    continue
                match_url = element.find_element_by_class_name("score-time").find_element_by_tag_name('a').get_attribute('href')

                # Write data to our csv file:
                with open(unclean_csv, 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow([league_id, match_time_ms, match_url, home_team, away_team, full_time_score])
            
            # Click on previous and be kind to soccerway..
            button = driver.find_element_by_class_name("previous ").click()
            time.sleep(0.5)
        
    # After looping through all the teams in a league, remove duplicates and then proceed
    league_id = 'fr_ligue1'
    # Read file first:
    all_matches_unclean = pd.read_csv(unclean_csv)
    all_matches_clean = all_matches_unclean[all_matches_unclean['league_id'] == league_id].drop_duplicates()

    # Loop through all matches in filtered list and gather extra data.
    for idx, unique_match in all_matches_clean.iterrows():
        #if idx == 1:
            #break
        driver.get(unique_match['match_url'])
        match_id = unique_match['match_url'].split('/')[-2]
        half_time = driver.find_element_by_xpath("//dl[dt='Half-time']/dd[1]").text
        unique_match = unique_match.append(pd.Series({"half_time_score": half_time}))
        
        # Switch focus to stats table:        
        try:
            stats = driver.find_element_by_xpath("//div//iframe[@src='/charts/statsplus/{}/']".format(match_id))
        except Exception as e:
            time_now = datetime.utcnow().replace(tzinfo=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
            match_date = str(datetime.utcfromtimestamp(unique_match['match_time'] / 1000.0).strftime("%Y-%m-%d"))
            print("{} - {} - {} at {} didn't have stats table, skipping. Here's the original error:"
                    .format(time_now, unique_match['home_team'], unique_match['away_team'], match_date), file=open('scraper_error.log', 'a'))
            print(repr(e), file=open('scraper_error.log', 'a'))
            continue
        driver.switch_to.frame(stats)
        # Gather stats
        home_corners = driver.find_element_by_xpath("//td[text()='Corners']/preceding-sibling::td").text
        away_corners = driver.find_element_by_xpath("//td[text()='Corners']/following-sibling::td").text
        unique_match = unique_match.append(pd.Series({"corners": "{} - {}".format(home_corners, away_corners)}))
        
        home_offsides = driver.find_element_by_xpath("//td[text()='Offsides']/preceding-sibling::td").text
        away_offsides = driver.find_element_by_xpath("//td[text()='Offsides']/following-sibling::td").text
        unique_match = unique_match.append(pd.Series({"offsides": "{} - {}".format(home_offsides, away_offsides)}))
        
        home_shots_on_target = driver.find_element_by_xpath("//td[text()='Shots on target']/preceding-sibling::td").text
        away_shots_on_target = driver.find_element_by_xpath("//td[text()='Shots on target']/following-sibling::td").text
        unique_match = unique_match.append(pd.Series({"shots_on_target": "{} - {}".format(home_shots_on_target, away_shots_on_target)}))
        
        home_fouls = driver.find_element_by_xpath("//td[text()='Fouls']/preceding-sibling::td").text
        away_fouls = driver.find_element_by_xpath("//td[text()='Fouls']/following-sibling::td").text
        unique_match = unique_match.append(pd.Series({"fouls": "{} - {}".format(home_fouls, away_fouls)}))
        
        # Switch focus back
        driver.switch_to.default_content()
        
        with open(clean_csv, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(unique_match.values[:])
    
driver.close()



    
"""
TODO list:
    1. Create a list of ligues to check for matches up until 2017.
    2. Try to navigate back to previous matches by triggering the "previous" button.
    3. Gather all matches ending either draw, or handicap win (i.e. 1-0; 2-1; 0-1; 1-2, etc.) --> Gathering all, selecting later
    3.1. Match characteristics: possession, corners, shots on target, fouls, offsides, goals (halftime, fulltime, home, away)
    4. Gather information to all these matches (i.e. last 5 matches stats, goals, wins,losses,draws, etc.)
    5. Implement neural network.
    6. Try scanning for potential matches and place bets and then check results.
        6.1. Create function that checks for the odds
        6.2. Create a function that simulates betting
        6.3. Create a function that checks results for previous bets and calculates winning
        6.4. Hopefully profit.

"""

