import json
import csv
import os
from datetime import datetime
from typing import Dict, List
from data.player_data import Player, GameMode, Region

class MatchDataHandler:
    def __init__(self, data_dir="match_history"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.csv_path = os.path.join(data_dir, "match_history.csv")
        self.json_path = os.path.join(data_dir, "match_history.json")
        
        # Initialize CSV if it doesn't exist
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['match_id', 'timestamp', 'mode', 'region', 'match_quality',
                               'team_1_avg_skill', 'team_2_avg_skill', 'team_1_win_probability'])
    
    def save_match_data(self, match_id: str, teams: Dict[int, List[Player]], 
                       mode: GameMode, region: Region, team_metrics: Dict):
        # Prepare match data for CSV
        csv_data = {
            'match_id': match_id,
            'timestamp': datetime.now().isoformat(),
            'mode': mode.value,
            'region': region.value,
            'match_quality': team_metrics['match_quality'],
            'team_1_avg_skill': team_metrics[0]['average_skill'],
            'team_2_avg_skill': team_metrics[1]['average_skill'],
            'team_1_win_probability': team_metrics[0]['predicted_win_rate']
        }
        
        # Save to CSV
        with open(self.csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(list(csv_data.values()))
        
        # Prepare detailed match data for JSON
        json_data = {
            'match_id': match_id,
            'timestamp': csv_data['timestamp'],
            'mode': mode.value,
            'region': region.value,
            'match_quality': team_metrics['match_quality'],
            'teams': {
                team_id: {
                    'average_skill': metrics['average_skill'],
                    'skill_variance': metrics['skill_variance'],
                    'average_latency': metrics['average_latency'],
                    'mode_preference_ratio': metrics['mode_preference_ratio'],
                    'predicted_win_rate': metrics['predicted_win_rate'],
                    'players': [
                        {
                            'id': p.id,
                            'skill_rating': p.skill_rating,
                            'rank': p.rank.name,
                            'rank_points': p.rank_points,
                            'win_rate': p.win_rate,
                            'latency': p.latency[region]
                        } for p in metrics['players']
                    ]
                }
                for team_id, metrics in team_metrics.items()
                if isinstance(team_id, int)
            }
        }
        
        # Load existing JSON data
        existing_data = []
        if os.path.exists(self.json_path):
            with open(self.json_path, 'r') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []
        
        # Append new match data
        existing_data.append(json_data)
        
        # Save updated JSON data
        with open(self.json_path, 'w') as f:
            json.dump(existing_data, f, indent=2)
    
    def load_historical_matches(self):
        if not os.path.exists(self.json_path):
            return []
        
        with open(self.json_path, 'r') as f:
            return json.load(f)