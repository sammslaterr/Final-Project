import sqlite3
import requests

# get holiday data from the API
def fetch_holiday_data(api_key, country, year):
    url = f'https://holidayapi.com/v1/holidays?key={api_key}&country={country}&year={year}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['holidays']
    else:
        return []

# create tables in the database
def create_tables():
    conn = sqlite3.connect('holidays.db')  # Updated database name
    c = conn.cursor()

    # renaming Holiday table to US_Holidays (if 'exists')
    c.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='Holiday' ''')
    table_exists = c.fetchone()
    if table_exists:
        c.execute('''ALTER TABLE Holiday RENAME TO US_Holidays''')

    # Create US_Holidays table with year, month, day columns
    c.execute('''CREATE TABLE IF NOT EXISTS US_Holidays (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    year INTEGER,
                    month INTEGER,
                    day INTEGER,
                    weekday_id INTEGER,
                    is_public BOOLEAN,
                    FOREIGN KEY (weekday_id) REFERENCES Weekday(id)
                )''')

    conn.commit()
    conn.close()

# store data in the database
def store_data_in_database(data):
    conn = sqlite3.connect('holidays.db')  # Updated database name
    c = conn.cursor()

    count=0
    
    for holiday in data:
        if count >= 25:
         break

    # Check if the holiday already exists in the database
        existing_holiday_count = c.execute('''SELECT COUNT(*) FROM US_Holidays WHERE name = ? AND year = ? AND month = ? AND day = ?''', (holiday['name'], holiday['date'][:4], holiday['date'][5:7], holiday['date'][8:10])).fetchone()[0]
        if existing_holiday_count > 0:
            continue

    # Get weekday_id for the holiday
        c.execute('''SELECT id FROM Weekday WHERE weekday = ?''', (holiday['weekday']['observed']['name'],))
        weekday_id = c.fetchone()[0]

    # Insert into US_Holidays table
        c.execute('''INSERT INTO US_Holidays (name, year, month, day, weekday_id, is_public) 
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (holiday['name'], holiday['date'][:4], holiday['date'][5:7], holiday['date'][8:10], weekday_id, holiday['public']))

        count += 1

    
    conn.commit()
    conn.close()

# Main function to fetch, store, and retrieve holiday data
def main():
    api_key = '524f0323-79a2-42a1-83e4-bb39c7e33948'
    country = 'US'
    year = 2023

    # Create tables
    create_tables()

    # Fetch data from API
    data = fetch_holiday_data(api_key, country, year)
    
    # Store data
    store_data_in_database(data)


if __name__ == "__main__":
    main()
