import json
import time
import numpy as np
from pathlib import Path
from collections import defaultdict, deque

# ===========================
# FISH MEMORY & LEARNING
# ===========================
class FishMemory:
    """Persistent cross-game memory of fish classes and kill patterns"""
    
    def __init__(self, storage_path='fish_memory.json'):
        self.storage_path = storage_path
        self.fish_classes = defaultdict(lambda: {
            'shots_to_kill': [],
            'value': 0,
            'hp_estimates': [],
            'kill_rate': 0.0,
            'avg_shots': 0.0,
            'encounters': 0
        })
        self.load()
    
    def save(self):
        """Persist memory to disk"""
        data = {k: dict(v) for k, v in self.fish_classes.items()}
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """Load previously learned patterns"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                for k, v in data.items():
                    self.fish_classes[int(k)] = v
        except FileNotFoundError:
            pass
    
    def record_kill(self, fish_class, shots_fired, value):
        """Record successful kill outcome"""
        entry = self.fish_classes[fish_class]
        entry['shots_to_kill'].append(shots_fired)
        entry['value'] = value
        entry['encounters'] += 1
        entry['kill_rate'] = len(entry['shots_to_kill']) / max(entry['encounters'], 1)
        entry['avg_shots'] = np.mean(entry['shots_to_kill']) if entry['shots_to_kill'] else 0
        self.save()
    
    def predict_killable(self, fish_class, shots_available):
        """Predict if fish dies in exactly X shots"""
        entry = self.fish_classes[fish_class]
        
        if not entry['shots_to_kill']:
            return None, 0.0
        
        kills = entry['shots_to_kill']
        
        three_shots = len([k for k in kills if k <= 3])
        fifty_plus = len([k for k in kills if k > 50])
        
        if three_shots > len(kills) * 0.7:
            category = '3-shot'
            confidence = three_shots / len(kills)
        elif fifty_plus > len(kills) * 0.3:
            category = '50+'
            confidence = fifty_plus / len(kills)
        else:
            category = 'uncertain'
            confidence = 0.5
        
        return category, confidence
    
    def get_game_fingerprint(self, fish_classes_present):
        """Identify game type by fish class composition"""
        return tuple(sorted(fish_classes_present))


# ===========================
# SHOT TRACKING & ANALYSIS
# ===========================
class ShotTracker:
    """Track every shot and build confidence statistics"""
    
    def __init__(self, storage_path='shot_history.json'):
        self.storage_path = storage_path
        self.session_shots = []
        self.load()
    
    def save(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.session_shots, f)
    
    def load(self):
        try:
            with open(self.storage_path, 'r') as f:
                self.session_shots = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.session_shots = []
    
    def record_shot(self, fish_id, fish_class, area, x, y, vx, vy, outcome):
        """Record shot details"""
        shot = {
            'timestamp': time.time(),
            'fish_id': fish_id,
            'fish_class': fish_class,
            'area': area,
            'x': x, 'y': y,
            'vx': vx, 'vy': vy,
            'outcome': outcome
        }
        self.session_shots.append(shot)
        self.save()
    
    def get_confidence_for_class(self, fish_class, min_threshold=65):
        """Get kill confidence % for a fish class"""
        class_shots = [s for s in self.session_shots if s['fish_class'] == fish_class]
        
        if not class_shots:
            return 0.0
        
        kills = len([s for s in class_shots if s['outcome'] == 'kill'])
        confidence = (kills / len(class_shots)) * 100
        
        return confidence if confidence >= min_threshold else 0.0


# ===========================
# ADAPTIVE SHOT COST STRATEGY
# ===========================
class AdaptiveStrategy:
    """Adjust shot costs & risk based on score proximity to zero"""
    
    def __init__(self, initial_shot_cost=1):
        self.base_shot_cost = initial_shot_cost
        self.shot_cost = initial_shot_cost
        self.burst_counter = 0
        self.score_threshold = 10  # Only fire when score > 10
        self.last_fire_time = time.time()
        self.mandatory_fire_interval = 60
    
    def should_fire(self, score):
        """Conservative firing: only fire when safe (score > threshold)"""
        # Exception: if we haven't fired in 60 seconds, fire regardless
        time_since_last_fire = time.time() - self.last_fire_time
        if time_since_last_fire > self.mandatory_fire_interval:
            return True
        
        return score > self.score_threshold
    
    def get_burst_size(self, priority_type, cluster_size=1):
        """Determine shots per burst"""
        if priority_type == 'convergence_burst':
            return 3 if cluster_size >= 3 else 2
        elif priority_type == 'killshot_65pct':
            return 3
        else:
            return 1
    
    def adjust_shot_cost(self, burst_index, burst_size):
        """Raise cost on 3rd, 4th, 5th shots"""
        if burst_index >= 2:
            self.shot_cost = self.base_shot_cost * (1.5 ** (burst_index - 1))
        else:
            self.shot_cost = self.base_shot_cost
        
        return self.shot_cost
    
    def reset_burst(self):
        """Reset cost after burst completes"""
        self.burst_counter = 0
        self.shot_cost = self.base_shot_cost
        self.last_fire_time = time.time()
    
    def get_time_since_fire(self):
        """Get seconds since last fire"""
        return time.time() - self.last_fire_time


# ===========================
# OBSERVATION LEARNING
# ===========================
class ObservationLearner:
    """Learn from watching replays/other players without firing"""
    
    def __init__(self, fish_memory):
        self.fish_memory = fish_memory
        self.observation_buffer = deque(maxlen=100)
    
    def analyze_replay(self, replay_events):
        """Ingest replay data: fish_class -> shots_fired -> kill_confirmation"""
        for event in replay_events:
            fish_class = event['fish_class']
            shots_fired = event['shots']
            was_killed = event['result'] == 'kill'
            value = event['value']
            
            if was_killed:
                self.fish_memory.record_kill(fish_class, shots_fired, value)
    
    def observe_live(self, fish_before, fish_after):
        """Track fish state changes without firing"""
        if fish_before.shots == fish_after.shots and fish_before.age < fish_after.age:
            self.observation_buffer.append({
                'class': fish_before.class_id,
                'area_delta': fish_after.area - fish_before.area,
                'survived': True
            })


# ===========================
# GAME CLASSIFIER
# ===========================
class GameClassifier:
    """Distinguish between different games by fish composition"""
    
    def __init__(self, storage_path='game_profiles.json'):
        self.storage_path = storage_path
        self.game_profiles = {}
        self.load()
    
    def save(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.game_profiles, f)
    
    def load(self):
        try:
            with open(self.storage_path, 'r') as f:
                self.game_profiles = json.load(f)
        except FileNotFoundError:
            pass
    
    def identify_game(self, fish_classes_present):
        """Get game type by fish class fingerprint"""
        fingerprint = tuple(sorted(fish_classes_present))
        
        for game_name, profile in self.game_profiles.items():
            if profile['fingerprint'] == list(fingerprint):
                return game_name
        
        return None
    
    def register_game(self, game_name, fish_classes):
        """Register a new game type"""
        self.game_profiles[game_name] = {
            'fingerprint': list(sorted(set(fish_classes))),
            'first_seen': time.time()
        }
        self.save()


# ===========================
# STATE PERSISTENCE
# ===========================
class StatePersistence:
    """Save/load system state between runs"""
    
    def __init__(self, state_file='system_state.json'):
        self.state_file = state_file
    
    def save_state(self, state_dict):
        """Persist system state"""
        state_dict['last_saved'] = time.time()
        with open(self.state_file, 'w') as f:
            json.dump(state_dict, f, indent=2)
    
    def load_state(self):
        """Restore system state"""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def get_score_state(self):
        """Get previous session's score"""
        state = self.load_state()
        return state.get('score', 1) if state else 1