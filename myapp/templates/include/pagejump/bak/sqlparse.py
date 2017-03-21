import json
import sys
from django.core.serializers.json import DjangoJSONEncoder

from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import (
    DeleteRowsEvent,
    UpdateRowsEvent,
    WriteRowsEvent,
)

MYSQL_SETTINGS = {
    "host": "10.1.70.220",
    "port": 3306,
    "user": "chang",
    "passwd": "chang"
}
def compare_items((k, v)):
    #caution: if v is NULL, may need to process
    if v is None:
        return '`%s` IS %s' % (k,v)
    else:
        return '`%s`=%s' % (k,v)

def fix_object(value):
    """Fixes python objects so that they can be properly inserted into SQL queries"""
    if isinstance(value, unicode):
        return value.encode('utf-8')
    else:
        return value

def main():
    stream = BinLogStreamReader(
        connection_settings=MYSQL_SETTINGS,
        server_id=220,
        only_events=[DeleteRowsEvent, WriteRowsEvent, UpdateRowsEvent]

    )

    for binlogevent in stream:

        for row in binlogevent.rows:
            event = {"schema": binlogevent.schema, "table": binlogevent.table}
            # print row
            # print "row values"
            # print row["values"]
            # print row['values'].items()
            # print "end row values"
            if isinstance(binlogevent, DeleteRowsEvent):
                event["action"] = "delete"
                event = dict(event.items() + row["values"].items())
                template = 'DELETE FROM `{0}`.`{1}` WHERE {2} LIMIT 1;'.format(
                    binlogevent.schema, binlogevent.table,
                    ' AND '.join(map(compare_items, row['values'].items()))
                )
                values = map(fix_object, row['values'].values())
                print template
                print "deleteing "
                print values
            elif isinstance(binlogevent, UpdateRowsEvent):
                event["action"] = "update"
                event = dict(event.items() + row["after_values"].items())
            elif isinstance(binlogevent, WriteRowsEvent):
                event["action"] = "insert"
                event = dict(event.items() + row["values"].items())
            # print json.dumps(event,cls=DjangoJSONEncoder)
            # sys.stdout.flush()


    stream.close()


if __name__ == "__main__":
    main()