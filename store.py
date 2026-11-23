"""ПР. Чтение и запись данных из папки data/. Код не изменять."""

import csv
import json
from datetime import date, datetime

DATA = "data"
FMT = "%Y-%m-%d %H:%M"


def read_csv(name):
    with open(f"{DATA}/{name}", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(name, rows):
    """Перезаписывает файл, сохраняя его заголовок (порядок столбцов)."""
    with open(f"{DATA}/{name}", encoding="utf-8") as f:
        fields = next(csv.reader(f))
    with open(f"{DATA}/{name}", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def load_json(name):
    with open(f"{DATA}/{name}", encoding="utf-8") as f:
        return json.load(f)


def today():
    """«Сегодня» для всех расчётов - дата из config.json, а не date.today()."""
    return date.fromisoformat(load_json("config.json")["today"])


def log_action(action, target, details):
    """Добавляет строку в журнал действий администратора data/audit_log.csv."""
    with open(f"{DATA}/audit_log.csv", "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([datetime.now().strftime(FMT), action, target, details])


def read_control():
    """Контрольные значения из data/control.txt: {название: число}."""
    with open(f"{DATA}/control.txt", encoding="utf-8") as f:
        return {
            k: int(v) for k, v in (line.rsplit(": ", 1) for line in f if line.strip())
        }


def compare(results, after_fix=False):
    """Сравнивает {название: число} с контрольными значениями и печатает итог.
    after_fix=True - после исправлений (задание 6) все значения должны быть 0."""
    control = read_control()
    for name, value in results.items():
        expected = 0 if after_fix else control.get(name)
        mark = "OK" if value == expected else f"НЕ СОВПАДАЕТ (ожидается {expected})"
        print(f"{name}: {value}  -> {mark}")
