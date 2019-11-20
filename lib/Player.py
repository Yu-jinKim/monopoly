class Player:
    def __init__(self, name):
        self.name = name
        self.balance = 1500
        self.possessions = []
        self.jail_status = 0

    def __str__(self):
        return self.name

    def get_name(self):
        return self.name

    def get_balance(self):
        return self.balance

    def get_possessions(self):
        return self.possessions

    def in_jail(self):
        return self.jail_status

    def add_possession(self, land, amount):
        self.balance -= amount
        self.possessions.append(land)

    def remove_possession(self, land, amount):
        self.balance += amount
        self.possessions.remove(land)

    def pay(self, amount):
        self.balance -= amount
        return self.balance

    def receive(self, amount):
        self.balance += amount
        return self.balance

    def go_to_jail(self):
        self.jail_status = 3

    def out_of_jail(self):
        self.jail_status = 0

    def pass_turn(self):
        self.jail_status -= 1


def main():
    pass

if __name__ == "__main__":
    main()