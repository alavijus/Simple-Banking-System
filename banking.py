from random import choice
import sqlite3


class BankSystem:

    def __init__(self):
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS card (
                id INTEGER,
                number TEXT,
                pin TEXT,
                balance INTEGER DEFAULT 0
            )""")
        self.conn.commit()
        self.main_menu()

    def main_menu(self):
        while True:
            print('\n1. Create and account')
            print('2. Log into account')
            print('0. Exit')
            selection = input()
            if selection == '1':
                self.create_acc()
            elif selection == '2':
                self.logging_menu()
            elif selection == '0':
                print("Bye!")
                exit()

    def create_acc(self):
        self.cur.execute("SELECT COUNT(*) FROM card")
        database_id = self.cur.fetchone()[0] + 1

        balance = 0

        iin = '400000'
        acc_id = ''
        for _ in range(9):
            digit = choice('0123456789')
            acc_id += digit
        checksum = self.create_checksum(iin + acc_id)
        card_no = iin + acc_id + checksum

        card_pin = ''
        for _ in range(4):
            digit = choice('0123456789')
            card_pin += digit

        self.cur.execute("INSERT INTO card VALUES (?, ?, ?, ?)", (database_id, card_no, card_pin, balance))
        self.conn.commit()
        print('\nYour card has been created')
        print(f'Your card number:\n{card_no}')
        print(f'Your card PIN:\n{card_pin}')

    @staticmethod
    def create_checksum(incomplete_no):
        original = list(incomplete_no)
        multiplied = []
        for i in range(0, 15):
            if i in range(0, 15, 2):
                new_value = int(original[i]) * 2
            else:
                new_value = int(original[i])
            multiplied.append(new_value)
        subtracted = []
        for i in range(0, 15):
            if multiplied[i] > 9:
                new_value = multiplied[i] - 9
            else:
                new_value = multiplied[i]
            subtracted.append(new_value)
        remainder = sum(subtracted) % 10
        if remainder == 0:
            return '0'
        else:
            return str(10 - remainder)

    def try_login(self, card, pin):
        self.cur.execute("SELECT number, pin FROM card WHERE number = ? AND pin = ?", (card, pin))
        return self.cur.fetchone()

    def logging_menu(self):
        card_input = input('Enter your card number:\n')
        pin_input = input('Enter your PIN:\n')
        if self.try_login(card_input, pin_input):
            print('\nYou have successfully logged in!')
            self.logged_menu(card_input)
        else:
            print('Wrong card number or PIN!')

    def get_balance(self, card):
        self.cur.execute("SELECT balance FROM card WHERE number = ?", (card,))
        return self.cur.fetchone()[0]

    def change_balance(self, card, amount):
        self.cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?", (amount, card))
        self.conn.commit()

    def do_transfer(self, card):
        print('Transfer')
        rec_card = input('Enter card number:\n')
        if rec_card == card:
            print("You can't transfer money to the same account!")
        elif rec_card[-1] != self.create_checksum(rec_card[:-1]):
            print("Probably you made a mistake in the card number. Please try again!")
        else:
            self.cur.execute("SELECT * FROM card WHERE number = ?", (rec_card,))
            if not self.cur.fetchone():
                print("Such a card does not exist.")
            else:
                money = int(input("Enter how much money you want to transfer:\n"))
                if money > self.get_balance(card):
                    print("Not enough money!")
                else:
                    self.change_balance(rec_card, money)
                    self.change_balance(card, -money)
                    print("Success!")

    def logged_menu(self, card):
        while True:
            print('\n1. Balance')
            print('2. Add income')
            print('3. Do transfer')
            print('4. Close account')
            print('5. Log out')
            print('0. Exit')
            selection = input()
            if selection == '1':
                print(f'Balance: {self.get_balance(card)}')
            elif selection == '2':
                amount = int(input('Enter income:\n'))
                self.change_balance(card, amount)
                print('Income was added!')
            elif selection == '3':
                self.do_transfer(card)
            elif selection == '4':
                self.cur.execute("DELETE FROM card WHERE number = ?", (card,))
                self.conn.commit()
                print("The account has been closed!")
                break
            elif selection == '5':
                print('You have successfully logged out!')
                break
            elif selection == '0':
                print("Bye!")
                exit()


new_login = BankSystem()
