#! /usr/bin/env python
#
#

import time
import json
import sys
import os
import argparse

# weight = [package: weight]
# ents = [(idname, quality, company)]
# bids = [[idname, quality, pindex, [packages], [package: price]]]


def get_data(arg_input):
    with open(arg_input, "r") as file_in:
        data_in = file_in.read()
    decoded = json.loads(data_in)

    # Entrepreneur tuple takes parameters in Name, Quality, Company
    ents_in = [(ent[0], ent[2], ent[1]) for ent in decoded["entrepreneurs"]]

    # Bid list takes parameters in Identity, Package, Price
    bids_in = [[bid_in[0], 0, 0, bid_in[2], {int(i): bid_in[1][i] for i in bid_in[1]}] for bid_in in decoded["bids"]]

    weight_in = {int(i): decoded["weight"][i] for i in decoded["weight"]}

    return ents_in, bids_in, weight_in


# Gives each bid their quality from their respective entrepreneur
def quality_check(bids_check, ents_check):  # (bids, ents)
    for bid_check in bids_check:
        for ent_check in ents_check:
            if bid_check[0] == ent_check[0]:
                bid_check[1] = ent_check[1]
                break
        else:
            print "error with: " + str(bid_check)
            sys.exit(0)


# Sorts the packages in each bid
def sort_packages(bids_sort):
    for bid_sort in bids_sort: bid_sort[3].sort()


# Finds the lowest price for each package and returns a dict
def lowest_prices(bids_low):
    # Lowest price dict2
    lpd = {}
    for bid_low in bids_low:
        for pack in bid_low[3]:
            if pack not in lpd or lpd[pack] > bid_low[4][pack]:
                lpd[pack] = bid_low[4][pack]
    return lpd


# Calculates the performanceindex for each bid
def calculate_performance(bids_perf, lowest_price_dict_perf):
    for bid_perf in bids_perf:
        total_price = sum(lowest_price_dict_perf[pack] * weight[pack] for pack in bid_perf[3])
        weighted_price = sum(bid_perf[4][key] * weight[key] for key in bid_perf[4])
        bid_perf[2] = (total_price * 60.0) / weighted_price + bid_perf[1] * 0.4


# Parse args
parser = argparse.ArgumentParser(description='Fynbus to Kombee')
parser.add_argument('--input', '-i', metavar='INPUT',
                    type=str, default='data.txt',
                    help='Input file (default: %(default)s)')
parser.add_argument('--output', '-o', metavar='OUTPUT',
                    type=str, default=None,
                    help='Output file (default: input filename appended with .modified)')
args = parser.parse_args()

if not os.path.isfile(args.input):
    parser.error('Input file not found: %r' % args.input)
if not args.output:
    args.output = args.input + '.modified'

ents, bids, weight = get_data(args.input)

quality_check(bids, ents)

sort_packages(bids)

lowest_price_dict = lowest_prices(bids)

calculate_performance(bids, lowest_price_dict)

data = {"bids": [[bid[0], bid[2], bid[3]] for bid in bids],
        "weight": weight}
encoded = json.dumps(data)
with open(args.output, "w") as file_:
    file_.write(encoded)
