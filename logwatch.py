from datetime import datetime, timedelta

from store import FMT, compare, load_json, read_csv


def bruteforce(log, attempts, minutes):
    failures = {}
    for entry in log:
        if entry["result"] == "fail":
            event_time = datetime.strptime(entry["time"], FMT)
            failures.setdefault(entry["ip"], []).append(event_time)

    limit = timedelta(minutes=minutes)
    detected = []
    for ip, times in failures.items():
        times.sort()
        for index in range(len(times) - attempts + 1):
            first = times[index]
            last = times[index + attempts - 1]
            if last - first <= limit:
                detected.append(ip)
                break

    return sorted(detected)


def off_hours(log, start, end):
    return [
        entry
        for entry in log
        if entry["result"] == "success"
        and not start <= datetime.strptime(entry["time"], FMT).hour < end
    ]


def disabled_logins(log, accounts):
    disabled = {
        account["login"]: datetime.fromisoformat(account["disabled_at"])
        for account in accounts
        if account["disabled_at"]
    }
    return [
        entry
        for entry in log
        if entry["result"] == "success"
        and entry["login"] in disabled
        and datetime.strptime(entry["time"], FMT) >= disabled[entry["login"]]
    ]


if __name__ == "__main__":
    cfg, log, acc = (
        load_json("config.json"),
        read_csv("auth_log.csv"),
        read_csv("accounts.csv"),
    )
    bf = cfg["bruteforce"]
    compare(
        {
            "IP-адреса с подбором пароля": len(
                bruteforce(log, bf["attempts"], bf["minutes"])
            ),
            "Входы в нерабочее время": len(off_hours(log, *cfg["work_hours"])),
            "Входы в отключённые учётные записи": len(disabled_logins(log, acc)),
        }
    )