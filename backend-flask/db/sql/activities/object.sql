SELECT 
    activities.uuid,
    users.handle,
    users.display_name,
    activities.message,
    activities.created_at,
    activities.expires_at,
    activities.reply_to_activity_uuid 
FROM public.activities
INNER JOIN public.users on users.uuid = activities.user_uuid
WHERE
    activities.uuid = %(uuid)s