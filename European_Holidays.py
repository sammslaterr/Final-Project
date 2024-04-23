import sqlite3
import requests
from datetime import datetime

def get_country_holidays(country_iso_code):
    holidays_url = f'https://openholidaysapi.org/PublicHolidays?countryIsoCode={country_iso_code}&languageIsoCode=EN&validFrom=2022-01-01&validTo=2022-12-31'
    response = requests.get(holidays_url)
    country_holidays = response.json()
    return country_holidays

def european_holiday_table_maker():
    country_iso_mapping = {
        "Albanien": "AL", "Andorra": "AD", "Austria": "AT", "Belgium": "BE", "Bulgaria": "BG",
        "Croatia": "HR", "Czechia": "CZ", "Estonia": "EE", "France": "FR", "Germany": "DE",
        "Hungary": "HU", "Ireland": "IE", "Italy": "IT", "Latvia": "LV", "Liechtenstein": "LI",
        "Lithuania": "LT", "Luxembourg": "LU", "Malta": "MT", "Monaco": "MC", "Netherlands": "NL",
        "Poland": "PL", "Portugal": "PT", "San Marino": "SM", "Slovakia": "SK", "Slovenia": "SI",
        "Switzerland": "CH", "Vatican City": "VA"
    }

    conn = sqlite3.connect('holidays.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS european_country_ids
                 (id INTEGER PRIMARY KEY, country TEXT UNIQUE, iso_code TEXT)''')

    for country, iso_code in country_iso_mapping.items():
        c.execute("INSERT OR IGNORE INTO european_country_ids (country, iso_code) VALUES (?, ?)", (country, iso_code))

    c.execute('''CREATE TABLE IF NOT EXISTS european_holidays
             (primary_id INTEGER PRIMARY KEY, country_id INTEGER, holiday_id INTEGER, day_of_year INTEGER,
             FOREIGN KEY(country_id) REFERENCES european_country_ids(id),
             FOREIGN KEY(holiday_id) REFERENCES european_holiday_ids(id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS european_holiday_ids
                 (id INTEGER PRIMARY KEY, holiday TEXT UNIQUE)''')

    total_entries = 0

    for country, iso_code in country_iso_mapping.items():
        country_id = c.execute("SELECT id FROM european_country_ids WHERE country=?", (country,)).fetchone()[0]

        # Retrieve holidays for the country
        country_holidays = get_country_holidays(iso_code)
        if country_holidays:
            for holiday in country_holidays:
                if total_entries >= 25:
                    break  # Stop fetching if the total limit is reached

                if 'name' in holiday and isinstance(holiday['name'], list):
                    for name_info in holiday['name']:
                        if 'language' in name_info and name_info['language'] == 'EN':
                            holiday_text = name_info['text']

                            existing_holiday_id = c.execute("SELECT id FROM european_holiday_ids WHERE holiday=?", (holiday_text,)).fetchone()
                            if existing_holiday_id:
                                holiday_id = existing_holiday_id[0]
                            else:
                                c.execute("INSERT INTO european_holiday_ids (holiday) VALUES (?)", (holiday_text,))
                                holiday_id = c.lastrowid

                            start_date = holiday['startDate']
                            day_of_year = datetime.strptime(start_date, '%Y-%m-%d').timetuple().tm_yday

                            existing_entry = c.execute("SELECT COUNT(*) FROM european_holidays WHERE country_id=? AND holiday_id=? AND day_of_year=?", (country_id, holiday_id, day_of_year)).fetchone()[0]
                            if existing_entry == 0:
                                c.execute("INSERT INTO european_holidays (country_id, holiday_id, day_of_year) VALUES (?, ?, ?)",
                                          (country_id, holiday_id, day_of_year))
                                total_entries += 1

    conn.commit()
    conn.close()

if __name__ == "__main__":
    european_holiday_table_maker()
