# config_manager.py
import json
import os

class ConfigManager:
    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self.default_config = {
            # UI Settings
            'method': 'key',
            'trigger_key': 'Space',
            'ip': '',
            'port': 0,
            'uuid': '',
            'require_crosshair': 0,
            'press_release_min_ms': 80,
            'press_release_max_ms': 100,
            'delay_after_shoot_min_ms': 100,
            'delay_after_shoot_max_ms': 150,
            'mode': 'always',
            'hotkey': 'T',
            
            # Advanced Settings (Previously Hidden)
            'target_color_tolerance': 60,
            'target_color': [252, 60, 250],
            'crosshair_color': [65, 255, 0],
            'crosshair_color_tolerance': 25,
            'trigger_zone_size': 50,
            'center_zone_size': 3,
            'max_ray_distance': 50,
            'rays_per_direction': 5,
            'ray_angle_spread': 30,
            'num_threads': 4
        }
    
    def load_config(self):
        """Load config from file with defaults"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged_config = self.default_config.copy()
                merged_config.update(config)
                return merged_config
            else:
                return self.default_config.copy()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_config.copy()
    
    def save_config(self, config):
        """Save config to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def validate_config(self, config):
        """Validate configuration values"""
        errors = []
        
        # Validate timing values
        timing_fields = ['press_release_min_ms', 'press_release_max_ms', 
                        'delay_after_shoot_min_ms', 'delay_after_shoot_max_ms']
        
        for field in timing_fields:
            value = config.get(field, 0)
            if not isinstance(value, int) or value < 0 or value > 10000:
                errors.append(f"{field} must be between 0 and 10000")
        
        # Validate color values, tolerance, zones, etc.
        return errors
