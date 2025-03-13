# Bobby Bets - NBA Betting Analysis

Bobby Bets is an AI-powered NBA analyst and sports betting advisor that provides data-driven insights and betting recommendations for NBA games.

## Features

- Get matchup analysis between any two NBA teams
- View team statistics and injury reports
- Get betting recommendations and trends
- Personalized experience with user memory system
- Command-line interface for quick analysis

## Preferred Python Version 

It is recommended to use **Python 3.9.13** or any later version.

## Setup and Installation

1. Clone this repository
2. Open project in vs code
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Set up API keys:
   - You'll need API keys for OpenAI, FireCrawl, and Mem0
   - I've left my API keys in the code for your testing purposes
   - Note: These keys will be deactivated at the end of the week (3/16)
   - For production use, replace them with your own API keys or use environment variables
   - **IMPORTANT** - you'll need to add your own OpenAI API key on line 23 of bobby_bets_agent.py 

## Usage

### Running the Command Line Interface

```bash
python app.py
```

This will start the command-line interface where you can interact with Bobby Bets directly.

## Interacting with Bobby Bets

You can ask Bobby Bets about:

1. **Team Matchups**: 
   - "How do the Lakers and Warriors match up on Jan, 5, 2025?"
   - "Analyze Celtics vs Bucks for their game tomorrow"

2. **Betting Insights**:
   - "What are the betting trends for Knicks vs Heat on March 17th, 2025?"
   - "Should I bet on the over for Suns vs Mavericks on March 9th, 2025?"

## Architecture Overview

Bobby Bets is built using a modular architecture with the following components:

1. **Core Agent**: Powered by LangChain and OpenAI's GPT-4o model, the agent orchestrates the analysis workflow and generates natural language responses.

2. **Data Collection Tools**: A set of specialized functions that gather data from various sources:
   - `fetch_team_schedule`: Retrieves game schedules between teams as well as some head to head stats
   - `fetch_team_stats`: Collects team statistics and injury reports
   - `fetch_betting_trends`: Gathers betting trends for specific matchups

3. **Analysis Engine**: Processes the collected data to generate insights:
   - `analyze_matchup_data`: Combines team stats and betting trends to create recommendations
   - `extract_team_names`: Identifies NBA teams mentioned in user queries

4. **Memory System**: Powered by Mem0, stores user preferences and previous analyses:
   - `manage_memory`: Handles memory operations (add, retrieve, clear)

5. **Command Line Interface**: A simple text-based interface for interacting with the agent.

## Design Decisions

1. **Tool-based Architecture**: The system uses a tool-based approach where specialized functions handle specific tasks. This makes the codebase modular and easier to maintain.

2. **Parallel Data Collection**: The system fetches data from multiple sources in parallel to reduce response time.

3. **Date Adjustment System**: When users request analysis for a date with no scheduled game, the system automatically finds the closest game date.

4. **Memory System**: The application remembers user preferences and previous analyses to provide more personalized recommendations over time.

5. **Sports Bettor Persona**: Responses are crafted to sound like a sports bettor with domain expertise, making the experience more engaging.

6. **Error Handling**: The system includes error handling to gracefully recover from API failures or data inconsistencies.

## Limitations and Potential Improvements

1. **Data Freshness**: The system relies on web scraping, which may not always provide the most up-to-date information. Future versions could integrate with official NBA APIs.

2. **API Dependencies**: The application depends on third-party services (FireCrawl, Mem0, OpenAI) which may have rate limits or service disruptions.

3. **Limited Betting Markets**: Currently focuses on basic betting markets (moneyline, spread, over/under). Could be expanded to include player props, parlays, etc.

4. **Performance Optimization**: Response times could be improved by caching frequently requested data.

5. **User Interface**: The command-line interface is functional but basic. A web or mobile interface would improve accessibility.

6. **Personalization**: While the memory system stores user preferences, the personalization could be enhanced with more sophisticated user modeling.

7. **Historical Analysis**: Adding historical performance data and trend analysis would strengthen the betting recommendations.

8. **Evaluation Metrics**: Implementing a system to track prediction accuracy would help users gauge reliability.

## Memory System

Bobby Bets remembers your previous interactions to provide more personalized recommendations. You can manage your memory with these commands:

- `clear memory`: Delete all stored memories for your user ID
- `list memory`: View all memories stored for your user ID
- `count memory`: See how many memories are stored for your user ID

## User IDs

Each user Set a custom ID by entering your username when prompted

## Technologies Used

- Python
- LangChain
- OpenAI
- Mem0 (for memory storage)
- FireCrawl (for web scraping)

## Dependencies

The application relies on the following main dependencies:
- langchain
- langchain-openai
- openai
- firecrawl-py
- mem0ai

For a complete list of dependencies, see the `requirements.txt` file.

## IMPORTANT NOTE

This project is for educational purposes only. Sports betting should be done responsibly. 
