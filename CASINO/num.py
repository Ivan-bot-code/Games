import random
from colorama import Fore, Style


class NumbersGame:
    def __init__(self, user):
        self.user = user
        self.bet = 0
        self.game_result = None
        self.attempts_left = 0
        self.secret_number = 0
        self.used_attempts = 0

    def start_game(self):
        """Основной метод запуска игры"""
        print(Fore.CYAN + "\n=== УГАДАЙ ЧИСЛО ===")
        print(Fore.YELLOW + "Правила:")
        print("- Я загадываю число от 1 до 100")
        print("- У вас есть 7 попыток, чтобы угадать его")
        print("- За победу вы получаете $50")

        self._place_bet()
        self._prepare_game()
        self._play_game()
        self._finish_game()

    def _place_bet(self):
        """Обработка ставки игрока (в этой игре фиксированная награда)"""
        print(Fore.MAGENTA + f"\nВаш баланс: ${self.user.money:,}")
        print(Fore.CYAN + "Для начала игры введите START или QUIT для выхода:")

        while True:
            choice = input(Fore.GREEN + "> " + Style.RESET_ALL).upper().strip()
            if choice == 'QUIT':
                print(Fore.YELLOW + "\nВозвращаемся в меню...")
                raise ExitToMenu
            elif choice == 'START':
                break

    def _prepare_game(self):
        """Подготовка игры"""
        self.secret_number = random.randint(1, 100)
        self.attempts_left = 7
        self.used_attempts = 0
        print(Fore.CYAN + "\nЯ загадал число от 1 до 100")
        print(Fore.RED + f"У вас есть {self.attempts_left} попыток!")

    def _play_game(self):
        """Основной игровой процесс"""
        while self.attempts_left > 0:
            try:
                guess = int(input(Fore.GREEN + "Ваша догадка: " + Style.RESET_ALL))
                self.attempts_left -= 1
                self.used_attempts += 1

                if guess == self.secret_number:
                    self.game_result = ('win', 50)
                    print(Fore.LIGHTCYAN_EX +
                          f"\nПоздравляю! Вы угадали число {self.secret_number}!")
                    print(f"Вы использовали {self.used_attempts} попыток.")
                    return
                elif guess < self.secret_number:
                    print(Fore.RED + f"Моё число больше {guess}")
                else:
                    print(Fore.RED + f"Моё число меньше {guess}")

                print(Fore.MAGENTA + f"Осталось попыток: {self.attempts_left}")

            except ValueError:
                print(Fore.RED + "Пожалуйста, вводите только целые числа!")

        # Если попытки закончились
        print(Fore.RED + f"\nВы проиграли! Я загадал число {self.secret_number}")

    def _finish_game(self):
        """Завершение игры и обновление статистики"""
        if self.game_result:
            result, amount = self.game_result
            self.user.money += amount
            self.user.update_stats(result, amount, 0)  # bet=0, так как ставки нет
        else:
            self.user.update_stats('lose', 0, 0)

        print(Fore.MAGENTA + f"\nВаш баланс: ${self.user.money:,}")



class ExitToMenu(Exception):
    """Исключение для возврата в меню"""
    pass


def main_num(user):
    """Точка входа в игру"""
    while True:
        try:
            game = NumbersGame(user)
            game.start_game()
        except ExitToMenu:
            break
        except Exception as e:
            print(Fore.RED + f"\nПроизошла ошибка: {e}")
            input(Fore.WHITE + "Нажмите Enter чтобы продолжить...")
            break