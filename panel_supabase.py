from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import os
import json
import random
from datetime import datetime, timedelta

# ✅ Supabase
from db_supabase import (
    get_user_stats, get_leaderboard, get_rank, get_all_partners,
    get_average_stats, get_calendar_data, update_user_xp, update_user,
    delete_user, send_notification, supabase
)

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-12345")

# ============================================
# Admin IDs
# ============================================
ADMIN_IDS = [
    725407103916703755,
    952854100901519420,
    1397972997951983708,
]


# ============================================
# فەنکشنەکانی یاریدەدەر
# ============================================

def get_achievements_progress(user):
    if not user:
        return []
    
    total_ads = user.get('all_ads', 0) or 0
    total_mins = user.get('all_mins', 0) or 0
    level = user.get('level', 1) or 1
    xp = user.get('xp', 0) or 0
    streak = user.get('daily_streak', 0) or 0
    
    achievements = [
        {"id": "first_ad", "name": "یەکەم ڕیکلام", "icon": "🎯", "rarity": "common", "target": 1, "current": min(total_ads, 1), "desc": "یەکەم ڕیکلامت بکە", "xp_reward": 50},
        {"id": "ad_10", "name": "١٠ ڕیکلام", "icon": "📢", "rarity": "common", "target": 10, "current": min(total_ads, 10), "desc": "١٠ ڕیکلام بکە", "xp_reward": 100},
        {"id": "ad_50", "name": "٥٠ ڕیکلام", "icon": "📣", "rarity": "rare", "target": 50, "current": min(total_ads, 50), "desc": "٥٠ ڕیکلام بکە", "xp_reward": 300},
        {"id": "ad_100", "name": "پارتنەری ڕیکلام", "icon": "🏅", "rarity": "epic", "target": 100, "current": min(total_ads, 100), "desc": "١٠٠ ڕیکلام بکە", "xp_reward": 500},
        {"id": "ad_500", "name": "ئەفسانەی ڕیکلام", "icon": "👑", "rarity": "legendary", "target": 500, "current": min(total_ads, 500), "desc": "٥٠٠ ڕیکلام بکە", "xp_reward": 1000},
        {"id": "voice_10", "name": "یەکەم ڤۆیس", "icon": "🎙️", "rarity": "common", "target": 10, "current": min(total_mins, 10), "desc": "١٠ خولەک ڤۆیس", "xp_reward": 50},
        {"id": "voice_500", "name": "پارتنەری ڤۆیس", "icon": "🔊", "rarity": "rare", "target": 500, "current": min(total_mins, 500), "desc": "٥٠٠ خولەک ڤۆیس", "xp_reward": 300},
        {"id": "voice_2000", "name": "ئەفسانەی ڤۆیس", "icon": "🎤", "rarity": "epic", "target": 2000, "current": min(total_mins, 2000), "desc": "٢٠٠٠ خولەک ڤۆیس", "xp_reward": 500},
        {"id": "voice_5000", "name": "پاشای ڤۆیس", "icon": "🎧", "rarity": "legendary", "target": 5000, "current": min(total_mins, 5000), "desc": "٥٠٠٠ خولەک ڤۆیس", "xp_reward": 1000},
        {"id": "level_5", "name": "ئاست ٥", "icon": "⭐", "rarity": "common", "target": 5, "current": min(level, 5), "desc": "گەیشتن بە ئاستی ٥", "xp_reward": 50},
        {"id": "level_10", "name": "ئاست ١٠", "icon": "💛", "rarity": "rare", "target": 10, "current": min(level, 10), "desc": "گەیشتن بە ئاستی ١٠", "xp_reward": 200},
        {"id": "level_20", "name": "ئاست ٢٠", "icon": "🔥", "rarity": "epic", "target": 20, "current": min(level, 20), "desc": "گەیشتن بە ئاستی ٢٠", "xp_reward": 500},
        {"id": "level_50", "name": "ئاست ٥٠", "icon": "💎", "rarity": "legendary", "target": 50, "current": min(level, 50), "desc": "گەیشتن بە ئاستی ٥٠", "xp_reward": 1500},
        {"id": "streak_7", "name": "هەفتەی بەردەوام", "icon": "📅", "rarity": "common", "target": 7, "current": min(streak, 7), "desc": "٧ ڕۆژ بەردەوام", "xp_reward": 100},
        {"id": "streak_30", "name": "مانگی بەردەوام", "icon": "🌙", "rarity": "rare", "target": 30, "current": min(streak, 30), "desc": "٣٠ ڕۆژ بەردەوام", "xp_reward": 500},
        {"id": "streak_100", "name": "١٠٠ ڕۆژ بەردەوام", "icon": "☀️", "rarity": "legendary", "target": 100, "current": min(streak, 100), "desc": "١٠٠ ڕۆژ بەردەوام", "xp_reward": 2000},
        {"id": "xp_1000", "name": "١٠٠٠ XP", "icon": "✨", "rarity": "common", "target": 1000, "current": min(xp, 1000), "desc": "١٠٠٠ XP کۆبکەرەوە", "xp_reward": 100},
        {"id": "xp_10000", "name": "١٠٠٠٠ XP", "icon": "🌟", "rarity": "epic", "target": 10000, "current": min(xp, 10000), "desc": "١٠٠٠٠ XP کۆبکەرەوە", "xp_reward": 1000},
    ]
    
    for a in achievements:
        a['percent'] = round((a['current'] / a['target']) * 100, 1)
        a['unlocked'] = a['current'] >= a['target']
    
    return achievements


def get_notifications(user_id):
    if not user_id:
        return []
    
    notifications = []
    user = get_user_stats(user_id)
    if not user:
        return []
    
    day_ads = user.get('day_ads', 0) or 0
    day_mins = user.get('day_mins', 0) or 0
    streak = user.get('daily_streak', 0) or 0
    xp = user.get('xp', 0) or 0
    level = user.get('level', 1) or 1
    
    if day_ads < 3:
        notifications.append({"type": "warning", "icon": "📢", "message": f"{3 - day_ads} ڕیکلامت ماوە بۆ تەواوکردنی مەرجی ئەمڕۆ", "time": "ئێستا"})
    else:
        notifications.append({"type": "success", "icon": "✅", "message": "ڕیکلامی ئەمڕۆت تەواو کرد!", "time": "ئێستا"})
    
    if day_mins < 120:
        remaining = 120 - day_mins
        notifications.append({"type": "info", "icon": "🎙️", "message": f"{remaining // 60} سەعات و {remaining % 60} خولەکت ماوە بۆ ڤۆیس", "time": "ئێستا"})
    else:
        notifications.append({"type": "success", "icon": "✅", "message": "ڤۆیسی ئەمڕۆت تەواو کرد!", "time": "ئێستا"})
    
    if streak > 0:
        if streak >= 7:
            notifications.append({"type": "success", "icon": "🔥", "message": f"Streak: {streak} ڕۆژ! زۆر باشە!", "time": "ئێستا"})
        else:
            notifications.append({"type": "info", "icon": "🔥", "message": f"Streak: {streak} ڕۆژ - {7 - streak} ڕۆژ ماوە بۆ دەستکەوتی هەفتەی بەردەوام", "time": "ئێستا"})
    
    xp_in_level = xp % 1000
    remaining_xp = 1000 - xp_in_level
    notifications.append({"type": "info", "icon": "⭐", "message": f"{remaining_xp} XP ماوە بۆ ئاستی {level + 1}", "time": "ئێستا"})
    
    return notifications


def get_daily_challenge(user_id):
    user = get_user_stats(user_id)
    if not user:
        return []
    
    day_ads = user.get('day_ads', 0) or 0
    day_mins = user.get('day_mins', 0) or 0
    
    challenges = [
        {"id": "ads_5", "name": "٥ ڕیکلام لە ڕۆژێکدا", "icon": "📢", "target": 5, "current": day_ads, "xp_reward": 200, "desc": "٥ ڕیکلام بکە لە یەک ڕۆژدا"},
        {"id": "voice_180", "name": "٣ سەعات ڤۆیس", "icon": "🎙️", "target": 180, "current": day_mins, "xp_reward": 300, "desc": "٣ سەعات ڤۆیس بکە لە یەک ڕۆژدا"},
        {"id": "both_perfect", "name": "ڕۆژی تەواو", "icon": "🏆", "target": 1, "current": 1 if (day_ads >= 3 and day_mins >= 120) else 0, "xp_reward": 500, "desc": "ڕیکلام و ڤۆیس هەردووکیان تەواو بکە"},
    ]
    
    for c in challenges:
        c['percent'] = min(round((c['current'] / c['target']) * 100, 1), 100)
        c['completed'] = c['current'] >= c['target']
    
    return challenges


# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        if not user_id.isdigit():
            return render_template('login.html', error="ID دەبێت تەنها ژمارە بێت!")
        user = get_user_stats(int(user_id))
        if user is None:
            return render_template('login.html', error="ئەم IDـە لە داتابەیسدا نەدۆزرایەوە!")
        session['user_id'] = int(user_id)
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = get_user_stats(user_id)

    if user is None:
        session.clear()
        return redirect(url_for('login'))

    day_ads = user.get('day_ads', 0) or 0
    day_mins = user.get('day_mins', 0) or 0
    week_ads = user.get('week_ads', 0) or 0
    week_mins = user.get('week_mins', 0) or 0
    month_ads = user.get('month_ads', 0) or 0
    month_mins = user.get('month_mins', 0) or 0
    all_ads = user.get('all_ads', 0) or 0
    all_mins = user.get('all_mins', 0) or 0
    xp = user.get('xp', 0) or 0
    level = user.get('level', 1) or 1
    streak = user.get('daily_streak', 0) or 0

    ads_percent = min((day_ads / 3) * 100, 100) if day_ads else 0
    voice_percent = min((day_mins / 120) * 100, 100) if day_mins else 0
    xp_in_level = xp % 1000
    level_percent = (xp_in_level / 1000) * 100

    goals = {
        "daily_ads": {"current": day_ads, "target": 3, "percent": min(day_ads / 3 * 100, 100)},
        "daily_voice": {"current": day_mins, "target": 120, "percent": min(day_mins / 120 * 100, 100)},
        "weekly_ads": {"current": week_ads, "target": 21, "percent": min(week_ads / 21 * 100, 100)},
        "weekly_voice": {"current": week_mins, "target": 840, "percent": min(week_mins / 840 * 100, 100)},
        "monthly_ads": {"current": month_ads, "target": 90, "percent": min(month_ads / 90 * 100, 100)},
        "monthly_voice": {"current": month_mins, "target": 3600, "percent": min(month_mins / 3600 * 100, 100)},
    }

    rank = get_rank(user_id)
    leaderboard = get_leaderboard(10)
    average = get_average_stats()

    comparison = {
        "ads": round(((all_ads - average['avg_ads']) / max(average['avg_ads'], 1)) * 100, 1),
        "voice": round(((all_mins - average['avg_mins']) / max(average['avg_mins'], 1)) * 100, 1),
        "xp": round(((xp - average['avg_xp']) / max(average['avg_xp'], 1)) * 100, 1),
    }

    achievements = get_achievements_progress(user)
    unlocked_count = sum(1 for a in achievements if a['unlocked'])

    # چالاکی
    activity = []
    today = datetime.now()
    for i in range(30):
        date = today - timedelta(days=29 - i)
        if i == 29:
            lvl = min(int((day_ads / 3 + day_mins / 120) * 2), 4)
        else:
            lvl = random.choice([0, 0, 1, 1, 2, 2, 3, 4])
        activity.append({"date": date.strftime("%Y-%m-%d"), "day": date.day, "month": date.month, "level": lvl})

    calendar_data = get_calendar_data(user_id)
    notifications = get_notifications(user_id)
    challenges = get_daily_challenge(user_id)
    is_admin = user_id in ADMIN_IDS

    analytics = {
        "best_day": "شەممە",
        "best_week": "هەفتەی ٣",
        "avg_per_day": round(all_ads / max(30, 1), 1),
        "trend": "up"
    }

    avatar_url = f"https://cdn.discordapp.com/embed/avatars/{(user_id >> 22) % 6}.png"

    if level >= 50:
        frame = "legend"; title = "👑 ئەفسانە"
    elif level >= 20:
        frame = "diamond"; title = "💎 ئەلماس"
    elif level >= 10:
        frame = "gold"; title = "🥇 زێڕین"
    elif level >= 5:
        frame = "silver"; title = "🥈 زیوین"
    else:
        frame = "bronze"; title = "🥉 بڕۆنزی"

    chart_data = {
        "ads": {"labels": ["ئەمڕۆ", "هەفتە", "مانگ", "گشتی"], "values": [day_ads, week_ads, month_ads, all_ads]},
        "voice": {"labels": ["ئەمڕۆ", "هەفتە", "مانگ", "گشتی"], "values": [round(day_mins/60,1), round(week_mins/60,1), round(month_mins/60,1), round(all_mins/60,1)]},
        "radar": {
            "labels": ["ڕیکلام", "ڤۆیس", "XP", "Streak", "چالاکی"],
            "values": [min(day_ads/3*100,100), min(day_mins/120*100,100), min(xp_in_level,100), min(streak/30*100,100), min((week_ads + week_mins/60)/10*100,100)]
        },
    }

    return render_template(
        'panel.html',
        user_id=user['user_id'],
        user_tag=f"User#{user['user_id']}",
        avatar_url=avatar_url,
        xp=xp, level=level, streak=streak, rank=rank,
        all_ads=all_ads, all_mins=all_mins,
        day_ads=day_ads, day_mins=day_mins,
        week_ads=week_ads, week_mins=week_mins,
        month_ads=month_ads, month_mins=month_mins,
        ads_percent=ads_percent, voice_percent=voice_percent,
        level_percent=level_percent,
        xp_in_level=xp_in_level, xp_for_next=1000,
        chart_data=chart_data, leaderboard=leaderboard,
        activity=activity, achievements=achievements,
        unlocked_count=unlocked_count, total_achievements=len(achievements),
        goals=goals, comparison=comparison, average=average,
        analytics=analytics, frame=frame, title=title,
        calendar_data=calendar_data, notifications=notifications,
        challenges=challenges, is_admin=is_admin,
    )


# ============================================
# ADMIN ROUTES
# ============================================

@app.route('/admin')
def admin_panel():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session['user_id'] not in ADMIN_IDS:
        return redirect(url_for('dashboard'))
    
    all_partners = get_all_partners()
    total_xp = sum(p.get('xp', 0) or 0 for p in all_partners)
    total_ads = sum(p.get('all_ads', 0) or 0 for p in all_partners)
    total_mins = sum(p.get('all_mins', 0) or 0 for p in all_partners)
    total_levels = sum(p.get('level', 1) or 1 for p in all_partners)
    avg_level = round(total_levels / max(len(all_partners), 1), 1)
    
    stats = {
        "total_partners": len(all_partners),
        "total_xp": total_xp,
        "total_ads": total_ads,
        "total_mins": total_mins,
        "active_today": sum(1 for p in all_partners if (p.get('day_ads', 0) or 0) >= 3 and (p.get('day_mins', 0) or 0) >= 120),
        "avg_level": avg_level,
    }
    
    return render_template('admin.html',
                          all_partners=all_partners,
                          stats=stats,
                          admin_ids=ADMIN_IDS)


@app.route('/admin/update', methods=['POST'])
def admin_update():
    if 'user_id' not in session or session['user_id'] not in ADMIN_IDS:
        return jsonify({"error": "unauthorized"}), 401
    
    data = request.get_json()
    target_user = data.get('user_id')
    
    if not target_user:
        return jsonify({"error": "no user_id"}), 400
    
    fields = ['xp', 'level', 'all_ads', 'all_mins', 
              'day_ads', 'day_mins', 'week_ads', 'week_mins',
              'month_ads', 'month_mins', 'daily_streak']
    
    update_data = {}
    for field in fields:
        if field in data and data[field] is not None:
            update_data[field] = int(data[field])
    
    if not update_data:
        return jsonify({"error": "no fields to update"}), 400
    
    if update_user(target_user, update_data):
        return jsonify({"success": True})
    return jsonify({"error": "failed"}), 500


@app.route('/admin/add_xp', methods=['POST'])
def admin_add_xp():
    if 'user_id' not in session or session['user_id'] not in ADMIN_IDS:
        return jsonify({"error": "unauthorized"}), 401
    
    data = request.get_json()
    target_user = data.get('user_id')
    amount = int(data.get('amount', 0))
    
    user = get_user_stats(target_user)
    if not user:
        return jsonify({"error": "user not found"}), 404
    
    new_xp = max(0, (user.get('xp', 0) or 0) + amount)
    
    if update_user_xp(target_user, new_xp):
        return jsonify({"success": True, "new_xp": new_xp})
    return jsonify({"error": "failed"}), 500


@app.route('/admin/delete_user', methods=['POST'])
def admin_delete_user():
    if 'user_id' not in session or session['user_id'] not in ADMIN_IDS:
        return jsonify({"error": "unauthorized"}), 401
    
    data = request.get_json()
    target_user = data.get('user_id')
    
    if delete_user(target_user):
        return jsonify({"success": True})
    return jsonify({"error": "failed"}), 500


@app.route('/admin/reset_user', methods=['POST'])
def admin_reset_user():
    if 'user_id' not in session or session['user_id'] not in ADMIN_IDS:
        return jsonify({"error": "unauthorized"}), 401
    
    data = request.get_json()
    target_user = data.get('user_id')
    
    reset_data = {
        'xp': 0, 'level': 1, 'all_ads': 0, 'all_mins': 0,
        'day_ads': 0, 'day_mins': 0, 'week_ads': 0, 'week_mins': 0,
        'month_ads': 0, 'month_mins': 0, 'daily_streak': 0
    }
    
    if update_user(target_user, reset_data):
        return jsonify({"success": True})
    return jsonify({"error": "failed"}), 500


@app.route('/admin/send_notification', methods=['POST'])
def admin_send_notification():
    if 'user_id' not in session or session['user_id'] not in ADMIN_IDS:
        return jsonify({"error": "unauthorized"}), 401
    
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({"error": "no message"}), 400
    
    if send_notification(message, session['user_id']):
        return jsonify({"success": True})
    return jsonify({"error": "failed"}), 500


@app.route('/admin/give_all_xp', methods=['POST'])
def admin_give_all_xp():
    if 'user_id' not in session or session['user_id'] not in ADMIN_IDS:
        return jsonify({"error": "unauthorized"}), 401
    
    data = request.get_json()
    amount = int(data.get('amount', 0))
    
    if amount == 0:
        return jsonify({"error": "amount is 0"}), 400
    
    try:
        all_partners = get_all_partners()
        for p in all_partners:
            new_xp = max(0, (p.get('xp', 0) or 0) + amount)
            update_user_xp(p['user_id'], new_xp)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# EXPORT ROUTES
# ============================================

@app.route('/export/json')
def export_json():
    if 'user_id' not in session or session['user_id'] not in ADMIN_IDS:
        return jsonify({"error": "unauthorized"}), 401
    
    all_partners = get_all_partners()
    
    export_data = {
        "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "exported_by": session['user_id'],
        "total_partners": len(all_partners),
        "partners": all_partners
    }
    
    response = app.response_class(
        response=json.dumps(export_data, ensure_ascii=False, indent=2),
        status=200,
        mimetype='application/json'
    )
    response.headers["Content-Disposition"] = f"attachment; filename=backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return response


@app.route('/export/csv')
def export_csv():
    if 'user_id' not in session or session['user_id'] not in ADMIN_IDS:
        return jsonify({"error": "unauthorized"}), 401
    
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['User ID', 'ئاست', 'XP', 'ڕیکلامی گشتی', 'ڤۆیسی گشتی', 
                     'ڕیکلامی ئەمڕۆ', 'ڤۆیسی ئەمڕۆ', 'Streak'])
    
    all_partners = get_all_partners()
    for p in all_partners:
        writer.writerow([
            p.get('user_id', ''),
            p.get('level', 1),
            p.get('xp', 0),
            p.get('all_ads', 0),
            p.get('all_mins', 0),
            p.get('day_ads', 0),
            p.get('day_mins', 0),
            p.get('daily_streak', 0),
        ])
    
    response = app.response_class(
        response='\ufeff' + output.getvalue(),
        status=200,
        mimetype='text/csv; charset=utf-8'
    )
    response.headers["Content-Disposition"] = f"attachment; filename=stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return response


@app.route('/export/pdf')
def export_pdf():
    if 'user_id' not in session or session['user_id'] not in ADMIN_IDS:
        return redirect(url_for('dashboard'))
    
    all_partners = get_all_partners()
    total_xp = sum(p.get('xp', 0) or 0 for p in all_partners)
    total_ads = sum(p.get('all_ads', 0) or 0 for p in all_partners)
    total_mins = sum(p.get('all_mins', 0) or 0 for p in all_partners)
    
    stats = {
        "total_partners": len(all_partners),
        "total_xp": total_xp,
        "total_ads": total_ads,
        "total_mins": total_mins,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    return render_template('pdf_report.html', partners=all_partners, stats=stats)


# ============================================
# MY DATA
# ============================================

@app.route('/my-data')
def my_data():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_stats(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    return render_template('my_data.html', user=user, user_id=session['user_id'])


@app.route('/export/my-json')
def export_my_json():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_stats(session['user_id'])
    if not user:
        return jsonify({"error": "not found"}), 404
    
    export_data = {
        "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user['user_id'],
        "stats": user,
    }
    
    response = app.response_class(
        response=json.dumps(export_data, ensure_ascii=False, indent=2),
        status=200,
        mimetype='application/json'
    )
    response.headers["Content-Disposition"] = f"attachment; filename=my_data_{user['user_id']}.json"
    return response


@app.route('/export/my-csv')
def export_my_csv():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_stats(session['user_id'])
    if not user:
        return jsonify({"error": "not found"}), 404
    
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['خانە', 'بەها'])
    writer.writerow(['User ID', user.get('user_id', '')])
    writer.writerow(['ئاست', user.get('level', 1)])
    writer.writerow(['XP', user.get('xp', 0)])
    writer.writerow(['ڕیکلامی گشتی', user.get('all_ads', 0)])
    writer.writerow(['ڤۆیسی گشتی', user.get('all_mins', 0)])
    writer.writerow(['ڕیکلامی ئەمڕۆ', user.get('day_ads', 0)])
    writer.writerow(['ڤۆیسی ئەمڕۆ', user.get('day_mins', 0)])
    writer.writerow(['Streak', user.get('daily_streak', 0)])
    
    response = app.response_class(
        response='\ufeff' + output.getvalue(),
        status=200,
        mimetype='text/csv; charset=utf-8'
    )
    response.headers["Content-Disposition"] = f"attachment; filename=my_data_{user['user_id']}.csv"
    return response


@app.route('/export/my-pdf')
def export_my_pdf():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_stats(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    return render_template('my_pdf.html',
                          user=user,
                          generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# ============================================
# API
# ============================================

@app.route('/api/notifications')
def api_notifications():
    if 'user_id' not in session:
        return jsonify([])
    return jsonify(get_notifications(session['user_id']))


@app.route('/api/live-stats')
def api_live_stats():
    if 'user_id' not in session:
        return jsonify({"error": "unauthorized"}), 401
    
    user = get_user_stats(session['user_id'])
    if not user:
        return jsonify({"error": "not found"}), 404
    
    return jsonify({
        "xp": user.get('xp', 0) or 0,
        "level": user.get('level', 1) or 1,
        "day_ads": user.get('day_ads', 0) or 0,
        "day_mins": user.get('day_mins', 0) or 0,
        "rank": get_rank(session['user_id']),
        "streak": user.get('daily_streak', 0) or 0,
    })


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/health')
def health():
    return {"status": "ok"}


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)