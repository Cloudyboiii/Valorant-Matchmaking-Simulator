from typing import Dict, List
import numpy as np
import random
import string
from data.player_data import Player, GameMode, Region
from matchmaking.constraints import MatchmakingConstraints

def generate_player_name() -> str:
    """Generate a random player name."""
    adjectives = ['Swift', 'Silent', 'Brave', 'Fierce', 'Cunning', 'Skilled', 'Sharp', 'Bold', 'Quick', 'Phantom']
    nouns = ['Wolf', 'Eagle', 'Hawk', 'Tiger', 'Shadow', 'Blade', 'Arrow', 'Storm', 'Fire', 'Ghost']
    return f"{random.choice(adjectives)}{random.choice(nouns)}"

def evaluate_teams(teams: Dict[int, List[Player]], mode: GameMode, region: Region):
    team_metrics = {}
    
    for team_number, players in teams.items():
        if len(players) != MatchmakingConstraints.PLAYERS_PER_TEAM:
            raise ValueError(f"Team {team_number} has {len(players)} players, expected {MatchmakingConstraints.PLAYERS_PER_TEAM}")
            
        # Add names to players if not already present
        for player in players:
            if not hasattr(player, 'name'):
                player.name = generate_player_name()
        
        skill_levels = [p.skill_rating for p in players]
        latencies = [p.latency[region] for p in players]
        mode_preferences = [1.0 if mode in p.preferred_modes else 0.0 for p in players]
        
        metrics = {
            'average_skill': np.mean(skill_levels),
            'skill_variance': np.var(skill_levels),
            'average_latency': np.mean(latencies),
            'mode_preference_ratio': np.mean(mode_preferences),
            'team_size': len(players),
            'players': players
        }
        
        # Calculate predicted win rate based on skill ratings
        total_skill = sum(skill_levels)
        metrics['predicted_win_rate'] = 1 / (1 + np.exp(-0.006 * (total_skill - 1500 * len(players))))
        
        team_metrics[team_number] = metrics
    
    # Calculate overall match quality
    match_quality = MatchmakingConstraints.calculate_match_quality(list(teams.values()), mode, region)
    team_metrics['match_quality'] = match_quality
    
    return team_metrics

def print_evaluation_results(team_metrics: Dict):
    print("\nMatchmaking Evaluation Results:")
    print(f"Overall Match Quality: {team_metrics['match_quality']:.3f}")
    
    for team_number, metrics in team_metrics.items():
        if team_number == 'match_quality':
            continue
            
        print(f"\nTeam {team_number + 1}:")
        print(f"  Team Size: {metrics['team_size']}")
        print(f"  Average Skill Rating: {metrics['average_skill']:.1f}")
        print(f"  Skill Variance: {metrics['skill_variance']:.1f}")
        print(f"  Average Latency: {metrics['average_latency']:.1f}ms")
        print(f"  Mode Preference Ratio: {metrics['mode_preference_ratio']:.2f}")
        # print(f"  Predicted Win Rate: {metrics['predicted_win_rate']:.3f}")
        
        print("  Players:")
        for player in metrics['players']:
            print(f"    - Name: {player.name}")
            print(f"      ID: {player.id}")
            print(f"      Rank: {player.rank.name}")
            print(f"      Skill Rating: {player.skill_rating:.1f}")
            print(f"      Latency: {player.latency[player.preferred_region]:.1f}ms")
            print(f"      Rank Points: {player.rank_points}")
            print()  # Extra line for readability