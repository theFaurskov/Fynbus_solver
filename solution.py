import time
import json
import sys

from solution_classes import Combination, Bid, Entrepreneur

n_routes = 13
m_bidders = 6

#Gives each bid their quality from their respective entrepreneur
def quality_check(a,b):  #(bids, ents)
    for i in a:
        for r in b:
            if i.company == r.company:
                i.quality = r.quality
                break
        else:
            print "error with: " + str(i)

def insertion_sort(a):
    for i in xrange(1,len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j].pindex < key.pindex:
            a[j+1] = a[j]
            j = j - 1
        a[j+1] = key

#Sorts the packages in each bid
def sort_packages(a):
    for i in a:
        i.pack.sort()

#Finds the lowest price for each package
def lowest_prices(a):
    d = dict()
    for i in a:
        for c in i.pack:
            if c not in d:
                d[c] = i.price
            elif d[c] > i.price:
                d[c] = i.price
    return d

#Calculates the performanceindex for each bid
def calculate_performance(a):
    for i in a:
        total = 0
        for p in i.pack:
                total += price_list[p]
        i.pindex = (total*60)/(len(i.pack)*i.price)+i.quality*0.4

#Removes the duplicate of a bid with the lowest performanceindex
def repeated_bids(a):
    r = 0
    while r < len(a)-1:
        i = r+1
        while i < len(a):
            if a[r].pack == a[i].pack:
                if a[r].pindex > a[i].pindex:
                    del a[i]
                elif a[r].pindex < a[i].pindex:
                    del a[r]
                    i = r+1
                else:
                    i += 1
            else:
                i += 1
        r += 1

#Finds the number of packages
def find_highest(a):
    highest = 0
    for i in a:
        if i.pack[-1] > highest:
            highest = i.pack[-1]
    return highest

#Sorts the bids into lists, where their first package determines their place.
def spec_bid_list(a, b):  #(bids, pack_val)
    bid_list = []
    for i in a:
        if i.pack[0] == b:
            bid_list.append(i)
    return bid_list

#Puts the lists of bids into another list
def sort_bids_list(a, highest):
    pack_val = 1
    l = []
    while pack_val < highest+1:
        l.append(spec_bid_list(a, pack_val))
        pack_val += 1
    return l

#Determines whether or not a value (in a list) exist in another list
def not_full(a, b): #(combi,current_bid.pack)
    c = []
    for x in a:
        for r in x.pack:
            c.append(r)
    for t in b:
        if t in c:
            return False
    return True

#Creates bid combinations
def find_combi(a, b, current, highest, performance): #(sorted_bids, combi, current, highest,
    if current < highest: #Does the list exist in "sorted_bids"?
        if not_full(b, [current+1]): #Does the specific bidvalue exist in the combination?
            for i in xrange(len(a[current])): #Use every element in the list
                if not_full(b, a[current][i].pack): #Do the other bidvalues exist in the combination?
                    b.append(a[current][i])
                    performance += a[current][i].pindex * len(a[current][i].pack)
                    find_combi(a, b, current + 1, highest, performance)
                    del b[-1]
                    performance -= a[current][i].pindex * len(a[current][i].pack)
        else:
            find_combi(a, b, current + 1, highest, performance) #Call the next bidlist
    else:
        #End the current runthrough and save the combination
        com = Combination(b[:], performance/highest)
        combi_list.append(com)

bids = []
ents = []

# Where to take data from
if (len(sys.argv) < 2):
    sys.exit("No filename for data provided in the arguments");

filename = sys.argv[1]
data = ""

with open(filename, "r") as file_:
    data = file_.read()
decoded = json.loads(data)

for ent in decoded["entrepreneurs"]:
    # Entrepreneuer contructor takes parameters in Name, Quality, Company
    ents.append(Entrepreneur(ent[1], ent[2], ent [0]))

for bid in decoded["bids"]:
    
    packs = []
    for i in bid[2]:
        packs.append(i+1)
    # Entrepreneuer contructor takes parameters in Identity, Package, Price, Company
    bids.append(Bid(str(bid[0]), packs, bid[1], bid[0]))

start = time.time()

quality_check(bids, ents)

sort_packages(bids)

price_list = lowest_prices(bids)

calculate_performance(bids)

repeated_bids(bids)

highest = find_highest(bids)

sorted_bids = sort_bids_list(bids, highest)

combi_list = []
combi = []
find_combi(sorted_bids, combi, 0, highest, 0)

insertion_sort(combi_list)

end = time.time()

spend = end-start

print sorted_bids
#for i in combi_list:
#    print i
print "Time: " + str(spend)

with open("result.txt", "w") as file_:
    best = []
    for i in xrange(len(combi_list)):
        if combi_list[i].pindex != combi_list[i+1].pindex:
            for n in xrange(i+1):
                best.append(combi_list[n])
                print "Best: " + str(combi_list[n])
            file_.write(str(best))
            break
