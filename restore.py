import os, glob, json, ast

files = sorted(glob.glob(r'C:\Users\himay\.gemini\antigravity\brain\*\.system_generated\logs\transcript.jsonl'), key=os.path.getmtime)

files_to_restore = [
    'guided_wizard_ui.py',
    'setup_wizard.py',
    'open_text.py',
    'modern_button.py',
    'nurse_tooltip.py',
    'body_map.py',
    'scale_slider.py',
    'mcq_checkbox.py'
]

latest_content = {}

for f in files:
    try:
        for line in open(f, 'r', encoding='utf-8'):
            try:
                d = json.loads(line)
                for c in d.get('tool_calls', []):
                    if c.get('name') == 'write_to_file':
                        args = c.get('args', {})
                        tf = args.get('TargetFile', '').strip('"\'')
                        content = args.get('CodeContent', '')
                        
                        if isinstance(content, str) and content.startswith('"') and content.endswith('"'):
                            try:
                                content = ast.literal_eval(content)
                            except:
                                pass
                        
                        for target in files_to_restore:
                            if target in tf:
                                latest_content[tf] = content
            except Exception as e: pass
    except: pass

print(f'Found {len(latest_content)} files to restore:')
for path, content in latest_content.items():
    print(f'Restoring {path} ({len(content)} bytes)')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
