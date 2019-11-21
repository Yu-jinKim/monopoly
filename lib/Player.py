from collections import defaultdict

class Player:
    def __init__(self, name):
        self.name = name
        self.balance = 1500
        self.possessions = []
        self.group_possessions = defaultdict(lambda: 0)
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

    def add_possession(self, tile):
        self.balance -= tile.get_price()
        self.possessions.append(tile)
        self.group_possessions[tile.get_group()] += 1

    def remove_possession(self, tile):
        self.balance += tile.get_mortgage()
        self.possessions.remove(tile)
        self.group_possessions[tile.get_group()] -= 1

    def has_one_group(self):
        group2tiles = {}

        for prop in self.possessions:
            group = prop.get_group()

            if prop.get_number_in_group() == self.group_possessions[group]:
                group2tiles.setdefault(group, []).append(prop)

        return group2tiles

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