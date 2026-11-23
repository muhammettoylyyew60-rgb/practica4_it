import sys
from datetime import date

from iam import effective_permissions, new_hires
from store import compare, load_json, read_csv, today


def enabled(account):
    return account["disabled_at"] == ""


def active_accounts(employees, accounts):
    active = {e["emp_id"]: e for e in employees if e["status"] == "active"}
    return [
        (a, active[a["emp_id"]])
        for a in accounts
        if enabled(a) and a["emp_id"] in active
    ]


def fired_enabled(employees, accounts):
    fired = {e["emp_id"] for e in employees if e["status"] == "fired"}
    return [a["login"] for a in accounts if enabled(a) and a["emp_id"] in fired]


def orphans(employees, accounts):
    employee_ids = {employee["emp_id"] for employee in employees}
    return [
        account["login"]
        for account in accounts
        if enabled(account) and account["emp_id"] not in employee_ids
    ]


def inactive(employees, accounts, today_, days):
    return [
        account["login"]
        for account, _ in active_accounts(employees, accounts)
        if account["last_login"]
        and (today_ - date.fromisoformat(account["last_login"])).days > days
    ]


def excess_rights(employees, accounts, grants, roles):
    allowed = {
        account["login"]: set(effective_permissions(employee["position"], roles))
        for account, employee in active_accounts(employees, accounts)
    }
    return [
        (grant["login"], grant["permission"])
        for grant in grants
        if grant["login"] in allowed
        and grant["permission"] not in allowed[grant["login"]]
    ]


def sod_conflicts(employees, accounts, grants, roles):
    permissions = {}
    for grant in grants:
        permissions.setdefault(grant["login"], set()).add(grant["permission"])

    conflicts = []
    for account, _ in active_accounts(employees, accounts):
        login = account["login"]
        granted = permissions.get(login, set())
        for first, second in roles["sod_conflicts"]:
            if first in granted and second in granted:
                conflicts.append((login, first, second))

    return conflicts


def run_audit():
    cfg, roles = load_json("config.json"), load_json("roles.json")
    emp, acc, gr = read_csv("hr.csv"), read_csv("accounts.csv"), read_csv("grants.csv")
    days = cfg["inactive_days"]
    return {
        "Новые сотрудники без учётной записи": len(new_hires(emp, acc)),
        "Уволенные с активной учётной записью": len(fired_enabled(emp, acc)),
        "Учётные записи без сотрудника": len(orphans(emp, acc)),
        f"Неактивные более {days} дней": len(inactive(emp, acc, today(), days)),
        "Лишние права (пар логин-право)": len(excess_rights(emp, acc, gr, roles)),
        "Сотрудники с конфликтом SoD": len(
            {c[0] for c in sod_conflicts(emp, acc, gr, roles)}
        ),
    }


if __name__ == "__main__":
    compare(run_audit(), after_fix="--after-fix" in sys.argv)