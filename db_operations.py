import sqlite3
from pydantic import BaseModel

DBFOLDER = "user_data.db"

# input models
class User(BaseModel):
    sub: str

class JournalEntry(BaseModel):
        user_sub: str
        entry_text: str

class EntryValues(BaseModel):
        journal_entry_no: int
        happiness: int
        stress: int
        energy: int
        focus: int
        anxiety: int

# output models
class UserOut(User):
    created_at: str

class JournalEntryOut(JournalEntry):
    entry: int
    created_at: str

class EntryValuesOut(EntryValues):
    value_set: int
    created_at: str

#Connect to db (or create if absent)
def get_connection():
    con = sqlite3.connect(DBFOLDER)
    con.execute("PRAGMA foreign_keys = ON")
    return con

con = get_connection()
cur = con.cursor()

# Create tables if not already present
cur.execute("CREATE TABLE IF NOT EXISTS users(SUB text primary key, created_at datetime default current_timestamp)")
cur.execute("CREATE TABLE IF NOT EXISTS journal_entries(entry_no integer primary key autoincrement, user_sub text, created_at datetime default current_timestamp, entry_text text, FOREIGN KEY (user_sub) REFERENCES users(SUB))")
cur.execute("CREATE TABLE IF NOT EXISTS entry_values(value_set integer primary key autoincrement, journal_entry_no integer, created_at datetime default current_timestamp, happiness integer, stress integer, energy integer, focus integer, anxiety integer, FOREIGN KEY (journal_entry_no) REFERENCES journal_entries(entry), UNIQUE(journal_entry_no))")
con.commit()
con.close()

# create user
def new_user(user: User):
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
def add_journal_entry(entry: JournalEntry):
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
def add_entry_values(values: EntryValues):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO entry_values(journal_entry_no, created_at, happiness, stress, energy, focus, anxiety) VALUES (?, ?, ?, ?, ?, ?)",
        (values.journal_entry_no, values.happiness, values.stress, values.energy, values.focus, values.anxiety),
    )
    con.commit()
    con.close()
    return True  # Values added successfully


# fetch journal entries for a user
def fetch_journal_entries(user_sub: str):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT entry_no, created_at, entry_text FROM journal_entries WHERE user_sub = ?",
        (user_sub,),
    )
    entries = cur.fetchall()
    con.close()
    return entries  # Return list of entries

# fetch entry values for a journal entry
def fetch_entry_values(entry_no: str):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT created_at, happiness, stress, energy, focus, anxiety FROM entry_values WHERE entry_no = ?",
        (entry_no,),
    )
    values = cur.fetchall()
    con.close()
    return values  # Return list of values

# fetch user details
def get_user(sub: str):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT SUB, created_at FROM users WHERE SUB=?", (sub,))
    user = cur.fetchone()
    con.close()
    return user  # Return user details

# fetch journal entry details
def get_journal_entry(entry_no: int):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT entry_no, user_sub, created_at, entry_text FROM journal_entries WHERE entry=?", (entry_no,))
    entry = cur.fetchone()
    con.close()
    return entry  # Return journal entry details

# fetch entry values set details
def get_value_set(value_set_no: int):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT value_set, journal_entry_no, created_at, happiness, stress, energy, focus, anxiety FROM entry_values WHERE value_set=?", (value_set_no,))
    value_set = cur.fetchone()
    con.close()
    return value_set  # Return entry values details



# check if user exists
def user_exists(sub: str):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE SUB=?", (sub,))
    user = cur.fetchone()
    con.close()
    return user is not None

# check if journal entry has values set
def journal_entry_has_values(entry_no: int):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM entry_values WHERE journal_entry_no=?", (entry_no,))
    values = cur.fetchone()
    con.close()
    return values is not None


# updates
def update_journal_entry(entry_no: int, new_text: str):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "UPDATE journal_entries SET entry_text=? WHERE entry_no=?",
        (new_text, entry_no),
    )
    con.commit()
    con.close()
    return True  # Update successful

def update_entry_values(entry_no: int, happiness: int, stress: int, energy: int, focus: int, anxiety: int):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "UPDATE entry_values SET happiness=?, stress=?, energy=?, focus=?, anxiety=? WHERE journal_entry_no=?",
        (happiness, stress, energy, focus, anxiety, entry_no),
    )
    con.commit()
    con.close()
    return True  # Update successful

# deletions
def delete_journal_entry(entry_no: int):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM journal_entries WHERE entry_no=?", (entry_no,))
    con.commit()
    con.close()
    return True  # Deletion successful

def delete_entry_values(entry_no: int):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM entry_values WHERE journal_entry_no=?", (entry_no,))
    con.commit()
    con.close()
    return True  # Deletion successful

def delete_user(sub: str):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM users WHERE SUB=?", (sub,))
    con.commit()
    con.close()
    return True  # Deletion successful