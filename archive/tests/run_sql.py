import tap_db2
import utils
import singer

sql_query = """
select *
from npfdwhts.mj_test_table;
"""

# Pick up the required arguments using the singer module
args = singer.utils.parse_args(tap_db2.REQUIRED_CONFIG_KEYS)
# Use the connection args from above to connect to your DB2 instance
db2_conn = utils.get_db2_sql_engine(args.config)

with db2_conn.connect() as open_conn:
	sql_res = open_conn.execute(sql_query)
	rec = sql_res.fetchone()
	print(rec)
	while rec is not None:
		rec = sql_res.fetchone()
		print(rec)
