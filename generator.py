import random
import json

class Generator:  # Script for generating examples of bids for FynBus combinatorial

    def __init__(self, n_routes, m_bidders):
        # Parameters:
        self.n_routes = n_routes  # Number of packages (of routes) that can be bid on.
        self.m_bidders = m_bidders  # Number of entrepreneurs giving bids.

        self.cost_min = 100.00  # Minimum route cost across packages.
        self.cost_max = 400.00  # Maximum route cost across packages.
        self.cost_rebate = 0.15  # Lowering of cost in percentage due to economies of scale.

        self.combination_force_singles = True  # Can only combine packages having single bids.
        self.combination_rules = []
        for i in xrange(2,int(n_routes*0.3)):
            self.combination_rules.append((1,i))  # Sequence of (count,size), i.e. (1,5) means at most 1 combination of 5 packages.
          
        self.combination_all = 1.0  # Probability of total offer for all packages (zero if not allowed).

        self.bidder_range = 0.30  # Variation in bidder's bids in percentage of mean of package.
        self.bidder_coverage = 1.0  # The percentage of the possible offers being made.

        self.quality_min = 75
        self.quality_max = 100

    # Helpers:
    def groupSortPredictor(self, x, y):
        if len(x) < len(y):
            return -1
        elif len(y) < len(x):
            return +1
        elif x < y:
            return -1
        elif y < x:
            return +1
        else:
            return 0

    # Bid generators:
    def generateEntrepreneur(self, index):
        name = ''
        i = index
        while True:
            name = chr(ord('A') + i % (ord('Z') - ord('A') + 1)) + name
            i = i / (ord('Z') - ord('A') + 1)
            if i == 0:
                break
            i = i - 1
        quality = random.randint(self.quality_min, self.quality_max)
        return (index, name, quality)

    def generateEntrepreneurBids(self, index, cost_structure):
        entrepreneur = self.generateEntrepreneur(index)
        bid_sequence = []
        routes_covered = set()
        individual_cost_structure = [random.randint(int(c * (1 - self.bidder_range)), int(c * (1 + self.bidder_range))) for c in cost_structure]
        pricer = lambda p: int(p) / 5 * 5
        combination_pricer = lambda p: int(sum(p) / len(p) * (1 - self.cost_rebate)) / 10 * 10
        # Combination bids:
        for (rule_count, rule_size) in self.combination_rules:
            for r in range(rule_count):
                if random.random() < self.bidder_coverage:
                    combination = tuple(sorted(random.sample(xrange(self.n_routes), rule_size)))
                    if combination not in routes_covered:
                        price = combination_pricer([individual_cost_structure[r] for r in combination])
                        bid_sequence.append((index, price, combination))
                        routes_covered.update([combination])
        # Bid on all:
        if random.random() < self.combination_all:
            combination = tuple(range(self.n_routes))
            if combination not in routes_covered:
                price = combination_pricer(individual_cost_structure)
                bid_sequence.append((index, price, combination))
                routes_covered.update([combination])
        # Single bids:
        single_routes_needed = reduce(lambda r, t: r.union(t), routes_covered, set())
        for i in range(self.n_routes):
            if random.random() < self.bidder_coverage or (self.combination_force_singles and i in single_routes_needed):
                if (i,) not in routes_covered:
                    combination = (i,)
                    price = pricer(individual_cost_structure[i])
                    bid_sequence.append((index, price+60, combination))
                    routes_covered.update([combination])
        # Sorting:
        bid_sequence = sorted(bid_sequence, cmp=lambda x, y: self.groupSortPredictor(x[2], y[2]))
        # Return:
        return (entrepreneur, bid_sequence)

    def generateAuctionBids(self):
        entrepreneur_sequence = []
        bid_sequence = []
        cost_structure = sorted([random.uniform(self.cost_min, self.cost_max) for k in range(self.n_routes)])
        for i in range(self.m_bidders):
            (entrepreneur, bids) = self.generateEntrepreneurBids(i, cost_structure)
            entrepreneur_sequence.append(entrepreneur)
            bid_sequence.extend(bids)

        data = {"entrepreneurs" : [(e[0], e[1], e[2]) for e in entrepreneur_sequence],
                "bids" : [(e[0], e[1], e[2]) for e in bid_sequence]}
        encoded = json.dumps(data)
        with open("data.txt", "w") as file_:
            file_.write(encoded)

        return (entrepreneur_sequence, bid_sequence)

gen = Generator(170,30)
gen.generateAuctionBids()

"""# Script entry point:

if __name__ == '__main__':
    (entrepreneurs, bids) = generateAuctionBids()
    print 'ENTREPRENEURS (%d)\nIndex:  Name:   Quality:' % len(entrepreneurs)
    print '\n'.join(['%4d%8s%8d' % (i, n, q) for (i, n, q) in entrepreneurs])
    print 'BIDS (%d)\nBidder: Price:  Packages:' % len(bids)
    print '\n'.join(['%4d%8d    %s' % (e, p, ','.join(['%d' % i for i in r])) for (e, p, r) in bids])
"""
