from pathlib import Path

BASEDIR  = Path(__file__).parent
DATABASE = BASEDIR / 'db.sqlite3'
TOKEN    = BASEDIR / 'token.key'
DEEPL_API_KEY = BASEDIR / 'deepl.key'
