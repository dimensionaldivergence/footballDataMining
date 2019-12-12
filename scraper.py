#!/usr/bin/env python3
from lib_scraper import *


#browse_matches_for_stats()

prepare_data_for_ML(matches_behind=5, categories="draw_and_handicap")

    
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

