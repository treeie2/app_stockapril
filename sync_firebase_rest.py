#!/usr/bin/env python3
"""Sync stocks_master.json -> Firebase Firestore via REST API (bypasses gRPC blocks)"""
import json, requests, time
from pathlib import Path

KEY_FILE = Path(__file__).parent / 'serviceAccountKey.json'
MASTER_FILE = Path(__file__).parent / 'data' / 'stocks' / 'stocks_master.json'
PROJECT_ID = 'webstock-724'

with open(KEY_FILE, 'r', encoding='utf-8') as f:
    sa_key = json.load(f)
with open(MASTER_FILE, 'r', encoding='utf-8') as f:
    master = json.load(f)

print('Loaded %d stocks' % len(master['stocks']))

import google.auth.transport.requests
import google.oauth2.service_account

SCOPES = ['https://www.googleapis.com/auth/datastore']
creds = google.oauth2.service_account.Credentials.from_service_account_info(sa_key, scopes=SCOPES)
creds.refresh(google.auth.transport.requests.Request())
token = creds.token
print('Got OAuth token')

BASE = 'https://firestore.googleapis.com/v1/projects/%s/databases/(default)/documents' % PROJECT_ID
headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
synced = failed = 0
stocks = list(master['stocks'].items())

def build_doc(code, s):
    fields = {
        'name': {'stringValue': s.get('name', '')},
        'code': {'stringValue': code},
        'board': {'stringValue': s.get('board', '')},
        'industry': {'stringValue': s.get('industry', '')},
        'concepts': {'arrayValue': {'values': [{'stringValue': c} for c in s.get('concepts', [])]}},
        'products': {'arrayValue': {'values': [{'stringValue': p} for p in s.get('products', [])]}},
        'core_business': {'arrayValue': {'values': [{'stringValue': c} for c in s.get('core_business', [])]}},
        'industry_position': {'arrayValue': {'values': [{'stringValue': p} for p in s.get('industry_position', [])]}},
        'chain': {'arrayValue': {'values': [{'stringValue': c} for c in s.get('chain', [])]}},
        'partners': {'arrayValue': {'values': [{'stringValue': p} for p in s.get('partners', [])]}},
        'mention_count': {'integerValue': str(s.get('mention_count', 0))},
        'last_updated': {'stringValue': s.get('last_updated', '')},
        'articles': {'arrayValue': {'values': [
            {'mapValue': {'fields': {
                'title': {'stringValue': a.get('title', '')},
                'date': {'stringValue': a.get('date', '')},
                'source': {'stringValue': a.get('source', '')},
                'accidents': {'arrayValue': {'values': [{'stringValue': x} for x in a.get('accidents', [])]}},
                'insights': {'arrayValue': {'values': [{'stringValue': x} for x in a.get('insights', [])]}},
                'key_metrics': {'arrayValue': {'values': [{'stringValue': x} for x in a.get('key_metrics', [])]}},
                'target_valuation': {'arrayValue': {'values': [{'stringValue': x} for x in a.get('target_valuation', [])]}},
            }}}
            for a in s.get('articles', [])
        ]}},
    }
    return fields

print('Syncing stocks (this may take a few minutes)...')
for i, (code, s) in enumerate(stocks):
    if not s.get('last_updated'):
        continue
    url = BASE + '/stocks?documentId=' + code
    r = requests.post(url, headers=headers, json={'fields': build_doc(code, s)})
    if r.status_code == 200:
        synced += 1
    else:
        failed += 1
    if (i+1) % 200 == 0:
        print('  %d/%d synced, %d failed' % (synced, len(stocks), failed))

print()
print('Sync complete: %d success, %d failed' % (synced, failed))
