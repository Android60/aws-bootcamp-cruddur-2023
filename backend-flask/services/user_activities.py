from datetime import datetime, timedelta, timezone
from aws_xray_sdk.core import xray_recorder

from lib.db import db

class UserActivities:
  def run(user_handle):
    xray_recorder.begin_subsegment('user_activities')   
    model = {
      'errors': None,
      'data': None
    }

    now = datetime.now(timezone.utc).astimezone()

    if user_handle == None or len(user_handle) < 1:
      model['errors'] = ['blank_user_handle']
    else:
      print("handle issss")
      print(user_handle)
      sql = db.template('users','show')
      subsegment = xray_recorder.begin_subsegment('query-db')
      results = db.query_object_json(sql, {'handle':user_handle})
      print("got results:.............")
      print(results)
      now = datetime.now()

      dict = {
        "now": now.isoformat(),
        "results-size": len(results)
      }
      subsegment.put_metadata('key', dict, 'namespace')
      xray_recorder.end_subsegment()
      xray_recorder.end_subsegment()
      model['data'] = results
      return model