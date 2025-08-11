import random
import time
from colorama import Fore, Back, Style, init

init(autoreset=True)

# Символы для слотов
SYMBOLS = {
    '7': Fore.RED + '🔴',
    'BAR': Fore.GREEN + '🍎',
    'BELL': Fore.YELLOW + '🔔',
    'DIAMOND': Fore.CYAN + '💎',
    'CHERRY': Fore.MAGENTA + '🍒',
    'LEMON': Fore.LIGHTYELLOW_EX + '🍋'
}


class OneArmBandit:
    def __init__(self, user):
        self.user = user
        self.bet = 0
        self.selected_symbol = None
        self.reels = []
        self.result_line = []
        self.game_result = None
        self.payouts = {
            '4_of_a_kind': 3,
            '4_selected': 4,
            '3_selected': 2
        }

    def start_game(self):
        """Основной метод запуска игры"""
        print(Fore.CYAN + "\n=== ONE-ARM BANDIT ===")
        self._show_rules()

        while True:
            try:
                if not self._place_bet():
                    return  # Возвращаемся в меню

                self._select_symbol()
                self._spin_reels()
                self._play_round()
                self._finish_game()

                if self.user.money <= 0:
                    print(Fore.RED + "\nУ вас закончились деньги!")
                    return

                choice = input(Fore.CYAN + "\nСыграть еще? (y/n): " + Style.RESET_ALL).lower()
                if choice != 'y':
                    return

            except KeyboardInterrupt:
                print(Fore.YELLOW + "\nВозвращаемся в меню...")
                return

    def _show_rules(self):
        """Показывает правила игры"""
        print(Fore.YELLOW + "\nПравила:")
        print("- Вы делаете ставку и выбираете фигуру")
        print(f"- 4 одинаковые фигуры в ряд: {Fore.GREEN}x{self.payouts['4_of_a_kind']} ставки")
        print(f"- 4 выбранные фигуры в ряд: {Fore.GREEN}x{self.payouts['4_selected']} ставки")
        print(f"- 3 выбранные фигуры (в любом порядке): {Fore.GREEN}x{self.payouts['3_selected']} ставки")
        print(Fore.RED + "- Во всех остальных случаях: проигрыш")
        print("\nДоступные символы:")
        for name, symbol in SYMBOLS.items():
            print(f"{symbol} - {name}")

    def _place_bet(self):
        """Обработка ставки игрока"""
        while True:
            print(Fore.MAGENTA + f"\nВаш баланс: ${self.user.money:,}")
            bet_input = input(Fore.CYAN + f"Введите ставку (1-{self.user.money}) или 0 для выхода: " + Style.RESET_ALL).strip()

            if bet_input == '0':
                print(Fore.YELLOW + "\nВозвращаемся в меню...")
                return False

            if not bet_input.isdigit():
                print(Fore.RED + "Пожалуйста, введите число!")
                continue

            bet = int(bet_input)
            if bet < 1:
                print(Fore.RED + "Ставка должна быть положительной!")
                continue
            if bet > self.user.money:
                print(Fore.RED + "Недостаточно средств!")
                continue

            self.bet = bet
            return True

    def _select_symbol(self):
        """Выбор символа для специальных выплат"""
        print(Fore.CYAN + "\nВыберите специальный символ:")
        symbols_list = list(SYMBOLS.items())

        for i, (name, symbol) in enumerate(symbols_list, 1):
            print(f"{i}. {symbol} {name}")

        while True:
            choice = input(Fore.GREEN + "> " + Style.RESET_ALL).strip()
            if not choice.isdigit():
                print(Fore.RED + "Пожалуйста, введите число!")
                continue

            choice_num = int(choice)
            if 1 <= choice_num <= len(symbols_list):
                self.selected_symbol = symbols_list[choice_num - 1][0]
                return
            print(Fore.RED + f"Введите число от 1 до {len(symbols_list)}")

    def _spin_reels(self):
        """Вращение барабанов с анимацией"""
        self.reels = []
        all_symbols = list(SYMBOLS.keys())

        # Генерируем финальные позиции барабанов
        final_reels = []
        for _ in range(4):
            reel = [random.choice(all_symbols) for _ in range(3)]
            final_reels.append(reel)

        # Анимация вращения
        print("\n" + "=" * 50)
        print(Fore.MAGENTA + "=== ВРАЩЕНИЕ ===")

        for spin in range(10):  # Количество шагов анимации
            temp_reels = []
            for i in range(4):
                # На последних шагах приближаемся к финальному результату
                reel = final_reels[i] if spin > 7 else [random.choice(all_symbols) for _ in range(3)]
                temp_reels.append(reel)

            # Отображаем анимацию
            for line in range(3):
                for reel in temp_reels:
                    symbol = reel[line]
                    color = Fore.YELLOW if symbol == self.selected_symbol else Fore.WHITE
                    print(color + SYMBOLS[symbol], end="  ")
                print()

            time.sleep(0.1)  # Задержка для анимации
            if spin < 9:
                print("\033[F" * 4)  # Возвращаем курсор вверх для следующего кадра

        self.reels = final_reels
        self.result_line = [reel[1] for reel in self.reels]  # Средняя линия для проверки

    def _play_round(self):
        """Проверка результатов и расчет выигрыша"""
        # Проверка на 4 одинаковых символа
        if all(s == self.result_line[0] for s in self.result_line):
            payout = self.bet * self.payouts['4_of_a_kind']
            self.game_result = ('win', payout)
        # Проверка на 4 выбранных символа
        elif self.selected_symbol and all(s == self.selected_symbol for s in self.result_line):
            payout = self.bet * self.payouts['4_selected']
            self.game_result = ('win', payout)
        # Проверка на 3 выбранных символа
        elif self.selected_symbol and self.result_line.count(self.selected_symbol) >= 3:
            payout = self.bet * self.payouts['3_selected']
            self.game_result = ('win', payout)
        else:
            self.game_result = ('lose', -self.bet)

    def _finish_game(self):
        """Отображение результатов и обновление статистики"""
        if self.game_result[0] == 'win':
            self._show_win_animation()
            print(Fore.GREEN + f"\nВы выиграли ${self.game_result[1]:,}!")
        else:
            print(Fore.RED + "\nВы проиграли эту ставку")

        # Обновление баланса и статистики
        self.user.money += self.game_result[1]
        self.user.update_stats(*self.game_result, self.bet)

        print(Fore.MAGENTA + f"\nВаш баланс: ${self.user.money:,}")
        input(Fore.WHITE + "\nНажмите Enter чтобы продолжить...")

    def _show_win_animation(self):
        """Праздничная анимация выигрыша"""
        print("\n" + "=" * 50)
        print(Back.YELLOW + Fore.BLACK + "=== ПОЗДРАВЛЯЕМ! ===")
        print(Style.RESET_ALL)

        # Анимация мигания
        for _ in range(3):
            print(Fore.YELLOW + Back.RED + "  CONGRATULATIONS!  " + Style.RESET_ALL)
            time.sleep(0.3)
            print(Fore.RED + Back.YELLOW + "  CONGRATULATIONS!  " + Style.RESET_ALL)
            time.sleep(0.3)

        # Отображение выигрышной комбинации
        print("\nВыигрышная комбинация:")
        for line in range(3):
            for reel in self.reels:
                symbol = reel[line]
                color = Fore.YELLOW if symbol == self.selected_symbol else Fore.WHITE
                print(color + SYMBOLS[symbol], end="  ")
            print()

        print("=" * 50)


def main_arm(user):
    """Точка входа в игру"""
    game = OneArmBandit(user)
    game.start_game()