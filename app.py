from datetime import datetime
from flask import Flask, render_template, request

app = Flask(__name__)

# 初期設定の時給
setting_money = 1000  

# 勤務記録を保存するリスト
records = []

# ホーム画面
@app.route("/")
def home():
    return render_template("index.html")


# 勤務の登録画面
@app.route("/register", methods=["GET", "POST"])
def register():
    work_hour = None
    money = None

    if request.method == "POST":
        # 入力されたデータの取得
        name = request.form["name"]
        date = request.form["date"]
        start = request.form["start"]
        end = request.form["end"]
        break_min = float(request.form["break"])

        # 分単位を時間単位に
        break_time = break_min / 60

        start_time = datetime.strptime(start, "%H:%M")
        end_time = datetime.strptime(end, "%H:%M")

        # 勤務時間の計算
        work_time = end_time - start_time
        work_hour = work_time.total_seconds() / 3600 - break_time

        # 勤務時間を少数以下２桁で表示
        work_hour_display = round(work_hour, 2)

        # 給料計算
        money = int(work_hour * setting_money)

        # リストにデータを保存
        records.append({
            "name": name,
            "date": date,
            "start": start,
            "end": end,
            "break": break_time,
            "work_hour": work_hour_display,
            "money": money
        })

    return render_template("register.html", work_hour=work_hour, money=money)


# 一覧表示
@app.route("/list")
def list():
    sort = request.args.get("sort")
    sorted_records = records.copy()

    # 並び替え
    if sort == "name_asc":
        sorted_records.sort(key=lambda r: r["name"])
    elif sort == "name_desc":
        sorted_records.sort(key=lambda r: r["name"], reverse=True)
    elif sort == "date_asc":
        sorted_records.sort(key=lambda r: r["date"])
    elif sort == "date_desc":
        sorted_records.sort(key=lambda r: r["date"], reverse=True)

    return render_template("list.html", records=sorted_records)


# 予算管理
@app.route("/management", methods=["GET", "POST"])
def management():
    start_day = None
    end_day = None
    budget = 0
    use = 0
    rest = 0

    if request.method == "POST":
        # 入力されたデータの取得
        start_day = request.form["start_day"]
        end_day = request.form["end_day"]
        budget = int(request.form["budget"])

        start_day2 = datetime.strptime(start_day, "%Y-%m-%d")
        end_day2 = datetime.strptime(end_day, "%Y-%m-%d")

        # 期間内のデータ抽出
        records_in_period = [
            r for r in records
            if start_day2 <= datetime.strptime(r["date"], "%Y-%m-%d") <= end_day2
        ]

        # 使用金額
        use = int(sum(r["money"] for r in records_in_period))

        # 残金
        rest = budget - use

    return render_template(
        "management.html",
        start_day=start_day,
        end_day=end_day,
        budget=budget,
        use=use,
        rest=rest
    )


# 時給設定
@app.route("/setting", methods=["GET", "POST"])
def setting():
    global setting_money

    if request.method == "POST":
        setting_money = float(request.form["money"])

    return render_template("setting.html", setting_money=setting_money)


if __name__ == "__main__":
    app.run(debug=True)