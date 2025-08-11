import json
from datetime import datetime
import os
from colorama import init, Fore, Style
import sys
from projects.CASINO.bj import main as main_game
from projects.CASINO.arm import main_arm
from projects.CASINO.num import main_num

init(autoreset=True)

DATA_FILE = "data.json"


class CasinoUser:
    def __init__(self, username, data):
        self.username = username
        self.data = data
        self.player_data = data[username]

    @property
    def money(self):
        return self.player_data['money']

    @money.setter
    def money(self, value):
        self.player_data['money'] = value

    @property
    def debt(self):
        return self.player_data['debt']

    @debt.setter
    def debt(self, value):
        self.player_data['debt'] = value

    def update_stats(self, result, amount, bet):
        self.player_data['games_played'] += 1
        if result == "win":
            self.player_data['games_won'] += 1
            if bet > self.player_data['max_win']:
                self.player_data['max_win'] = bet

        self.player_data['history'].append({
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'result': "Победа" if result == "win" else "Поражение" if result == "lose" else "Ничья",
            'amount': amount,
            'bet': bet
        })
        save_data(self.data)


def load_data():
    """Загружает данные из JSON файла"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding='utf-8') as f:
                return json.load(f)
        return {}
    except (json.JSONDecodeError, IOError) as e:
        print(Fore.RED + f"Ошибка загрузки данных: {e}")
        return {}


def save_data(data):
    """Сохраняет данные в JSON файл"""
    try:
        with open(DATA_FILE, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(Fore.RED + f"Ошибка сохранения данных: {e}")


def register():
    """Регистрация нового пользователя"""
    data = load_data()
    print(Fore.CYAN + "\nРегистрация нового игрока")

    while True:
        username = input(Fore.GREEN + "Введите логин (или 'quit' для выхода): " + Style.RESET_ALL).strip()
        if username.lower() == 'quit':
            sys.exit()
        if not username:
            print(Fore.RED + "Логин не может быть пустым!")
            continue
        if username in data:
            print(Fore.RED + "Этот логин уже занят!")
            continue
        break

    while True:
        password = input(Fore.GREEN + "Введите пароль: " + Style.RESET_ALL).strip()
        if not password:
            print(Fore.RED + "Пароль не может быть пустым!")
            continue
        break

    data[username] = {
        'password': password,
        'money': 5000,
        'games_played': 0,
        'games_won': 0,
        'max_win': 0,
        'debt': 0,
        'history': []
    }

    save_data(data)
    print(Fore.GREEN + f"\nИгрок {username} успешно зарегистрирован! Начальный баланс: $5,000")
    return CasinoUser(username, data)


def login():
    """Авторизация пользователя"""
    data = load_data()
    print(Fore.CYAN + "\nАвторизация")

    attempts = 3
    while attempts > 0:
        username = input(Fore.GREEN + "Логин (или 'quit' для выхода): " + Style.RESET_ALL).strip()
        if username.lower() == 'quit':
            sys.exit()

        password = input(Fore.GREEN + "Пароль: " + Style.RESET_ALL).strip()

        if username in data and data[username]['password'] == password:
            print(Fore.GREEN + f"\nДобро пожаловать, {username}!")
            return CasinoUser(username, data)
        else:
            attempts -= 1
            print(Fore.RED + f"\nНеверный логин или пароль! Осталось попыток: {attempts}")

    print(Fore.RED + "\nСлишком много неудачных попыток. Попробуйте позже.")
    sys.exit()


def show_stats(user):
    """Отображение статистики игрока"""
    print(Fore.CYAN + "\nВаша статистика:")
    print(f"Баланс: ${user.money:,}")
    print(f"Сыграно игр: {user.player_data['games_played']}")
    print(f"Выиграно игр: {user.player_data['games_won']}")
    win_rate = (user.player_data['games_won'] / user.player_data['games_played'] * 100) if user.player_data[
                                                                                               'games_played'] > 0 else 0
    print(f"Процент побед: {win_rate:.1f}%")
    print(f"Максимальный выигрыш: ${user.player_data['max_win']:,}")
    print(f"Текущий долг: ${user.debt:,.2f}")

    if user.player_data['history']:
        print(Fore.YELLOW + "\nПоследние 5 игр:")
        for game in user.player_data['history'][-5:]:
            result_color = Fore.GREEN if game['amount'] > 0 else Fore.RED if game['amount'] < 0 else Fore.YELLOW
            print(f"{game['date']}: {result_color}{game['result']} (${game['amount']:,}){Style.RESET_ALL}")

    input(Fore.WHITE + "\nНажмите Enter чтобы продолжить...")


def take_loan(user):
    """Функция взятия кредита"""
    if user.debt > 0:
        print(Fore.RED + "\nУ вас уже есть непогашенный долг!")
        return

    max_loan = min(10000, user.money * 2)
    if max_loan < 1000:
        max_loan = 1000

    print(Fore.CYAN + f"\nВы можете взять кредит до ${max_loan:,}")
    print(Fore.RED + "Внимание! Кредит нужно будет вернуть с 10% комиссией!")

    while True:
        amount = input(Fore.GREEN + f"Сколько взять? (1-{max_loan:,} или 0 для отмены): " + Style.RESET_ALL).strip()
        if not amount.isdigit():
            continue

        amount = int(amount)
        if amount == 0:
            return
        if 1 <= amount <= max_loan:
            user.money += amount
            user.debt = amount * 1.1  # 10% комиссия
            save_data(user.data)
            print(Fore.GREEN + f"\nВы взяли кредит ${amount:,}. Теперь ваш долг: ${user.debt:,.2f}")
            return


def repay_loan(user):
    """Функция погашения долга"""
    if user.debt <= 0:
        print(Fore.GREEN + "\nУ вас нет долгов!")
        return

    print(Fore.CYAN + f"\nВаш текущий долг: ${user.debt:,.2f}")
    print(Fore.CYAN + f"Ваш текущий баланс: ${user.money:,}")

    if user.money < user.debt:
        print(Fore.RED + "\nУ вас недостаточно средств для погашения долга!")
        return

    while True:
        print("\n1. Погасить полностью")
        print("2. Погасить частично")
        print("3. Отмена")
        choice = input(Fore.GREEN + "> " + Style.RESET_ALL).strip()

        if choice == '1':
            user.money -= user.debt
            user.debt = 0
            save_data(user.data)
            print(Fore.GREEN + "\nВы полностью погасили свой долг!")
            break
        elif choice == '2':
            while True:
                amount = input(
                    Fore.GREEN + f"Сколько погасить? (1-{min(user.money, user.debt):,.2f}): " + Style.RESET_ALL).strip()
                try:
                    amount = float(amount)
                    if 1 <= amount <= min(user.money, user.debt):
                        user.money -= amount
                        user.debt -= amount
                        save_data(user.data)
                        print(Fore.GREEN + f"\nВы погасили ${amount:,.2f}. Остаток долга: ${user.debt:,.2f}")
                        break
                except ValueError:
                    continue
            break
        elif choice == '3':
            print(Fore.YELLOW + "\nПогашение долга отменено.")
            break


def main_menu(user):
    """Главное меню игры"""
    while True:
        print(Fore.MAGENTA + f"\nДобро пожаловать, {user.username}!")
        print(Fore.CYAN + f"Баланс: ${user.money:,}")
        if user.debt > 0:
            print(Fore.RED + f"Долг: ${user.debt:,.2f}")

        print(Fore.CYAN + "\n1. Играть в Blackjack")
        print(Fore.CYAN + "2. Играть в ONE-ARM BANDIT")
        print(Fore.CYAN + "3. Играть в NUMBERS")
        print("4. Статистика")
        print("5. Взять кредит")
        print("6. Погасить долг")
        print("7. Выйти")

        choice = input(Fore.GREEN + "> " + Style.RESET_ALL).strip()

        if choice == '1':
            main_game(user)
        if choice == '2':
            main_arm(user)
        if choice == '3':
            main_num(user)
        elif choice == '4':
            show_stats(user)
        elif choice == '5':
            take_loan(user)
        elif choice == '6':
            repay_loan(user)
        elif choice == '7':
            print(Fore.YELLOW + "\nСпасибо за игру!")
            sys.exit()


def main():
    """Точка входа в программу"""
    print(Fore.CYAN + "=== КАЗИНО ===")
    print(Fore.YELLOW + "Добро пожаловать!")

    data = load_data()
    if not data:
        print(Fore.CYAN + "\nНет зарегистрированных пользователей")
        user = register()
    else:
        print(Fore.CYAN + "\n1. Войти")
        print("2. Зарегистрироваться")
        print("3. Выйти")
        choice = input(Fore.GREEN + "> " + Style.RESET_ALL).strip()

        if choice == '1':
            user = login()
        elif choice == '2':
            user = register()
        else:
            sys.exit()

    main_menu(user)


if __name__ == "__main__":
    main()