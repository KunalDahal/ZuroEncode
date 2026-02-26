# GENERATE SESSION STRING 

from pyrogram import Client
from dotenv import load_dotenv
import os

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = str(os.getenv("API_HASH"))
with Client(
    "my_account",
    api_id=api_id,
    api_hash=api_hash,
    in_memory=True
) as app:
    session_string = app.export_session_string()
    print("\nYour Session String:\n")
    print(session_string)