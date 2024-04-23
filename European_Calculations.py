import sqlite3
import csv

def average_holidays_per_country(output_file='holidays_data.csv'):
    conn = sqlite3.connect('holidays.db')
    c = conn.cursor()
    c.execute('''SELECT country, COUNT(*) AS holiday_count
                 FROM european_country_ids
                 JOIN european_holidays ON european_country_ids.id = european_holidays.country_id
                 GROUP BY country''')
    holiday_counts = c.fetchall()
    total_countries = len(holiday_counts)
    total_holidays = sum(count for _, count in holiday_counts)
    conn.close()

    if total_countries > 0:
        average_holidays = total_holidays / total_countries
        with open(output_file, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([f'The average number of holidays per country in Europe is {average_holidays:.2f}.'])
    else:
        print("No countries found in the database.")

def country_with_most_holidays(output_file='holidays_data.csv'):
    conn = sqlite3.connect('holidays.db')
    c = conn.cursor()
    c.execute('''SELECT country, COUNT(*) AS holiday_count
                 FROM european_country_ids
                 JOIN european_holidays ON european_country_ids.id = european_holidays.country_id
                 GROUP BY country
                 ORDER BY holiday_count DESC
                 LIMIT 1''')
    result = c.fetchone()
    conn.close()

    if result:
        country_with_most_holidays, holiday_count = result
        with open(output_file, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([f'The country with the most holidays in Europe is {country_with_most_holidays} with {holiday_count} holidays.'])
    else:
        print("No holidays found in the database.")

def country_with_least_holidays(output_file='holidays_data.csv'):
    conn = sqlite3.connect('holidays.db')
    c = conn.cursor()
    c.execute('''SELECT country, COUNT(*) AS holiday_count
                 FROM european_country_ids
                 JOIN european_holidays ON european_country_ids.id = european_holidays.country_id
                 GROUP BY country
                 ORDER BY holiday_count ASC
                 LIMIT 1''')
    result = c.fetchone()
    conn.close()

    if result:
        country_with_least_holidays, holiday_count = result
        with open(output_file, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([f'The country with the least holidays in Europe is {country_with_least_holidays} with {holiday_count} holidays.'])
    else:
        print("No holidays found in the database.")

# Call both functions to write data to the same CSV file
average_holidays_per_country()
country_with_most_holidays()
country_with_least_holidays()

