# exercise.py

class Exercise:
    def __init__(self, name, muscle_group, sets, reps, duration, difficulty, category='General'):
        # Basic input checks so the program doesn’t break unexpectedly
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string")
        if not isinstance(duration, (int, float)) or duration < 0:
            raise ValueError("Duration must be a non-negative number")
        if not isinstance(difficulty, int) or not (1 <= difficulty <= 10):
            raise ValueError("Difficulty must be integer between 1 and 10")

        # Save cleaned-up exercise info
        self.name = name.strip()
        self.muscle_group = muscle_group.strip() if muscle_group else 'General'
        self.sets = int(sets)
        self.reps = int(reps)
        self.duration = duration      # minutes
        self.difficulty = difficulty  # scale 1–10
        self.category = category

    def to_dict(self):
        # Helpful for JSON saving or exporting later
        return {
            'name': self.name,
            'muscle_group': self.muscle_group,
            'sets': self.sets,
            'reps': self.reps,
            'duration': self.duration,
            'difficulty': self.difficulty,
            'category': self.category
        }

    def __str__(self):
        # Clean string for displaying exercise info nicely
        return f"{self.name} ({self.muscle_group}) — {self.sets}x{self.reps}, {self.duration}min, Diff:{self.difficulty}"
