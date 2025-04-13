import hashlib

def hash_password(password):
    """
    Хеширует пароль с использованием SHA-256
    """
    return hashlib.sha256(password.encode()).hexdigest()

# Проверяем хеш пароля "andrew009"
correct_password = "andrew009"
generated_hash = hash_password(correct_password)

# Текущий хеш в файле
current_hash = "cc31e42c5271ea456ac8644a3b8a1a0deb8c2eff21d5a70c7cc6b5bc12b23103"

print(f"Пароль: {correct_password}")
print(f"Сгенерированный хеш: {generated_hash}")
print(f"Текущий хеш в файле: {current_hash}")
print(f"Совпадают ли хеши: {generated_hash == current_hash}")