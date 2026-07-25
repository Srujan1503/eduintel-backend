import sys
from pathlib import Path
# ensure project root is on sys.path
root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
	sys.path.insert(0, str(root))

from app.core.config import get_settings
from sqlalchemy import create_engine, inspect

s = get_settings()
engine = create_engine(s.database_url)
ins = inspect(engine)
print('tables:', ins.get_table_names())
