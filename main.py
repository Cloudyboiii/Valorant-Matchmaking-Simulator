from data.player_data import generate_player_data, GameMode, Region
from matchmaking.kmeans_matchmaking import perform_matchmaking
from matchmaking.evaluation import evaluate_teams, print_evaluation_results
from matchmaking.reinforcement_learning import QLearningMatchmaker
from matchmaking.constraints import MatchmakingConstraints
import json
from datetime import datetime
import os

def save_match_result(teams, team_metrics, mode, region):
    """Save match result to JSON file"""
    match_data = {
        'timestamp': datetime.now().isoformat(),
        'mode': mode.value,
        'region': region.value,
        'match_quality': team_metrics['match_quality'],
        'teams': {}
    }
    
    for team_id, metrics in team_metrics.items():
        if isinstance(team_id, int):
            match_data['teams'][f'team_{team_id + 1}'] = {
                'average_skill': float(metrics['average_skill']),
                'skill_variance': float(metrics['skill_variance']),
                'average_latency': float(metrics['average_latency']),
                'predicted_win_rate': float(metrics['predicted_win_rate']),
                'players': [
                    {
                        'id': p.id,
                        'name': p.name,
                        'rank': p.rank.name,
                        'skill_rating': float(p.skill_rating),
                        'win_rate': float(p.win_rate)
                    } for p in metrics['players']
                ]
            }
    
    # Create results directory if it doesn't exist
    os.makedirs('match_results', exist_ok=True)
    
    # Save to file
    filename = f'match_results/match_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(filename, 'w') as f:
        json.dump(match_data, f, indent=2)
    
    print(f"\nMatch results saved to {filename}")

def main():
    # Configuration
    num_teams = 2  # Valorant 5v5
    players_per_team = MatchmakingConstraints.PLAYERS_PER_TEAM
    num_players = num_teams * players_per_team
    num_episodes = 1000
    mode = GameMode.COMPETITIVE
    region = Region.NA
    
    print("\nValorant Matchmaking Simulator")
    print("==============================")
    
    # Generate player data
    print(f"\nGenerating {num_players} players for {num_teams} teams of {players_per_team}...")
    players = generate_player_data(num_players)
    
    # Initialize and train Q-learning matchmaker
    matchmaker = QLearningMatchmaker(num_teams, mode, region)
    matchmaker.train(players, num_episodes)
    
    # Perform matchmaking
    print("\nPerforming final matchmaking...")
    teams = perform_matchmaking(players, num_teams, mode, region)
    
    # Evaluate and print results
    team_metrics = evaluate_teams(teams, mode, region)
    print_evaluation_results(team_metrics)
    
    # Save match results
    save_match_result(teams, team_metrics, mode, region)

if __name__ == "__main__":
    main()