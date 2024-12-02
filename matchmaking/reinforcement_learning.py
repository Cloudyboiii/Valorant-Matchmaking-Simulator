import numpy as np
from typing import List, Dict
from data.player_data import Player, GameMode, Region
from matchmaking.kmeans_matchmaking import perform_matchmaking
from matchmaking.constraints import MatchmakingConstraints
import json
import os

class QLearningMatchmaker:
    def __init__(self, num_teams: int, mode: GameMode, region: Region,
                 learning_rate=0.1, discount_factor=0.9, exploration_rate=1.0,
                 model_path="models/q_table.npy"):
        self.num_teams = num_teams
        self.mode = mode
        self.region = region
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.model_path = model_path
        
        # Q-table: states are discretized skill levels, actions are team assignments
        self.num_skill_levels = 20  # Increased for finer granularity
        self.num_latency_levels = 5
        self.state_size = self.num_skill_levels * self.num_latency_levels
        
        # Initialize or load Q-table
        self.initialize_q_table()
        
        # Training metrics
        self.training_history = {
            'match_qualities': [],
            'exploration_rates': [],
            'episodes': []
        }
    
    def initialize_q_table(self):
        """Initialize or load existing Q-table"""
        if os.path.exists(self.model_path):
            self.q_table = np.load(self.model_path)
            print(f"Loaded existing Q-table from {self.model_path}")
        else:
            self.q_table = np.zeros((self.state_size, self.num_teams))
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            print("Initialized new Q-table")
    
    def save_q_table(self):
        """Save Q-table to file"""
        np.save(self.model_path, self.q_table)
        print(f"Saved Q-table to {self.model_path}")
    
    def get_state(self, player: Player) -> int:
        """Convert player attributes to state index"""
        skill_level = min(self.num_skill_levels - 1,
                         int(player.skill_rating / 6000 * self.num_skill_levels))
        latency_level = min(self.num_latency_levels - 1,
                          int(player.latency[self.region] / 200 * self.num_latency_levels))
        return skill_level * self.num_latency_levels + latency_level
    
    def choose_action(self, state: int) -> int:
        """Choose team assignment using epsilon-greedy policy"""
        if np.random.rand() < self.exploration_rate:
            return np.random.randint(self.num_teams)
        else:
            return np.argmax(self.q_table[state])
    
    def update(self, state: int, action: int, reward: float, next_state: int):
        """Update Q-value using Q-learning update rule"""
        best_next_value = np.max(self.q_table[next_state])
        current_value = self.q_table[state, action]
        
        self.q_table[state, action] = current_value + \
            self.learning_rate * (reward + self.discount_factor * best_next_value - current_value)
    
    def train(self, players: List[Player], num_episodes: int):
        """Train the matchmaker using Q-learning"""
        if len(players) % (self.num_teams * MatchmakingConstraints.PLAYERS_PER_TEAM) != 0:
            raise ValueError("Number of players must be divisible by total required players")
        
        print("\nTraining Q-Learning Matchmaker...")
        best_quality = 0.0
        
        for episode in range(num_episodes):
            # Shuffle players for variety
            np.random.shuffle(players)
            
            # Perform matchmaking
            teams = perform_matchmaking(players, self.num_teams, self.mode, self.region)
            
            # Calculate match quality as reward
            reward = MatchmakingConstraints.calculate_match_quality(
                list(teams.values()), self.mode, self.region)
            
            # Update Q-values for each player
            for player in players:
                state = self.get_state(player)
                action = self.choose_action(state)
                next_state = min(self.state_size - 1, state + 1)
                self.update(state, action, reward, next_state)
            
            # Track best quality
            best_quality = max(best_quality, reward)
            
            # Update training history
            self.training_history['match_qualities'].append(reward)
            self.training_history['exploration_rates'].append(self.exploration_rate)
            self.training_history['episodes'].append(episode + 1)
            
            # Decay exploration rate
            self.exploration_rate = max(0.01, self.exploration_rate * 0.995)
            
            # Print progress
            if (episode + 1) % 100 == 0:
                avg_quality = np.mean(self.training_history['match_qualities'][-100:])
                print(f"Episode {episode + 1}/{num_episodes}, "
                      f"Average Quality: {avg_quality:.3f}, "
                      f"Best Quality: {best_quality:.3f}, "
                      f"Exploration Rate: {self.exploration_rate:.3f}")
        
        # Save final Q-table
        self.save_q_table()
        
        # Save training history
        with open('models/training_history.json', 'w') as f:
            json.dump(self.training_history, f, indent=2)
        
        print("\nTraining completed!")
        print(f"Final Best Match Quality: {best_quality:.3f}")