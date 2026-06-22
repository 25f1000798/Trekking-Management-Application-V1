import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
base_dir  = os.path.abspath(os.path.dirname(__file__))
print(base_dir)
# print(os.path.abspath(__file__))
# what is the difference between __name__ and __file__

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "RoamQuest_secret_key-2026"+ str(datetime.utcnow)
    DATABASE_URI = os.environ.get('DATABASE_URI')
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


# demo = Config()
# print(demo.SECRET_KEY)
# print(demo.DATABASE_URI)

# print(demo.ADMIN_USERNAME,demo.ADMIN_PASSWORD,demo.ADMIN_EMAIL)
