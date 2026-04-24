# ZERO HYBRID v3.5 - Complete Advanced AI System

**Production-ready fishing game AI with advanced prediction, learning, and failsafes**

## 📋 System Overview

### Core Components Implemented

#### 1. **Motion-Only Detection** ✅
- Pure frame differencing (only moving pixels)
- Static background completely ignored
- No false positives from UI overlays
- Oscillation filtering for overlays with 0.5-2sec frequency

#### 2. **Fish Classification** ✅
- 5-class system by size/area:
  - Class 0: Tiny (< 100px)
  - Class 1: Small (100-300px)
  - Class 2: Medium (300-600px)
  - Class 3: Large (600-1200px)
  - Class 4: Huge (> 1200px)

#### 3. **Convergence Prediction** ✅
```python
# Detects when 2+ smallest class fish are on collision course
collisions = detector.predict_collision(fish_list, time_horizon_frames=15)

# For each collision: frame, location, fish IDs, confidence
collision = {
    'fish_ids': (f1.id, f2.id),
    'collision_frame': 8,
    'collision_point': (350, 200),
    'confidence': 0.92
}
```

#### 4. **Multi-Shot Burst Strategy** ✅
```python
# For 2+ smallest class on collision course: 3-shot burst
Shot 1: 1x cost (base)
Shot 2: 1.1x cost (slight increase)
Shot 3: 2x cost (double)
Then reset to base cost

# All 3 shots time-coordinated to hit at collision point
```

#### 5. **Splash Damage System** ✅
- Configurable splash radius (40px default)
- Adaptive learning from hit patterns
- Multi-target optimization
- Radius visualization on every hit

#### 6. **HP Cycle Learning** ✅
```python
learner.record_hp_event(fish_class=0, shots_fired=2, area_before=95, area_after=40)

# Learns patterns: up/down/stable cycles
# Predicts shots-to-kill with confidence
shots_needed, confidence = learner.predict_shots_to_kill(fish_class=0)
# Returns: (3 shots, 0.87 confidence)
```

#### 7. **Adaptive Mask Learning** ✅
- Per-game motion detection parameter profiles
- Auto-adjusts threshold for lighting changes
- Learns optimal kernel sizes
- Persists learning to disk

#### 8. **Radar Evolution** ✅
- 4 visualization modes: dot, gradient, trajectory, threat_map
- Auto-selects best mode based on target clustering
- Updates in real-time

#### 9. **Player Position Prediction** ✅
```python
# Tracks cannon position
predictor.update_position(x=640, y=720)

# Predicts future player position (5 frames ahead)
pred_x, pred_y = predictor.predict_player_position(frames_ahead=5)

# Detects stationary state
is_moving = not predictor.is_stationary()
```

#### 10. **Bullet Trajectory Learning** ✅
```python
# Records successful/failed shots
learner.record_bullet_event(player_pos, target_pos, target_vel, hit=True)

# Estimates bullet speed from hit patterns
speed = learner.estimate_bullet_speed()  # pixels/frame

# Calculates optimal lead for interception
lead_x, lead_y = learner.predict_bullet_intercept(player_pos, target_pos, target_vel)
```

#### 11. **Score Pattern Recognition** ✅
- Wave structure detection (kill sequences)
- Volatility analysis
- Safe reserve estimation based on pattern
- Profit cycle prediction

#### 12. **Corrupted Data Handler** ✅
```python
# Validates all fish tracking data
is_valid = handler.validate_fish_data(fish)  # Checks impossible speed/area/position

# Corrects corrupted state using previous known-good state
fish = handler.correct_fish_state(fish, previous_state)

# Overall data quality score (0-1)
quality = handler.get_data_quality()
```

#### 13. **Shift-Key Auto-Fire Toggle** ✅
```python
# Press Shift to toggle on/off
# On/off state persists through system
auto_fire.toggle()  # 🟢 ON / 🔴 OFF
```

#### 14. **Failsafe Systems** ✅
- Emergency shutdown (disables all firing)
- Contingency protocols (data corruption, target loss, critical score, FPS drop)
- Performance monitoring with auto-optimization
- Recovery procedures for critical failures

#### 15. **Contingency Protocols** ✅
```python
- Data Corruption: Revert to safe defaults
- Target Loss: Hold fire, wait for re-acquisition
- Score Critical: Conservative mode (high confidence only)
- FPS Drop: Reduce processing load
- No Motion: Check for game state change
- Network Lag: Compensate lead prediction
```

---

## 🚀 Installation

### Requirements
```bash
pip install opencv-python numpy mss pyautogui pynput
```

### Optional (for advanced features)
```bash
pip install win32gui  # Windows window detection
```

### File Structure
```
zero_hybrid/
├── main_v3_5.py              # Main integrated system
├── advanced_predictor.py      # Convergence, multi-shot, HP learning
├── adaptive_learning.py       # Mask, radar, health, position, bullets, score
├── failsafe_system.py         # Shift toggle, failsafes, contingencies, recovery
├── fish_memory.json           # Persistent fish kill patterns
├── shot_history.json          # Shot tracking
├── mask_profiles.json         # Adaptive mask parameters per game
├── game_profiles.json         # Game fingerprint database
└── system_state.json          # Last session state (score, shots)
```

---

## 🎮 Usage

### Basic Start
```bash
python main_v3_5.py
```

### Controls
- **Q** - Quit
- **Shift** - Toggle auto-fire on/off
- **E** - Emergency shutdown (stop all firing)
- **+/-** - Adjust motion detection sensitivity

### What It Does On Each Frame

1. **Capture** - Grab right-half of Chrome window
2. **Motion Detection** - Find only moving pixels
3. **Track Fish** - Build single target per fish
4. **Classify** - Determine fish class (0-4)
5. **Predict Convergence** - Check for collision courses
6. **Check HP Patterns** - Estimate shots-to-kill
7. **Optimize Splash** - Find best multi-target point
8. **Validate Data** - Check for corruption
9. **Update Learning** - Evolve all parameters
10. **Fire Decision** - Burst if convergence + high confidence
11. **Visualize** - Draw debug overlay
12. **Check Failsafes** - Monitor system health

---

## 📊 Key Algorithms

### Convergence Detection
```python
# For each pair of class-0 (smallest) fish:
for t in range(1, 15):  # 15 frames ahead
    f1_future = fish1.pos + fish1.vel * t
    f2_future = fish2.pos + fish2.vel * t
    
    if distance(f1_future, f2_future) < 50px:
        CONVERGENCE DETECTED!
        collision_point = (f1_future + f2_future) / 2
        collision_frame = t
```

### Multi-Shot Coordination
```python
# All 3 shots coordinated to hit at same frame
for shot in [1, 2, 3]:
    cost = base_cost * [1.0, 1.1, 2.0][shot-1]
    fire_at(collision_point)
    if shot < 3:
        sleep(0.03)  # Burst spacing
```

### HP Cycle Learning
```python
# Track area changes frame-to-frame
if area_loss > 5px:
    record_damage_event(shots, area_loss, was_moving)

# Pattern detection (last 20 kills)
three_shot_kills = count(kills where shots <= 3)
if three_shot_kills / total > 70%:
    predict_class_as_3_shot_kill
```

### Adaptive Mask
```python
# Per-game parameters stored by game fingerprint
fingerprint = hash(fish_classes_present)

# Auto-adjust threshold toward middle gray (127)
if motion_brightness < 127:
    threshold *= 0.95  # Lower threshold
else:
    threshold *= 1.05  # Raise threshold

# Learn kernel size based on motion density
if motion_density > 50%:
    kernel_size = 7
elif motion_density > 20%:
    kernel_size = 5
else:
    kernel_size = 3
```

---

## ⚙️ Performance Optimizations

### Lightweight by Design
- **Circular buffers** - Fixed memory footprint
- **Adaptive optimization** - Auto-adjusts based on FPS
- **Frame skipping** - At low FPS (optional)
- **Downsampling** - Reduces processing at optimization level 3+
- **Contour simplification** - Fewer vertices at high optimization

### Performance Tiers
```python
Level 1: Full quality, no optimization
Level 2: 80% quality, skip 1 frame
Level 3: 60% quality, skip 2 frames  
Level 4: 50% quality, skip 3 frames
Level 5: 40% quality, skip 4 frames (emergency mode)
```

---

## 🛡️ Failsafe & Contingency Examples

### Example 1: Data Corruption Detected
```
⚠️ Failsafe: corrupted_tracking_data
→ Reverting to safe threshold (15px)
→ Clearing motion history
✅ Failsafe resolved: corrupted_tracking_data
```

### Example 2: Critical Low Score
```
💰 CRITICAL LOW SCORE - conservative mode activated
→ Only fire targets with 65%+ historical success
→ Hold fire for 60 seconds if no high-confidence target
```

### Example 3: Emergency Stop
```
Pressing 'E':
🛑 EMERGENCY SHUTDOWN ACTIVATED
🔴 Auto-Fire DISABLED: emergency_stop
All firing halted immediately
```

### Example 4: Recovery
```
🔄 Recovery attempt 1/3
  → Clearing buffers...
  → Reducing memory usage...
  → Resetting tracking...
✅ Recovery procedures completed
```

---

## 📈 Observable Data & Learning

The system learns from and tracks:

| Data Type | Tracked | Adaptive | Corrupted Data Handled |
|-----------|---------|----------|----------------------|
| Motion mask params | ✅ | Per-game | ✅ Validation |
| Radar visualization | ✅ | Per state | ✅ Fallback mode |
| Fish HP cycles | ✅ | Per class | ✅ Damage outlier rejection |
| Player position | ✅ | Real-time | ✅ Position bounds check |
| Bullet physics | ✅ | Per game | ✅ Lead distance validation |
| Score patterns | ✅ | Wave-based | ✅ Volatility bounds |
| Shot confidence | ✅ | Class-specific | ✅ Historical weighting |

---

## 🔮 Advanced Features

### Observation Learning
Even without firing, the system learns from:
- Fish state changes
- Movement patterns
- Spawn locations
- Wave structures
- Difficulty curves

### Cross-Game Learning
- Game fingerprints stored by fish class composition
- Parameters shared across similar games
- But adapted per specific title

### Predictive Firing
- Preemptive shots calculated 1-2 seconds in advance
- Convergence detection at 15-frame horizon
- Lead calculation with bullet physics learning

### Safe Reserve Management
```python
safe_reserve = 5 + (score_volatility * 2)

# Based on recent 30 kills:
# High volatility (std_dev=10) → reserve 25
# Low volatility (std_dev=2) → reserve 9
```

---

## 📝 Configuration

Edit `CONFIG` dict in `main_v3_5.py`:

```python
CONFIG = {
    'MOTION_THRESHOLD': 15,           # Frame diff sensitivity
    'ADAPT_RATE': 5,                  # % per frame
    'SAFE_RESERVE': 10,               # Min score to fire
    'CONVERGENCE_TIME_HORIZON': 15,   # Frames to predict
    'SPLASH_RADIUS': 40,              # Pixels
    'TARGET_FPS': 30,                 # Desired FPS
}
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| No motion detected | Lower MOTION_THRESHOLD (10-12) |
| Too much false motion | Raise MOTION_THRESHOLD (18-20) |
| Missed convergences | Increase CONVERGENCE_TIME_HORIZON (20-25) |
| Firing too much | Raise SAFE_RESERVE or enable conservative mode |
| Low FPS | System auto-optimizes; check screen resolution |
| Shift key not working | Requires `pip install pynput` |
| Chrome window not detected | Falls back to primary monitor right-half |

---

## 📊 Output Files

After running:

- **fish_memory.json** - Kill patterns per class
- **shot_history.json** - All shots with outcomes
- **mask_profiles.json** - Learned motion parameters per game
- **game_profiles.json** - Game fingerprints
- **system_state.json** - Last session score/shots

---

## 🎯 Next Steps / Future Enhancements

- [ ] GPU acceleration for motion detection
- [ ] Neural network classifier for fish type
- [ ] Multi-screen support
- [ ] Custom game calibration wizard
- [ ] Live dashboard UI
- [ ] Network multiplayer learning
- [ ] Voice notifications
- [ ] Performance profiling mode

---

## 📞 Support

For issues, check:
1. Console output for error messages
2. Active failsafes (printed each frame)
3. System quality score (printed in stats)
4. Recovery logs in contingency_log

---

**ZERO HYBRID v3.5 - Adaptive, Resilient, Lightweight. Deploy with confidence.**
