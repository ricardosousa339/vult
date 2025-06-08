\
class Story:
    def __init__(self):
        self.scenes = [] # Default to empty, will be populated by Game
        self.current_scene = 0
    
    def get_current_scene(self):
        if 0 <= self.current_scene < len(self.scenes):
            return self.scenes[self.current_scene]
        return None # Indicates no more scenes or invalid index
    
    def next_scene(self):
        # Advance the scene index.
        # The check for whether the dialogue should end will happen in get_current_scene()
        # or by checking the length of scenes vs current_scene index.
        self.current_scene += 1
        # No automatic reset here. Game logic will handle resetting or ending dialogue.
    
    def reset(self):
        self.current_scene = 0
