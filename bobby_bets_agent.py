from langchain_community.document_loaders.firecrawl import FireCrawlLoader
from langchain.agents import AgentExecutor, create_openai_tools_agent, AgentType, initialize_agent
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import AgentAction, AgentFinish
from langchain.agents.agent import AgentOutputParser
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
import re
from datetime import datetime, timedelta
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.messages import BaseMessage
import concurrent.futures
import os
import warnings

# Filter out the specific deprecation warning from mem0
warnings.filterwarnings("ignore", message="Using default output format 'v1.0' is deprecated")

from mem0 import MemoryClient

OPEN_AI_API = '{PUT OPEN AI API KEY HERE}'

# Initialize Mem0 client
MEM0_API_KEY = "m0-qwD2FjEl5Y4ex0RCXkSBv9e5tfsRPYLASr7pFgzs"
os.environ["MEM0_API_KEY"] = MEM0_API_KEY
memory_client = MemoryClient()

# Set up the FireCrawl with provided API key
FIRECRAWL_API_KEY = "fc-98fd4caa098e4c9e96e7d2cbe51259c2"

# Dictionary mapping team names to their ESPN team codes
TEAM_CODES = {
    "hawks": "atl", "atlanta": "atl",
    "celtics": "bos", "boston": "bos",
    "nets": "bkn", "brooklyn": "bkn",
    "hornets": "cha", "charlotte": "cha",
    "bulls": "chi", "chicago": "chi",
    "cavaliers": "cle", "cleveland": "cle",
    "mavericks": "dal", "dallas": "dal",
    "nuggets": "den", "denver": "den",
    "pistons": "det", "detroit": "det",
    "warriors": "gsw", "golden state": "gsw",
    "rockets": "hou", "houston": "hou",
    "pacers": "ind", "indiana": "ind",
    "clippers": "lac", "la clippers": "lac",
    "lakers": "lal", "los angeles lakers": "lal", "la lakers": "lal",
    "grizzlies": "mem", "memphis": "mem",
    "heat": "mia", "miami": "mia",
    "bucks": "mil", "milwaukee": "mil",
    "timberwolves": "min", "minnesota": "min",
    "pelicans": "no", "new orleans": "no",
    "knicks": "ny", "new york": "ny",
    "thunder": "okc", "oklahoma city": "okc",
    "magic": "orl", "orlando": "orl",
    "76ers": "phi", "philadelphia": "phi", "sixers": "phi",
    "suns": "phx", "phoenix": "phx",
    "trail blazers": "por", "portland": "por",
    "kings": "sac", "sacramento": "sac",
    "spurs": "sa", "san antonio": "sa",
    "raptors": "tor", "toronto": "tor",
    "jazz": "utah", "utah": "utah",
    "wizards": "wsh", "washington": "wsh"
}

# Dictionary mapping team names to their Basketball Reference codes
BBALL_REF_CODES = {
    "hawks": "ATL", "atlanta": "ATL",
    "celtics": "BOS", "boston": "BOS",
    "nets": "BKN", "brooklyn": "BKN",
    "hornets": "CHA", "charlotte": "CHA",
    "bulls": "CHI", "chicago": "CHI",
    "cavaliers": "CLE", "cleveland": "CLE",
    "mavericks": "DAL", "dallas": "DAL",
    "nuggets": "DEN", "denver": "DEN",
    "pistons": "DET", "detroit": "DET",
    "warriors": "GSW", "golden state": "GSW",
    "rockets": "HOU", "houston": "HOU",
    "pacers": "IND", "indiana": "IND",
    "clippers": "LAC", "la clippers": "LAC",
    "lakers": "LAL", "los angeles lakers": "LAL", "la lakers": "LAL",
    "grizzlies": "MEM", "memphis": "MEM",
    "heat": "MIA", "miami": "MIA",
    "bucks": "MIL", "milwaukee": "MIL",
    "timberwolves": "MIN", "minnesota": "MIN",
    "pelicans": "NOP", "new orleans": "NOP",
    "knicks": "NYK", "new york": "NYK",
    "thunder": "OKC", "oklahoma city": "OKC",
    "magic": "ORL", "orlando": "ORL",
    "76ers": "PHI", "philadelphia": "PHI", "sixers": "PHI",
    "suns": "PHX", "phoenix": "PHX",
    "trail blazers": "POR", "portland": "POR",
    "kings": "SAC", "sacramento": "SAC",
    "spurs": "SAS", "san antonio": "SAS",
    "raptors": "TOR", "toronto": "TOR",
    "jazz": "UTA", "utah": "UTA",
    "wizards": "WAS", "washington": "WAS"
}

# Dictionary mapping team names to their scores24.live format
SCORES24_TEAM_NAMES = {
    "hawks": "atlanta-hawks", "atlanta": "atlanta-hawks",
    "celtics": "boston-celtics", "boston": "boston-celtics",
    "nets": "brooklyn-nets", "brooklyn": "brooklyn-nets",
    "hornets": "charlotte-hornets", "charlotte": "charlotte-hornets",
    "bulls": "chicago-bulls", "chicago": "chicago-bulls",
    "cavaliers": "cleveland-cavaliers", "cleveland": "cleveland-cavaliers",
    "mavericks": "dallas-mavericks", "dallas": "dallas-mavericks",
    "nuggets": "denver-nuggets", "denver": "denver-nuggets",
    "pistons": "detroit-pistons", "detroit": "detroit-pistons",
    "warriors": "golden-state-warriors", "golden state": "golden-state-warriors",
    "rockets": "houston-rockets", "houston": "houston-rockets",
    "pacers": "indiana-pacers", "indiana": "indiana-pacers",
    "clippers": "los-angeles-clippers", "la clippers": "los-angeles-clippers",
    "lakers": "los-angeles-lakers", "los angeles lakers": "los-angeles-lakers", "la lakers": "los-angeles-lakers",
    "grizzlies": "memphis-grizzlies", "memphis": "memphis-grizzlies",
    "heat": "miami-heat", "miami": "miami-heat",
    "bucks": "milwaukee-bucks", "milwaukee": "milwaukee-bucks",
    "timberwolves": "minnesota-timberwolves", "minnesota": "minnesota-timberwolves",
    "pelicans": "new-orleans-pelicans", "new orleans": "new-orleans-pelicans",
    "knicks": "new-york-knicks", "new york": "new-york-knicks",
    "thunder": "oklahoma-city-thunder", "oklahoma city": "oklahoma-city-thunder",
    "magic": "orlando-magic", "orlando": "orlando-magic",
    "76ers": "philadelphia-76ers", "philadelphia": "philadelphia-76ers", "sixers": "philadelphia-76ers",
    "suns": "phoenix-suns", "phoenix": "phoenix-suns",
    "trail blazers": "portland-trail-blazers", "portland": "portland-trail-blazers",
    "kings": "sacramento-kings", "sacramento": "sacramento-kings",
    "spurs": "san-antonio-spurs", "san antonio": "san-antonio-spurs",
    "raptors": "toronto-raptors", "toronto": "toronto-raptors",
    "jazz": "utah-jazz", "utah": "utah-jazz",
    "wizards": "washington-wizards", "washington": "washington-wizards"
}

@tool
def fetch_team_schedule(teams_and_params: str) -> str:
    """
    Fetch games between two teams from Basketball Reference.
    Format: "team1 team2 [date=YYYY-MM-DD]"
    Only returns games where these two teams play against each other.
    If date is provided, will look for games on or near that date.
    If the exact date doesn't have a game, automatically uses the closest game date.
    """
    # Parse the input string to extract team names and date
    params = teams_and_params.split()
    
    # Extract optional date parameter first
    game_date = None
    team_parts = []
    
    for param in params:
        if param.startswith("date="):
            game_date = param.split("=")[1]
        else:
            # If not a parameter, it's part of the team names
            team_parts.append(param.lower())
    
    # Extract team names using the extract_team_names function
    teams_info = extract_team_names.invoke({"text": " ".join(team_parts)})
    
    if 'error' in teams_info:
        return "Could not identify two team names in the input. Please provide both team names clearly."
    
    if 'team2' not in teams_info:
        return "Please provide two team names to find games between them."
    
    # We'll use team1 as the primary team to look up the schedule
    team1_name = teams_info['team1']
    team2_name = teams_info['team2']
    
    # Helper function to get team code from team name
    def get_team_code(team_name):
        if team_name in BBALL_REF_CODES:
            return BBALL_REF_CODES[team_name]
        else:
            # Try each part of the name
            for part in team_name.split():
                if part in BBALL_REF_CODES:
                    return BBALL_REF_CODES[part]
        return None

    # Helper function to fetch a team's schedule
    def fetch_schedule(team_name, team_code):
        url = f"https://www.basketball-reference.com/teams/{team_code}/2025_games.html"
        
        try:
            # Use FireCrawl to get the content
            loader = FireCrawlLoader(
                api_key=FIRECRAWL_API_KEY,
                url=url,
                mode="scrape"
            )
            
            documents = loader.load()
            if not documents or len(documents) == 0:
                return None
            
            content = documents[0].page_content
            
            # Extract the schedule table
            schedule_match = re.search(r'## Regular Season\s*(.*?)(?=##|\Z)', content, re.DOTALL)
            if not schedule_match:
                schedule_match = re.search(r'Regular Season Table(.*?)(?=\n\n\n|\Z)', content, re.DOTALL)
            
            if not schedule_match:
                return None
            
            schedule_table = schedule_match.group(1).strip()
            
            # Parse the table rows
            rows = schedule_table.split('\n')
            if len(rows) < 3:
                return None
            
            # Find the header row
            header_row_index = -1
            for i, row in enumerate(rows):
                if '|' in row and 'G' in row and 'Date' in row and 'Opponent' in row:
                    header_row_index = i
                    break
            
            if header_row_index == -1:
                return None
            
            # Process each game row
            games = []
            
            # Skip header row and separator row
            for row in rows[header_row_index + 2:]:
                if '|' not in row:
                    continue
                    
                columns = row.split('|')
                if len(columns) < 10:
                    continue
                
                # Clean up columns
                columns = [col.strip() for col in columns]
                
                # Extract game information
                game_num = columns[1].strip() if len(columns) > 1 else "N/A"
                
                # Extract date
                date_text = columns[2].strip() if len(columns) > 2 else ""
                date_match = re.search(r'\[(.*?)\]', date_text)
                if date_match:
                    date_text = date_match.group(1)
                
                # Parse the date
                date_parts_match = re.search(r'([A-Za-z]+),\s+([A-Za-z]+)\s+(\d+),\s+(\d{4})', date_text)
                if date_parts_match:
                    weekday, month, day, year = date_parts_match.groups()
                    month_num = {
                        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                    }.get(month, 1)
                    game_date_obj = datetime(int(year), month_num, int(day))
                    formatted_date = game_date_obj.strftime('%Y-%m-%d')
                else:
                    formatted_date = "Unknown date"
                    game_date_obj = None
                
                # Extract opponent name
                opponent_col = -1
                for i, col in enumerate(columns):
                    if "Opponent" in col or (i > 5 and any(team in col for team in ["Lakers", "Bulls", "Knicks", "Spurs", "Warriors", "Rockets"])):
                        opponent_col = i
                        break
                
                if opponent_col == -1:
                    opponent_col = 7 if len(columns) > 7 else -1
                
                if opponent_col != -1 and opponent_col < len(columns):
                    opp_text = columns[opponent_col].strip()
                    opp_match = re.search(r'\[(.*?)\]', opp_text)
                    opp_name = opp_match.group(1) if opp_match else opp_text
                else:
                    opp_name = "Unknown opponent"
                
                # Determine home/away
                location = "Away" if "@" in opp_name else "Home"
                
                # Extract result (W/L)
                result = ""
                result_col = 8 if len(columns) > 8 else -1
                if result_col != -1 and result_col < len(columns):
                    result = columns[result_col].strip()
                
                # Extract scores
                team_score = "N/A"
                opp_score = "N/A"
                if len(columns) > 10:
                    team_score = columns[10].strip()
                if len(columns) > 11:
                    opp_score = columns[11].strip()
                
                # Create game dictionary
                game = {
                    'game_num': game_num,
                    'date': formatted_date,
                    'date_obj': game_date_obj,
                    'opponent': opp_name,
                    'location': location,
                    'result': result,
                    'team_score': team_score,
                    'opp_score': opp_score
                }
                
                games.append(game)
            
            return games
            
        except Exception as e:
            return None

    # Get team codes
    team1_code = get_team_code(team1_name)
    team2_code = get_team_code(team2_name)
    
    if not team1_code:
        return f"Could not find team code for {team1_name}. Please use a valid team name."
    
    if not team2_code:
        return f"Could not find team code for {team2_name}. Please use a valid team name."
    
    # Store the original requested date for reference
    original_date = game_date
    adjusted_date = None
    
    # Fetch the schedule for team1
    try:
        # Get all games for team1
        all_games_team1 = fetch_schedule(team1_name, team1_code)
        
        if not all_games_team1:
            # Fall back to generic message if we couldn't fetch team1's schedule
            return f"Unable to fetch schedule data for {team1_name.title()} at this time. The service may be experiencing high traffic or temporary issues. Please try again later."
        
        # Get all games for team2
        all_games_team2 = fetch_schedule(team2_name, team2_code)
        
        # Find games between team1 and team2 from team1's schedule
        matchup_games_team1 = []
        for game in all_games_team1:
            is_matchup = False
            for part in team2_name.split():
                if part.lower() in game['opponent'].lower():
                    is_matchup = True
                    break
            
            if is_matchup:
                matchup_games_team1.append(game)
        
        # Find games between team1 and team2 from team2's schedule (to get the complete picture)
        matchup_games_team2 = []
        if all_games_team2:
            for game in all_games_team2:
                is_matchup = False
                for part in team1_name.split():
                    if part.lower() in game['opponent'].lower():
                        is_matchup = True
                        break
                
                if is_matchup:
                    # Invert the result since these are from team2's perspective
                    inverted_result = ""
                    if game['result'] == 'W':
                        inverted_result = 'L'  # If team2 won, it means team1 lost
                    elif game['result'] == 'L':
                        inverted_result = 'W'  # If team2 lost, it means team1 won
                    
                    # Adjust the game from team2's perspective
                    adjusted_game = {
                        'game_num': game['game_num'],
                        'date': game['date'],
                        'date_obj': game['date_obj'],
                        'opponent': team2_name.title(),  # This is from team1's perspective
                        'location': "Home" if game['location'] == "Away" else "Away",  # Invert location
                        'result': inverted_result,
                        'team_score': game['opp_score'],  # Swap scores
                        'opp_score': game['team_score']
                    }
                    matchup_games_team2.append(adjusted_game)
        
        # Combine and deduplicate matchup games from both schedules
        matchup_games = []
        date_tracker = set()
        
        # Add games from team1's schedule
        for game in matchup_games_team1:
            if game['date'] not in date_tracker:
                date_tracker.add(game['date'])
                matchup_games.append(game)
        
        # Add games from team2's schedule that aren't already included
        for game in matchup_games_team2:
            if game['date'] not in date_tracker:
                date_tracker.add(game['date'])
                matchup_games.append(game)
        
        # Sort matchup games by date
        matchup_games.sort(key=lambda g: g['date_obj'] if g['date_obj'] else datetime.min)
        
        if not matchup_games:
            return f"No games found between {team1_name.title()} and {team2_name.title()} in the 2024-2025 season. Please check the team names or consider a different matchup."
        
        # Calculate head-to-head record
        team1_wins = 0
        team2_wins = 0
        
        for game in matchup_games:
            if game['result'] == 'W':
                team1_wins += 1
            elif game['result'] == 'L':
                team2_wins += 1
        
        # Generate head-to-head record string
        if team1_wins > 0 or team2_wins > 0:
            if team1_wins > team2_wins:
                h2h_record = f"{team1_name.title()} leads {team1_wins}-{team2_wins}"
            elif team2_wins > team1_wins:
                h2h_record = f"{team2_name.title()} leads {team2_wins}-{team1_wins}"
            else:
                h2h_record = f"Series tied {team1_wins}-{team2_wins}"
        else:
            h2h_record = "No previous matchups this season"
        
        # Find the closest game to the requested date
        closest_game = None
        closest_date_diff = float('inf')
        exact_date_match = False
        
        if game_date:
            try:
                target_date = datetime.strptime(game_date, '%Y-%m-%d')
                
                for game in matchup_games:
                    if game['date_obj']:
                        if game['date_obj'].date() == target_date.date():
                            exact_date_match = True
                            closest_game = game
                            closest_date_diff = 0
                            break
                        else:
                            date_diff = abs((game['date_obj'] - target_date).days)
                            if date_diff < closest_date_diff:
                                closest_date_diff = date_diff
                                closest_game = game
                
            except ValueError:
                return f"Invalid date format: {game_date}. Please use YYYY-MM-DD."
        
        # Handle specific date query
        if game_date:
            if exact_date_match or closest_game:
                # Use the matched game
                match_game = closest_game
                
                # Set the adjusted date
                adjusted_date = match_game['date'] if not exact_date_match else game_date
                
                # Calculate rest days for team1
                team1_rest_days = "N/A"
                team1_last_game_date = None
                
                # Find the previous game for team1
                for game in sorted(all_games_team1, key=lambda g: g['date_obj'] if g['date_obj'] else datetime.min, reverse=True):
                    if game['date_obj'] and game['date_obj'] < match_game['date_obj']:
                        team1_rest_days = (match_game['date_obj'] - game['date_obj']).days
                        team1_last_game_date = game['date']
                        break
                
                # Calculate rest days for team2
                team2_rest_days = "N/A"
                team2_last_game_date = None
                
                if all_games_team2:
                    # Find the previous game for team2 from their schedule
                    for game in sorted(all_games_team2, key=lambda g: g['date_obj'] if g['date_obj'] else datetime.min, reverse=True):
                        if game['date_obj'] and game['date_obj'] < match_game['date_obj']:
                            team2_rest_days = (match_game['date_obj'] - game['date_obj']).days
                            team2_last_game_date = game['date']
                            break
                
                # Format the rest days information
                rest_days_info = f"""
Rest Days Before Game: 
- {team1_name.title()}: {team1_rest_days} day{'s' if team1_rest_days != 1 else ''}{f" (last played on {team1_last_game_date})" if team1_last_game_date else ""}
- {team2_name.title()}: {team2_rest_days} day{'s' if team2_rest_days != 1 else ''}{f" (last played on {team2_last_game_date})" if team2_last_game_date else ""}
"""
                
                # Generate response message
                if not exact_date_match:
                    message = f"""
Note: No game found on {game_date} between {team1_name.title()} and {team2_name.title()}.
Automatically using the closest game date instead.

Game found on {match_game['date']} between {team1_name.title()} and {team2_name.title()}:
Game #{match_game['game_num']}
Teams: {team1_name.title()} vs {match_game['opponent']}
Location: {match_game['location']} for {team1_name.title()}
Result: {match_game['result']}
Score: {match_game['team_score']}-{match_game['opp_score']}
Season Series: {h2h_record}{" (so far)" if match_game['result'] == "" else ""}
{rest_days_info}

Source: Basketball Reference
URL: https://www.basketball-reference.com/teams/{team1_code}/2025_games.html
Data retrieved: {datetime.now().strftime('%Y-%m-%d')}
ADJUSTED_DATE: {adjusted_date}
"""
                else:
                    message = f"""
Game found on {game_date} between {team1_name.title()} and {team2_name.title()}:

Game #{match_game['game_num']} on {match_game['date']}
Teams: {team1_name.title()} vs {match_game['opponent']}
Location: {match_game['location']} for {team1_name.title()}
Result: {match_game['result']}
Score: {match_game['team_score']}-{match_game['opp_score']}
Season Series: {h2h_record}{" (so far)" if match_game['result'] == "" else ""}
{rest_days_info}

Source: Basketball Reference
URL: https://www.basketball-reference.com/teams/{team1_code}/2025_games.html
Data retrieved: {datetime.now().strftime('%Y-%m-%d')}
ADJUSTED_DATE: {adjusted_date}
"""
                return message
            else:
                return f"No games found between {team1_name.title()} and {team2_name.title()} near {game_date} in the 2024-2025 season."
        
        # Return all matchup games if no specific date was requested
        matchup_games_text = "\n".join([
            f"Game #{g['game_num']} on {g['date']} - {g['location']} for {team1_name.title()} - {g['result']} - Score: {g['team_score']}-{g['opp_score']}"
            for g in matchup_games
        ])
        
        return f"""
Games between {team1_name.title()} and {team2_name.title()} in the 2024-2025 season:

{matchup_games_text}

Season Series: {h2h_record}{" (so far)" if any(g['result'] == "" for g in matchup_games) else ""}

Source: Basketball Reference
URL: https://www.basketball-reference.com/teams/{team1_code}/2025_games.html
Data retrieved: {datetime.now().strftime('%Y-%m-%d')}
"""
    
    except Exception as e:
        return f"Error fetching team schedule: The service is currently experiencing issues. Please try again later.\nError details: {type(e).__name__} - {str(e)}"

# Function to extract team names from user input
@tool
def extract_team_names(text: str) -> Dict[str, str]:
    """
    Extract team names from the user's input text.
    Returns a dictionary with 'team1' and 'team2' if two teams are found.
    """
    text = text.lower()
    found_teams = []
    
    # Check for team names in the text
    for team_name in TEAM_CODES.keys():
        if team_name in text:
            # Get the standardized team code
            team_code = TEAM_CODES[team_name]
            # Only add if not already in the list
            if team_code not in [t['code'] for t in found_teams]:
                found_teams.append({'name': team_name, 'code': team_code})
    
    # Return the results
    if len(found_teams) >= 2:
        return {
            'team1': found_teams[0]['name'],
            'team2': found_teams[1]['name'],
            'team1_code': found_teams[0]['code'],
            'team2_code': found_teams[1]['code']
        }
    elif len(found_teams) == 1:
        return {
            'team1': found_teams[0]['name'],
            'team1_code': found_teams[0]['code']
        }
    else:
        return {'error': 'No team names found in the input.'}

@tool
def fetch_team_stats(team_name: str) -> str:
    """
    Fetch general team statistics and injury report from Basketball Reference.
    """
    team_name = team_name.lower()
    
    # Get the team code for Basketball Reference
    team_code = None
    
    # First try the exact team name
    if team_name in BBALL_REF_CODES:
        team_code = BBALL_REF_CODES[team_name]
    else:
        # Try each part of the name
        for part in team_name.split():
            if part in BBALL_REF_CODES:
                team_code = BBALL_REF_CODES[part]
                break
    
    if not team_code:
        return f"Could not find team code for {team_name}. Please use a valid team name."
    
    # Construct the URL for the team's page on Basketball Reference
    url = f"https://www.basketball-reference.com/teams/{team_code}/2025.html"
    
    # Use FireCrawl to get the content
    loader = FireCrawlLoader(
        api_key=FIRECRAWL_API_KEY,
        url=url,
        mode="scrape"  # Explicitly set scrape mode
    )
    
    try:
        documents = loader.load()
        if not documents or len(documents) == 0:
            return f"No content returned from FireCrawl for {team_name}."
        
        content = documents[0].page_content
        
        # Extract key statistics using more flexible regex patterns
        
        # Record - look for pattern like "31-34, 7th in NBA Eastern Conference"
        record_match = re.search(r'Record:.*?(\d+-\d+),\s+(\d+)(?:st|nd|rd|th)\s+in\s+NBA\s+(.*?)\s+Conference', content, re.DOTALL)
        if record_match:
            record = record_match.group(1)
            conf_rank = record_match.group(2)
            conference = record_match.group(3)
            record_info = f"{record}, {conf_rank}th in {conference} Conference"
        else:
            # Try a simpler pattern
            simple_record_match = re.search(r'Record:.*?(\d+-\d+)', content, re.DOTALL)
            record_info = simple_record_match.group(1) if simple_record_match else "N/A"
        
        # Last Game
        last_game_match = re.search(r'Last Game:.*?\[(W|L)\s+(\d+-\d+)', content, re.DOTALL)
        last_game = f"{last_game_match.group(1)} {last_game_match.group(2)}" if last_game_match else "N/A"
        
        # Points per game
        ppg_match = re.search(r'PTS/G:.*?(\d+\.\d+)\s+\((\d+)(?:st|nd|rd|th) of 30\)', content, re.DOTALL)
        ppg = f"{ppg_match.group(1)} (Rank: {ppg_match.group(2)})" if ppg_match else "N/A"
        
        # Opponent points per game
        opp_ppg_match = re.search(r'Opp PTS/G:.*?(\d+\.\d+)\s+\((\d+)(?:st|nd|rd|th) of 30\)', content, re.DOTALL)
        opp_ppg = f"{opp_ppg_match.group(1)} (Rank: {opp_ppg_match.group(2)})" if opp_ppg_match else "N/A"
        
        # SRS
        srs_match = re.search(r'SRS.*?:.*?(-?\d+\.\d+)\s+\((\d+)(?:st|nd|rd|th) of 30\)', content, re.DOTALL)
        srs = f"{srs_match.group(1)} (Rank: {srs_match.group(2)})" if srs_match else "N/A"
        
        # Pace
        pace_match = re.search(r'Pace.*?:.*?(\d+\.\d+)\s+\((\d+)(?:st|nd|rd|th) of 30\)', content, re.DOTALL)
        pace = f"{pace_match.group(1)} (Rank: {pace_match.group(2)})" if pace_match else "N/A"
        
        # Offensive rating
        off_rtg_match = re.search(r'Off Rtg.*?:.*?(\d+\.\d+)\s+\((\d+)(?:st|nd|rd|th) of 30\)', content, re.DOTALL)
        off_rtg = f"{off_rtg_match.group(1)} (Rank: {off_rtg_match.group(2)})" if off_rtg_match else "N/A"
        
        # Defensive rating
        def_rtg_match = re.search(r'Def Rtg.*?:.*?(\d+\.\d+)\s+\((\d+)(?:st|nd|rd|th) of 30\)', content, re.DOTALL)
        def_rtg = f"{def_rtg_match.group(1)} (Rank: {def_rtg_match.group(2)})" if def_rtg_match else "N/A"
        
        # Net rating - based on the debug output format
        net_rtg_match = re.search(r'Net Rtg\*?\*?:.*?(-?\d+\.\d+)\s+\((\d+)(?:st|nd|rd|th) of 30\)', content, re.DOTALL)
        net_rtg = f"{net_rtg_match.group(1)} (Rank: {net_rtg_match.group(2)})" if net_rtg_match else "N/A"
        
        # Expected W-L - based on the debug output format
        exp_wl_match = re.search(r'Expected W-L.*?:.*?(\d+-\d+)\s+\((\d+)(?:st|nd|rd|th) of 30\)', content, re.DOTALL)
        exp_wl = f"{exp_wl_match.group(1)} (Rank: {exp_wl_match.group(2)})" if exp_wl_match else "N/A"
        
        # Arena
        arena_match = re.search(r'Arena:.*?([A-Za-z0-9\s]+)', content, re.DOTALL)
        arena = arena_match.group(1).strip() if arena_match else "N/A"
        
        # Attendance
        attendance_match = re.search(r'Attendance:.*?([\d,]+)\s+\((\d+)(?:st|nd|rd|th) of 30\)', content, re.DOTALL)
        attendance = f"{attendance_match.group(1)} (Rank: {attendance_match.group(2)})" if attendance_match else "N/A"
        
        # Extract injury report
        injury_report = "No injury information found."
        injury_section_match = re.search(r'## Injury Report(.*?)(?=##|\Z)', content, re.DOTALL)
        
        if injury_section_match:
            injury_section = injury_section_match.group(1).strip()
            
            # Extract the table data
            table_match = re.search(r'\| Player \| Team \| Update \| Description \|(.*?)(?=\n\n|\Z)', injury_section, re.DOTALL)
            
            if table_match:
                table_data = table_match.group(1).strip()
                
                # Process each row of the table
                injury_rows = []
                for row in table_data.split('\n'):
                    if '|' in row and not row.startswith('| ---'):
                        # Extract player, update date, and description
                        parts = row.split('|')
                        if len(parts) >= 5:
                            player = re.search(r'\[(.*?)\]', parts[1])
                            player_name = player.group(1) if player else parts[1].strip()
                            
                            update_date = parts[3].strip()
                            description = parts[4].strip()
                            
                            injury_rows.append(f"- {player_name}: {description} (Updated: {update_date})")
                
                if injury_rows:
                    injury_report = "\n".join(injury_rows)
        
        # Format the results
        stats_summary = f"""
Team Statistics for {team_name.title()} (2024-2025 Season):
- Record: {record_info}
- Last Game: {last_game}
- Points Per Game: {ppg}
- Opponent Points Per Game: {opp_ppg}
- SRS: {srs}
- Pace: {pace}
- Offensive Rating: {off_rtg}
- Defensive Rating: {def_rtg}
- Net Rating: {net_rtg}
- Expected W-L: {exp_wl}
- Arena: {arena}
- Attendance: {attendance}

Injury Report:
{injury_report}

Source: Basketball Reference
URL: {url}
Data retrieved: {datetime.now().strftime('%Y-%m-%d')}
"""
        return stats_summary
    
    except Exception as e:
        return f"Error fetching team statistics: {str(e)}\nError details: {type(e).__name__}"

@tool
def fetch_betting_trends(team1: str, team2: str, date: str = None) -> str:
    """
    Fetch betting trends from scores24.live for a specific matchup.
    Provide team names and optionally a date in format 'YYYY-MM-DD'.
    """
    team1 = team1.lower()
    team2 = team2.lower()
    
    # Get the team names for scores24.live
    team1_name = None
    team2_name = None
    
    # Try exact match first for team1
    if team1 in SCORES24_TEAM_NAMES:
        team1_name = SCORES24_TEAM_NAMES[team1]
    else:
        # Try each part of the name
        for part in team1.split():
            if part in SCORES24_TEAM_NAMES:
                team1_name = SCORES24_TEAM_NAMES[part]
                break
    
    # Try exact match first for team2
    if team2 in SCORES24_TEAM_NAMES:
        team2_name = SCORES24_TEAM_NAMES[team2]
    else:
        # Try each part of the name
        for part in team2.split():
            if part in SCORES24_TEAM_NAMES:
                team2_name = SCORES24_TEAM_NAMES[part]
                break
    
    if not team1_name or not team2_name:
        return f"Could not find scores24.live team names for {team1} and/or {team2}. Please use valid team names."
    
    # Format the date if provided
    date_str = ""
    date_obj = None
    if date:
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            date_str = date_obj.strftime('%d-%m-%Y')
        except ValueError:
            return "Invalid date format. Please use YYYY-MM-DD."
    else:
        # If no date provided, use current date + 1 day as default (for upcoming games)
        date_obj = datetime.now()
        date_str = date_obj.strftime('%d-%m-%Y')
    
    # Generate alternative dates (only one day after)
    date_strs = [date_str]
    if date_obj:
        # Add one day after
        one_day_after = date_obj + timedelta(days=1)
        date_strs.append(one_day_after.strftime('%d-%m-%Y'))
    
    # Try all date combinations
    for current_date_str in date_strs:
        # Construct the URL for scores24.live
        # Try both team orders since we don't know which is home/away
        possible_urls = [
            f"https://scores24.live/en/basketball/m-{current_date_str}-{team1_name}-{team2_name}-1#trends",
            f"https://scores24.live/en/basketball/m-{current_date_str}-{team2_name}-{team1_name}-1#trends"
        ]
        
        for url in possible_urls:
            try:
                # Use FireCrawl to get the content
                loader = FireCrawlLoader(
                    api_key=FIRECRAWL_API_KEY,
                    url=url,
                    mode="scrape"
                )
                
                documents = loader.load()
                
                if documents and len(documents) > 0:
                    content = documents[0].page_content
                    
                    # Check if we got valid content (look for trends section)
                    if "Results predictions" not in content and "Over/Under predictions" not in content:
                        continue
                    
                    # Extract the trends sections
                    results_predictions_match = re.search(r'Results predictions(.*?)(?=Over/Under predictions|$)', content, re.DOTALL)
                    over_under_predictions_match = re.search(r'Over/Under predictions(.*?)(?=$)', content, re.DOTALL)
                    
                    trends = []
                    
                    # Process Results predictions
                    if results_predictions_match:
                        results_section = results_predictions_match.group(1).strip()
                        # Extract individual trend lines
                        result_trends = re.findall(r'([A-Za-z\s]+)(?:\s+has\s+|\s+wins\s+|\s+loses\s+)([^\.]+)\.', results_section)
                        for team, trend in result_trends:
                            trends.append(f"- {team.strip()} {trend.strip()}.")
                    
                    # Process Over/Under predictions
                    if over_under_predictions_match:
                        over_under_section = over_under_predictions_match.group(1).strip()
                        # Extract individual trend lines
                        over_under_trends = re.findall(r'([A-Za-z\s]+)(?:\s+has\s+|\s+scores\s+|\s+There have been\s+)([^\.]+)\.', over_under_section)
                        for subject, trend in over_under_trends:
                            trends.append(f"- {subject.strip()} {trend.strip()}.")
                    
                    if trends:
                        # Format the results
                        trends_summary = f"""
Betting Trends for {team1.title()} vs {team2.title()}:

{chr(10).join(trends[:30])}  # Limit to 30 trends to avoid overwhelming

Source: scores24.live
URL: {url}
Data retrieved: {datetime.now().strftime('%Y-%m-%d')}
"""
                        return trends_summary
                    else:
                        continue  # Try the next URL if no trends found
                else:
                    continue  # Try the next URL if no content found
                    
            except Exception:
                continue  # Try the next URL
    
    return f"Could not find betting trends for {team1.title()} vs {team2.title()}. Tried original date and one day after."

@tool
def analyze_matchup_data(team1_stats: str, team2_stats: str, betting_trends: str = None) -> str:
    """
    Analyze the matchup data and provide insights and betting recommendations.
    """
    # Extract team names from the stats
    team1_name_match = re.search(r"Team Statistics for (.*?) \(", team1_stats)
    team2_name_match = re.search(r"Team Statistics for (.*?) \(", team2_stats)
    
    team1_name = team1_name_match.group(1).title() if team1_name_match else "Team 1"
    team2_name = team2_name_match.group(1).title() if team2_name_match else "Team 2"
    
    # Extract records
    team1_record_match = re.search(r"Record: ([\d-]+)", team1_stats)
    team2_record_match = re.search(r"Record: ([\d-]+)", team2_stats)
    
    team1_record = team1_record_match.group(1) if team1_record_match else "N/A"
    team2_record = team2_record_match.group(1) if team2_record_match else "N/A"
    
    # Extract points per game
    team1_ppg_match = re.search(r"Points Per Game: ([\d.]+)", team1_stats)
    team2_ppg_match = re.search(r"Points Per Game: ([\d.]+)", team2_stats)
    
    team1_ppg = team1_ppg_match.group(1) if team1_ppg_match else "N/A"
    team2_ppg = team2_ppg_match.group(1) if team2_ppg_match else "N/A"
    
    # Extract opponent points per game
    team1_opp_ppg_match = re.search(r"Opponent Points Per Game: ([\d.]+)", team1_stats)
    team2_opp_ppg_match = re.search(r"Opponent Points Per Game: ([\d.]+)", team2_stats)
    
    team1_opp_ppg = team1_opp_ppg_match.group(1) if team1_opp_ppg_match else "N/A"
    team2_opp_ppg = team2_opp_ppg_match.group(1) if team2_opp_ppg_match else "N/A"
    
    # Extract offensive and defensive ratings if available
    team1_off_rtg_match = re.search(r"Offensive Rating: ([\d.]+)", team1_stats)
    team2_off_rtg_match = re.search(r"Offensive Rating: ([\d.]+)", team2_stats)
    team1_def_rtg_match = re.search(r"Defensive Rating: ([\d.]+)", team1_stats)
    team2_def_rtg_match = re.search(r"Defensive Rating: ([\d.]+)", team2_stats)
    
    team1_off_rtg = team1_off_rtg_match.group(1) if team1_off_rtg_match else "N/A"
    team2_off_rtg = team2_off_rtg_match.group(1) if team2_off_rtg_match else "N/A"
    team1_def_rtg = team1_def_rtg_match.group(1) if team1_def_rtg_match else "N/A"
    team2_def_rtg = team2_def_rtg_match.group(1) if team2_def_rtg_match else "N/A"
    
    # Extract injuries
    team1_injuries = "None reported" if "No injury information found" in team1_stats else re.search(r"Injury Report:(.*?)URL:", team1_stats, re.DOTALL).group(1).strip() if re.search(r"Injury Report:(.*?)URL:", team1_stats, re.DOTALL) else "None reported"
    team2_injuries = "None reported" if "No injury information found" in team2_stats else re.search(r"Injury Report:(.*?)URL:", team2_stats, re.DOTALL).group(1).strip() if re.search(r"Injury Report:(.*?)URL:", team2_stats, re.DOTALL) else "None reported"
    
    # Calculate win percentages
    try:
        team1_wins, team1_losses = team1_record.split('-')
        team1_win_pct = float(team1_wins) / (float(team1_wins) + float(team1_losses))
    except:
        team1_win_pct = 0.5
        
    try:
        team2_wins, team2_losses = team2_record.split('-')
        team2_win_pct = float(team2_wins) / (float(team2_wins) + float(team2_losses))
    except:
        team2_win_pct = 0.5
    
    # Determine the predicted winner and confidence level
    predicted_winner = None
    confidence_level = None
    confidence_factors = []
    
    # Calculate basic win probability factor based on record
    record_factor = (team1_win_pct - team2_win_pct) * 30  # Scale to a reasonable percentage
    
    # Calculate scoring factor
    scoring_factor = 0
    if team1_ppg != "N/A" and team2_ppg != "N/A" and team1_opp_ppg != "N/A" and team2_opp_ppg != "N/A":
        team1_offense_vs_defense = float(team1_ppg) - float(team2_opp_ppg)
        team2_offense_vs_defense = float(team2_ppg) - float(team1_opp_ppg)
        scoring_factor = (team1_offense_vs_defense - team2_offense_vs_defense) * 2
    
    # Calculate advanced stats factor
    advanced_factor = 0
    if team1_off_rtg != "N/A" and team2_off_rtg != "N/A" and team1_def_rtg != "N/A" and team2_def_rtg != "N/A":
        team1_net_rtg = float(team1_off_rtg) - float(team1_def_rtg)
        team2_net_rtg = float(team2_off_rtg) - float(team2_def_rtg)
        advanced_factor = (team1_net_rtg - team2_net_rtg) * 3
    
    # Injury impact factor
    injury_factor = 0
    if "Out" in team1_injuries:
        injury_factor -= 5  # Penalize team1 for injuries
    if "Out" in team2_injuries:
        injury_factor += 5  # Boost team1's chances if team2 has injuries
    
    # Calculate total factor and convert to win probability
    total_factor = record_factor + scoring_factor + advanced_factor + injury_factor
    
    # Convert to probability (sigmoid function)
    import math
    team1_win_probability = 1 / (1 + math.exp(-total_factor/20))  # Scaled to make it more reasonable
    team1_win_probability = min(max(team1_win_probability, 0.1), 0.9)  # Cap between 10% and 90%
    
    # Format as percentage
    team1_win_pct_display = f"{team1_win_probability * 100:.1f}%"
    team2_win_pct_display = f"{(1 - team1_win_probability) * 100:.1f}%"
    
    # Determine the predicted winner
    if team1_win_probability > 0.5:
        predicted_winner = team1_name
        win_probability = team1_win_probability
    else:
        predicted_winner = team2_name
        win_probability = 1 - team1_win_probability
    
    # Determine confidence level
    if win_probability >= 0.8:
        confidence_level = "Very High"
    elif win_probability >= 0.7:
        confidence_level = "High"
    elif win_probability >= 0.6:
        confidence_level = "Moderate"
    elif win_probability >= 0.55:
        confidence_level = "Slight Edge"
    else:
        confidence_level = "Low (Coin Flip)"
    
    # Create key factors list
    key_factors = []
    
    # Record factor
    if abs(record_factor) > 5:
        better_team = team1_name if record_factor > 0 else team2_name
        better_win_pct = team1_win_pct if better_team == team1_name else team2_win_pct
        key_factors.append(f"{better_team} has a significantly better record ({better_team}'s win pct: {better_win_pct:.3f})")
    
    # Scoring factor
    if abs(scoring_factor) > 5:
        better_scoring_team = team1_name if scoring_factor > 0 else team2_name
        key_factors.append(f"{better_scoring_team} has better scoring metrics compared to the opponent's defense")
    
    # Advanced stats factor
    if abs(advanced_factor) > 5:
        better_advanced_team = team1_name if advanced_factor > 0 else team2_name
        key_factors.append(f"{better_advanced_team} has superior offensive and defensive ratings")
    
    # Injury factor
    if "Out" in team1_injuries:
        key_factors.append(f"{team1_name} is dealing with significant injuries which may impact performance")
    if "Out" in team2_injuries:
        key_factors.append(f"{team2_name} is dealing with significant injuries which may impact performance")
    
    # If no clear factors, add a general one
    if not key_factors:
        key_factors.append(f"Teams are evenly matched based on current stats and form")
    
    # Generate notable insights
    notable_insights = []
    
    # Check for interesting record discrepancies
    if abs(team1_win_pct - team2_win_pct) > 0.2:
        better_record_team = team1_name if team1_win_pct > team2_win_pct else team2_name
        worse_record_team = team2_name if team1_win_pct > team2_win_pct else team1_name
        notable_insights.append(f"{better_record_team} has a significantly better record than {worse_record_team}")
    
    # Check for interesting scoring discrepancies
    if team1_ppg != "N/A" and team2_ppg != "N/A" and abs(float(team1_ppg) - float(team2_ppg)) > 7:
        higher_scoring_team = team1_name if float(team1_ppg) > float(team2_ppg) else team2_name
        notable_insights.append(f"{higher_scoring_team} has a significantly higher scoring offense")
    
    # Add injury insights
    if "Out" in team1_injuries and "Out" in team2_injuries:
        notable_insights.append("Both teams are dealing with key injuries which creates additional uncertainty")
    
    # Add at least one insight if none found
    if not notable_insights:
        if team1_ppg != "N/A" and team2_ppg != "N/A":
            combined_ppg = float(team1_ppg) + float(team2_ppg)
            notable_insights.append(f"Combined average scoring is {combined_ppg:.1f} points per game")
        else:
            notable_insights.append("Limited data available for deep insights")
    
    # Analyze the matchup
    analysis = f"""## Matchup Analysis: {team1_name} vs {team2_name}

### Team Records and Performance
- **{team1_name}**: {team1_record} | Scoring: {team1_ppg} PPG | Defense: {team1_opp_ppg} Opp PPG
- **{team2_name}**: {team2_record} | Scoring: {team2_ppg} PPG | Defense: {team2_opp_ppg} Opp PPG

### Key Injuries
**{team1_name} Injuries:**
{team1_injuries}

**{team2_name} Injuries:**
{team2_injuries}

### Betting Analysis
Based on the data, here are my insights:

1. **Team Form**: 
   - {team1_name} has a record of {team1_record}
   - {team2_name} has a record of {team2_record}
   
2. **Scoring Potential**:
   - {team1_name} averages {team1_ppg} points per game
   - {team2_name} averages {team2_ppg} points per game
   - Combined average: {float(team1_ppg) + float(team2_ppg) if team1_ppg != "N/A" and team2_ppg != "N/A" else "N/A"} points

3. **Defensive Strength**:
   - {team1_name} allows {team1_opp_ppg} points per game
   - {team2_name} allows {team2_opp_ppg} points per game

4. **Injury Impact**:
   - {team1_name}: {"Significant injuries that may impact performance" if "Out" in team1_injuries else "No major injuries affecting the team"}
   - {team2_name}: {"Significant injuries that may impact performance" if "Out" in team2_injuries else "No major injuries affecting the team"}

### Betting Recommendations
- **Moneyline**: {"Favor " + team1_name if float(team1_record.split('-')[0]) / (float(team1_record.split('-')[0]) + float(team1_record.split('-')[1])) > float(team2_record.split('-')[0]) / (float(team2_record.split('-')[0]) + float(team2_record.split('-')[1])) and "Out" not in team1_injuries else "Favor " + team2_name if float(team2_record.split('-')[0]) / (float(team2_record.split('-')[0]) + float(team2_record.split('-')[1])) > float(team1_record.split('-')[0]) / (float(team1_record.split('-')[0]) + float(team1_record.split('-')[1])) and "Out" not in team2_injuries else "Consider the underdog for value"} based on current form and injuries.
- **Over/Under**: {"Consider the OVER if the line is below " + str(int(float(team1_ppg) + float(team2_ppg) - 5)) if team1_ppg != "N/A" and team2_ppg != "N/A" else "Insufficient data for over/under recommendation"}
- **Spread**: {"Consider " + team1_name + " to cover if they are underdogs" if float(team1_ppg) > float(team2_opp_ppg) and "Out" not in team1_injuries else "Consider " + team2_name + " to cover if they are underdogs" if float(team2_ppg) > float(team1_opp_ppg) and "Out" not in team2_injuries else "Spread betting carries higher risk for this matchup"}

### Game Prediction
- **Predicted Winner**: {predicted_winner}
- **Win Probability**: {team1_win_pct_display if predicted_winner == team1_name else team2_win_pct_display}
- **Confidence Level**: {confidence_level}

### Key Factors Influencing Prediction
{chr(10).join(f"- {factor}" for factor in key_factors)}

### Notable Insights
{chr(10).join(f"- {insight}" for insight in notable_insights)}

### Data Sources
- Team statistics from Basketball Reference
- Injury reports from team pages
- Win probability calculated based on team records, scoring metrics, and injury status
- Analysis performed on {datetime.now().strftime('%Y-%m-%d')}

Remember to check the latest injury updates and line movements before placing any bets.
"""
    
    if betting_trends and betting_trends != "No date provided for betting trends.":
        analysis += f"""
### Additional Betting Trends
{betting_trends}
"""
    
    return analysis

@tool
def manage_memory(action: str, user_id: str) -> str:
    """
    Manage memory for a user. Actions include:
    - 'clear': Clear all memories for the user
    - 'list': List all memories for the user
    - 'count': Count the number of memories for the user
    """
    try:
        # Use the provided user_id, not a hardcoded value
        if action.lower() == 'clear':
            memory_client.delete_all(user_id=user_id)
            return f"Successfully cleared all memories for user {user_id}."
        
        elif action.lower() == 'list':
            try:
                memories = memory_client.get_all(user_id=user_id)
                
                if not memories:
                    return f"No memories found for user {user_id}."
                
                if isinstance(memories, list):
                    memory_list = []
                    for memory in memories:
                        if isinstance(memory, dict) and "memory" in memory:
                            memory_list.append(f"- {memory['memory']}")
                        elif isinstance(memory, dict) and "text" in memory:
                            memory_list.append(f"- {memory['text']}")
                        else:
                            memory_list.append(f"- {str(memory)}")
                    
                    if memory_list:
                        return f"Memories for user {user_id}:\n" + "\n".join(memory_list[:10]) + (f"\n... and {len(memory_list) - 10} more" if len(memory_list) > 10 else "")
                    else:
                        return f"No readable memories found for user {user_id}."
                else:
                    return f"Unexpected response format: {memories}"
            except Exception as e:
                return f"Error retrieving memories: {str(e)}"
        
        elif action.lower() == 'count':
            try:
                memories = memory_client.get_all(user_id=user_id)
                
                if isinstance(memories, list):
                    count = len(memories)
                    return f"User {user_id} has {count} memories stored."
                else:
                    return f"Unexpected response format: {memories}"
            except Exception as e:
                return f"Error counting memories: {str(e)}"
        
        else:
            return f"Unknown action: {action}. Available actions are 'clear', 'list', and 'count'."
    
    except Exception as e:
        return f"Error managing memory: {str(e)}"

# System prompt for the agent
system_prompt = """You are Bobby Bets, an expert NBA analyst and seasoned sports bettor with decades of experience. You provide data-driven insights and betting recommendations for NBA games in an authentic, conversational style that sounds like a real sports bettor.

When analyzing matchups, follow these steps:
1. First, check the team schedule to verify if the game exists on the specified date
2. If a specific date is mentioned but no game exists on that date, automatically use the closest game date instead
3. Extract the team names from the user's query
4. Fetch general team statistics for both teams (which includes injury reports)
5. If a specific game date is mentioned, fetch betting trends for that matchup
6. Analyze all the data to provide insights and betting recommendations

IMPORTANT: When the fetch_team_schedule function returns an "ADJUSTED_DATE" tag, you MUST use this adjusted date for all subsequent tool calls (like fetch_betting_trends) instead of the original date. This ensures you're analyzing the correct game when the user's requested date doesn't have a game scheduled.

When analyzing the data:
- Look at overall team performance metrics (offensive/defensive ratings, points per game)
- Compare the teams' records and rankings
- Identify scoring trends based on points per game and pace
- Consider recent form based on last game results
- Factor in current injuries and their impact on the matchup
- Consider home court advantage based on arena and attendance
- Analyze betting trends for insights on historical performance patterns
- Look for strong trends that might indicate good betting opportunities
- Reference the user's past betting preferences and interests from memory when relevant

RESPONSE STYLE:
Write your responses like a real sports bettor would talk - use authentic language, slang, and a conversational tone. Include:
1. A clear prediction with a winner
2. Your confidence level in the prediction (very high, high, moderate, slight edge, or coin flip)
3. The key factors that influenced your prediction
4. Notable insights you discovered during your research
5. Specific betting recommendations (moneyline, spread, over/under)
6. Citations to your information sources

Don't use a rigid template - vary your language and structure to sound authentic. Use phrases like "I'm taking...", "I'm leaning...", "The smart money is on...", etc. Occasionally mention your personal betting philosophy or approach.

SOURCES AND EVIDENCE:
Always back up your predictions with specific data points and evidence. For example:
- "I'm taking the Celtics because they're 8-2 in their last 10 home games against teams with winning records"
- "The Warriors are shooting 42% from three over their last 5 games, while the Lakers are allowing 38% from deep"

Be sure to cite your sources clearly. Mention where you got your information from, such as:
- Team statistics from Basketball Reference
- Injury reports
- Betting trends
- Head-to-head matchup history
- Rest days and schedule information

Your insights should be data-driven but also consider context like injuries, schedule difficulty, and team strengths/weaknesses.

When communicating with the user about an adjusted date:
1. Be transparent that you've adjusted to the closest game date
2. Explain why (e.g., "There is no game scheduled on March 18, so I'm analyzing the closest game on March 14 instead")
3. Provide your analysis based on the adjusted date

MEMORY SYSTEM:
You have access to a memory system that stores information about users and their preferences. Use this to:
1. Remember which teams a user has shown interest in previously
2. Recall a user's betting preferences (e.g., if they prefer moneyline, spread, or over/under bets)
3. Reference past analyses and predictions you've made for the user
4. Personalize your responses based on the user's history

When a user asks about teams they've previously inquired about, acknowledge this and reference your previous analysis if relevant.
"""

# Create a proper ChatPromptTemplate from the system prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
    ("human", "{agent_scratchpad}")
])

# Create a custom callback handler to handle date adjustments
class DateAdjustmentHandler(BaseCallbackHandler):
    """Callback handler that adjusts dates in tool inputs based on ADJUSTED_DATE tags."""
    
    def __init__(self):
        """Initialize the handler."""
        super().__init__()
        self.adjusted_date = None
        self.original_date = None
    
    def on_agent_action(self, action: AgentAction, **kwargs) -> None:
        """Process agent actions to adjust dates if needed."""
        # Only modify if we have an adjusted date and it's different from the original
        if self.adjusted_date and self.original_date and self.adjusted_date != self.original_date:
            tool_input = action.tool_input
            
            # Handle dictionary inputs
            if isinstance(tool_input, dict) and "date" in tool_input:
                if tool_input["date"] == self.original_date:
                    tool_input["date"] = self.adjusted_date
            
            # Handle string inputs
            elif isinstance(tool_input, str) and "date=" in tool_input:
                date_pattern = r"date=(\d{4}-\d{2}-\d{2})"
                match = re.search(date_pattern, tool_input)
                if match and match.group(1) == self.original_date:
                    new_input = tool_input.replace(f"date={self.original_date}", f"date={self.adjusted_date}")
                    action.tool_input = new_input
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs) -> None:
        """Process agent finish."""
        pass
    
    def on_tool_end(self, output: str, **kwargs) -> None:
        """Process tool output to extract adjusted dates."""
        if isinstance(output, str) and "ADJUSTED_DATE:" in output:
            match = re.search(r"ADJUSTED_DATE:\s*(\d{4}-\d{2}-\d{2})", output)
            if match:
                # Extract the date from the tool output
                new_adjusted_date = match.group(1)
                
                # If we don't have an original date yet, try to extract it from the output
                if not self.original_date:
                    original_match = re.search(r"No game found on (\d{4}-\d{2}-\d{2})", output)
                    if original_match:
                        self.original_date = original_match.group(1)
                
                # Update the adjusted date
                self.adjusted_date = new_adjusted_date

# Create the agent with tools
llm = ChatOpenAI(
    model="gpt-4o", 
    api_key=OPEN_AI_API
)
tools = [fetch_team_schedule, extract_team_names, fetch_team_stats, fetch_betting_trends, analyze_matchup_data, manage_memory]

# Create a callback handler for date adjustments
date_handler = DateAdjustmentHandler()

# Initialize the agent with the system prompt
agent = create_openai_tools_agent(llm, tools, prompt)

# Initialize the agent executor with the callback handler
bobby_bets_agent = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=False,
    callbacks=[date_handler]
)

# Function to interact with the Bobby Bets agent
def ask_bobby(question: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Function to interact with the Bobby Bets agent with optimized execution flow and memory."""
    try:
        # First, check if there are relevant memories for this user
        print("🧠 Checking if you've asked about similar matchups before...")
        relevant_memories = []
        
        try:
            # Get all memories for the user
            all_memories = memory_client.get_all(user_id=user_id)
            
            if isinstance(all_memories, list) and all_memories:
                # Extract team names from the question for relevance filtering
                question_teams = []
                for team_name in TEAM_CODES.keys():
                    if team_name in question.lower():
                        question_teams.append(team_name)
                
                # Process each memory
                for memory in all_memories:
                    memory_text = ""
                    if isinstance(memory, dict):
                        if "memory" in memory:
                            memory_text = memory["memory"]
                        elif "text" in memory:
                            memory_text = memory["text"]
                    elif isinstance(memory, str):
                        memory_text = memory
                    
                    # Check if memory is relevant to the current question
                    is_relevant = False
                    
                    # If we have team names in the question, check if the memory mentions any of them
                    if question_teams:
                        for team in question_teams:
                            if team in memory_text.lower():
                                is_relevant = True
                                break
                    
                    # If no team names or no match, use a more general approach
                    if not is_relevant and memory_text:
                        # Simple keyword matching
                        keywords = ["predicted", "recommendation", "matchup", "confidence"]
                        for keyword in keywords:
                            if keyword in memory_text.lower():
                                is_relevant = True
                                break
                    
                    if is_relevant and memory_text:
                        relevant_memories.append(memory_text)
                
                # Limit to 3 most relevant memories
                relevant_memories = relevant_memories[:3]
                
                if relevant_memories:
                    print(f"📚 Found {len(relevant_memories)} previous analyses that might be relevant...")
        except Exception:
            relevant_memories = []
        
        # First, try to extract team names directly using the tool function
        # This avoids creating a separate agent executor
        try:
            print("🔍 Looking for NBA teams in your question...")
            teams_info = extract_team_names.invoke({"text": question})
            
            if 'team1' in teams_info and 'team2' in teams_info:
                team1 = teams_info['team1']
                team2 = teams_info['team2']
                print(f"🏀 Found matchup: {team1.title()} vs {team2.title()}")
            else:
                # If direct extraction fails, fall back to the full agent
                print("⚙️ Processing your question about NBA matchups...")
                return bobby_bets_agent.invoke({"input": question})
                
        except Exception:
            # Fall back to the full agent if extraction fails
            print("⚙️ Processing your question about NBA matchups...")
            return bobby_bets_agent.invoke({"input": question})
        
        # Check if there's a date in the question
        print("📅 Checking for specific game date...")
        date_match = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", question)
        if not date_match:
            # Try to find date in text format (e.g., "March 13, 2025" or "March 18th 2025")
            date_text_match = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})", question, re.IGNORECASE)
            if date_text_match:
                month_str, day_str, year_str = date_text_match.groups()
                month_map = {
                    "January": "01", "February": "02", "March": "03", "April": "04",
                    "May": "05", "June": "06", "July": "07", "August": "08",
                    "September": "09", "October": "10", "November": "11", "December": "12"
                }
                month_num = month_map.get(month_str.capitalize(), "01")
                day_num = day_str.zfill(2)
                date_str = f"{year_str}-{month_num}-{day_num}"
                print(f"📆 Found game date: {month_str} {day_str}, {year_str}")
            else:
                date_str = None
                print("📆 No specific date mentioned, looking at all matchups")
        else:
            date_str = date_match.group(1)
            print(f"📆 Found game date: {date_str}")
        
        # Create a date parameter string if a date was found
        date_param = f" date={date_str}" if date_str else ""
        
        # Directly fetch the schedule using the tool function
        try:
            print(f"🔎 Searching for {team1.title()} vs {team2.title()} games{' on ' + date_str if date_str else ''}...")
            schedule_info = fetch_team_schedule.invoke({"teams_and_params": f"{team1} {team2}{date_param}"})
            
            # Check if we have an adjusted date in the schedule info
            adjusted_date_match = re.search(r"ADJUSTED_DATE:\s*(\d{4}-\d{2}-\d{2})", schedule_info)
            if adjusted_date_match:
                adjusted_date = adjusted_date_match.group(1)
                if date_str and adjusted_date != date_str:
                    print(f"📌 No game on {date_str}, using closest game on {adjusted_date} instead")
            else:
                adjusted_date = date_str
                
        except Exception:
            # If direct schedule fetching fails, use the full agent
            print("⚙️ Having trouble finding the game schedule, trying a different approach...")
            return bobby_bets_agent.invoke({"input": question})
        
        # Now run the remaining tools in parallel using direct function calls
        results = {}
        
        print(f"📊 Gathering team statistics and betting trends and game context...")
        
        # Define functions to run each tool directly
        def get_team1_stats():
            try:
                return fetch_team_stats.invoke({"team_name": team1})
            except Exception as e:
                return f"Error fetching stats for {team1}: {str(e)}"
        
        def get_team2_stats():
            try:
                return fetch_team_stats.invoke({"team_name": team2})
            except Exception as e:
                return f"Error fetching stats for {team2}: {str(e)}"
        
        def get_betting_trends():
            try:
                if adjusted_date:
                    return fetch_betting_trends.invoke({"team1": team1, "team2": team2, "date": adjusted_date})
                return "No date provided for betting trends."
            except Exception as e:
                return f"Error fetching betting trends: {str(e)}"
        
        # Run the functions in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_func = {
                executor.submit(get_team1_stats): "team1_stats",
                executor.submit(get_team2_stats): "team2_stats",
                executor.submit(get_betting_trends): "betting_trends"
            }
            
            for future in concurrent.futures.as_completed(future_to_func):
                func_name = future_to_func[future]
                try:
                    result = future.result()
                    results[func_name] = result
                    if func_name == "team1_stats":
                        print(f"📈 Got {team1.title()}'s season stats and injury report")
                    elif func_name == "team2_stats":
                        print(f"📈 Got {team2.title()}'s season stats and injury report")
                    elif func_name == "betting_trends":
                        print(f"💰 Checked betting trends for this matchup and H2H stats")
                except Exception as exc:
                    error_msg = f"Error getting {func_name}: {exc}"
                    results[func_name] = error_msg
        
        # Combine all the results
        team1_stats = results.get("team1_stats", "")
        team2_stats = results.get("team2_stats", "")
        betting_trends = results.get("betting_trends", "")
        
        # Use the full agent for the final analysis
        try:
            print(f"🧮 Analyzing {team1.title()} vs {team2.title()} matchup data...")
            # Use the analyze_matchup_data tool directly instead of the full agent
            analysis_output = analyze_matchup_data.invoke({"team1_stats": team1_stats, "team2_stats": team2_stats, "betting_trends": betting_trends})
        except Exception as e:
            analysis_output = f"Error during analysis: {str(e)}"
        
        # Instead of extracting and formatting the data ourselves, pass all the raw data to the LLM
        print("🎲 Crafting a sports bettor style analysis...")
        
        # Extract source URLs from the data for citation purposes
        schedule_source = ""
        if "URL:" in schedule_info:
            schedule_source_match = re.search(r"URL:\s*(https?://[^\s]+)", schedule_info)
            if schedule_source_match:
                schedule_source = schedule_source_match.group(1)
        
        team1_source = ""
        if "URL:" in team1_stats:
            team1_source_match = re.search(r"URL:\s*(https?://[^\s]+)", team1_stats)
            if team1_source_match:
                team1_source = team1_source_match.group(1)
        
        team2_source = ""
        if "URL:" in team2_stats:
            team2_source_match = re.search(r"URL:\s*(https?://[^\s]+)", team2_stats)
            if team2_source_match:
                team2_source = team2_source_match.group(1)
        
        betting_source = ""
        if betting_trends and "Source:" in betting_trends:
            betting_source_match = re.search(r"Source:\s*(https?://[^\s]+)", betting_trends)
            if betting_source_match:
                betting_source = betting_source_match.group(1)
        
        # Prepare a prompt for the LLM with all the raw data
        bettor_prompt = f"""
I need you to analyze this NBA matchup between {team1.title()} and {team2.title()} and provide your insights as a seasoned sports bettor.

Here's all the data I've collected:

## SCHEDULE INFO:
{schedule_info}

## TEAM 1 STATS ({team1.title()}):
{team1_stats}

## TEAM 2 STATS ({team2.title()}):
{team2_stats}

## BETTING TRENDS:
{betting_trends if betting_trends else "No specific betting trends available."}

## ANALYSIS OUTPUT:
{analysis_output}

## SOURCE INFORMATION FOR CITATIONS:
- Schedule and Game Information: {schedule_source if schedule_source else "Basketball Reference"}
- {team1.title()} Team Statistics: {team1_source if team1_source else "Basketball Reference"}
- {team2.title()} Team Statistics: {team2_source if team2_source else "Basketball Reference"}
- Betting Trends: {betting_source if betting_source else "Not available"}

Based on all this information, give me your take on this matchup as a seasoned sports bettor. Include:
1. Your prediction for the winner with your confidence level
2. Key factors influencing your prediction
3. Notable insights you discovered
4. Specific betting recommendations (moneyline, spread, over/under)
5. Citations to the information sources

IMPORTANT: Back up your predictions with specific data points and evidence. For example:
- "I'm taking the Celtics because they're 8-2 in their last 10 home games against teams with winning records"
- "The Warriors are shooting 42% from three over their last 5 games, while the Lakers are allowing 38% from deep"

Be sure to cite your sources clearly. Mention where you got your information from, such as:
- Team statistics from Basketball Reference (use the actual URLs provided in the SOURCE INFORMATION section)
- Injury reports
- Betting trends
- Head-to-head matchup history
- Rest days and schedule information

Use an authentic sports bettor voice - conversational, with some slang and personality. Don't use a rigid template - make it sound natural and vary your language.
"""

        try:
            # Use the LLM directly to generate the response
            bettor_response = llm.invoke(bettor_prompt)
            final_response = bettor_response.content
        except Exception as e:
            # Fall back to the analysis output if there's an error
            print(f"Error generating bettor response: {str(e)}")
            final_response = f"""
# {team1.title()} vs {team2.title()} Analysis

{analysis_output}

Note: I encountered an error while formatting the response in a sports bettor style. The above is the raw analysis.
"""
        
        # Store the analysis in memory
        print("💾 Saving your interest in this matchup for future reference...")
        try:
            # Create memory entries as simple strings
            
            # Store team interest
            team_interest = f"User showed interest in {team1.title()} vs {team2.title()} matchup"
            
            # Extract predicted winner from analysis for memory
            predicted_winner_match = re.search(r"\*\*Predicted Winner\*\*: (.*?)$", analysis_output, re.MULTILINE)
            predicted_winner = predicted_winner_match.group(1) if predicted_winner_match else "Unknown"
            
            # Extract confidence level from analysis for memory
            confidence_level_match = re.search(r"\*\*Confidence Level\*\*: (.*?)$", analysis_output, re.MULTILINE)
            confidence_level = confidence_level_match.group(1) if confidence_level_match else "Unknown"
            
            # Store prediction
            prediction_memory = f"Bobby Bets predicted {predicted_winner} to win against {team2.title() if predicted_winner == team1.title() else team1.title()} with {confidence_level} confidence"
            
            # Store betting recommendation if available
            betting_memory = None
            betting_recs_match = re.search(r"### Betting Recommendations\n(.*?)(?=###|$)", analysis_output, re.DOTALL)
            if betting_recs_match:
                betting_recs_section = betting_recs_match.group(1).strip()
                if betting_recs_section and betting_recs_section != "No betting recommendations available.":
                    betting_memory = f"Betting recommendation for {team1.title()} vs {team2.title()}: {betting_recs_section[:200]}..."
            
            # Add to memory with metadata
            metadata = {
                "team1": team1,
                "team2": team2,
                "predicted_winner": predicted_winner,
                "confidence_level": confidence_level
            }
            
            if adjusted_date:
                metadata["game_date"] = adjusted_date
                
            # Store in memory - one at a time to ensure they're all stored
            memory_client.add(team_interest, user_id=user_id, metadata=metadata)
            memory_client.add(prediction_memory, user_id=user_id, metadata=metadata)
            
            if betting_memory:
                memory_client.add(betting_memory, user_id=user_id, metadata=metadata)
            
        except Exception:
            pass  # Silently continue if memory storage fails
        
        print(f"✅ Analysis complete!")
        
        return {"output": final_response}
    except Exception as e:
        # Fall back to the full agent for any unexpected errors
        print("⚙️ Processing your NBA question...")
        try:
            return bobby_bets_agent.invoke({"input": question})
        except Exception as fallback_error:
            return {"output": f"Error analyzing your question: {str(fallback_error)}"}

# Example usage
if __name__ == "__main__":
    # Example question with a date that needs adjustment
    sample_question = "How do the Lakers and Warriors match up for their game on January 18, 2025?"
    print(f"Question: {sample_question}")
    
    # Use a test user ID
    test_user_id = "test_user_123"
    
    result = ask_bobby(sample_question, user_id=test_user_id)
    print("\nFinal Answer:")
    print(result["output"]) 
    
    # Show memory count after analysis
    memory_count = manage_memory.invoke({"action": 'count', "user_id": test_user_id})
    print(f"\n{memory_count}")


