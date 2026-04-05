import sqlite3
conn = sqlite3.connect('data/stock_research.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check table schema
cursor.execute('PRAGMA table_info(insights)')
print('Insights table columns:')
for col in cursor.fetchall():
    print(f'  {col[\"name\"]}')

cursor.execute('PRAGMA table_info(accidents)')
print('\nAccidents table columns:')
for col in cursor.fetchall():
    print(f'  {col[\"name\"]}')

# Check counts
cursor.execute('SELECT COUNT(*) as count FROM insights')
insights_count = cursor.fetchone()['count']
print(f'\nInsights in SQLite: {insights_count}')

cursor.execute('SELECT COUNT(*) as count FROM accidents')
accidents_count = cursor.fetchone()['count']
print(f'Accidents in SQLite: {accidents_count}')

# Show sample data
cursor.execute('SELECT * FROM insights LIMIT 3')
print('\nSample insights:')
for row in cursor.fetchall():
    print(f'  {dict(row)}')

cursor.execute('SELECT * FROM accidents LIMIT 3')
print('\nSample accidents:')
for row in cursor.fetchall():
    print(f'  {dict(row)}')

# Check unique stocks
cursor.execute('SELECT COUNT(DISTINCT stock_code) as count FROM insights')
insights_stocks = cursor.fetchone()['count']
cursor.execute('SELECT COUNT(DISTINCT stock_code) as count FROM accidents')
accidents_stocks = cursor.fetchone()['count']
print(f'\nUnique stocks with insights: {insights_stocks}')
print(f'Unique stocks with accidents: {accidents_stocks}')

conn.close()
