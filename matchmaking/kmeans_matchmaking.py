import numpy as np
from sklearn.cluster import KMeans
from typing import List, Dict
from data.player_data import Player, GameMode, Region
from matchmaking.constraints import MatchmakingConstraints

def perform_matchmaking(players: List[Player], num_teams: int, mode: GameMode, region: Region) -> Dict[int, List[Player]]:
    # Ensure we have the correct number of players
    if len(players) != num_teams * MatchmakingConstraints.PLAYERS_PER_TEAM:
        raise ValueError(f"Number of players must be exactly {num_teams * MatchmakingConstraints.PLAYERS_PER_TEAM}")
    
    # Extract features for clustering
    features = np.array([[
        p.skill_rating,
        p.rank.value,
        p.win_rate,
        p.latency[region],
        1.0 if mode in p.preferred_modes else 0.0
    ] for p in players])
    
    # Normalize features
    features = (features - features.mean(axis=0)) / features.std(axis=0)
    
    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=num_teams, random_state=42)
    labels = kmeans.fit_predict(features)
    
    # Create teams based on cluster labels
    teams = {i: [] for i in range(num_teams)}
    for player, label in zip(players, labels):
        teams[label].append(player)
    
    # Balance teams to ensure exactly 5 players per team
    # and rank/skill similarity
    all_players = players.copy()
    balanced_teams = {i: [] for i in range(num_teams)}
    
    # Sort players by skill rating and rank
    all_players.sort(key=lambda p: (p.rank.value, p.skill_rating), reverse=True)
    
    # Distribute players to ensure balanced team sizes and ranks
    while all_players:
        for team_id in range(num_teams):
            if len(balanced_teams[team_id]) < MatchmakingConstraints.PLAYERS_PER_TEAM and all_players:
                # Find best available player for this team
                best_player = min(all_players, 
                    key=lambda p: (
                        abs(np.mean([p2.rank.value for p2 in balanced_teams[team_id]]) - p.rank.value) 
                        if balanced_teams[team_id] else abs(p.rank.value - 11)  # Aim for middle ranks if team is empty
                    )
                )
                balanced_teams[team_id].append(best_player)
                all_players.remove(best_player)
    
    return balanced_teams