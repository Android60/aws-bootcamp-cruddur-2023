from datetime import datetime, timedelta, timezone
from opentelemetry import trace

from lib.db import pool, query_wrap_array

tracer = trace.get_tracer("home.activities")

class HomeActivities:
  def run(cognito_user_id=None):

    sql = query_wrap_array("""
      SELECT
        activities.uuid,
        users.display_name,
        users.handle,
        activities.message,
        activities.replies_count,
        activities.reposts_count,
        activities.likes_count,
        activities.reply_to_activity_uuid,
        activities.expires_at,
        activities.created_at
      FROM public.activities
      LEFT JOIN public.users ON users.uuid = activities.user_uuid
      ORDER BY activities.created_at DESC
    """)
    with pool.connection() as conn:
      with conn.cursor() as cur:
        cur.execute(sql)
        # this will return a tuple
        # the first field being the data
        json = cur.fetchone()

    return json[0]

    # Logger.info("HomeActivities")
    # with tracer.start_as_current_span("home-activities-mock-data"):
    #   now = datetime.now(timezone.utc).astimezone()
    #   span = trace.get_current_span()
    #   span.set_attribute("app.now", now.isoformat())
    #   results = [{
    #     'uuid': '68f126b0-1ceb-4a33-88be-d90fa7109eee',
    #     'handle':  'Andrew Brown',
    #     'message': 'Cloud is fun!',
    #     'created_at': (now - timedelta(days=2)).isoformat(),
    #     'expires_at': (now + timedelta(days=5)).isoformat(),
    #     'likes_count': 5,
    #     'replies_count': 1,
    #     'reposts_count': 0,
    #     'replies': [{
    #       'uuid': '26e12864-1c26-5c3a-9658-97a10f8fea67',
    #       'reply_to_activity_uuid': '68f126b0-1ceb-4a33-88be-d90fa7109eee',
    #       'handle':  'Worf',
    #       'message': 'This post has no honor!',
    #       'likes_count': 0,
    #       'replies_count': 0,
    #       'reposts_count': 0,
    #       'created_at': (now - timedelta(days=2)).isoformat()
    #     }],
    #   },
    #   {
    #     'uuid': '66e12864-8c26-4c3a-9658-95a10f8fea67',
    #     'handle':  'Worf',
    #     'message': 'I am out of prune juice',
    #     'created_at': (now - timedelta(days=7)).isoformat(),
    #     'expires_at': (now + timedelta(days=9)).isoformat(),
    #     'likes': 0,
    #     'replies': []
    #   },
    #   {
    #     'uuid': '248959df-3079-4947-b847-9e0892d1bab4',
    #     'handle':  'Garek',
    #     'message': 'My dear doctor, I am just simple tailor',
    #     'created_at': (now - timedelta(hours=1)).isoformat(),
    #     'expires_at': (now + timedelta(hours=12)).isoformat(),
    #     'likes': 0,
    #     'replies': []
    #   }
    #   ]
    #   if cognito_user_id != None:
    #     extra_crud = {
    #     'uuid': '248959df-3079-4947-b847-9e0892d1bab4',
    #     'handle':  'Lore',
    #     'message': 'My dear brother, it the humans that are the problem',
    #     'created_at': (now - timedelta(hours=1)).isoformat(),
    #     'expires_at': (now + timedelta(hours=12)).isoformat(),
    #     'likes': 1000,
    #     'replies': []
    #     }
    #     results.insert(0, extra_crud)

    #   span.set_attribute("app.result_length", len(results))
    #   return results