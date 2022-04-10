from spoolmanager import Spool
import logging
import sys

console_handler = logging.StreamHandler(sys.stdout)
logging.basicConfig(
    handlers=[console_handler,],
    format='%(message)s',
    level=logging.DEBUG)

log = logging.getLogger()

spool = Spool('test.db')
#spool.import_csv('spool_import.csv')
#print(spool.columns())
data = spool.list_data()
print(data)
for each in spool.list_data():
    print(each)
