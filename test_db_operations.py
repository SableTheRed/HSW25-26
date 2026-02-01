import pytest
import os
from db_operations import *

TEST_DBFOLDER = "user_data.db"
DBFOLDER = TEST_DBFOLDER  # override database path for testing

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Initialize a clean test database
    if os.path.exists(TEST_DBFOLDER):
        os.remove(TEST_DBFOLDER)
    initialize_db()
    yield
    # Teardown: delete test DB
    if os.path.exists(TEST_DBFOLDER):
        os.remove(TEST_DBFOLDER)

def test_user_crud():
    user = User(sub="test_user")
    
    # Create
    assert new_user(user) is True
    # Duplicate
    assert new_user(user) is False
    
    # Fetch
    fetched = get_user("test_user")
    assert fetched is not None
    assert fetched.sub == "test_user"
    
    # Exists
    assert user_exists("test_user") is True
    assert user_exists("nonexistent") is False
    
    # Delete
    assert delete_user("test_user") is True
    assert get_user("test_user") is None

def test_journal_entry_crud():
    # Setup user
    new_user(User(sub="journal_user"))
    
    entry = JournalEntry(user_sub="journal_user", entry_text="Test entry")
    
    # Create
    assert add_journal_entry(entry) is True
    
    # Fetch all
    entries = fetch_journal_entries("journal_user")
    assert len(entries) == 1
    assert entries[0].entry_text == "Test entry"
    
    # Fetch single
    fetched = get_journal_entry(entries[0].journal_entry_no)
    assert fetched is not None
    assert fetched.entry_text == "Test entry"
    
    # Update
    fetched.entry_text = "Updated entry"
    assert update_journal_entry(fetched) is True
    updated = get_journal_entry(fetched.journal_entry_no)
    assert updated.entry_text == "Updated entry"
    
    # Delete
    assert delete_journal_entry(fetched.journal_entry_no) is True
    assert get_journal_entry(fetched.journal_entry_no) is None

def test_entry_values_crud():
    # Setup user and journal entry
    new_user(User(sub="values_user"))
    add_journal_entry(JournalEntry(user_sub="values_user", entry_text="Entry for values"))
    entry_no = fetch_journal_entries("values_user")[0].journal_entry_no
    
    values = EntryValues(
        journal_entry_no=entry_no,
        primary_emotion="happy",
        stress=3,
        energy=7,
        mood=8,
        motivation=6,
        trend="stable",
        burnout_risk=0.2
    )
    
    # Create
    assert add_entry_values(values) is True
    
    # Fetch
    fetched = fetch_entry_values(entry_no)
    assert fetched is not None
    assert fetched.primary_emotion == "happy"
    
    # Update
    fetched.mood = 5
    fetched.stress = 6
    assert update_entry_values(fetched) is True
    updated = fetch_entry_values(entry_no)
    assert updated.mood == 5
    assert updated.stress == 6
    
    # Delete
    assert delete_entry_values(entry_no) is True
    assert fetch_entry_values(entry_no) is None





