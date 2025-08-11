import random
from colorama import Fore, Style
from datetime import datetime

# Символы карт
HEARTS = chr(9829)  # '♥'
DIAMONDS = chr(9830)  # '♦'
SPADES = chr(9824)  # '♠'
CLUBS = chr(9827)  # '♣'
BACKSIDE = 'backside'


class BlackjackGame:
    def __init__(self, user):
        self.user = user
        self.deck = []
        self.player_hand = []
        self.dealer_hand = []
        self.bet = 0
        self.game_result = None

    def start_game(self):
        """Основной метод запуска игры"""
        print(Fore.CYAN + "\n=== BLACKJACK ===")
        print(Fore.YELLOW + "Правила:")
        print("- Дилер останавливается на 17")
        print("- Даблдаун доступен только при первых двух картах")
        print("- Блекджек выплачивается 3:2")

        self._place_bet()
        self._prepare_deck()
        self._deal_initial_cards()
        self._player_turn()

        if self._check_player_bust():
            return self._finish_game()

        self._dealer_turn()
        self._finish_game()

    def _place_bet(self):
        """Обработка ставки игрока"""
        while True:
            print(Fore.MAGENTA + f"\nВаш баланс: ${self.user.money:,}")
            print(Fore.CYAN + f"Введите ставку (1-{self.user.money} или QUIT):")
            bet_input = input(Fore.GREEN + "> " + Style.RESET_ALL).upper().strip()

            if bet_input == 'QUIT':
                print(Fore.YELLOW + "\nВозвращаемся в меню...")
                raise ExitToMenu

            if not bet_input.isdigit():
                continue

            bet = int(bet_input)
            if 1 <= bet <= self.user.money:
                self.bet = bet
                break

    def _prepare_deck(self):
        """Создает и перемешивает колоду"""
        self.deck = []
        for suit in (HEARTS, DIAMONDS, SPADES, CLUBS):
            for rank in range(2, 11):
                self.deck.append((str(rank), suit))
            for rank in ('J', 'Q', 'K', 'A'):
                self.deck.append((rank, suit))
        random.shuffle(self.deck)

    def _deal_initial_cards(self):
        """Раздает начальные карты"""
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]
        print(Fore.BLUE + f"\nСтавка: ${self.bet:,}")
        self._display_hands(show_dealer_card=False)

    def _player_turn(self):
        """Ход игрока"""
        while True:
            player_value = self._calculate_hand_value(self.player_hand)

            print(Fore.CYAN + "\nВаши действия:")
            moves = ['(H)it', '(S)tand']

            # Проверка возможности даблдауна
            if len(self.player_hand) == 2 and self.user.money >= self.bet:
                moves.append('(D)ouble down')

            move = self._get_player_move(", ".join(moves))

            if move == 'D':  # Даблдаун
                self.bet *= 2
                print(Fore.GREEN + f"Ставка удвоена до ${self.bet:,}")
                self._hit_player()
                break
            elif move == 'H':  # Хит
                self._hit_player()
                if self._calculate_hand_value(self.player_hand) > 21:
                    break
            else:  # Стенд
                break

    def _hit_player(self):
        """Игрок берет карту"""
        new_card = self.deck.pop()
        self.player_hand.append(new_card)
        print(Fore.CYAN + f"\nВы взяли {new_card[0]} {new_card[1]}")
        self._display_hands(show_dealer_card=False)

    def _get_player_move(self, prompt):
        """Получает действие игрока с проверкой"""
        while True:
            move = input(Fore.GREEN + prompt + "> " + Style.RESET_ALL).upper()
            if move in ('H', 'S', 'D'):
                return move
            print(Fore.RED + "Некорректный ввод. Попробуйте еще.")

    def _check_player_bust(self):
        """Проверяет, не перебрал ли игрок"""
        if self._calculate_hand_value(self.player_hand) > 21:
            self._display_hands(show_dealer_card=True)
            print(Fore.RED + "\nВы перебрали! Проигрыш.")
            self.game_result = ('lose', -self.bet)
            return True
        return False

    def _dealer_turn(self):
        """Ход дилера"""
        print(Fore.YELLOW + "\nХод дилера...")
        self._display_hands(show_dealer_card=True)

        while self._calculate_hand_value(self.dealer_hand) < 17:
            input(Fore.WHITE + "Нажмите Enter чтобы продолжить...")
            new_card = self.deck.pop()
            self.dealer_hand.append(new_card)
            print(Fore.YELLOW + f"\nДилер берет {new_card[0]} {new_card[1]}")
            self._display_hands(show_dealer_card=True)

    def _finish_game(self):
        """Определяет результат игры и обновляет баланс"""
        player_value = self._calculate_hand_value(self.player_hand)
        dealer_value = self._calculate_hand_value(self.dealer_hand)

        # Если результат еще не определен (не было перебора)
        if not self.game_result:
            if dealer_value > 21:
                print(Fore.GREEN + "\nДилер перебрал! Вы выиграли!")
                self.game_result = ('win', self.bet)
            elif player_value > dealer_value:
                print(Fore.GREEN + "\nВы выиграли!")
                self.game_result = ('win', self.bet)
            elif player_value < dealer_value:
                print(Fore.RED + "\nВы проиграли!")
                self.game_result = ('lose', -self.bet)
            else:
                print(Fore.YELLOW + "\nНичья! Ставка возвращается.")
                self.game_result = ('draw', 0)

        # Проверка на блекджек (3:2 выплата)
        if (len(self.player_hand) == 2 and
                player_value == 21 and
                self.game_result[0] == 'win'):
            payout = int(self.bet * 1.5)
            print(Fore.GREEN + f"\nБлекджек! Выигрыш ${payout:,}!")
            self.game_result = ('win', payout)

        # Обновление баланса и статистики
        self.user.money += self.game_result[1]
        self.user.update_stats(*self.game_result, self.bet)

        print(Fore.MAGENTA + f"\nВаш баланс: ${self.user.money:,}")
        input(Fore.WHITE + "\nНажмите Enter чтобы продолжить...")

    def _calculate_hand_value(self, hand):
        """Вычисляет значение руки"""
        value = 0
        aces = 0

        for card in hand:
            rank = card[0]
            if rank == 'A':
                aces += 1
                value += 11
            elif rank in ('K', 'Q', 'J'):
                value += 10
            else:
                value += int(rank)

        # Корректировка для тузов
        while value > 21 and aces:
            value -= 10
            aces -= 1

        return value

    def _display_hands(self, show_dealer_card):
        """Отображает карты игрока и дилера"""
        print("\n" + "=" * 50)
        print(Fore.BLUE + "Дилер:" if show_dealer_card else "Дилер: ???")
        self._display_cards(self.dealer_hand if show_dealer_card else [BACKSIDE] + self.dealer_hand[1:])

        print(Fore.GREEN + f"\nИгрок ({self._calculate_hand_value(self.player_hand)}):")
        self._display_cards(self.player_hand)
        print("=" * 50 + "\n")

    def _display_cards(self, cards):
        """Отображает карты в графическом виде"""
        rows = ['', '', '', '', '']

        for card in cards:
            rows[0] += ' ___  '

            if card == BACKSIDE:
                rows[1] += '|## | '
                rows[2] += '|###| '
                rows[3] += '|_##| '
            else:
                rank, suit = card
                rows[1] += f'|{rank.ljust(2)} | '
                rows[2] += f'| {suit} | '
                rows[3] += f'|_{rank.rjust(2, "_")}| '

        for row in rows:
            print(Fore.WHITE + row)


class ExitToMenu(Exception):
    """Исключение для возврата в меню"""
    pass


def main(user):
    """Точка входа в игру"""
    while True:
        try:
            game = BlackjackGame(user)
            game.start_game()
        except ExitToMenu:
            break
        except Exception as e:
            print(Fore.RED + f"\nПроизошла ошибка: {e}")
            input(Fore.WHITE + "Нажмите Enter чтобы продолжить...")
            break