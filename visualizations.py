import matplotlib
import matplotlib.pyplot as plt
import sqlite3
import csv

def create_csv_file(filename):
    with open(filename, 'w', newline='') as csvfile:
        pass  

def get_holiday_frequencies_by_month(db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    holiday_freq_dict = {}
    info = cur.execute('SELECT M.month, COUNT(H.id) FROM Fun_Holidays H JOIN Month M ON H.month_id = M.id GROUP BY M.id')
    for holiday in info:
        holiday_freq_dict[holiday[0]] = holiday[1]
    
    with open('holiday_data.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for month, count in holiday_freq_dict.items():
            writer.writerow([f"From the Fun Holidays API, {count} holidays are in {month}"])

    plt.plot(list(holiday_freq_dict.keys()), list(holiday_freq_dict.values()), color='pink')
    plt.xlabel('Month')
    plt.ylabel('Total Holidays')
    plt.title('Holiday Frequencies by Month')
    plt.show()

    conn.close()

def get_holiday_percentage_by_country(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''SELECT c.country, COUNT(h.country_id) AS holiday_count
                 FROM european_country_ids c
                 LEFT JOIN european_holidays h ON c.id = h.country_id
                 GROUP BY c.country''')
    holiday_counts = c.fetchall()
    conn.close()
    holiday_counts.sort(key=lambda x: x[1], reverse=True)
    top_countries = holiday_counts[:12]
    other_count = sum(row[1] for row in holiday_counts[12:])
    top_countries.append(('Other', other_count))
    total_holidays = sum(count for country, count in top_countries)
    
    with open('holiday_data.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for country, count in top_countries:
            percentage = (count / total_holidays) * 100
            writer.writerow([f"From the European Holidays API, {percentage:.1f}% of holidays are in {country}"])

    countries = [country for country, count in top_countries]
    holiday_counts = [count for country, count in top_countries]
    plt.figure(figsize=(8, 8))
    plt.pie(holiday_counts, labels=countries, autopct='%1.1f%%', startangle=140)
    plt.title('Percentage of Holidays by Country')
    plt.axis('equal')
    plt.show()


def get_countries_by_region():
    regions = {
        'Northern Europe': ['Norway', 'Sweden', 'Denmark', 'Finland', 'Iceland', 'Estonia', 'Latvia', 'Lithuania'],
        'Western Europe': ['United Kingdom', 'Ireland', 'Netherlands', 'Belgium', 'Luxembourg', 'France', 'Germany'],
        'Southern Europe': ['Spain', 'Portugal', 'Italy', 'Greece', 'Malta', 'Andorra', 'San Marino', 'Vatican City', 'Monaco'],
        'Central Europe': ['Austria', 'Switzerland', 'Liechtenstein', 'Czechia', 'Slovakia', 'Poland', 'Hungary', 'Slovenia', 'Croatia'],
        'Eastern Europe': ['Russia', 'Belarus', 'Ukraine', 'Moldova', 'Romania', 'Bulgaria', 'Serbia', 'Montenegro', 'Bosnia and Herzegovina', 'North Macedonia', 'Albania', 'Kosovo']
    }

    region_counts = {region: len(countries) for region, countries in regions.items()}

    with open('holiday_data.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for region, count in region_counts.items():
            writer.writerow([f"From the European Holidays API, {count} countries are in {region}"])

    plt.figure(figsize=(10, 8))
    plt.pie(region_counts.values(), labels=region_counts.keys(), autopct='%1.1f%%', startangle=140)
    plt.title('Distribution of European Countries by Region')
    plt.axis('equal')
    plt.show()

def get_holiday_frequency(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    holiday_counts = {}
    info = c.execute('''SELECT W.weekday, COUNT(USH.id) as ush_count 
                        FROM Weekday W 
                        JOIN US_Holidays USH ON W.id = USH.weekday_id
                        GROUP BY W.id''').fetchall()
    for weekday, count in info:
        holiday_counts[weekday] = count
    with open('holiday_data.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for weekday, count in holiday_counts.items():
            writer.writerow([f"From the US Holidays API, {count} holidays are on {weekday}"])
    plt.figure(figsize=(10, 6))
    plt.bar(list(holiday_counts.keys()), list(holiday_counts.values()), color='blue')
    plt.xlabel('Day of Week')
    plt.ylabel('Frequencies')
    plt.title('Frequency of US Holidays on Each Day of the Week')
    plt.show()

def retrieve_holiday_data(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    query = '''
            SELECT COUNT(*) FROM US_Holidays WHERE is_public = ?
            '''
    c.execute(query, (1,))
    public_count = c.fetchone()[0]
    c.execute(query, (0,))
    non_public_count = c.fetchone()[0]
    conn.close()
    with open('holiday_data.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([f"From the US Holidays API, {public_count} public holidays"])
        writer.writerow([f"From the US Holidays API, {non_public_count} non-public holidays"])
    labels = ['Public Holidays', 'Non-Public Holidays']
    sizes = [public_count, non_public_count]
    colors = ['#ff9999', '#66b3ff']
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, colors=colors, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Distribution of Public and Non-Public Holidays')
    plt.axis('equal')
    plt.show()

def main():
    db = 'holidays.db'
    create_csv_file('holiday_data.csv')
    get_holiday_frequencies_by_month(db)
    get_holiday_percentage_by_country(db)
    get_countries_by_region()
    get_holiday_frequency(db)
    retrieve_holiday_data(db)


    
if __name__ == "__main__":
    main()
