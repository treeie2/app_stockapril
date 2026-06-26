import json

f = open(r'e:\github\stock-research-backup\data\groups\groups.json', 'r', encoding='utf-8')
groups = json.load(f)
f.close()

items = list(groups.items())[1:]  # skip first already inserted
for i in range(0, len(items), 15):
    batch = items[i:i+15]
    fname = fr'e:\github\stock-research-backup\_gp_{i//15}.sql'
    with open(fname, 'w', encoding='utf-8') as out:
        for gid, g in batch:
            n = str(g.get('name', gid)).replace("'", "''")
            d = str(g.get('description', '')).replace("'", "''")
            c = g.get('color', '#3b82f6')
            ic = g.get('icon', '')
            s = json.dumps(g.get('stocks', []), ensure_ascii=False).replace("'", "''")
            ca = str(g.get('created_at', '')).replace("'", "''")
            ua = str(g.get('updated_at', '')).replace("'", "''")
            out.write(f"INSERT INTO groups_data (id, name, description, color, icon, stocks, created_at, updated_at) VALUES ('{gid}', '{n}', '{d}', '{c}', '{ic}', '{s}'::jsonb, '{ca}', '{ua}') ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name, stocks=EXCLUDED.stocks, updated_at=EXCLUDED.updated_at;\n")
    print(f'{fname}: {len(batch)} groups')

print('Done - run these .sql files via supabase_execute_sql')
