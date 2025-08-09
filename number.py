import random
from colorama import init, Fore, Back, Style

def game():
    i = 7
    random_number = random.randint(1, 100)
    print(Fore.CYAN + "Я загадал число от 1 до 100")
    print(Fore.RED + f"Попробуй угадать его за {i} попыток!")

    while True:
        try:
            user_choice = int(input(Fore.GREEN + "Ваша догадка: "))
            i -= 1

            if user_choice > random_number:
                print(Fore.RED + f"Моё число меньше {user_choice}")
            elif user_choice < random_number:
                print(Fore.RED + f"Моё число больше {user_choice}")
            else:
                print(Fore.LIGHTCYAN_EX + f"Я загадал число {random_number}, вы выиграли!")
                print(f"Вы использовали {7 - i} попыток.")
                print(Fore.RESET + "Вы хотите сыграть снова?")
                user_input = input("Введите да или нет: ").lower()
                if user_input == "нет":
                    print(Fore.BLUE + "До свидания!")
                    return
                else:
                    game()
                    return

            print(Fore.MAGENTA + f"У тебя осталось {i} попыток.")

            if i == 0:
                print(f"Вы проиграли, я загадал число {random_number}")
                print("Вы хотите сыграть снова?")
                user_input = input("Введите да или нет: ").lower()
                if user_input == "нет":
                    print("До свидания!")
                    return
                else:
                    game()
                    return

        except ValueError:
            print("Пожалуйста, вводите только целые числа!")

game()