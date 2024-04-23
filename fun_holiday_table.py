from bs4 import BeautifulSoup
import requests
import sqlite3
import os
import re

def set_up_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
    return cur, conn

def day_of_week_table(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Weekday (id INTEGER PRIMARY KEY, weekday TEXT)")

    cur.execute('''SELECT COUNT(*) FROM Weekday''')
    count = cur.fetchone()[0]

    if count == 0:
        weekdays = [('Monday',), ('Tuesday',), ('Wednesday',), ('Thursday',), ('Friday',), ('Saturday',), ('Sunday',)]
        
        cur.executemany('''INSERT INTO Weekday (weekday) VALUES (?)''', weekdays)
    
    conn.commit()

def month_table(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Month (id INTEGER PRIMARY KEY, month TEXT)")

    cur.execute("SELECT COUNT(*) FROM Month")
    count = cur.fetchone()[0]

    if count == 0:
        months = [('Jan',), ('Feb',), ('Mar',), ('Apr',), ('May',), ('Jun',), ('Jul',), ('Aug',), ('Sep',), ('Oct',), ('Nov',), ('Dec',)]
        
        cur.executemany("INSERT INTO Month (month) VALUES (?)", months)
    
    conn.commit()

def fun_holiday_info (soup):
    found_info = soup.find('table', class_='zebra fw tb-hover')
    date_data = found_info.find_all('th')
    holiday_data = found_info.find_all('a')
    day_of_week_data = found_info.find_all('td')

    day_data_list = []
    month_data_list = []
    holiday_data_list = []
    day_of_week_data_list = []

    for date in date_data:
        pattern = r'(\w{3})\s(\d{1,2})'
        found_dates = re.findall(pattern, date.text)
        for month, day in found_dates:
            day_data_list.append(day)
            month_data_list.append(month)

    for holiday in holiday_data:
        holiday_data_list.append(holiday.text)
    
    for index in range(0, len(day_of_week_data), 2):
        day_of_week_data_list.append(day_of_week_data[index].text)
    
    info_list = []
    id_num = 1
    for i in range(len(holiday_data)):
        info_list.append({'id': id_num, 'holiday': holiday_data_list[i],'month': month_data_list[i], 'date': day_data_list[i], 'day_of_week': day_of_week_data_list[i]})
        id_num += 1
    
    return info_list

def create_fun_holiday_table(data, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Fun_Holidays (id INTEGER PRIMARY KEY, name TEXT, month_id INTEGER, date INTEGER, weekday_id INTEGER, FOREIGN KEY (month_id) REFERENCES Month(id), FOREIGN KEY (weekday_id) REFERENCES Weekday(id))")

    total_entries = 0
    for holiday_data in data:
        if total_entries >= 25:
            break
        
        cur.execute("SELECT id FROM Weekday WHERE weekday=?", (holiday_data['day_of_week'],))
        weekday_id = cur.fetchone()[0]
   
        cur.execute("SELECT id FROM Month WHERE month=?", (holiday_data['month'],))
        month_id = cur.fetchone()[0]

        existing_entry = cur.execute("SELECT COUNT(*) FROM Fun_Holidays WHERE id=? AND name=? AND month_id=? AND date=? AND weekday_id=?", (holiday_data['id'], holiday_data['holiday'], month_id, holiday_data['date'], weekday_id)).fetchone()[0]
        if existing_entry == 0:
            cur.execute("INSERT OR IGNORE INTO Fun_Holidays (id, name, month_id, date, weekday_id) VALUES (?, ?, ?, ?, ?)",
                        (holiday_data['id'],
                        holiday_data['holiday'],
                        month_id,
                        holiday_data['date'],
                        weekday_id
                        ))
            total_entries += 1
    
    conn.commit()

def main():
    
    url = 'https://www.timeanddate.com/holidays/fun/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    info = fun_holiday_info (soup)
    cur, conn = set_up_database("holidays.db")
    day_of_week_table(cur, conn)
    month_table(cur, conn)
    create_fun_holiday_table(info, cur, conn)

    conn.close()

if __name__ == "__main__":
    main()
