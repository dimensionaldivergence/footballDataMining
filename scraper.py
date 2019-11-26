#!/usr/bin/env python3
from datetime import datetime, timezone
import pytz
from selenium import webdriver
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.action_chains import ActionChains
#from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
#from selenium.webdriver.chrome.options import Options
import time
import copy
import json,csv
import os
import pandas as pd



#2019-11-19 05:50:40 - SessionNotCreatedException('Tried to run command without establishing a connection', None, None)
# --> marionette False --> Doesn't work
#2019-11-19 05:50:21 - ElementClickInterceptedException('Element <a id="page_team_1_block_team_matches_summary_7_previous" class="previous "> is not clickable at point (612.0833587646484,334.75) because another element <div id="div-gpt-ad-1478706130315-4"> obscures it', None, None)
# sudo apt-get install openssl gem ruby xvfb
# sudo pip3 install pyvirtualdisplay
# 2019-11-19 16:49:06 - MoveTargetOutOfBoundsException('(623.0833587646484, 757.875) is out of bounds of viewport width (720) and height (466)', None, None)
# fbset -s      # raspbian get resolution   720x480
# 2019-11-19 17:08:07 - NoSuchElementException("Unable to locate element: //a[@id='page_team_1_block_team_matches_summary_7_previous']", None, None)

# 2019-11-19 20:12:28 - ElementNotInteractableException('Element <button class="qc-cmp-button"> could not be scrolled into view', None, None)

# File "./scraper.py", line 240, in <module> driver.get(unique_match['match_url'])
# selenium.common.exceptions.WebDriverException: Message: Failed to decode response from marionette  --> Caused by:
# This bug is related to zombie processes that hangs after driver.quit(), when you open many browsers one task after 
# another, your machine will run out of memory or out of PIDs, that is happening on docker for chromedriver and geckodriver.

# File "./scraper.py", line 237, in <module> driver.get(unique_match['match_url'])   --> Fixed
# selenium.common.exceptions.SessionNotCreatedException: Message: Tried to run command without establishing a connection

# FileNotFoundError: [Errno 2] No such file or directory: '/tmp/tmpe_zjqvbz/webdriver-py-profilecopy/user.js'
# Possible solution: https://stackoverflow.com/questions/6652819/selenium-firefoxprofile-fails-with-not-found-exception
# Modifying selenium/webdriver/firefox/firefox_profile.py and add try-except
# /usr/local/lib/python3.7/dist-packages/selenium/webdriver/firefox/firefox_profile.py --> Already done...


firefox_profile = webdriver.FirefoxProfile('profile.default')  # Saved profile from tmp folder...
#firefox_profile.set_preference('permissions.default.image', 2)
#firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
#firefox_profile.set_preference("browser.cache.disk.enable", False)
#firefox_profile.set_preference("browser.cache.memory.enable", False)
#firefox_profile.set_preference("browser.cache.offline.enable", False)
#firefox_profile.set_preference("network.http.use-cache", False)
#firefox_profile.set_preference("browser.tabs.warnOnClose", False)
##firefox_profile.add_extension('adblock_plus-3.6.3-an fx.xpi')
##firefox_profile.set_preference("extensions.adblockplus.currentVersion", "3.6.3")

# =============================================================================
# from pyvirtualdisplay import Display
# display = Display(visible=0, size=(1920, 1080))
# display.start()
# =============================================================================

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


def close_popup(driver):
    while True:
        try:
            consent_button = driver.find_element_by_xpath("//div[@id='qcCmpButtons']//button[@class='qc-cmp-button']")
            consent_button.click()
            break
        except Exception as e:
            time_now = datetime.utcnow().replace(tzinfo=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
            print("{} - {}".format(time_now, repr(e)), file=open('error_log', 'a'))
            time.sleep(0.5)

def wait_for_page_refresh(very_first_match_date):
    while True:
        time.sleep(0.01)
        time_now = datetime.utcnow().replace(tzinfo=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
        try:
            last_10_matches = driver.find_elements_by_css_selector("tr[id^='page_team_1_block_team_matches_summary_7']")
            if very_first_match_date != last_10_matches[0].find_element_by_class_name("full-date").text:
                print("{} - New data present on page.".format(time_now), file=open('stdout.log', 'a'))
                very_first_match_date = last_10_matches[0].find_element_by_class_name("full-date").text
                return last_10_matches, very_first_match_date
            else:
                print("{} - Page hasn't refreshed yet.".format(time_now), file=open('stdout.log', 'a'))
                time.sleep(0.5)    
        except Exception as e:
            print("{} - {}".format(time_now, repr(e)), file=open('error_log', 'a'))
        time.sleep(0.01)

team_done = None
last_match_url = None
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

"""   
if pd.read_csv(unclean_csv).size > 2:
    unclean_unfinished_data = pd.read_csv(unclean_csv)
    last_data = unclean_unfinished_data.iloc[-1,3:5]
    last_data2 = unclean_unfinished_data.iloc[-2,3:5]
    league = unclean_unfinished_data.iloc[-1,0]     # All leagues before this are supposed to be ready.
    team_done = list(set(last_data) & set(last_data2))[0]
    # Remove already done leagues from the dict (unclean)
    for league_id in list(potential_leagues.keys()):
        if league_id != league:
            del potential_leagues[league_id]
            time_now = datetime.utcnow().replace(tzinfo=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
            print("{} - Removed: {}".format(time_now, league_id), file=open('stdout.log', 'a'))
        else:
            break

# Start looping through the filtered (or original) league dict.
for league_id,league_url in potential_leagues.items():    
    #if league_id == 'fr_ligue2':
        #break
    while True:
        time.sleep(0.01)
        try:
            driver = webdriver.Firefox(firefox_profile=webdriver.FirefoxProfile('profile.default'))
            driver.get(league_url)
            break
        except WebDriverException as e:
            time_now = datetime.utcnow().replace(tzinfo=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
            print("{} - {}".format(time_now, repr(e)), file=open('error_log', 'a'))
        time.sleep(0.01)
    
    # Closing pop-up about accepting cookies
    close_popup(driver)

    # Remove already done teams from the list
    teams = driver.find_element_by_xpath("//div[starts-with(@id, 'page_competition_1_block_competition_tables_')]").find_elements_by_class_name("team_rank")
    if team_done:
        for team in teams[:]:
            if team.find_element_by_class_name('team').text != team_done:
                teams.remove(team)
            else:
                team_done = None    # Resetting back to None so our script will not remove all matches from next leagues
                break
    teams_urls = [team.find_element_by_class_name('team').find_element_by_tag_name('a').get_attribute('href') for team in teams]
    
    # Start iterating on the cleaned data
    for team_url in teams_urls:
        #if team_url == teams_urls[1]:
            #break
        try:
            driver.get(team_url)
        except Exception as e:
            print("{} - {}".format(time_now, repr(e)), file=open('error_log', 'a'))
            driver = webdriver.Firefox(firefox_profile=webdriver.FirefoxProfile('profile.default'))
            driver.get(team_url)
            close_popup(driver)

        # Initialize some variables
        very_first_match_date = None
        first_match_reached = False
        
        while not first_match_reached:
            time.sleep(0.01)
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
            while True:
                time.sleep(0.01)
                time_now = datetime.utcnow().replace(tzinfo=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
                try:
                    button = driver.find_element_by_xpath("//a[@id='page_team_1_block_team_matches_summary_7_previous']")
                    if not "disabled" in button.get_attribute('class'):
                        button.click()
                        break
                    else: # First match reached ahead of time, due to disabled 'previous' button
                        first_match_reached = True
                        break
                except Exception as e:
                    print("{} - {}".format(time_now, repr(e)), file=open('error_log', 'a'))
                time.sleep(0.01)
            time.sleep(0.01)
                    
        # Close browser so that the computer can recover and open fresh
        driver.close()
        driver.quit()
        time_now = datetime.utcnow().replace(tzinfo=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
        print("{} - Closed the browser to start next round".format(time_now), file=open('stdout.log', 'a'))
        time.sleep(0.5)
"""

# Doing things the faster way
import requests
from lxml import etree

# Finding league to continue from
if pd.read_csv(clean_csv).size > 2:
    clean_unfinished_data = pd.read_csv(clean_csv)
    last_teams = clean_unfinished_data.iloc[-1,3:5]
    last_teams2 = clean_unfinished_data.iloc[-2,3:5]
    league = clean_unfinished_data.iloc[-1,0]     # All leagues before this are supposed to be ready.
    team_done = list(set(last_teams) & set(last_teams2))[0]
    # Remove already done leagues from the dict (unclean)
    for league_id in list(potential_leagues.keys()):
        if league_id != league:
            del potential_leagues[league_id]
            time_now = datetime.utcnow().replace(tzinfo=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
            print("{} - Removed: {}".format(time_now, league_id), file=open('stdout.log', 'a'))
        else:
            # When we got to our current league, find match to continue from
            last_match_url = clean_unfinished_data.iloc[-1,2]
            break

# Start looping through the filtered (or original) league dict.
for league_id,league_url in potential_leagues.items():    
    #if league_id == 'fr_ligue2':
        #break
    # After looping through all the teams in a league, remove duplicates and then proceed
    all_matches_unclean = pd.read_csv(unclean_csv)
    all_matches_clean = all_matches_unclean[all_matches_unclean['league_id'] == league_id].drop_duplicates()

    # Finding match to continue from
    if last_match_url:
        for idx, match in all_matches_clean.iterrows():
            if match['match_url'] != last_match_url:
                # While we haven't reached last match, keep removing matches
                all_matches_clean = all_matches_clean.drop([idx])
            else:
                # When we reached the last match, remove it, and break out of loop
                all_matches_clean = all_matches_clean.drop([idx])
                last_match_url = None
                break

    # Loop through all matches in filtered list and gather extra data.
    for idx, unique_match in all_matches_clean.iterrows():
        #if idx == 1:
            #break
        #Need to disable verifying ssl.Be careful!
        r = requests.get(unique_match['match_url'],verify=False)
        dom = etree.HTML(r.text)
        match_id = unique_match['match_url'].split('/')[-2]
        try:
            half_time = dom.xpath("//dl[dt='Half-time']/dd[1]/text()")[0]
            unique_match = unique_match.append(pd.Series({"half_time_score": half_time}))
        except Exception as e:
            time_now = datetime.utcnow().replace(tzinfo=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
            print("{} - Skipping match: {}, because: {} (not having half-time score)"
                  .format(time_now, unique_match['match_url'], repr(e)), file=open('error_log', 'a'))
            continue

        # Get contents of the stats table:
        try:
            stats = requests.get('https://us.soccerway.com/charts/statsplus/{}/'.format(match_id),verify=False)
            inner_dom = etree.HTML(stats.text)
        except Exception as e:
            time_now = datetime.utcnow().replace(tzinfo=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
            match_date = str(datetime.utcfromtimestamp(unique_match['match_time'] / 1000.0).strftime("%Y-%m-%d"))
            print("{} - {} - {} at {} didn't have stats table, skipping. Here's the original error:"
                    .format(time_now, unique_match['home_team'], unique_match['away_team'], match_date), file=open('error_log', 'a'))
            print(repr(e), file=open('error_log', 'a'))
            continue
        # Gather stats
        home_corners = str(inner_dom.xpath("//td[text()='Corners']/preceding-sibling::td/text()")[0])
        away_corners = str(inner_dom.xpath("//td[text()='Corners']/following-sibling::td/text()")[0])
        unique_match = unique_match.append(pd.Series({"corners": "{} - {}".format(home_corners, away_corners)}))
        
        home_offsides = str(inner_dom.xpath("//td[text()='Offsides']/preceding-sibling::td/text()")[0])
        away_offsides = str(inner_dom.xpath("//td[text()='Offsides']/following-sibling::td/text()")[0])
        unique_match = unique_match.append(pd.Series({"offsides": "{} - {}".format(home_offsides, away_offsides)}))
        
        home_shots_on_target = str(inner_dom.xpath("//td[text()='Shots on target']/preceding-sibling::td/text()")[0])
        away_shots_on_target = str(inner_dom.xpath("//td[text()='Shots on target']/following-sibling::td/text()")[0])
        unique_match = unique_match.append(pd.Series({"shots_on_target": "{} - {}".format(home_shots_on_target, away_shots_on_target)}))
        
        home_fouls = str(inner_dom.xpath("//td[text()='Fouls']/preceding-sibling::td/text()")[0])
        away_fouls = str(inner_dom.xpath("//td[text()='Fouls']/following-sibling::td/text()")[0])
        unique_match = unique_match.append(pd.Series({"fouls": "{} - {}".format(home_fouls, away_fouls)}))
        
        with open(clean_csv, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(unique_match.values[:])
    
    # Finished with current league, log it.
    time_now = datetime.utcnow().replace(tzinfo=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
    print("{} - Finished dealing with league '{}' (clean stage)".format(time_now, league_id), file=open('stdout.log', 'a'))
    time.sleep(0.5)


    
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

