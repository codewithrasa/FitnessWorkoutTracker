# workout.py

from exercise import Exercise
from data_structures import ExerciseBST, ExerciseQueue
from sort import insertion_sort

class WorkoutManager:
    def __init__(self):
        # Tree stores all exercises, queue stores today’s workout order
        self.exercise_bst = ExerciseBST()
        self.daily_routine = ExerciseQueue()

    def add_exercise(self, name, muscle_group, sets, reps, duration, difficulty, category='General'):
        # Create new exercise and add it to BST
        ex = Exercise(name, muscle_group, sets, reps, duration, difficulty, category)
        inserted = self.exercise_bst.insert(ex)
        return ex if inserted else None

    def edit_exercise(self, original_name, **kwargs):
        # Find the exercise first
        ex = self.exercise_bst.find_by_name(original_name)
        if not ex:
            return None

        # Update allowed fields
        for k, v in kwargs.items():
            if hasattr(ex, k):
                setattr(ex, k, v)
        return ex

    def delete_exercise(self, name):
        # Just call BST delete
        deleted = self.exercise_bst.delete(name)
        return deleted

    def get_all_exercises(self, sort_key=None, category_filter=None, search=None):
        # Start with full list (already sorted alphabetically from BST)
        items = self.exercise_bst.in_order()

        # Optional filtering
        if category_filter:
            items = [x for x in items if x.category.lower() == category_filter.lower()]

        if search:
            items = [x for x in items if search.lower() in x.name.lower()]

        # Optional sorting by duration, difficulty, etc.
        if sort_key:
            items = insertion_sort(items, key=sort_key)

        return items

    def add_to_daily_routine(self, exercise):
        # Queue keeps exercises in order for the day
        self.daily_routine.enqueue(exercise)

    def complete_next_exercise(self):
        # Pop next exercise to perform
        return self.daily_routine.dequeue()

    def get_routine_list(self):
        # Return the entire routine as list
        return self.daily_routine.to_list()

    def clear_routine(self):
        # Reset queue
        self.daily_routine.clear()
