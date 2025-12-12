# tests.py
import unittest
from workout import WorkoutManager

class TestWorkoutManager(unittest.TestCase):
    def setUp(self):
        # Make a fresh manager for each test
        self.m = WorkoutManager()
        self.a = self.m.add_exercise('Push-Up','Chest',3,12,10,3,'Strength')
        self.b = self.m.add_exercise('Squat','Legs',4,15,15,4,'Strength')

    def test_add_and_list(self):
        # Check if both exercises were added correctly
        all_ex = self.m.get_all_exercises(sort_key='name')
        names = [e.name for e in all_ex]
        self.assertIn('Push-Up', names)
        self.assertIn('Squat', names)

    def test_delete(self):
        # Make sure delete actually removes things
        deleted = self.m.delete_exercise('Push-Up')
        self.assertIsNotNone(deleted)
        remaining = [e.name for e in self.m.get_all_exercises()]
        self.assertNotIn('Push-Up', remaining)

    def test_queue(self):
        # Queue operations for daily routine
        ex = self.m.get_all_exercises()[0]
        self.m.add_to_daily_routine(ex)
        self.assertEqual(self.m.get_routine_list()[0].name, ex.name)
        self.m.clear_routine()
        self.assertEqual(len(self.m.get_routine_list()), 0)

if __name__ == '__main__':
    unittest.main()
