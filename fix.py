from audit import excess_rights, fired_enabled, inactive, orphans
from iam import create_account, new_hires
from store import load_json, log_action, read_csv, today, write_csv


def disable_account(accounts, login, reason):
    for a in accounts:
        if a["login"] == login and a["disabled_at"] == "":
            a["disabled_at"] = today().isoformat()
            log_action("disable", login, reason)
            return True
    return False


def revoke(grants, login, permission, reason):
    for index, grant in enumerate(grants):
        if grant["login"] == login and grant["permission"] == permission:
            del grants[index]
            log_action("revoke", login, f"{permission}: {reason}")
            return True
    return False


if __name__ == "__main__":
    cfg, roles = load_json("config.json"), load_json("roles.json")
    emp, acc, gr = read_csv("hr.csv"), read_csv("accounts.csv"), read_csv("grants.csv")
    for lg in fired_enabled(emp, acc):
        disable_account(acc, lg, "сотрудник уволен")
    for lg in orphans(emp, acc):
        disable_account(acc, lg, "нет сотрудника в hr.csv")
    for lg in inactive(emp, acc, today(), cfg["inactive_days"]):
        disable_account(acc, lg, f"нет входа более {cfg['inactive_days']} дней")
    for lg, perm in excess_rights(emp, acc, gr, roles):
        revoke(gr, lg, perm, "нет в ролевой модели")
    for e in new_hires(emp, acc):
        create_account(e, acc, gr, roles, cfg["password_policy"])
    write_csv("hr.csv", emp)
    write_csv("accounts.csv", acc)
    write_csv("grants.csv", gr)
    print("Исправления выполнены. Журнал действий: data/audit_log.csv")