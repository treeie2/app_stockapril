import re

p = '.trae/skills/tdx_mark/generate_tdx_mark.py'
with open(p, 'r', encoding='utf-8') as f:
    content = f.read()

# Resolve each conflict by keeping "ours" (HEAD) version
def resolve_conflict(match):
    text = match.group(0)
    # Find the ours and theirs parts
    parts = re.split(r'=======\n', text)
    if len(parts) == 2:
        # Take the first part (ours), remove "<<<<<<< HEAD\n" prefix
        ours = re.sub(r'^<<<<<<< .+?\n', '', parts[0])
        # Remove the ">>>>>>> ...\n" suffix from the match
        ours = ours.rstrip('\n')
        return ours + '\n'
    return text

new_content = re.sub(r'<<<<<<< .+?\n(?:.|\n)*?>>>>>>> .+?\n', resolve_conflict, content)

with open(p, 'w', encoding='utf-8') as f:
    f.write(new_content)

# Verify no more conflicts
if '<<<<<<<' in new_content:
    print('WARNING: Some conflicts may remain')
else:
    print(f'✅ All conflicts resolved. File size: {len(new_content)} chars')

# Verify syntax
try:
    compile(new_content, p, 'exec')
    print('✅ Python syntax OK')
except SyntaxError as e:
    print(f'❌ Syntax error: {e}')