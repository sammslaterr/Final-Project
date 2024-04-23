import matplotlib
import matplotlib.pyplot as plt
import sqlite3

def get_holiday_frequencies_by_month (db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    dict = {}
    info = cur.execute('SELECT M.month, COUNT(H.id) FROM Fun_Holidays H JOIN Month M ON H.month_id = M.id GROUP BY M.id')

    for holiday in info:
        dict[holiday[0]] = holiday[1]
    
    plt.plot(list(dict.keys()), list(dict.values()), color = 'pink')
    plt.xlabel('Month')
    plt.ylabel('Total Holidays')
    plt.title('Holiday Frequencies by Month')
    plt.show()

def get_holiday_percentage_by_country(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute('''SELECT c.country, COUNT(h.country_id) AS holiday_count
                 FROM european_country_ids c
                 LEFT JOIN european_holidays h ON c.id = h.country_id
                 GROUP BY c.country''')
    holiday_counts = c.fetchall()
    conn.close()

    # Sort the holiday counts in descending order
    holiday_counts.sort(key=lambda x: x[1], reverse=True)

    # Take only the top 5 countries
    top_countries = holiday_counts[:12]

    # Sum up the holiday counts of the rest of the countries
    other_count = sum(row[1] for row in holiday_counts[12:])

    # Append 'Other' with its count to the list of top countries
    top_countries.append(('Other', other_count))

    # Separate countries and counts
    countries = [row[0] for row in top_countries]
    holiday_counts = [row[1] for row in top_countries]

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

    plt.figure(figsize=(10, 8))
    plt.pie(region_counts.values(), labels=region_counts.keys(), autopct='%1.1f%%', startangle=140)
    plt.title('Distribution of European Countries by Region')
    plt.axis('equal')
    plt.show()

def get_holiday_frequency(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    dict = {}
    info = c.execute('SELECT W.weekday, COUNT(USH.id), COUNT(FH.id) FROM Weekday W JOIN US_Holidays USH ON USH.weekday_id = W.id JOIN Fun_Holidays FH ON FH.weekday_id = W.id GROUP BY W.id')

    for holiday in info:
        dict[holiday[0]] = holiday[1] + holiday[2]
    
    plt.figure(figsize=(10, 6))
    plt.bar(list(dict.keys()), list(dict.values()), color = 'blue')
    plt.xlabel('Weekday')
    plt.ylabel('Frequencies')
    plt.title('Frequency of Fun and US Holidays Based on Weekdays')
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

    labels = ['Public Holidays', 'Non-Public Holidays']

    sizes = [public_count, non_public_count]

    colors = ['#ff9999','#66b3ff']

    plt.figure(figsize=(8, 6))
    plt.pie(sizes, colors=colors, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Distribution of Public and Non-Public Holidays')

    plt.axis('equal')

    plt.show()

def main():
    db = 'holidays.db'
    get_holiday_frequencies_by_month(db)
    get_holiday_percentage_by_country(db)
    get_countries_by_region()
    get_holiday_frequency(db)
    retrieve_holiday_data(db)
    
if __name__ == "__main__":
    main()
