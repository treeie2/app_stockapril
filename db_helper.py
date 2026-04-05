"""
Database helper module for SQLite operations
"""
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / 'data' / 'stock_research.db'

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_stocks(limit=None, offset=None, filters=None):
    """Get all stocks with optional filtering"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT s.code, s.name, s.industry, s.board, s.article_count,
               GROUP_CONCAT(c.concept_name) as concepts
        FROM stocks s
        LEFT JOIN concepts c ON s.code = c.stock_code
    '''
    
    params = []
    if filters:
        conditions = []
        if filters.get('industry'):
            conditions.append("s.industry LIKE ?")
            params.append(f"%{filters['industry']}%")
        if filters.get('concept'):
            conditions.append("c.concept_name = ?")
            params.append(filters['concept'])
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
    
    query += " GROUP BY s.code"
    
    # Default sort by article_count desc
    query += " ORDER BY s.article_count DESC"
    
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)
    if offset is not None:
        query += " OFFSET ?"
        params.append(offset)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    stocks = []
    for row in rows:
        stock = dict(row)
        # Parse concepts string to list
        if stock.get('concepts'):
            stock['concepts'] = stock['concepts'].split(',')
        else:
            stock['concepts'] = []
        stocks.append(stock)
    
    return stocks

def get_stock_by_code(code):
    """Get single stock by code"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.*, GROUP_CONCAT(c.concept_name) as concepts
        FROM stocks s
        LEFT JOIN concepts c ON s.code = c.stock_code
        WHERE s.code = ?
        GROUP BY s.code
    ''', (code,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        stock = dict(row)
        if stock.get('concepts'):
            stock['concepts'] = stock['concepts'].split(',')
        else:
            stock['concepts'] = []
        return stock
    return None

def get_all_concepts():
    """Get all unique concepts"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT concept_name FROM concepts ORDER BY concept_name')
    rows = cursor.fetchall()
    conn.close()
    
    return [row['concept_name'] for row in rows]

def get_all_industries():
    """Get all unique industries"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT industry FROM stocks WHERE industry IS NOT NULL ORDER BY industry')
    rows = cursor.fetchall()
    conn.close()
    
    return [row['industry'] for row in rows if row['industry']]

def get_articles_by_stock(code):
    """Get articles for a stock"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM articles WHERE stock_code = ? ORDER BY date DESC
    ''', (code,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_insights_by_stock(code):
    """Get insights for a stock"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM insights WHERE stock_code = ?', (code,))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_accidents_by_stock(code):
    """Get accidents for a stock"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM accidents WHERE stock_code = ?', (code,))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def search_stocks(query):
    """Search stocks by name or code"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.code, s.name, s.industry,
               GROUP_CONCAT(c.concept_name) as concepts
        FROM stocks s
        LEFT JOIN concepts c ON s.code = c.stock_code
        WHERE s.name LIKE ? OR s.code LIKE ?
        GROUP BY s.code
        LIMIT 20
    ''', (f'%{query}%', f'%{query}%'))
    
    rows = cursor.fetchall()
    conn.close()
    
    stocks = []
    for row in rows:
        stock = dict(row)
        if stock.get('concepts'):
            stock['concepts'] = stock['concepts'].split(',')
        else:
            stock['concepts'] = []
        stocks.append(stock)
    
    return stocks

def get_stocks_by_concept(concept_name):
    """Get all stocks with a specific concept"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.code, s.name, s.industry,
               GROUP_CONCAT(c2.concept_name) as concepts
        FROM stocks s
        JOIN concepts c ON s.code = c.stock_code
        LEFT JOIN concepts c2 ON s.code = c2.stock_code
        WHERE c.concept_name = ?
        GROUP BY s.code
    ''', (concept_name,))
    
    rows = cursor.fetchall()
    conn.close()
    
    stocks = []
    for row in rows:
        stock = dict(row)
        if stock.get('concepts'):
            stock['concepts'] = stock['concepts'].split(',')
        else:
            stock['concepts'] = []
        stocks.append(stock)
    
    return stocks

def get_total_stock_count():
    """Get total number of stocks"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM stocks')
    result = cursor.fetchone()
    conn.close()
    
    return result['count']

def get_total_article_count():
    """Get total number of articles"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM articles')
    result = cursor.fetchone()
    conn.close()
    
    return result['count']
