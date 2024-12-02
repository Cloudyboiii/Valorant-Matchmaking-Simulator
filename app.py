# import streamlit as st
# import json
# import os
# import plotly.express as px
# import plotly.graph_objects as go
# import pandas as pd

# # Import necessary modules from the existing project
# from data.player_data import generate_player_data, GameMode, Region, Rank
# from matchmaking.kmeans_matchmaking import perform_matchmaking
# from matchmaking.evaluation import evaluate_teams, print_evaluation_results
# from matchmaking.reinforcement_learning import QLearningMatchmaker
# from matchmaking.constraints import MatchmakingConstraints
# from main import save_match_result

# # Custom CSS for Valorant-inspired design
# def set_custom_styling():
#     st.markdown("""
#     <style>
#     /* Valorant-inspired color palette */
#     :root {
#         --valorant-red: #FF4655;
#         --valorant-dark-blue: #0F1923;
#         --valorant-light-blue: #1F2933;
#         --valorant-accent: #BD3944;
#         --valorant-text: #FFFFFF;
#     }

#     /* Background and base styling */
#     .stApp {
#         background-color: var(--valorant-dark-blue);
#         color: var(--valorant-text);
#     }

#     /* Sidebar styling */
#     [data-testid="stSidebar"] {
#         background-color: var(--valorant-light-blue);
#     }

#     /* Header styling */
#     h1, h2, h3, h4, h5, h6 {
#         color: var(--valorant-text) !important;
#     }

#     /* Button styling */
#     .stButton>button {
#         background-color: var(--valorant-red);
#         color: white;
#         border: none;
#         transition: all 0.3s ease;
#     }

#     .stButton>button:hover {
#         background-color: var(--valorant-accent);
#         transform: scale(1.05);
#     }

#     /* Card-like containers */
#     [data-testid="stVerticalBlock"] {
#         background-color: var(--valorant-light-blue);
#         border-radius: 10px;
#         padding: 15px;
#         margin-bottom: 10px;
#     }

#     /* Metric containers */
#     [data-testid="metric-container"] {
#         background-color: var(--valorant-dark-blue);
#         border-radius: 10px;
#         padding: 10px;
#     }

#     /* Select box styling */
#     .stSelectbox>div>div>div {
#         background-color: var(--valorant-dark-blue);
#         color: var(--valorant-text);
#     }

#     /* Plotly chart styling */
#     .js-plotly-plot {
#         background-color: var(--valorant-light-blue);
#     }
#     </style>
#     """, unsafe_allow_html=True)

# def load_recent_matches():
#     """Load recent match results from JSON files."""
#     match_results = []
#     if os.path.exists('match_results'):
#         # Sort match result files by modification time, most recent first
#         result_files = sorted(
#             [f for f in os.listdir('match_results') if f.endswith('.json')],
#             key=lambda x: os.path.getmtime(os.path.join('match_results', x)),
#             reverse=True
#         )
        
#         # Load the 5 most recent matches
#         for filename in result_files[:5]:
#             with open(os.path.join('match_results', filename), 'r') as f:
#                 match_results.append(json.load(f))
    
#     return match_results

# def display_match_details(match_data):
#     """Display detailed information about a specific match."""
#     st.subheader(f"Match Details - {match_data['timestamp']}")
    
#     # Create two columns for team comparison
#     col1, col2 = st.columns(2)
    
#     # Team 1 details
#     with col1:
#         st.markdown("### Team 1 🔴")
#         team1 = match_data['teams']['team_1']
#         st.metric("Average Skill", f"{team1['average_skill']:.2f}")
        
#         st.markdown("**Players:**")
#         for player in team1['players']:
#             st.write(f"- {player['name']} (Rank: {player['rank']}, Skill: {player['skill_rating']:.2f})")
    
#     # Team 2 details
#     with col2:
#         st.markdown("### Team 2 🔵")
#         team2 = match_data['teams']['team_2']
#         st.metric("Average Skill", f"{team2['average_skill']:.2f}")
        
#         st.markdown("**Players:**")
#         for player in team2['players']:
#             st.write(f"- {player['name']} (Rank: {player['rank']}, Skill: {player['skill_rating']:.2f})")
    
#     # Match quality visualization
#     st.subheader("Match Quality")
#     st.metric("Overall Match Quality", f"{match_data['match_quality']:.2%}")

# def plot_team_skills(match_data):
#     """Create a bar plot comparing team skills."""
#     # Prepare data for plotting
#     team_data = [
#         {'Team': 'Team 1', 'Avg Skill': match_data['teams']['team_1']['average_skill']},
#         {'Team': 'Team 2', 'Avg Skill': match_data['teams']['team_2']['average_skill']}
#     ]
    
#     df = pd.DataFrame(team_data)
    
#     fig = px.bar(df, x='Team', y='Avg Skill', 
#                  title='Team Average Skill Comparison',
#                  labels={'Avg Skill': 'Average Skill Rating'},
#                  color='Team',
#                  color_discrete_map={'Team 1': '#FF4655', 'Team 2': '#1D9ED8'})
    
#     # Customize the layout
#     fig.update_layout(
#         plot_bgcolor='rgba(0,0,0,0)',
#         paper_bgcolor='rgba(0,0,0,0)',
#         font_color='white'
#     )
    
#     st.plotly_chart(fig)

# def main_app():
#     # Set custom styling
#     set_custom_styling()
    
#     st.title("🎮 Valorant Matchmaking Simulator")
    
#     # Sidebar for configuration
#     st.sidebar.header("Matchmaking Configuration")
    
#     # Game Mode Selection
#     mode_options = {
#         'Competitive': GameMode.COMPETITIVE, 
#         'Casual': GameMode.CASUAL
#     }
#     selected_mode = st.sidebar.selectbox("Select Game Mode", list(mode_options.keys()))
#     mode = mode_options[selected_mode]
    
#     # Region Selection
#     region_options = {
#         'North America': Region.NA, 
#         'Europe': Region.EU, 
#         'Asia': Region.ASIA, 
#         'Oceania': Region.OCE
#     }
#     selected_region = st.sidebar.selectbox("Select Region", list(region_options.keys()))
#     region = region_options[selected_region]
    
#     # Number of Players
#     num_teams = 2  # Valorant 5v5
#     players_per_team = MatchmakingConstraints.PLAYERS_PER_TEAM
#     num_players = num_teams * players_per_team
    
#     # Simulate Matchmaking Button
#     if st.sidebar.button("Create New Match"):
#         # Generate player data
#         st.sidebar.info(f"Generating {num_players} players...")
#         players = generate_player_data(num_players)
        
#         # Perform matchmaking
#         st.sidebar.info("Performing matchmaking...")
#         teams = perform_matchmaking(players, num_teams, mode, region)
        
#         # Evaluate teams
#         st.sidebar.info("Evaluating match...")
#         team_metrics = evaluate_teams(teams, mode, region)
        
#         # Save match result
#         save_match_result(teams, team_metrics, mode, region)
        
#         st.success("New match created successfully!")
    
#     # Recent Matches Section
#     st.header("Recent Matches")
    
#     # Load and display recent matches
#     recent_matches = load_recent_matches()
    
#     if recent_matches:
#         # Create tabs for recent matches
#         tabs = st.tabs([f"Match {i+1}" for i in range(len(recent_matches))])
        
#         for i, match_data in enumerate(recent_matches):
#             with tabs[i]:
#                 display_match_details(match_data)
#                 plot_team_skills(match_data)
#     else:
#         st.info("No recent matches. Click 'Create New Match' to start.")

# def main():
#     main_app()

# if __name__ == "__main__":
#     main()


import streamlit as st
import json
import os
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Import necessary modules from the existing project
from data.player_data import generate_player_data, GameMode, Region, Rank
from matchmaking.kmeans_matchmaking import perform_matchmaking
from matchmaking.evaluation import evaluate_teams, print_evaluation_results
from matchmaking.reinforcement_learning import QLearningMatchmaker
from matchmaking.constraints import MatchmakingConstraints
from main import save_match_result

# Custom CSS for Valorant-inspired design
def set_custom_styling():
    st.markdown("""
    <style>
    /* Valorant-inspired color palette */
    :root {
        --valorant-red: #FF4655;
        --valorant-dark-blue: #0F1923;
        --valorant-light-blue: #1F2933;
        --valorant-accent: #BD3944;
        --valorant-text: #FFFFFF;
        --valorant-grey: #696969;
    }

    /* Background and base styling */
    .stApp {
        background-color: var(--valorant-dark-blue);
        color: var(--valorant-text);
        font-family: 'Roboto', sans-serif;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: var(--valorant-light-blue);
        padding: 20px;
        border-radius: 10px;
    }

    /* Header styling */
    h1, h2, h3, h4, h5, h6 {
        color: var(--valorant-text) !important;
    }

    /* Button styling */
    .stButton>button {
        background-color: var(--valorant-red);
        color: white;
        border: none;
        transition: all 0.3s ease;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        cursor: pointer;
    }

    .stButton> button:hover {
        background-color: var(--valorant-accent);
        transform: scale(1.05);
    }

    /* Card-like containers */
    [data-testid="stVerticalBlock"] {
        background-color: var(--valorant-light-blue);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }

    /* Metric containers */
    [data-testid="metric-container"] {
        background-color: var(--valorant-dark-blue);
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    /* Select box styling */
    .stSelectbox>div>div>div {
        background-color: var(--valorant-dark-blue);
        color: var(--valorant-text);
        border-radius: 5px;
    }

    /* Plotly chart styling */
    .js-plotly-plot {
        background-color: var(--valorant-light-blue);
    }
    </style>
    """, unsafe_allow_html=True)

def load_recent_matches():
    """Load recent match results from JSON files."""
    match_results = []
    if os.path.exists('match_results'):
        # Sort match result files by modification time, most recent first
        result_files = sorted(
            [f for f in os.listdir('match_results') if f.endswith('.json')],
            key=lambda x: os.path.getmtime(os.path.join('match_results', x)),
            reverse=True
        )
        
        # Load the 5 most recent matches
        for filename in result_files[:5]:
            with open(os.path.join('match_results', filename), 'r') as f:
                match_results.append(json.load(f))
    
    return match_results

def display_match_details(match_data):
    """Display detailed information about a specific match."""
    st.subheader(f"Match Details - {match_data['timestamp']}")
    
    # Create two columns for team comparison
    col1, col2 = st.columns(2)
    
    # Team 1 details
    with col1:
        st.markdown("### Team 1 🔴")
        team1 = match_data['teams']['team_1']
        st.metric("Average Skill", f"{team1['average_skill']:.2f}")
        
        st.markdown("**Players:**")
        for player in team1['players']:
            st.write(f"- {player['name']} (Rank: {player['rank']}, Skill: {player['skill_rating']:.2f})")
    
    # Team 2 details
    with col2:
        st.markdown("### Team 2 🔵")
        team2 = match_data['teams']['team_2']
        st.metric("Average Skill", f"{team2['average_skill']:.2f}")
        
        st.markdown("**Players:**")
        for player in team2['players']:
            st.write(f"- {player['name']} (Rank: {player['rank']}, Skill: {player['skill_rating']:.2f})")
    
    # Match quality visualization
    st.subheader("Match Quality")
    st.metric("Overall Match Quality", f"{match_data['match_quality']:.2%}")

def plot_team_skills(match_data):
    """Create a bar plot comparing team skills."""
    # Prepare data for plotting
    team_data = [
        {'Team': 'Team 1', 'Avg Skill': match_data['teams']['team_1']['average_skill']},
        {'Team': 'Team 2', 'Avg Skill': match_data['teams']['team_2']['average_skill']}
    ]
    
    df = pd.DataFrame(team_data)
    
    fig = px.bar(df, x='Team', y='Avg Skill', 
                 title='Team Average Skill Comparison',
                 labels={'Avg Skill': 'Average Skill Rating'},
                 color='Team',
                 color_discrete_map={'Team 1': '#FF4655', 'Team 2': '#1D9ED8'})
    
    # Customize the layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    
    st.plotly_chart(fig)

def main_app():
    # Set custom styling
    set_custom_styling()
    
    st.title("🎮 Valorant Matchmaking Simulator")
    
    # Sidebar for configuration
    st.sidebar.header("Matchmaking Configuration")
    
    # Game Mode Selection
    mode_options = {
        'Competitive': GameMode.COMPETITIVE, 
 'Casual': GameMode.CASUAL
    }
    selected_mode = st.sidebar.selectbox("Select Game Mode", list(mode_options.keys()))
    mode = mode_options[selected_mode]
    
    # Region Selection
    region_options = {
        'North America': Region.NA, 
        'Europe': Region.EU, 
        'Asia': Region.ASIA, 
        'Oceania': Region.OCE
    }
    selected_region = st.sidebar.selectbox("Select Region", list(region_options.keys()))
    region = region_options[selected_region]
    
    # Number of Players
    num_teams = 2  # Valorant 5v5
    players_per_team = MatchmakingConstraints.PLAYERS_PER_TEAM
    num_players = num_teams * players_per_team
    
    # Simulate Matchmaking Button
    if st.sidebar.button("Create New Match"):
        # Generate player data
        st.sidebar.info(f"Generating {num_players} players...")
        players = generate_player_data(num_players)
        
        # Perform matchmaking
        st.sidebar.info("Performing matchmaking...")
        teams = perform_matchmaking(players, num_teams, mode, region)
        
        # Evaluate teams
        st.sidebar.info("Evaluating match...")
        team_metrics = evaluate_teams(teams, mode, region)
        
        # Save match result
        save_match_result(teams, team_metrics, mode, region)
        
        st.success("New match created successfully!")
    
    # Recent Matches Section
    st.header("Recent Matches")
    
    # Load and display recent matches
    recent_matches = load_recent_matches()
    
    if recent_matches:
        # Create tabs for recent matches
        tabs = st.tabs([f"Match {i+1}" for i in range(len(recent_matches))])
        
        for i, match_data in enumerate(recent_matches):
            with tabs[i]:
                display_match_details(match_data)
                plot_team_skills(match_data)
    else:
        st.info("No recent matches. Click 'Create New Match' to start.")

def main():
    main_app()

if __name__ == "__main__":
    main()