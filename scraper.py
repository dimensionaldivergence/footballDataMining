#!/usr/bin/env python3
from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import time
import copy

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

def close_popup(webdriver):
    while True:
        try:
            consent_button = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//div[@id='qcCmpButtons']//button[@class='qc-cmp-button']")))
            consent_button.click()
            break
        except Exception as e:
            print("There was no consent button. But here's the original error:\n{}".format(repr(e)))
            time.sleep(0.5)

all_matches_unclean = {k: [] for k,v in potential_leagues.items()}
all_matches_clean = {k: [] for k,v in potential_leagues.items()}

for league_id,league_url in potential_leagues.items():    
    if league_id == 'fr_ligue2':
        break
    driver = webdriver.Firefox(firefox_profile=firefox_profile)
    driver.get(league_url)
    
    # Closing pop-up about accepting cookies
    close_popup(driver)

    teams = driver.find_elements_by_class_name('team_rank')
    for team in teams:
        if team == teams[1]:
            break
        team_url = team.find_element_by_class_name('team').find_element_by_tag_name('a').get_attribute('href')        
        driver.get(team_url)

        # Initialize some variables
        very_first_match_date = None
        first_match_reached = False
        
        while not first_match_reached:
            # Checking if new data present on page (either in the beginning or after button click)
            while True:
                try:
                    last_10_matches = driver.find_elements_by_css_selector("tr[id^='page_team_1_block_team_matches_summary_7']")
                    if very_first_match_date != last_10_matches[0].find_element_by_class_name("full-date").text:
                        print("New data present on page.")
                        very_first_match_date = last_10_matches[0].find_element_by_class_name("full-date").text
                        break
                    else:
                        raise Exception()
                except:
                    print("Page hasn't refreshed yet.")
                    time.sleep(0.5)
            
            for element in last_10_matches:
                match_time_unchecked = element.find_element_by_class_name("full-date").text
                match_time_ms = int(datetime.strptime(match_time_unchecked, '%d/%m/%y').replace(tzinfo=timezone.utc).timestamp() * 1000)
                if match_time_ms < int(datetime(2017, 1, 1).replace(tzinfo=timezone.utc).timestamp() * 1000):
                    first_match_reached = True
                home_team = element.find_element_by_class_name("team-a").text
                away_team = element.find_element_by_class_name("team-b").text
                score = element.find_element_by_class_name("score-time").text
                if ":" in score:        # Future matches reached
                    break
                elif "PSTP" in score:   # Postponed match, skip
                    continue
                match_url = element.find_element_by_class_name("score-time").find_element_by_tag_name('a').get_attribute('href')
                all_matches_unclean[league_id].append({'match_time': match_time_ms,
                                            'home_team': home_team, 
                                            'away_team': away_team, 
                                            'score': score,
                                            'match_url': match_url})
            
            button = driver.find_element_by_class_name("previous ").click()
            # Be kind to soccerway..
            time.sleep(0.5)
        
    # After looping through all the teams in a league, remove duplicates and then proceed
    all_matches_clean[league_id] = [i for idx,i in enumerate(all_matches_unclean[league_id]) if i not in all_matches_unclean[league_id][idx+1:]]
    
    # Loop through all matches in filtered list and gather extra data.
    for unique_match in all_matches_clean['fr_ligue1']:
        if unique_match == all_matches_clean['fr_ligue1'][1]:
            break
        driver.get(unique_match['match_url'])
        match_id = unique_match['match_url'].split('/')[-2]
        half_time = driver.find_element_by_xpath("//dl[dt='Half-time']/dd[1]").text
        
        # Switch focus to stats table:        
        stats = driver.find_element_by_xpath("//div//iframe[@src='/charts/statsplus/{}/']".format(match_id))
        driver.switch_to.frame(stats)
        # Home stats
        home_corners = driver.find_element_by_xpath("//td[text()='Corners']/preceding-sibling::td").text
        home_offsides = driver.find_element_by_xpath("//td[text()='Offsides']/preceding-sibling::td").text
        home_shots_on_target = driver.find_element_by_xpath("//td[text()='Shots on target']/preceding-sibling::td").text
        home_fouls = driver.find_element_by_xpath("//td[text()='Fouls']/preceding-sibling::td").text
        # Away stats
        away_corners = driver.find_element_by_xpath("//td[text()='Corners']/following-sibling::td").text
        away_shots_on_target = driver.find_element_by_xpath("//td[text()='Shots on target']/following-sibling::td").text
        away_fouls = driver.find_element_by_xpath("//td[text()='Fouls']/following-sibling::td").text
        away_offsides = driver.find_element_by_xpath("//td[text()='Offsides']/following-sibling::td").text
        # Switch focus back        
        driver.switch_to.default_content()
        
        

                            

        
    
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