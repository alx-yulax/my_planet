import random
import datetime

class Calendar:
    def __init__(self):
        self.today = datetime.datetime(2029, 1, 1)

    def addDay(self):
        self.today += datetime.timedelta(days=1)

    def __str__(self):
        return self.today.strftime("%c")


class Shop:
    def __init__(self):
        self.products = []
        self.order_products()

    def order_products(self):
        # name, calories, health, price
        self.products.append(['Eggplant', 2.5, 1, 25])
        self.products.append(['Squid', 7.7, 3, 77])
        self.products.append(['Potato', 8.7, 4, 87])
        self.products.append(['Olives', 51.9, 25, 519])
        self.products.append(['Garlic', 11, 5, 110])
        self.products.append(['Prunes', 26.4, 13, 264])
        self.products.append(['Shrimps', 9.7, 4, 97])
        self.products.append(['Water', 0.1, 0.1, 1])

    def get_available_products(self, money):
        products = []
        for product in self.products:
            if product[3] <= money:
                products.append(product)
        return products

    def buy_products(self, resident):
        # money, energy, health
        for count in range(1, 50):
            basket = self.get_available_products(resident.money)
            if len(basket) > 1:
                if len(basket) == 2:
                    product = basket[0]
                else:
                    product = basket[random.randint(0, len(basket) - 2)]

                money = product[3]
                health = product[2]
                energy = product[1]
                name = product[0]

                resident.add_money(-money)
                resident.add_health(health + energy)

            elif len(basket) == 1:
                product = basket[0]
                name = product[0]

                money = product[3]
                health = product[2]
                energy = product[1]

                resident.add_money(-money)
                resident.add_health(health + energy)
            else:
                break

            if resident.money < 1 or resident.energy >= 100:
                break


class Planet:
    def __init__(self, name, calendar):
        self.name = name
        self.spaceships = []
        self.residents = []
        self.calendar = calendar
        self.shop = Shop()

    def spaceship_arrival(self, spaceship):
        self.spaceships.append(spaceship)

        while spaceship.passengers:
            self.add_resident(spaceship.passengers.pop())

    def spaceship_departure(self, spaceship):
        self.spaceships.remove(spaceship)

    def add_resident(self, resident):
        self.residents.append(resident)

    def remove_resident(self, resident):
        self.residents.remove(resident)

    def get_spaceship(self):
        return self.spaceships.pop()

    def go_to_shop(self, resident):
        self.shop.buy_products(resident=resident)

    # marriage
    def find_pair(self, resident):
        candidates = []
        if isinstance(resident, Man):
            for human in self.residents:
                if isinstance(human, Woman) and human.get_age(self.calendar.today) >= 18 \
                        and human.pair is None and human.energy > 30:
                    candidates.append(human)
        elif isinstance(resident, Woman):
            for human in self.residents:
                if isinstance(human, Man) and human.get_age(self.calendar.today) >= 18 \
                        and human.pair is None and human.energy > 30:
                    candidates.append(human)

        count_candidates = len(candidates)
        if count_candidates == 0:
            return None
        else:
            return random.choice(candidates)

    def marriage(self, resident):
        candidate = self.find_pair(resident)
        if candidate is None:
            print('Sorry no candidates available.')
        else:
            resident.pair = candidate
            candidate.pair = resident

            resident.add_health(-80)
            candidate.add_health(-80)
            print('Congratulations! {} and {} you got married'.format(resident.name, candidate.name))

    def day(self):
        print('----------------------------------{}----------------------------------'.format(self.calendar))
        # action residents
        zombies = []
        for resident in self.residents:
            print('')
            resident.act(planet=self)
            if resident.dead:
                zombies.append(resident)

        for zombi in zombies:
            self.residents.remove(zombi)

        self.calendar.addDay()


class Human:
    def __init__(self, birthday):
        self.birthday = birthday
        self.health = 100
        self.energy = 100
        self.money = 500
        self.pair = None
        self.children = []
        self.dead = False

    def add_child(self, child):
        self.children.append(child)

    def add_money(self, money):
        self.money += money

    def add_health(self, health):
        if health < 0:
            self.energy += health
            if self.energy < 0:
                self.health += self.energy
                self.energy = 0
        elif health > 0:
            self.health += health

        if self.health > 100:
            self.energy += self.health - 100
            self.health = 100

        if self.health <= 0:
            self.to_dying()

    def get_age(self, today):
        years = today.year - self.birthday.year
        if today.month < self.birthday.month or (today.month == self.birthday.month and today.day < self.birthday.day):
            years -= 1
        return years

    def __str__(self):
        return ('{} birthday:{} health:{} energy:{} money:{}'.format(self.name, self.birthday,
                                                                     '%.2f' % self.health, '%.2f' % self.energy,
                                                                     '%.2f' % self.money))

    def sex(self, woman, today):
        if self.energy > 70 and self.pair.energy > 70:
            self.add_health(-30)
            self.pair.add_health(-30)
            if random.randint(0, 1) == 1:
                woman.date_of_conception = today

    def add_child(self, child):
        self.children.append(child)
        if self.pair:
            self.pair.children.append(child)

    def birth_of_child(self, planet):
        today = planet.calendar.today
        if (today - self.date_of_conception).days >= 280:
            if random.randint(0, 1) == 1:
                child = Man(birthday=today)
            else:
                child = Woman(birthday=today)
            self.add_child(child)
            planet.add_resident(child)
            self.date_of_conception = None

    def to_eat(self, planet, age):
        print('I want eat.')
        if age >= 18:
            if self.money > 1:
                planet.go_to_shop(resident=self)
            else:
                print('I don\'t have money.')
        else:
            self.add_health(13)

    def to_dying(self):
        print('I\'m dying')
        self.dead = True
        if self.pair is not None:
            self.pair.money += self.money
            self.pair = None
        else:
            count_children = len(self.children)
            if count_children > 0 and self.money > 0:
                part_of_money = self.money / count_children
                for child in self.children:
                    child.money += part_of_money
        self.money = 0
        self.energy = 0
        self.health = 0
        self.children.clear()

    def act(self, planet):
        # day start
        print(self)

        if isinstance(self, Woman):
            if self.date_of_conception is not None:
                self.birth_of_child(planet)

        self.add_health(-10)
        age = self.get_age(planet.calendar.today)
        print('age {}'.format(age))

        if not self.dead and self.energy < 30:
            self.to_eat(planet, age)

        if not self.dead and self.energy > 20 and age >= 18 and self.money < 3000:
            print('I want work.')

            self.add_money(200)
            self.add_health(-18)

        if not self.dead and self.energy < 30:
            self.to_eat(planet, age)

        if not self.dead and self.energy > 50 and age >= 18 and self.money > 2000 and self.pair is None:
            print('I want to get married.')
            planet.marriage(self)

        # children
        if not self.dead and age >= 18 and age < 45 and self.pair is not None:
            if isinstance(self, Woman):
                if self.date_of_conception is None:
                    print('I want a child.')
                    self.sex(self, planet.calendar.today)  # + 280 days
            elif isinstance(self, Man):
                if self.pair.date_of_conception is None:
                    print('I want a child.')
                    self.sex(self.pair, planet.calendar.today)  # + 280 days

        if not self.dead and self.money >= 2500 and self.energy > 30 and age >= 18:
            print('I want train.')

            self.add_money(-1200)
            self.add_health(43)

        if not self.dead:
            if len(planet.residents) > 100:
                if age > random.randint(0, 101):
                    self.add_health(-100)
            if age > 120:
                self.add_health(-200)

        if not self.dead:
            if self.energy < 0:
                print('sleep.')
                self.add_health(5)


class Man(Human):
    count = 0

    def __init__(self, birthday, name=None):
        super().__init__(birthday)
        if not name:
            Man.count += 1
            self.name = 'Adam {}'.format(Man.count)

        else:
            self.name = name


class Woman(Human):
    count = 0

    def __init__(self, birthday, name=None):
        super().__init__(birthday)
        self.date_of_conception = None
        if not name:
            Woman.count += 1
            self.name = 'Eva {}'.format(Woman.count)

        else:
            self.name = name


class Spaceship:
    def __init__(self, name):
        self.passengers = []
        self.name = name

    def add_passenger(self, passenger):
        self.passengers.append(passenger)

    def remove_passenger(self):
        return self.passengers.pop()

    def fly_to_planet(self, planet):
        planet.spaceship_arrival(self)


def main():
    calendar = Calendar()
    mars = Planet(name='Mars', calendar=calendar)
    earth = Planet(name='Earth', calendar=calendar)

    spaceship747 = Spaceship(name='sp747')
    spaceship748 = Spaceship(name='sp748')
    spaceship749 = Spaceship(name='sp749')

    earth.spaceship_arrival(spaceship747)
    earth.spaceship_arrival(spaceship748)
    earth.spaceship_arrival(spaceship749)

    adam = Man(birthday=datetime.datetime(1980, 9, 11), name='Adam')
    svetlana = Woman(birthday=datetime.datetime(1981, 9, 11), name='Svatlana')

    boris = Man(birthday=datetime.datetime(2000, 2, 6), name='Boris')
    svetlana.add_child(boris)

    ekaterina = Woman(birthday=datetime.datetime(2005, 4, 3), name='Ekaterina')
    svetlana.add_child(ekaterina)

    spaceship_to_mars = earth.get_spaceship()

    spaceship_to_mars.add_passenger(adam)
    spaceship_to_mars.add_passenger(svetlana)
    spaceship_to_mars.add_passenger(boris)
    spaceship_to_mars.add_passenger(ekaterina)

    spaceship_to_mars.fly_to_planet(mars)

    years = 365 * 500
    for i in range(1, years):
        mars.day()
        if len(mars.residents) == 0:
            break


if __name__ == '__main__':
    main()
