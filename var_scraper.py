from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

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

clean_csv = 'all_matches_clean.csv'
unclean_csv = 'all_matches_unclean.csv'

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
