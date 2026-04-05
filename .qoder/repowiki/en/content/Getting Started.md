# Getting Started

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [requirements.txt](file://requirements.txt)
- [Procfile](file://Procfile)
- [main.py](file://main.py)
- [build_index.py](file://build_index.py)
- [templates/dashboard.html](file://templates/dashboard.html)
- [templates/stock_detail.html](file://templates/stock_detail.html)
- [data/master/stocks_master.json](file://data/master/stocks_master.json)
- [data/master/social_security_2025q4.json](file://data/master/social_security_2025q4.json)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Local Development Environment Setup](#local-development-environment-setup)
4. [Installation](#installation)
5. [Initial Project Configuration](#initial-project-configuration)
6. [Dependency Installation](#dependency-installation)
7. [Local Server Startup](#local-server-startup)
8. [First-Time User Guide](#first-time-user-guide)
9. [Basic Navigation](#basic-navigation)
10. [Understanding the Dashboard Interface](#understanding-the-dashboard-interface)
11. [Exploring Stock Data](#exploring-stock-data)
12. [Verification Steps](#verification-steps)
13. [Troubleshooting](#troubleshooting)
14. [Conclusion](#conclusion)

## Introduction
This guide helps you set up and run the Stock Research Platform locally. It covers prerequisites, environment setup, installation, configuration, and first-time usage. The platform is a Flask web app that serves an interactive dashboard for stock research, concepts exploration, and social security fund holdings.

## Prerequisites
- Python 3.x installed on your system
- pip (Python package installer)
- Basic familiarity with command-line tools

## Local Development Environment Setup
- Ensure Python 3.x is installed and accessible from your terminal or command prompt.
- Confirm pip is available by running:
  - python -m pip --version
  - Or pip --version

## Installation
Follow these steps to install and prepare the project:

1. Clone or download the repository to your local machine.
2. Navigate to the project root directory in your terminal.

## Initial Project Configuration
The project requires a few key data files to function. These are located under the data directory:
- data/master/stocks_master.json: Main stock metadata and articles
- data/sentiment/search_index_full.json.gz: Search index generated from sentiment data
- data/master/social_security_2025q4.json: Social Security Fund holdings for Q4 2025

Important note: The Flask app expects a gzipped search index file at data/sentiment/search_index_full.json.gz. If this file does not exist, the app will load an empty dataset and display a warning. You can generate this index using the provided script.

**Section sources**
- [main.py:94-104](file://main.py#L94-L104)
- [main.py:23-26](file://main.py#L23-L26)

## Dependency Installation
Install the required Python packages using pip and the provided requirements.txt:

- Run: pip install -r requirements.txt

This installs:
- Flask 3.0.0
- Gunicorn 21.2.0
- requests 2.31.0
- akshare >= 1.18.40

Notes:
- akshare is lazily imported to avoid slow startup.
- The app uses requests for fetching market data from a third-party API.

**Section sources**
- [requirements.txt:1-5](file://requirements.txt#L1-L5)
- [main.py:12-18](file://main.py#L12-L18)
- [main.py:696-768](file://main.py#L696-L768)

## Local Server Startup
There are two ways to run the server locally:

Option A: Using Flask’s development server
- Export the FLASK_APP environment variable:
  - Windows: set FLASK_APP=main.py
  - macOS/Linux: export FLASK_APP=main.py
- Run: flask run
- Access the app at http://127.0.0.1:5000

Option B: Using Gunicorn (as configured in Procfile)
- Run: gunicorn main:app --bind 0.0.0.0:8000
- Access the app at http://127.0.0.1:8000

Procfile defines the production command used by platforms like Railway. Locally, you can use either Flask dev server or Gunicorn.

**Section sources**
- [Procfile:1](file://Procfile#L1)
- [README.md:38-66](file://README.md#L38-L66)

## First-Time User Guide
After starting the server, you can explore the platform:

- Open your browser and navigate to the local URL shown during startup.
- The homepage displays a dashboard of stocks with filtering, sorting, and pagination.
- Use the navigation bar to switch between pages:
  - Dashboard
  - Stocks List
  - Social Security New Holdings
  - Concepts
- Use the search bar to quickly find stocks by name or code.

## Basic Navigation
- Dashboard: View all stocks with key metrics and concepts.
- Stocks List: Browse all stocks in a sortable list.
- Social Security New: See newly entered holdings by Social Security Fund in Q4 2025.
- Concepts: Explore concept tags and which stocks belong to each concept.
- Search: Enter a term to search across names, codes, concepts, and content fields.

**Section sources**
- [templates/dashboard.html:529-547](file://templates/dashboard.html#L529-L547)
- [templates/stock_detail.html:54-113](file://templates/stock_detail.html#L54-L113)

## Understanding the Dashboard Interface
Key elements of the dashboard:
- Navigation bar with links to major sections
- Filters for concept counts
- Sorting options (by date, mention count, price change, articles, name)
- Refresh button to fetch live market data
- Load more button for pagination
- Stock table with columns for name, industry, concepts, price, change, market cap, mentions, and articles
- Concept tags displayed per stock
- Article counts and mention badges

The dashboard loads stock data from the search index and renders it using Jinja templates. Market data is fetched via an external API when requested.

**Section sources**
- [templates/dashboard.html:559-582](file://templates/dashboard.html#L559-L582)
- [templates/dashboard.html:584-663](file://templates/dashboard.html#L584-L663)
- [main.py:138-210](file://main.py#L138-L210)

## Exploring Stock Data
- Click a stock row to view its detailed page.
- On the stock detail page, you can:
  - See core business, industry position, chain, products, partners
  - Review articles with insights, accidents, key metrics, and target valuation
  - View concept tags and related information
  - See social security fund indicators if applicable
  - Explore similar stocks based on concept overlap

The stock detail page aggregates data from the main stock record and associated articles.

**Section sources**
- [templates/stock_detail.html:124-260](file://templates/stock_detail.html#L124-L260)
- [main.py:280-336](file://main.py#L280-L336)
- [data/master/social_security_2025q4.json:1-217](file://data/master/social_security_2025q4.json#L1-L217)

## Verification Steps
To confirm the installation and data are working:

1. Start the server using either Flask dev server or Gunicorn.
2. Visit the dashboard at http://127.0.0.1:5000 (Flask) or http://127.0.0.1:8000 (Gunicorn).
3. Verify:
   - The dashboard loads without errors
   - At least some stocks appear in the table
   - The “Refresh Prices” button triggers market data fetching
   - Pagination controls work and “Load More” adds more stocks
   - Navigation links are functional
   - Search returns results

If the dashboard appears empty or shows warnings about missing data, generate the search index as described below.

**Section sources**
- [main.py:94-104](file://main.py#L94-L104)
- [main.py:138-210](file://main.py#L138-L210)

## Troubleshooting
Common issues and resolutions:

- Missing search index file
  - Symptom: App logs indicate failure to load the search index and displays empty data.
  - Cause: data/sentiment/search_index_full.json.gz is missing.
  - Resolution: Generate the index using the provided script.
    - Run: python build_index.py
    - This reads data/master/stocks_master.json and data/sentiment/company_mentions.json, builds the index, and saves it as data/sentiment/search_index_full.json.gz.

- akshare import fails
  - Symptom: App warns that akshare could not be imported.
  - Cause: akshare is not installed or not importable.
  - Resolution: Install it via pip or skip if not needed.

- Market data API failures
  - Symptom: Price refresh shows errors or blank values.
  - Cause: External API may be down or blocked.
  - Resolution: Retry later or check network connectivity.

- Port conflicts
  - Symptom: Server fails to bind to the configured port.
  - Resolution: Change the port in Procfile or environment variable and restart.

- Missing data files
  - Symptom: App cannot find stocks_master.json or social_security_2025q4.json.
  - Resolution: Ensure these files exist in data/master/ and data/sentiment/.

**Section sources**
- [build_index.py:77-271](file://build_index.py#L77-L271)
- [main.py:12-18](file://main.py#L12-L18)
- [main.py:696-768](file://main.py#L696-L768)
- [Procfile:1](file://Procfile#L1)

## Conclusion
You now have the Stock Research Platform running locally. Use the dashboard to explore stocks, concepts, and social security fund holdings. If you encounter missing data, regenerate the search index using the provided script. For deployment to platforms like Railway, refer to the project’s deployment notes.