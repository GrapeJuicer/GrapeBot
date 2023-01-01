from pathlib import Path
import sqlite3

BASEDIR  = Path(__file__).parent
DATABASE = BASEDIR / 'db.sqlite3'
TOKEN    = BASEDIR / 'token.key'
