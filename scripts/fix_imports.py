import pathlib

def fix_file(p):
    try:
        text = p.read_text(encoding='utf-8')
    except:
        return
        
    if 'nim.nim_key_manager' in text or 'NIMKeyManager' in text or 'key_manager' in text:
        text = text.replace('from llm.local_client import LocalLLMClient', 'from llm.local_client import LocalLLMClient')
        text = text.replace('from llm.local_client import LocalLLMClient', 'from llm.local_client import LocalLLMClient')
        text = text.replace('', '')
        text = text.replace('llm_client: LocalLLMClient', 'llm_client: LocalLLMClient')
        text = text.replace('self.llm_client = llm_client', 'self.llm_client = llm_client')
        text = text.replace('llm_client=self.llm_client', 'llm_client=self.llm_client')
        text = text.replace('llm_client=llm_client', 'llm_client=llm_client')
        text = text.replace('llm_client: Optional[LocalLLMClient] = None', 'llm_client: Optional[LocalLLMClient] = None')
        p.write_text(text, encoding='utf-8')

for p in pathlib.Path('c:/mediassist').rglob('*.py'):
    if 'venv' not in p.parts:
        fix_file(p)
