from datetime import datetime, timezone
import pytz
import time
import copy
import json,csv
import os
import pandas as pd
import numpy as np
import traceback

# Doing things the faster way
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
from lxml import etree

from var_scraper import *


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

def wait_for_page_refresh(very_first_match_date, driver):
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


def browse_leagues_for_matches():
    team_done = None
    # Create unclean file if not existing
    if not os.path.isfile(unclean_csv):
        with open(unclean_csv, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(matches_unclean_headers)
    # Finding league and team to continue from
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
                last_10_matches, very_first_match_date = wait_for_page_refresh(very_first_match_date, driver)
                
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
        driver.close()
        driver.quit()


def browse_matches_for_stats():
    last_match_url = None
    # Create clean file if not existing
    if not os.path.isfile(clean_csv):
        with open(clean_csv, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(matches_clean_headers) 
    # Finding league and team to continue from
    if pd.read_csv(clean_csv).size > 2:
        clean_unfinished_data = pd.read_csv(clean_csv)
        league = clean_unfinished_data.iloc[-1,0]     # All leagues before this are supposed to be ready.
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
            time_now = datetime.utcnow().replace(tzinfo=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
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
                print("{} - Skipping match: {}, because: {} (not having half-time score)"
                    .format(time_now, unique_match['match_url'], repr(e)), file=open('error_log', 'a'))
                continue

            # Get contents of the stats table:
            try:
                stats = requests.get('https://us.soccerway.com/charts/statsplus/{}/'.format(match_id),verify=False)
                inner_dom = etree.HTML(stats.text)
            except Exception as e:
                match_date = str(datetime.utcfromtimestamp(unique_match['match_time'] / 1000.0).strftime("%Y-%m-%d"))
                print("{} - {} - {} at {} didn't have stats table, skipping. Here's the original error:"
                        .format(time_now, unique_match['home_team'], unique_match['away_team'], match_date), file=open('error_log', 'a'))
                print(repr(e), file=open('error_log', 'a'))
                continue

            # Gather stats
            try:
                home_corners = str(inner_dom.xpath("//td[text()='Corners']/preceding-sibling::td/text()")[0])
            except Exception as e:
                print("{} - Different stats format for match (also not all data available), continuing: {}"
                    .format(time_now, unique_match['match_url']), file=open('error_log', 'a'))
                continue
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
full_time_score_frequencies = all_matches_clean['full_time_score'].value_counts()
full_time_score_freq_perc = full_time_score_frequencies / full_time_score_frequencies.sum()
half_time_score_frequencies = all_matches_clean['half_time_score'].value_counts()
half_time_score_freq_perc = half_time_score_frequencies / half_time_score_frequencies.sum()

matches_draw = np.sum(a['full_time_score'].isin(["0 - 0", "1 - 1", "2 - 2", "3 - 3"]))
matches_10 = np.sum(a['full_time_score'].isin(["1 - 0", "2 - 1", "3 - 2", "4 - 3"]))
matches_01 = np.sum(a['full_time_score'].isin(["0 - 1", "1 - 2", "2 - 3", "3 - 4"]))

full_times_scores = []
half_times_scores = []
for league_id in potential_leagues:
    current_league_matches = all_matches_clean[all_matches_clean['league_id'] == league_id]
    current_league_full_time_score_frequencies = current_league_matches['full_time_score'].value_counts()
    current_league_full_time_score_frequencies = current_league_full_time_score_frequencies.rename(league_id)
    full_times_scores.append(current_league_full_time_score_frequencies)
    
    current_league_half_time_score_frequencies = current_league_matches['half_time_score'].value_counts()
    current_league_half_time_score_frequencies = current_league_half_time_score_frequencies.rename(league_id)
    half_times_scores.append(current_league_half_time_score_frequencies)
    
full_times_scores = pd.concat(full_times_scores, axis=1, sort=False)
half_times_scores = pd.concat(half_times_scores, axis=1, sort=False)
"""


def extract_scores(match, matches_before, stat_to_extract, team):
    if team == 'home_team':
        return sum([int(m[stat_to_extract].strip().split()[0]) \
                   if m[team] == match[team] \
                   else int(m[stat_to_extract].strip().split()[-1]) \
                   for i, m in matches_before.iterrows()])
    else: # away_team
        return sum([int(m[stat_to_extract].strip().split()[-1]) \
                   if m[team] == match[team] \
                   else int(m[stat_to_extract].strip().split()[0]) \
                   for i, m in matches_before.iterrows()])


def prepare_data_for_ML():
    data_for_ML = []
    matches_behind = 3
    all_matches_clean = pd.read_csv('all_matches_clean.csv')
    for league_id in potential_leagues:
        current_league_matches = all_matches_clean[all_matches_clean['league_id'] == league_id].sort_values('match_time').reset_index(drop=True)        
        for idx, match in current_league_matches.iterrows():
            try:
                # Find all matches having any of the current teams from before its match_time
                matches_before = current_league_matches[current_league_matches['match_time'] < match['match_time']]
                matches_before_home_team = matches_before[(matches_before['home_team'] == match['home_team']) | \
                                                          (matches_before['away_team'] == match['home_team'])][-matches_behind:]
                matches_before_away_team = matches_before[(matches_before['home_team'] == match['away_team']) | \
                                                          (matches_before['away_team'] == match['away_team'])][-matches_behind:]
                if len(matches_before_home_team) == matches_behind and len(matches_before_away_team) == matches_behind:
                    # Home team stats
                    home_team_goals_full_time = extract_scores(match, matches_before_home_team, 'full_time_score', 'home_team')
                    home_team_goals_half_time = extract_scores(match, matches_before_home_team, 'half_time_score', 'home_team')
                    home_team_corners = extract_scores(match, matches_before_home_team, 'corners', 'home_team')
                    home_team_offsides = extract_scores(match, matches_before_home_team, 'offsides', 'home_team')
                    home_team_shots_on_target = extract_scores(match, matches_before_home_team, 'shots_on_target', 'home_team')
                    home_team_fouls = extract_scores(match, matches_before_home_team, 'fouls', 'home_team')
                    
                    # Away team stats
                    away_team_goals_full_time = extract_scores(match, matches_before_away_team, 'full_time_score', 'away_team')
                    away_team_goals_half_time = extract_scores(match, matches_before_away_team, 'half_time_score', 'away_team')
                    away_team_corners = extract_scores(match, matches_before_away_team, 'corners', 'away_team')
                    away_team_offsides = extract_scores(match, matches_before_away_team, 'offsides', 'away_team')
                    away_team_shots_on_target = extract_scores(match, matches_before_away_team, 'shots_on_target', 'away_team')
                    away_team_fouls = extract_scores(match, matches_before_away_team, 'fouls', 'away_team')
                else:
                    continue
                
                if int(match['full_time_score'].strip().split()[0]) - int(match['full_time_score'].strip().split()[-1]) == 0:
                    match_outcome_full_time = 0
                elif int(match['full_time_score'].strip().split()[0]) - int(match['full_time_score'].strip().split()[-1]) == 1:
                    match_outcome_full_time = 1
                elif int(match['full_time_score'].strip().split()[0]) - int(match['full_time_score'].strip().split()[-1]) == -1:
                    match_outcome_full_time = -1
                elif int(match['full_time_score'].strip().split()[0]) - int(match['full_time_score'].strip().split()[-1]) == 2:
                    match_outcome_full_time = 2
                elif int(match['full_time_score'].strip().split()[0]) - int(match['full_time_score'].strip().split()[-1]) == -2:
                    match_outcome_full_time = -2
                else:
                    match_outcome_full_time = 3
                    
                if int(match['half_time_score'].strip().split()[0]) - int(match['half_time_score'].strip().split()[-1]) == 0:
                    match_outcome_half_time = 0
                elif int(match['half_time_score'].strip().split()[0]) - int(match['half_time_score'].strip().split()[-1]) == 1:
                    match_outcome_half_time = 1
                elif int(match['half_time_score'].strip().split()[0]) - int(match['half_time_score'].strip().split()[-1]) == -1:
                    match_outcome_half_time = -1
                elif int(match['half_time_score'].strip().split()[0]) - int(match['half_time_score'].strip().split()[-1]) == 2:
                    match_outcome_half_time = 2
                elif int(match['half_time_score'].strip().split()[0]) - int(match['half_time_score'].strip().split()[-1]) == -2:
                    match_outcome_half_time = -2
                else:
                    match_outcome_half_time = 3
                
                data_for_ML.append(pd.Series({'league_id': match.league_id, 'match_time': match.match_time, 'match_url': match.match_url,
                                              'home_team': match.home_team, 'away_team': match.away_team, 'full_time_score': match.full_time_score,
                                              'half_time_score': match.half_time_score, 
                                              'home_team_goals_full_time': home_team_goals_full_time, 'home_team_goals_half_time': home_team_goals_half_time,
                                              'home_team_corners': home_team_corners, 'home_team_offsides': home_team_offsides, 
                                              'home_team_shots_on_target': home_team_shots_on_target, 'home_team_fouls': home_team_fouls,
                                              'away_team_goals_full_time': away_team_goals_full_time, 'away_team_goals_half_time': away_team_goals_half_time,
                                              'away_team_corners': away_team_corners, 'away_team_offsides': away_team_offsides, 
                                              'away_team_shots_on_target': away_team_shots_on_target, 'away_team_fouls': away_team_fouls,
                                              'match_outcome_full_time': match_outcome_full_time, 'match_outcome_half_time': match_outcome_half_time}))
            except Exception:
                print(traceback.print_exc())
        
    data_for_ML_csv = pd.concat(data_for_ML, axis=1, sort=False).transpose()
    data_for_ML_csv.to_csv('matches_ready_for_ML.csv', index=False)