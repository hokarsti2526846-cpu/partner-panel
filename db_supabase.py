import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://pswnlfmyvgwwbawqsypw.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_s_4Kb9eD3c86Hz8BtjGIlg_xap07coe")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_user_stats(user_id):
    try:
        result = supabase.table('stats_history').select('*').eq('user_id', user_id).execute()
        if result.data and len(result.data) > 0:
            user = result.data[0]
            defaults = {
                'user_id': user_id, 'xp': 0, 'level': 1,
                'all_ads': 0, 'all_mins': 0, 'day_ads': 0, 'day_mins': 0,
                'week_ads': 0, 'week_mins': 0, 'month_ads': 0, 'month_mins': 0,
                'year_ads': 0, 'year_mins': 0,
                'total_ads': 0, 'total_mins': 0, 'daily_streak': 0,
                'achievements': '[]'
            }
            defaults.update(user)
            return defaults
        return None
    except Exception as e:
        print(f"Error in get_user_stats: {e}")
        return None


def get_leaderboard(limit=10):
    try:
        result = supabase.table('stats_history').select('user_id, xp, level, all_ads, all_mins').order('xp', desc=True).limit(limit).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error in get_leaderboard: {e}")
        return []


def get_rank(user_id):
    try:
        user = supabase.table('stats_history').select('xp').eq('user_id', user_id).execute()
        if not user.data:
            return 0
        xp = user.data[0].get('xp', 0)
        result = supabase.table('stats_history').select('user_id', count='exact').gt('xp', xp).execute()
        return (result.count or 0) + 1
    except Exception as e:
        print(f"Error in get_rank: {e}")
        return 0


def get_all_partners():
    try:
        result = supabase.table('stats_history').select('*').order('xp', desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error in get_all_partners: {e}")
        return []


def get_average_stats():
    try:
        result = supabase.table('stats_history').select('all_ads, all_mins, xp').execute()
        if not result.data:
            return {"avg_ads": 0, "avg_mins": 0, "avg_xp": 0}
        total_ads = sum(r.get('all_ads', 0) or 0 for r in result.data)
        total_mins = sum(r.get('all_mins', 0) or 0 for r in result.data)
        total_xp = sum(r.get('xp', 0) or 0 for r in result.data)
        n = len(result.data)
        return {
            "avg_ads": round(total_ads / n, 1),
            "avg_mins": round(total_mins / n, 1),
            "avg_xp": round(total_xp / n, 1)
        }
    except Exception as e:
        print(f"Error in get_average_stats: {e}")
        return {"avg_ads": 0, "avg_mins": 0, "avg_xp": 0}


def get_calendar_data(user_id):
    from datetime import datetime, timedelta
    calendar_data = {}
    try:
        excuses = supabase.table('excuses').select('excuse_date').eq('user_id', user_id).eq('status', 'approved').execute()
        for e in excuses.data:
            calendar_data[e['excuse_date']] = "excuse"
        
        vacations = supabase.table('vacations').select('start_date, end_date').eq('user_id', user_id).eq('status', 'approved').execute()
        for v in vacations.data:
            start = datetime.strptime(v['start_date'], "%Y-%m-%d")
            end = datetime.strptime(v['end_date'], "%Y-%m-%d")
            current = start
            while current <= end:
                calendar_data[current.strftime("%Y-%m-%d")] = "vacation"
                current += timedelta(days=1)
    except Exception as e:
        print(f"Error in get_calendar_data: {e}")
    return calendar_data


def update_user_xp(user_id, new_xp):
    try:
        new_level = 1 + (new_xp // 1000)
        supabase.table('stats_history').update({'xp': new_xp, 'level': new_level}).eq('user_id', user_id).execute()
        return True
    except Exception as e:
        print(f"Error in update_user_xp: {e}")
        return False


def update_user(user_id, data):
    try:
        supabase.table('stats_history').update(data).eq('user_id', user_id).execute()
        return True
    except Exception as e:
        print(f"Error in update_user: {e}")
        return False


def delete_user(user_id):
    try:
        for table in ['stats_history', 'active_ads', 'active_voice', 'excuses', 'vacations', 'punishment_history']:
            supabase.table(table).delete().eq('user_id', user_id).execute()
        return True
    except Exception as e:
        print(f"Error in delete_user: {e}")
        return False


def send_notification(message, sent_by):
    from datetime import datetime
    try:
        supabase.table('admin_notifications').insert({
            'message': message,
            'sent_by': sent_by,
            'sent_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }).execute()
        return True
    except Exception as e:
        print(f"Error in send_notification: {e}")
        return False