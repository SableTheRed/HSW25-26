import sqlite3
from pydantic import BaseModel
from typing import Optional, List

DBFOLDER = "user_data.db"

# data models
class User(BaseModel):
    sub: Optional[str] = None
    created_at: Optional[str] = None

class JournalEntry(BaseModel):
        journal_entry_no: Optional[int] = None
        user_sub: Optional[str] = None
        created_at: Optional[int] = None
        entry_text: Optional[str] = None

class EntryValues(BaseModel):
        entry_values_no: Optional[int] = None
        journal_entry_no: Optional[int] = None
        created_at: Optional[str] = None
        primary_emotion: Optional[str] = None
        stress: Optional[int] = None
        energy: Optional[int] = None
        mood: Optional[int] = None
        motivation: Optional[int] = None
        trend: Optional[str] = None
        burnout_risk: Optional[float] = None

#Connect to db (or create if absent)
def get_connection():
    con = sqlite3.connect(DBFOLDER)
    con.execute("PRAGMA foreign_keys = ON")
    return con

# Create tables if not already present
def initialize_db():
    con = get_connection()
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users(SUB text PRIMARY KEY, created_at datetime default current_timestamp)")
    cur.execute("CREATE TABLE IF NOT EXISTS journal_entries(journal_entry_no integer PRIMARY KEY autoincrement, user_sub text, created_at datetime default current_timestamp, entry_text text, FOREIGN KEY (user_sub) REFERENCES users(SUB) ON DELETE CASCADE)")
    cur.execute("CREATE TABLE IF NOT EXISTS entry_values(entry_values_no integer PRIMARY KEY autoincrement, journal_entry_no integer, created_at datetime default current_timestamp, primary_emotion text, stress integer, energy integer, mood integer, motivation integer, trend text, burnout_risk float, FOREIGN KEY (journal_entry_no) REFERENCES journal_entries(journal_entry_no) ON DELETE CASCADE, UNIQUE(journal_entry_no))")
    con.commit()
    con.close()

initialize_db()

# create user
def new_user(user: User) -> bool:
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute(
        "INSERT INTO users(SUB) VALUES (?)",
        (user.sub,),
        )
    except sqlite3.IntegrityError:
        con.close()
        return False  # User already exists
    con.commit()
    con.close()
    return True  # User created successfully

# create journal entry
def add_journal_entry(entry: JournalEntry) -> bool:
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO journal_entries(user_sub, entry_text) VALUES (?, ?)",
        (entry.user_sub, entry.entry_text),
    )
    con.commit()
    con.close()
    return True  # Entry added successfully

# create entry values
def add_entry_values(values: EntryValues) -> bool:
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO entry_values(journal_entry_no, primary_emotion, stress, energy, mood, motivation, trend, burnout_risk) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (values.journal_entry_no, values.primary_emotion, values.stress, values.energy, values.mood, values.motivation, values.trend, values.burnout_risk),)
    con.commit()
    con.close()
    return True  # Values added successfully


# fetch journal entries for a user
def fetch_journal_entries(user_sub: str) -> List[JournalEntry]:
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT journal_entry_no, created_at, entry_text FROM journal_entries WHERE user_sub = ?",
        (user_sub,),
    )
    entries = cur.fetchall()
    con.close()
    return [JournalEntry(journal_entry_no=row[0], user_sub = user_sub, created_at=row[1], entry_text=row[2]) for row in entries]  # Return list of JournalEntry objects

# fetch entry values for a journal entry
def fetch_entry_values(journal_entry_no: int) -> Optional[EntryValues]:
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT created_at, primary_emotion, stress, energy, mood, motivation, trend, burnout_risk FROM entry_values WHERE journal_entry_no = ?",
        (journal_entry_no,),
    )
    values = cur.fetchone()
    con.close()
    return EntryValues(journal_entry_no=journal_entry_no, created_at=values[0], primary_emotion=values[1], stress=values[2], energy=values[3], mood=values[4], motivation=values[5], trend=values[6], burnout_risk=values[7]) if values else None  # Return EntryValues object or None

# get user details from sub
def get_user(sub: str) -> Optional[User]:
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT SUB, created_at FROM users WHERE SUB=?", (sub,))
    user = cur.fetchone()
    con.close()
    return User(sub=sub, created_at=user[1]) if user else None  # Return user details

# get journal entry details from journal_entry_no
def get_journal_entry(journal_entry_no: int) -> Optional[JournalEntry]:
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT journal_entry_no, user_sub, created_at, entry_text FROM journal_entries WHERE journal_entry_no=?", (journal_entry_no,))
    entry = cur.fetchone()
    con.close()
    return JournalEntry(journal_entry_no=entry[0], user_sub=entry[1], created_at=entry[2], entry_text=entry[3]) if entry else None  # Return journal entry details

# get entry values from entry_values_no
def get_entry_values(entry_values_no: int) -> Optional[EntryValues]:
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT entry_values_no, journal_entry_no, created_at, primary_emotion, stress, energy, mood, motivation, trend, burnout_risk FROM entry_values WHERE entry_values_no=?", (entry_values_no,))
    value_set = cur.fetchone()
    con.close()
    return EntryValues(entry_values_no=value_set[0], journal_entry_no=value_set[1], created_at=value_set[2], primary_emotion=value_set[3], stress=value_set[4], energy=value_set[5], mood=value_set[6], motivation=value_set[7], trend=value_set[8], burnout_risk=value_set[9]) if value_set else None  # Return entry values details



# check if user exists
def user_exists(sub: str) -> bool:
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE SUB=?", (sub,))
    user = cur.fetchone()
    con.close()
    return user is not None

# check if journal entry has values set
def journal_entry_has_values(journal_entry_no: int) -> bool:
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM entry_values WHERE journal_entry_no=?", (journal_entry_no,))
    values = cur.fetchone()
    con.close()
    return values is not None


# updates
def update_journal_entry(journal_entry: JournalEntry) -> bool:
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "UPDATE journal_entries SET entry_text=? WHERE journal_entry_no=?",
        (journal_entry.entry_text, journal_entry.journal_entry_no),
    )
    con.commit()
    con.close()
    return True  # Update successful

def update_entry_values(entry_values: EntryValues) -> bool:
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "UPDATE entry_values SET primary_emotion=?, stress=?, energy=?, mood=?, motivation=?, trend=?, burnout_risk=?, created_at=CURRENT_TIMESTAMP WHERE journal_entry_no=?",
        (entry_values.primary_emotion, entry_values.stress, entry_values.energy, entry_values.mood, entry_values.motivation, entry_values.trend, entry_values.burnout_risk, entry_values.journal_entry_no),
    )
    con.commit()
    con.close()
    return True  # Update successful


# deletions
def delete_journal_entry(journal_entry_no: int) -> bool:
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM journal_entries WHERE journal_entry_no=?", (journal_entry_no,))
    con.commit()
    con.close()
    return True  # Deletion successful

def delete_entry_values(journal_entry_no: int) -> bool:
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM entry_values WHERE journal_entry_no=?", (journal_entry_no,))
    con.commit()
    con.close()
    return True  # Deletion successful

def delete_user(sub: str) -> bool:
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM users WHERE SUB=?", (sub,))
    con.commit()
    con.close()
    return True  # Deletion successful