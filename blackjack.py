import random
import sys
from colorama import init, Fore, Back, Style
from tqdm import tqdm
import time
init(autoreset=True)


HEARTS = chr(9829)  # '♥'
DIAMONDS = chr(9830)  # '♦'
SPADES = chr(9824)  # '♠'
CLUBS = chr(9827)  # '♣'
BACKSIDE = 'backside'


def main():


    money = 5000
    games_played = 0

    with tqdm(total=5000, desc=Fore.CYAN + "Баланс" + Style.RESET_ALL) as pbar:
        while True:
            games_played += 1
            pbar.n = money
            pbar.refresh()

            if money <= 0:
                print(Fore.RED + "\nВы банкрот!")
                print(Fore.GREEN + "Хорошо, что вы не играли на реальные деньги!")
                print("Спасибо за игру!")
                sys.exit()

            print(Fore.MAGENTA + f"\nДеньги: ${money:,}")
            bet = get_bet(money)

            deck = get_deck()
            dealer_hand = [deck.pop(), deck.pop()]
            player_hand = [deck.pop(), deck.pop()]

            print(Fore.BLUE + f"\nСтавка: ${bet:,}")

            while True:
                display_hands(player_hand, dealer_hand, False)
                print()

                if get_hand_value(player_hand) > 21:
                    break

                move = get_move(player_hand, money - bet)

                if move == 'D':
                    additional_bet = get_bet(min(bet, (money - bet)))
                    bet += additional_bet
                    print(Fore.GREEN + f"Ставка увеличена до ${bet:,}")
                    print(Fore.BLUE + f"Текущая ставка: ${bet:,}")

                if move in ('H', 'D'):
                    new_card = deck.pop()
                    rank, suit = new_card
                    print(Fore.CYAN + f"Вы взяли {rank} {suit}")
                    player_hand.append(new_card)

                    if get_hand_value(player_hand) > 21:
                        continue

                if move in ('S', 'D'):
                    break

            if get_hand_value(player_hand) <= 21:
                while get_hand_value(dealer_hand) < 17:
                    print(Fore.YELLOW + "\nДилер берет карту...")
                    dealer_hand.append(deck.pop())
                    display_hands(player_hand, dealer_hand, False)

                    if get_hand_value(dealer_hand) > 21:
                        break

                    input(Fore.WHITE + "Нажмите Enter чтобы продолжить...")

            print("\n" + "=" * 50)
            display_hands(player_hand, dealer_hand, True)

            player_value = get_hand_value(player_hand)
            dealer_value = get_hand_value(dealer_hand)

            if dealer_value > 21:
                print(Fore.GREEN + f"\nДилер перебрал! Вы выиграли ${bet:,}!")
                money += bet
            elif player_value > 21 or player_value < dealer_value:
                print(Fore.RED + "\nВы проиграли!")
                money -= bet
            elif player_value > dealer_value:
                print(Fore.GREEN + f"\nВы выиграли ${bet:,}!")
                money += bet
            elif player_value == dealer_value:
                print(Fore.YELLOW + "\nНичья! Ставка возвращается вам.")

            print(Fore.MAGENTA + f"\nВаш баланс: ${money:,}")
            print(Fore.CYAN + f"Сыграно игр: {games_played}")

            input(Fore.WHITE + "\nНажмите Enter чтобы продолжить...")
            print("\n" * 3)


def get_bet(max_bet):
    """Получаем ставку от игрока"""
    while True:
        print(Fore.CYAN + f"\nСколько ставите? (1-{max_bet:,} или QUIT)")
        bet = input(Fore.GREEN + "> " + Style.RESET_ALL).upper().strip()

        if bet == 'QUIT':
            print(Fore.YELLOW + "\nСпасибо за игру!")
            sys.exit()

        if not bet.isdecimal():
            continue

        bet = int(bet)
        if 1 <= bet <= max_bet:
            return bet


def get_deck():
    deck = []
    for suit in (HEARTS, DIAMONDS, SPADES, CLUBS):
        for rank in range(2, 11):
            deck.append((str(rank), suit))
        for rank in ('J', 'Q', 'K', 'A'):
            deck.append((rank, suit))
    random.shuffle(deck)
    return deck


def display_hands(player_hand, dealer_hand, show_dealer_hand):
    print()
    if show_dealer_hand:
        print(Fore.BLUE + f"ДИЛЕР: {get_hand_value(dealer_hand)}")
        display_cards(dealer_hand)
    else:
        print(Fore.BLUE + "ДИЛЕР: ???")
        display_cards([BACKSIDE] + dealer_hand[1:])

    print(Fore.GREEN + f"ИГРОК: {get_hand_value(player_hand)}")
    display_cards(player_hand)


def get_hand_value(cards):
    value = 0
    aces = 0

    for card in cards:
        rank = card[0]
        if rank == 'A':
            aces += 1
        elif rank in ('K', 'Q', 'J'):
            value += 10
        else:
            value += int(rank)

    value += aces
    for _ in range(aces):
        if value + 10 <= 21:
            value += 10

    return value


def display_cards(cards):
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


def get_move(player_hand, money):
    while True:
        moves = ['(H)it', '(S)tand']

        if len(player_hand) == 2 and money > 0:
            moves.append('(D)ouble down')

        move_prompt = ', '.join(moves) + '> '
        move = input(Fore.CYAN + move_prompt + Style.RESET_ALL).upper()

        if move in ('H', 'S'):
            return move
        if move == 'D' and '(D)ouble down' in moves:
            return move


if __name__ == '__main__':
    main()