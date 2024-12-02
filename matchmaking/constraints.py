from typing import List
import numpy as np
from data.player_data import Player, GameMode, Region, Rank

class MatchmakingConstraints:
    MAX_RANK_DIFFERENCE = 2  # Maximum rank levels difference
    MAX_SKILL_DIFFERENCE = 500
    MAX_LATENCY = 150
    MAX_QUEUE_TIME = 300
    PLAYERS_PER_TEAM = 5
    
    @staticmethod
    def calculate_match_quality(teams: List[List[Player]], mode: GameMode, region: Region) -> float:
        if any(len(team) != MatchmakingConstraints.PLAYERS_PER_TEAM for team in teams):
            return 0.0  # Invalid team composition
            
        quality_scores = []
        
        for team in teams:
            # Evaluate rank consistency
            rank_values = [p.rank.value for p in team]
            rank_variance = np.var(rank_values)
            rank_score = 1.0 / (1.0 + rank_variance / 10)
            
            skill_variance = np.var([p.skill_rating for p in team])
            skill_score = 1.0 / (1.0 + skill_variance / 10000)
            
            avg_latency = np.mean([p.latency[region] for p in team])
            latency_score = 1.0 - (avg_latency / MatchmakingConstraints.MAX_LATENCY)
            
            mode_score = np.mean([1.0 if mode in p.preferred_modes else 0.5 for p in team])
            
            team_score = 0.4 * rank_score + 0.3 * skill_score + 0.2 * latency_score + 0.1 * mode_score
            quality_scores.append(team_score)
        
        return np.mean(quality_scores)