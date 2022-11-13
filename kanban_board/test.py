import unittest
from app import app, Note

class AuthManager:
    def __init__(self, client):
        self.client = client
    
    def __enter__(self):
        r = self.client.post('/login', data = {"username": "john", "password": "john123"})
        
    def __exit__(self, exc_type, exc_value, exc_traceback):
        r = self.client.get('/logout')
class testing(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()
    def tearDown(self):
        self.ctx.pop()
    def test_updates(self):
        with AuthManager(self.client):
            r = self.client.post('/updates', data = {"id": 1, "level": "in-progress"})
            note = Note.query.get(1)
            self.assertEqual(note.level, "in-progress") 
            r = self.client.post('/updates', data = {"id": 3, "level": "done"})
            note = Note.query.get(3)
            self.assertEqual(note.level, "done") 
            r = self.client.post('/updates', data = {"id": 6, "level": "todo"})
            note = Note.query.get(6)
            self.assertEqual(note.level, "todo") 
        
    def test_delete(self):
        with AuthManager(self.client):
            r = self.client.post('/updates', data = {"id": 1, "level": ""})
            note = Note.query.get(1)
            self.assertEqual(note.level, "") 
            r = self.client.post('/updates', data = {"id": 3, "level": ""})
            note = Note.query.get(3)
            self.assertEqual(note.level, "") 
            r = self.client.post('/updates', data = {"id": 6, "level": ""})
            note = Note.query.get(6)
            self.assertEqual(note.level, "") 
        
    def test_add(self):
        with AuthManager(self.client):
            r = self.client.post('/add', data = {'TaskName': "Go to Bellini"})
            note = Note.query.filter(Note.TaskName == "Go to Bellini", Note.user_id == 1).first()
            self.assertIsNotNone(note)
            r = self.client.post('/add', data = {'TaskName': "Hit the gym"})
            note = Note.query.filter(Note.TaskName == "Hit the gym", Note.user_id == 1).first()
            self.assertIsNotNone(note)
            r = self.client.post('/add', data = {'TaskName': "Cook"})
            note = Note.query.filter(Note.TaskName == "Cook", Note.user_id == 1).first()
            self.assertIsNotNone(note)
    
    
    
if __name__ == "__main__":
    unittest.main()