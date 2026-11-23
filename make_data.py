"""ПР. Генератор данных организации по номеру варианта. Код не изменять."""

import csv
import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path

# организация, отделы, сотрудников, пароль (длина, классов), неактивность (дней),
# подбор пароля (попыток, минут), рабочие часы (с, до)
VARIANTS = {
    1: ("Интернет-магазин", ["office", "warehouse", "it"], 30, 10, 3, 45, 5, 10, 9, 18),
    2: ("Поликлиника", ["reception", "doctors", "lab"], 34, 12, 3, 30, 4, 10, 8, 20),
    3: ("Школа", ["teachers", "admin", "it"], 30, 8, 2, 60, 6, 15, 8, 17),
    4: ("Банк (филиал)", ["operators", "credit", "it"], 38, 14, 4, 30, 3, 5, 9, 18),
    5: ("Университет", ["dekanat", "kafedra", "library"], 40, 10, 3, 90, 5, 15, 8, 19),
    6: ("Склад-логистика", ["sklad", "logistic", "buh"], 28, 10, 2, 45, 5, 10, 7, 19),
    7: ("Нотариальная контора", ["clients", "contracts", "office"], 28, 12, 3, 60, 4, 10, 9, 18),
    8: ("IT-компания", ["dev", "qa", "docs"], 36, 14, 4, 30, 5, 5, 10, 19),
    9: ("Лаборатория", ["reception", "lab", "doctors"], 30, 12, 3, 45, 3, 10, 8, 18),
    10: ("Сеть кафе", ["office", "shop1", "shop2"], 28, 8, 2, 90, 6, 20, 8, 22),
    11: ("Строительная компания", ["buh", "kadry", "pto"], 32, 10, 3, 60, 5, 15, 8, 17),
    12: ("Колл-центр", ["sales", "support", "it"], 40, 10, 3, 30, 4, 5, 8, 20),
    13: ("Колледж", ["teachers", "students", "admin"], 30, 8, 3, 90, 6, 15, 8, 17),
    14: ("Сеть аптек", ["pharmacy1", "pharmacy2", "office"], 28, 10, 3, 45, 5, 10, 8, 21),
    15: ("Типография", ["design", "print", "buh"], 28, 12, 3, 60, 4, 15, 9, 18),
    16: ("Гостиница", ["reception", "rooms", "restaurant"], 30, 10, 2, 45, 5, 10, 7, 23),
    17: ("Страховая компания", ["insurance", "claims", "buh"], 34, 14, 4, 30, 3, 10, 9, 18),
    18: ("Автопарк", ["garage", "drivers", "office"], 28, 8, 2, 90, 6, 20, 7, 19),
    19: ("Телеканал", ["editors", "video", "archive"], 36, 12, 4, 45, 4, 5, 9, 21),
    20: ("Акимат района", ["priem", "docs", "it"], 32, 12, 3, 60, 5, 15, 9, 18),
}

ROLES = {
    "roles": {
        "employee": ["mail.use", "portal.read"],
        "finance": ["payment.create", "report.finance.read", "accounting.edit"],
        "finance_approver": ["payment.approve", "report.finance.read"],
        "hr": ["hr.read", "hr.edit"],
        "sales": ["crm.read", "crm.edit"],
        "it_admin": ["server.login", "backup.run", "ad.admin"],
        "management": ["report.all.read", "payment.approve", "hr.read"],
    },
    "positions": {
        "director": ["employee", "management"],
        "chief_accountant": ["employee", "finance_approver"],
        "accountant": ["employee", "finance"],
        "hr_specialist": ["employee", "hr"],
        "manager": ["employee", "sales"],
        "it_admin": ["employee", "it_admin"],
        "specialist": ["employee"],
    },
    "sod_conflicts": [
        ["payment.create", "payment.approve"],
        ["hr.edit", "payment.create"],
        ["ad.admin", "hr.edit"],
    ],
}

# фамилия (кириллица, латиница) и имена (кириллица, латиница первой буквы)
SURNAMES = [
    ("Сериков", "serikov"),
    ("Ахметов", "akhmetov"),
    ("Ибраев", "ibraev"),
    ("Касымов", "kasymov"),
    ("Петров", "petrov"),
    ("Смагулов", "smagulov"),
    ("Жунусов", "zhunusov"),
    ("Оспанов", "ospanov"),
    ("Тулегенов", "tulegenov"),
    ("Иванов", "ivanov"),
    ("Бекенов", "bekenov"),
    ("Абдрахманов", "abdrakhmanov"),
    ("Нуржанов", "nurzhanov"),
    ("Сейткалиев", "seytkaliev"),
    ("Каримов", "karimov"),
    ("Есенов", "esenov"),
    ("Мусин", "musin"),
    ("Ильин", "ilin"),
]
MALE = [
    ("Алмаз", "a"),
    ("Арман", "a"),
    ("Бауыржан", "b"),
    ("Берик", "b"),
    ("Данияр", "d"),
    ("Ерлан", "e"),
    ("Нурлан", "n"),
    ("Марат", "m"),
    ("Максим", "m"),
    ("Руслан", "r"),
    ("Сергей", "s"),
    ("Тимур", "t"),
]
FEMALE = [
    ("Айгерим", "a"),
    ("Алия", "a"),
    ("Дана", "d"),
    ("Динара", "d"),
    ("Жанна", "zh"),
    ("Мадина", "m"),
    ("Мария", "m"),
    ("Сауле", "s"),
    ("Светлана", "s"),
    ("Гульнара", "g"),
]
NEW_HIRES = [
    "Шәріпов Нұрсұлтан",
    "Щербакова Юлия",
    "Өтегенова Әсел",
    "Қуанышев Ғалым",
    "Жұмабаев Ілияс",
    "Иманғали Аңсар",
    "Ильясова Яна",
    "Үмбетов Һадис",
]

POS_WEIGHTS = [
    ("specialist", 6),
    ("manager", 5),
    ("accountant", 4),
    ("chief_accountant", 1),
    ("hr_specialist", 2),
    ("it_admin", 2),
    ("director", 1),
]
FMT = "%Y-%m-%d %H:%M"


def perms_for(position):
    return sorted({p for r in ROLES["positions"][position] for p in ROLES["roles"][r]})


def main():
    v = int(input("Номер варианта (1-20): "))
    org, depts, n_emp, pw_len, pw_cls, inactive, bf_n, bf_min, h_from, h_to = VARIANTS[v]
    rnd = random.Random(v * 7919)
    today = date.today()
    out = Path("data")
    out.mkdir(exist_ok=True)

    config = {
        "variant": v,
        "org": org,
        "departments": depts,
        "today": today.isoformat(),
        "password_policy": {"min_length": pw_len, "min_classes": pw_cls},
        "inactive_days": inactive,
        "bruteforce": {"attempts": bf_n, "minutes": bf_min},
        "work_hours": [h_from, h_to],
    }

    # ---------- сотрудники с учётными записями ----------
    employees, accounts, grants, used = [], [], [], set()
    positions = [p for p, w in POS_WEIGHTS for _ in range(w)]
    for i in range(n_emp):
        sur, sur_lat = rnd.choice(SURNAMES)
        female = rnd.random() < 0.45
        name, init = rnd.choice(FEMALE if female else MALE)
        if female:
            sur, sur_lat = sur + "а", sur_lat + "a"
        login, k = f"{init}.{sur_lat}", 2
        while login in used:
            login, k = f"{init}.{sur_lat}{k}", k + 1
        used.add(login)
        pos = "director" if i == 0 else rnd.choice(positions)
        hired = today - timedelta(days=rnd.randint(200, 2500))
        employees.append(
            {
                "emp_id": f"E{1001 + i}",
                "fullname": f"{sur} {name}",
                "department": rnd.choice(depts),
                "position": pos,
                "status": "active",
                "hire_date": hired.isoformat(),
                "fire_date": "",
            }
        )
        accounts.append(
            {
                "login": login,
                "emp_id": f"E{1001 + i}",
                "created": hired.isoformat(),
                "last_login": (today - timedelta(days=rnd.randint(0, 20))).isoformat(),
                "disabled_at": "",
            }
        )
    by_login = {a["login"]: a for a in accounts}
    emp_of = {e["emp_id"]: e for e in employees}
    pool = [a["login"] for a in accounts[1:]]
    rnd.shuffle(pool)

    def take(cond=lambda e: True):
        for i, lg in enumerate(pool):
            if cond(emp_of[by_login[lg]["emp_id"]]):
                return pool.pop(i)
        raise RuntimeError("недостаточно сотрудников")

    ctrl = {}
    # уволенные корректно (учётная запись отключена)
    for _ in range(4):
        a = by_login[take()]
        fired = today - timedelta(days=rnd.randint(25, 200))
        emp_of[a["emp_id"]].update(status="fired", fire_date=fired.isoformat())
        a.update(
            last_login=(fired - timedelta(days=1)).isoformat(), disabled_at=fired.isoformat()
        )
    disabled_ok = [a for a in accounts if a["disabled_at"]]
    # 1. уволенные, но учётная запись активна
    ctrl["fired_enabled"] = rnd.randint(2, 4)
    for _ in range(ctrl["fired_enabled"]):
        a = by_login[take()]
        fired = today - timedelta(days=rnd.randint(5, 120))
        emp_of[a["emp_id"]].update(status="fired", fire_date=fired.isoformat())
        a["last_login"] = (fired - timedelta(days=1)).isoformat()
    # 3. неактивные (+ одна запись ровно на границе, она нарушением не считается)
    ctrl["inactive"] = rnd.randint(2, 4)
    for _ in range(ctrl["inactive"]):
        by_login[take()]["last_login"] = (
            today - timedelta(days=inactive + rnd.randint(1, 60))
        ).isoformat()
    by_login[take()]["last_login"] = (today - timedelta(days=inactive)).isoformat()

    # права: ровно по ролевой модели
    for a in accounts:
        for p in perms_for(emp_of[a["emp_id"]]["position"]):
            grants.append({"login": a["login"], "permission": p})
    # 5. конфликты SoD (это тоже лишние права)
    ctrl["sod"] = rnd.randint(1, 3)
    for _ in range(ctrl["sod"]):
        lg = take(lambda e: e["position"] in ("accountant", "manager", "specialist"))
        pos = emp_of[by_login[lg]["emp_id"]]["position"]
        extra = (
            ["payment.approve"] if pos == "accountant" else ["payment.create", "payment.approve"]
        )
        grants += [{"login": lg, "permission": p} for p in extra]
    sod_excess = sum(1 for g in grants) - sum(
        len(perms_for(emp_of[a["emp_id"]]["position"])) for a in accounts
    )
    # 4. прочие лишние права
    others = rnd.randint(2, 4)
    for _ in range(others):
        lg = take(lambda e: e["position"] in ("specialist", "manager"))
        grants.append(
            {
                "login": lg,
                "permission": rnd.choice(["report.all.read", "backup.run", "server.login"]),
            }
        )
    ctrl["excess"] = sod_excess + others

    # 2. учётные записи без сотрудника
    orphans = rnd.sample(
        ["test", "temp_admin", "olduser", "guest1", "scanner"], rnd.randint(2, 3)
    )
    ctrl["orphans"] = len(orphans)
    for lg in orphans:
        accounts.append(
            {
                "login": lg,
                "emp_id": "",
                "created": (today - timedelta(days=rnd.randint(100, 900))).isoformat(),
                "last_login": (today - timedelta(days=rnd.randint(0, 10))).isoformat(),
                "disabled_at": "",
            }
        )
        grants.append({"login": lg, "permission": "server.login"})

    # 6. новые сотрудники без учётной записи (один - с совпадающим логином)
    hires = rnd.sample(NEW_HIRES, rnd.randint(2, 3))
    twins = {n: m for n, i in MALE for m, j in MALE if i == j and n != m}
    base = next(
        e for e in employees if e["status"] == "active" and e["fullname"].split()[1] in twins
    )
    sur, twin = base["fullname"].split()[0], twins[base["fullname"].split()[1]]
    hires.append(f"{sur} {twin}")
    ctrl["new_hires"] = len(hires)
    for i, fio in enumerate(hires):
        employees.append(
            {
                "emp_id": f"E{2001 + i}",
                "fullname": fio,
                "department": rnd.choice(depts),
                "position": rnd.choice(["specialist", "manager", "accountant"]),
                "status": "active",
                "hire_date": (today - timedelta(days=rnd.randint(0, 6))).isoformat(),
                "fire_date": "",
            }
        )

    # ---------- журнал входов за 30 дней ----------
    log = []
    start = today - timedelta(days=30)

    def at(day, hour, minute):
        return datetime.combine(start + timedelta(days=day), datetime.min.time()) + timedelta(
            hours=hour, minutes=minute
        )

    active = [
        a
        for a in accounts
        if not a["disabled_at"] and a["emp_id"] and emp_of[a["emp_id"]]["status"] == "active"
    ]
    for n, a in enumerate(active):
        ip = f"10.0.{n // 200}.{n % 200 + 10}"
        for day in rnd.sample(range(30), rnd.randint(8, 15)):
            t = at(day, rnd.randint(h_from, h_to - 1), rnd.randint(1, 58))
            if rnd.random() < 0.1:
                log.append((t - timedelta(minutes=1), a["login"], ip, "fail"))
            log.append((t, a["login"], ip, "success"))
    # 7. подбор пароля
    ctrl["bruteforce_ips"] = rnd.randint(1, 3)
    for k in range(ctrl["bruteforce_ips"]):
        ip, t = (
            f"185.220.{rnd.randint(1, 250)}.{rnd.randint(1, 250)}",
            at(rnd.randint(0, 29), rnd.randint(0, 23), 0),
        )
        step = (bf_min * 60 - 1) // (bf_n - 1)  # секунд между попытками
        for j in range(bf_n + rnd.randint(0, 4)):
            log.append(
                (
                    t + timedelta(seconds=step * (j % bf_n) + j),
                    rnd.choice(["admin", "root", active[0]["login"]]),
                    ip,
                    "fail",
                )
            )
    slow_ip, t = ("45.155.205.233", at(rnd.randint(0, 20), 2, 0))  # медленный перебор: не подбор
    for j in range(bf_n):
        log.append((t + timedelta(minutes=(bf_min + 1) * j), "admin", slow_ip, "fail"))
    # 8. вход в нерабочее время
    ctrl["off_hours"] = rnd.randint(2, 4)
    off = [h for h in range(24) if not h_from <= h < h_to]
    for _ in range(ctrl["off_hours"]):
        a = rnd.choice(active)
        log.append(
            (
                at(rnd.randint(0, 29), rnd.choice(off), rnd.randint(0, 59)),
                a["login"],
                "10.0.9.9",
                "success",
            )
        )
    # 9. вход в отключённую учётную запись
    ctrl["disabled_logins"] = rnd.randint(1, 2)
    for a in rnd.sample(disabled_ok, ctrl["disabled_logins"]):
        d0 = max(date.fromisoformat(a["disabled_at"]) + timedelta(days=1), start)
        day = (d0 - start).days + rnd.randint(0, (today - d0).days - 1)
        log.append(
            (
                at(day, rnd.randint(h_from, h_to - 1), rnd.randint(0, 59)),
                a["login"],
                "91.203.4.17",
                "success",
            )
        )
    log.sort()

    # ---------- запись файлов ----------
    def write(name, rows, fields):
        with open(out / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    write(
        "hr.csv",
        employees,
        ["emp_id", "fullname", "department", "position", "status", "hire_date", "fire_date"],
    )
    write("accounts.csv", accounts, ["login", "emp_id", "created", "last_login", "disabled_at"])
    write("grants.csv", grants, ["login", "permission"])
    write(
        "auth_log.csv",
        [dict(zip(["time", "login", "ip", "result"], (t.strftime(FMT), *r))) for t, *r in log],
        ["time", "login", "ip", "result"],
    )
    (out / "roles.json").write_text(
        json.dumps(ROLES, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (out / "config.json").write_text(
        json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write("audit_log.csv", [], ["time", "action", "target", "details"])

    labels = {
        "new_hires": "Новые сотрудники без учётной записи",
        "fired_enabled": "Уволенные с активной учётной записью",
        "orphans": "Учётные записи без сотрудника",
        "inactive": f"Неактивные более {inactive} дней",
        "excess": "Лишние права (пар логин-право)",
        "sod": "Сотрудники с конфликтом SoD",
        "bruteforce_ips": "IP-адреса с подбором пароля",
        "off_hours": "Входы в нерабочее время",
        "disabled_logins": "Входы в отключённые учётные записи",
    }
    text = "\n".join(f"{labels[k]}: {ctrl[k]}" for k in labels)
    (out / "control.txt").write_text(text + "\n", encoding="utf-8")
    print(f"Вариант {v}: {org}. Данные созданы в папке data/")
    print("\nКонтрольные значения (ваша программа должна получить ровно их):")
    print(text)


if __name__ == "__main__":
    main()
