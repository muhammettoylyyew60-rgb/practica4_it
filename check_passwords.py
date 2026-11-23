from iam import check_password, generate_password
from store import load_json


if __name__ == "__main__":
    policy = load_json("config.json")["password_policy"]
    passwords = [generate_password(policy) for _ in range(1000)]
    invalid_count = sum(
        bool(check_password(password, "x.test", policy))
        for password in passwords
    )

    print(f"Политика варианта: {policy}")
    print(f"Пример пароля: {passwords[0]}")
    print(f"Паролей с нарушениями: {invalid_count} из {len(passwords)}")