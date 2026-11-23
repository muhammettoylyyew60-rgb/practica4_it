"""ПР. Учётные записи: логины, пароли, ролевая модель."""

import csv
import secrets
import string

from store import load_json, log_action, read_csv, today, write_csv


TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "zh",
    "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
    "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "kh", "ц": "ts",
    "ч": "ch", "ш": "sh", "щ": "shch", "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu",
    "я": "ya", "ә": "a", "ғ": "g", "қ": "k", "ң": "n", "ө": "o", "ұ": "u", "ү": "u",
    "һ": "h", "і": "i",
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


def check_password(password, login, policy):
    violations = []
    if len(password) < policy["min_length"]:
        violations.append("LENGTH")

    classes = set()
    for char in password:
        if char.islower():
            classes.add("lower")
        elif char.isupper():
            classes.add("upper")
        elif char.isdigit():
            classes.add("digit")
        else:
            classes.add("other")

    if len(classes) < policy["min_classes"]:
        violations.append("CLASSES")

    surname = login.partition(".")[2].rstrip(string.digits).lower()
    if len(surname) >= 3 and surname in password.lower():
        violations.append("LOGIN")

    if password.lower() in COMMON_PASSWORDS:
        violations.append("COMMON")

    return violations


def generate_password(policy):
    alphabets = (
        string.ascii_lowercase,
        string.ascii_uppercase,
        string.digits,
        string.punctuation,
    )
    length = max(policy["min_length"], 12)
    characters = [secrets.choice(alphabet) for alphabet in alphabets]
    pool = "".join(alphabets)

    for _ in range(length - len(characters)):
        characters.append(secrets.choice(pool))

    secrets.SystemRandom().shuffle(characters)
    return "".join(characters)


def effective_permissions(position, roles):
    permissions = set()
    for role in roles["positions"].get(position, []):
        permissions.update(roles["roles"][role])
    return sorted(permissions)


def write_role_matrix(roles, path="role_matrix.csv"):
    permissions = sorted({
        permission
        for group in roles["roles"].values()
        for permission in group
    })

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["position", *permissions])

        for position in roles["positions"]:
            allowed = set(effective_permissions(position, roles))
            marks = ["+" if permission in allowed else "" for permission in permissions]
            writer.writerow([position, *marks])


def create_account(emp, accounts, grants, roles, policy):
    existing = {account["login"] for account in accounts}
    login = make_login(emp["fullname"], existing)
    password = generate_password(policy)

    accounts.append({
        "login": login,
        "emp_id": emp["emp_id"],
        "created": today().isoformat(),
        "last_login": "",
        "disabled_at": "",
    })

    for permission in effective_permissions(emp["position"], roles):
        grants.append({"login": login, "permission": permission})

    log_action("create", login, f"{emp['fullname']}, {emp['position']}")
    return login, password


if __name__ == "__main__":
    cfg, roles = load_json("config.json"), load_json("roles.json")
    employees, accounts, grants = (
        read_csv("hr.csv"),
        read_csv("accounts.csv"),
        read_csv("grants.csv"),
    )

    write_role_matrix(roles)
    for emp in new_hires(employees, accounts):
        login, pw = create_account(emp, accounts, grants, roles, cfg["password_policy"])
        print(f"{emp['emp_id']}  {emp['fullname']:<25} {login:<16} {pw}")

    write_csv("accounts.csv", accounts)
    write_csv("grants.csv", grants)