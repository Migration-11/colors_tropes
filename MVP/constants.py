import os 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'TracksEditedLB.xlsx')
DB_PATH = os.path.join(BASE_DIR, 'data', 'track_interactions.csv')
CHAT_DB_PATH = os.path.join(BASE_DIR, 'data', 'chat_history.csv')

NAV_ITEMS = ["Home", "FAQ", "Contact Us", "Admin"]
TEMPERATURE_CREATIVITY = {'Low':0.1, 'Medium':0.5, 'High':1.0}

USERS = ['abcd', 'lmno', 'pqrs', 'xyz'] #TO Change