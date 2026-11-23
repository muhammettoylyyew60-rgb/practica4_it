import secrets
import string

from store import load_json, log_action, read_csv, today, write_csv

TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d",
    "е": "e", "ё": "e", "ж": "zh", "з": "z", "и": "i",
    "й": "y", "к": "k", "л": "l", "м": "m", "н": "n",
    "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
    "у": "u", "ф": "f", "х": "kh", "ц": "ts", "ч": "ch",
    "ш": "sh", "щ": "shch", "ъ": "", "ы": "y", "ь": "",
    "э": "e", "ю": "yu", "я": "ya",
    "ә": "a", "ғ": "g", "қ": "k", "ң": "n", "ө": "o",
    "ұ": "u", "ү": "u", "һ": "h", "і": "i",
}

COMMON_PASSWORDS = {
    "password", "qwerty", "123456", "12345678", "admin",
    "welcome", "p@ssw0rd", "qwerty123", "iloveyou", "1q2w3e4r",
}


def translit(text):
    result = []
    for char in text.lower():
        if char in TRANSLIT:
            result.append(TRANSLIT[char])
        elif char in string.ascii_lowercase + string.digits:
            result.append(char)
    return "".join(result)


def make_login(fullname, existing):
    surname, name = fullname.split()[:2]
    base = f"{translit(name[0])}.{translit(surname)}"
    login = base
    suffix = 2

    while login in existing:
        login = f"{base}{suffix}"
        suffix += 1

    return login


def new_hires(employees, accounts):
    assigned = {account["emp_id"] for account in accounts}
    return [
        employee
        for employee in employees
        if employee["status"] == "active"
        and employee["emp_id"] not in assigned
    ]