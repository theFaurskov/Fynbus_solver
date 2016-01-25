class Combination:
    def __init__(self, bids_combination, performance_index):
        self.bic = bids_combination
        self.pindex = performance_index

    def __str__(self):
        return str(self.bic) + ": " + str(self.pindex)

    def __repr__(self):
        return self.__str__()

    
class Bid:
    def __init__(self, identity, package, price, company):
        self.id = identity
        self.pack = package
        self.price = price
        self.company = company

    def __str__(self):
        return self.id + str(self.pack)

    def __repr__(self):
        return self.__str__()

class Entrepreneur:
    def __init__(self, name, quality, company):
        self.name = name
        self.quality = quality
        self.company = company

    def __str__(self):
        return self.name + ", " + str(self.quality) + ", " + self.company

    def __repr__(self):
        return self.__str__()

