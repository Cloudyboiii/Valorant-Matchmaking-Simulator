import random
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum, auto

class Rank(Enum):
    IRON_1 = 1
    IRON_2 = 2
    IRON_3 = 3
    BRONZE_1 = 4
    BRONZE_2 = 5
    BRONZE_3 = 6
    SILVER_1 = 7
    SILVER_2 = 8
    SILVER_3 = 9
    GOLD_1 = 10
    GOLD_2 = 11
    GOLD_3 = 12
    PLATINUM_1 = 13
    PLATINUM_2 = 14
    PLATINUM_3 = 15
    DIAMOND_1 = 16
    DIAMOND_2 = 17
    DIAMOND_3 = 18
    IMMORTAL_1 = 19
    IMMORTAL_2 = 20
    IMMORTAL_3 = 21
    RADIANT = 22

class GameMode(Enum):
    CASUAL = "casual"
    COMPETITIVE = "competitive"
    DEATHMATCH = "deathmatch"

class Region(Enum):
    NA = "north_america"
    EU = "europe"
    ASIA = "asia"
    OCE = "oceania"

@dataclass
class Player:
    id: int
    skill_rating: float
    rank: Rank
    rank_points: int
    uncertainty: float
    win_rate: float
    latency: Dict[Region, float]
    preferred_modes: List[GameMode]
    preferred_region: Region
    previous_wins: int
    previous_losses: int
    last_match_time: float
    party_id: Optional[int] = None

def calculate_rank(skill_rating: float) -> Rank:
    # Map skill rating to Valorant ranks
    if skill_rating < 500:
        return Rank.IRON_1
    elif skill_rating < 750:
        return Rank.IRON_2
    elif skill_rating < 1000:
        return Rank.IRON_3
    elif skill_rating < 1250:
        return Rank.BRONZE_1
    elif skill_rating < 1500:
        return Rank.BRONZE_2
    elif skill_rating < 1750:
        return Rank.BRONZE_3
    elif skill_rating < 2000:
        return Rank.SILVER_1
    elif skill_rating < 2250:
        return Rank.SILVER_2
    elif skill_rating < 2500:
        return Rank.SILVER_3
    elif skill_rating < 2750:
        return Rank.GOLD_1
    elif skill_rating < 3000:
        return Rank.GOLD_2
    elif skill_rating < 3250:
        return Rank.GOLD_3
    elif skill_rating < 3500:
        return Rank.PLATINUM_1
    elif skill_rating < 3750:
        return Rank.PLATINUM_2
    elif skill_rating < 4000:
        return Rank.PLATINUM_3
    elif skill_rating < 4250:
        return Rank.DIAMOND_1
    elif skill_rating < 4500:
        return Rank.DIAMOND_2
    elif skill_rating < 4750:
        return Rank.DIAMOND_3
    elif skill_rating < 5000:
        return Rank.IMMORTAL_1
    elif skill_rating < 5250:
        return Rank.IMMORTAL_2
    elif skill_rating < 5500:
        return Rank.IMMORTAL_3
    else:
        return Rank.RADIANT

def generate_player_data(num_players: int) -> List[Player]:
    # Ensure num_players is divisible by 10
    if num_players % 10 != 0:
        num_players = (num_players // 10 + 1) * 10
        print(f"Adjusted number of players to {num_players} to ensure 10-player lobbies")
    
    players = []
    
    for i in range(num_players):
        skill_rating = np.random.normal(2500, 500)
        skill_rating = max(100, min(5700, skill_rating))  # Constrain skill rating
        
        rank = calculate_rank(skill_rating)
        rank_points = random.randint(0, 99)  # 0-99 points within rank
        
        latencies = {
            Region.NA: max(20, random.normalvariate(60, 20)),
            Region.EU: max(20, random.normalvariate(90, 30)),
            Region.ASIA: max(20, random.normalvariate(120, 40)),
            Region.OCE: max(20, random.normalvariate(150, 50))
        }
        
        preferred_region = min(latencies.items(), key=lambda x: x[1])[0]
        num_preferred_modes = random.randint(1, 3)
        preferred_modes = random.sample(list(GameMode), num_preferred_modes)
        
        base_win_rate = 0.5 + (skill_rating - 2500) / 3000
        win_rate = max(0.1, min(0.9, base_win_rate + random.uniform(-0.1, 0.1)))
        
        player = Player(
            id=i,
            skill_rating=skill_rating,
            rank=rank,
            rank_points=rank_points,
            uncertainty=random.uniform(30, 100),
            win_rate=win_rate,
            latency=latencies,
            preferred_modes=preferred_modes,
            preferred_region=preferred_region,
            previous_wins=random.randint(0, 100),
            previous_losses=random.randint(0, 100),
            last_match_time=random.uniform(0, 1000)
        )
        
        if random.random() < 0.2:
            player.party_id = random.randint(0, num_players // 10)
        
        players.append(player)
    
    return players