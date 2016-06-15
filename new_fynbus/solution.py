#! /usr/bin/env python
#
#

import time
import json
import pp
import os
import argparse
import copy


# weight = {package: weight}
# bids = [(identity, pindex, [packages])]

def get_data(arg_input):
    with open(arg_input + '.modified', "r") as file_in:
        data_in = file_in.read()
    decoded = json.loads(data_in)

    # Bid list takes parameters in Identity, Pindex, Package
    bids_in = [(bid_in[0], bid_in[1], bid_in[2]) for bid_in in decoded["bids"]]
    # Weight list takes the parameters Package and Weight for package
    weight_in = {int(i): decoded["weight"][i] for i in decoded["weight"]}

    return bids_in, weight_in


# Sorts the packages in each bid
def sort_packages(bids_sort):
    temp_bids = copy.deepcopy(bids_sort)
    for temp_bid in temp_bids:
        temp_bid[2].sort()
    return temp_bids


# Removes the duplicate of a bid with the lowest performanceindex
def repeated_bids(bids_rep):
    temp_bids = copy.deepcopy(bids_rep)
    r = 0
    while r < len(temp_bids) - 1:
        i = r + 1
        while i < len(temp_bids):
            if temp_bids[r][2] == temp_bids[i][2]:
                if temp_bids[r][1] > temp_bids[i][1]:
                    del temp_bids[i]
                elif temp_bids[r][1] < temp_bids[i][1]:
                    del temp_bids[r]
                    i = r + 1
                else:
                    i += 1
            else:
                i += 1
        r += 1
    return temp_bids


# Creates a dictionary with the pindex of the single pack bids
def single_packs(bids_single):
    single_pindex = dict()
    for bid_single in bids_single:
        if len(bid_single[2]) == 1: single_pindex[bid_single[2][0]] = bid_single[1]
    return single_pindex


# Removes combination bids if combinations of single bids is better
def is_single_best(bids_sbest, single_pindex_sbest, weight_sbest):
    temp_bids = copy.deepcopy(bids_sbest)
    i = 0
    while i < len(temp_bids):
        single_perf = sum(single_pindex_sbest[n] * weight_sbest[n] for n in temp_bids[i][2])
        total_weight = sum(weight_sbest[n] for n in temp_bids[i][2])
        if single_perf > temp_bids[i][1] * total_weight:
            del temp_bids[i]
        else:
            i += 1
    return temp_bids


# Finds the number of packages
def find_highest(bids_highest):
    highest = 0
    for bid_highest in bids_highest:
        if max(bid_highest[2]) > highest: highest = max(bid_highest[2])
    return highest


# Sorts the bids into lists, where their first package determines their place.
def spec_bid_list(bids_slist, pack_val_slist):  # (bids, pack_val)
    bid_list = [bid_slist for bid_slist in bids_slist if min(bid_slist[2]) == pack_val_slist]
    return bid_list


# Puts the lists of bids into another list
def sort_bids_list(bids_sbl):
    highest_sbl = find_highest(bids_sbl)
    sorted_bids_sbl = [spec_bid_list(bids_sbl, pack_val) for pack_val in xrange(highest_sbl + 1)]
    return sorted_bids_sbl


# Determines whether or not a value (in a list) exist in another list
def is_not_full(combi_seq_nf, current_bid_packs_nf, sorted_bids_nf, nec_packs_nf=None):
    if nec_packs_nf:
        for bid_nf in current_bid_packs_nf:
            if bid_nf not in nec_packs_nf:
                return False
    combi_packs = [pack_nf for key, value in combi_seq_nf.iteritems()
                   if isinstance(value, int) and isinstance(key, int) for pack_nf in sorted_bids_nf[key][value][2]]
    for current_pack_nf in current_bid_packs_nf:
        if current_pack_nf in combi_packs: return False
    return True


# Creates bid combinations for bid remover and compare their value to a given value
def is_pindex_highest(sorted_bids_ph, weight_ph, nec_packs_ph, pindex_value_ph, combi_seq_ph=None):
    if combi_seq_ph is None:
        combi_seq_ph = {}  # Takes index in sorted_bids
    combinas = []
    sort_counter = 0
    total_weight = sum(bid_weight for pack, bid_weight in weight_ph.iteritems() if pack in nec_packs_ph)
    while True:
        current_bid_packs_ph = []
        if 'reverse' not in combi_seq_ph:
            try:
                new_max = max(key for key in combi_seq_ph.keys() if isinstance(key, int)) + 1
                current_bid_packs_ph = sorted_bids_ph[new_max]
                if not is_not_full(combi_seq_ph, [new_max], sorted_bids_ph, nec_packs_ph):
                    combi_seq_ph[new_max] = None
                    combi_seq_ph['bid_pindex' + str(new_max)] = 0
                    continue
            except ValueError:
                new_max = 0
                if not is_not_full(combi_seq_ph, [new_max], sorted_bids_ph, nec_packs_ph):
                    combi_seq_ph[new_max] = None
                    combi_seq_ph['bid_pindex' + str(new_max)] = 0
                else:
                    current_bid_packs_ph = sorted_bids_ph[new_max]
            except IndexError:
                combi_seq_ph['pindex'] = sum(pin for key, pin in combi_seq_ph.iteritems()
                                             if str(key).startswith('bid_pindex')) / total_weight
                combinas.append(copy.deepcopy(combi_seq_ph))
                combi_seq_ph['reverse'] = True

                sort_counter = sort_counter + 1 if sort_counter < 10000000 else 0
                if sort_counter % 100 == 0:
                    combinas.sort(key=lambda x: x['pindex'], reverse=True)
                    for i in xrange(len(combinas) - 1):
                        if combinas[i]['pindex'] != combinas[i + 1]['pindex']:
                            combinas = combinas[:i + 1]
                            break
                    for combi in combinas:
                        if combi['pindex'] > pindex_value_ph and \
                           1 < sum(1 for key, value in combi.iteritems()
                                   if isinstance(key, int) and isinstance(value, int)):
                            return False
            for i, bid_ph in enumerate(current_bid_packs_ph):
                if is_not_full(combi_seq_ph, bid_ph[2], sorted_bids_ph, nec_packs_ph):
                    combi_seq_ph[new_max] = i
                    bid_sum_perf = sum(sorted_bids_ph[new_max][i][1] * weight_ph[pack_ph]
                                       for pack_ph in sorted_bids_ph[new_max][i][2])
                    combi_seq_ph['bid_pindex' + str(new_max)] = bid_sum_perf
                    break

        else:
            try:
                max_key = max(key for key in combi_seq_ph.keys() if isinstance(key, int))
                if combi_seq_ph.get('lock') == max_key:
                    break
            except ValueError:
                break

            try:
                in_jump = combi_seq_ph[max_key] + 1
                del combi_seq_ph[max_key]
                del combi_seq_ph['bid_pindex' + str(max_key)]
                current_bid_packs_ph = sorted_bids_ph[max_key]

                for i, bid_ph in enumerate(current_bid_packs_ph[in_jump:]):
                    if is_not_full(combi_seq_ph, bid_ph[2], sorted_bids_ph, nec_packs_ph):
                        index = i + in_jump
                        combi_seq_ph[max_key] = index
                        bid_sum_perf = sum(sorted_bids_ph[max_key][index][1] * weight_ph[pack_ph]
                                           for pack_ph in sorted_bids_ph[max_key][index][2])
                        combi_seq_ph['bid_pindex' + str(max_key)] = bid_sum_perf
                        del combi_seq_ph['reverse']
                        break
            except TypeError:
                del combi_seq_ph[max_key]
                del combi_seq_ph['bid_pindex' + str(max_key)]

    combinas.sort(key=lambda x: x['pindex'], reverse=True)
    for key_combi in xrange(len(combinas) - 1):
        if combinas[key_combi]['pindex'] != combinas[key_combi + 1]['pindex']:
            combinas = combinas[:key_combi + 1]
            break
    for combi in combinas:
        if combi['pindex'] > pindex_value_ph and 1 < sum(1 for key, value in combi.iteritems()
                                                         if isinstance(key, int) and isinstance(value, int)):
            return False
    return True


def split_is_pindex_highest(sorted_bids_sph, weight_sph, nec_packs_sph,
                            pindex_value_sph, srv_sph=None, job_parts_sph=0):
    jobs_sph = []
    combi_seq_sph = {}  # Takes index in sorted_bids
    while True:
        current_bid_packs_sph = []
        if 'reverse' not in combi_seq_sph:
            try:
                new_max = max(key for key in combi_seq_sph.keys() if isinstance(key, int)) + 1
                current_bid_packs_sph = sorted_bids_sph[new_max]
                if not is_not_full(combi_seq_sph, [new_max], sorted_bids_sph, nec_packs_sph):
                    combi_seq_sph[new_max] = None
                    combi_seq_sph['bid_pindex' + str(new_max)] = 0
            except ValueError:
                new_max = 0
                if not is_not_full(combi_seq_sph, [new_max], sorted_bids_sph, nec_packs_sph):
                    combi_seq_sph[new_max] = None
                    combi_seq_sph['bid_pindex' + str(new_max)] = 0
                else:
                    current_bid_packs_sph = sorted_bids_sph[new_max]

            for i, bid_sph in enumerate(current_bid_packs_sph):
                if is_not_full(combi_seq_sph, bid_sph[2], sorted_bids_sph, nec_packs_sph):
                    combi_seq_sph[new_max] = i
                    bid_sum_perf = sum(sorted_bids_sph[new_max][i][1] * weight_sph[pack_sph]
                                       for pack_sph in sorted_bids_sph[new_max][i][2])
                    combi_seq_sph['bid_pindex' + str(new_max)] = bid_sum_perf
                    break
            if new_max == job_parts_sph:
                combi_seq_sph['lock'] = new_max
                jobs_sph.append(srv_sph.submit(func=is_pindex_highest, args=(sorted_bids_sph, weight_sph,
                                                                             nec_packs_sph, pindex_value_sph,
                                                                             copy.deepcopy(combi_seq_sph)),
                                               depfuncs=(is_not_full,), modules=('copy',)))
                combi_seq_sph['reverse'] = True
                del combi_seq_sph['lock']
        else:
            try:
                max_key = max(key for key in combi_seq_sph.keys() if isinstance(key, int))
            except ValueError:
                break

            try:
                in_jump = combi_seq_sph[max_key] + 1
                del combi_seq_sph[max_key]
                del combi_seq_sph['bid_pindex' + str(max_key)]
                current_bid_packs_sph = sorted_bids_sph[max_key]

                for i, bid_sph in enumerate(current_bid_packs_sph[in_jump:]):
                    if is_not_full(combi_seq_sph, bid_sph[2], sorted_bids_sph, nec_packs_sph):
                        index = i + in_jump
                        combi_seq_sph[max_key] = index
                        bid_sum_perf = sum(sorted_bids_sph[max_key][index][1] * weight_sph[pack_sph]
                                           for pack_sph in sorted_bids_sph[max_key][index][2])
                        combi_seq_sph['bid_pindex' + str(max_key)] = bid_sum_perf
                        del combi_seq_sph['reverse']
                        if max_key == job_parts_sph:
                            combi_seq_sph['lock'] = max_key
                            jobs_sph.append(srv_sph.submit(func=is_pindex_highest,
                                                           args=(sorted_bids_sph, weight_sph,
                                                                 nec_packs_sph, pindex_value_sph,
                                                                 copy.deepcopy(combi_seq_sph)),
                                                           depfuncs=(is_not_full,), modules=('copy',)))
                            combi_seq_sph['reverse'] = True
                            del combi_seq_sph['lock']
                        break
            except TypeError:
                del combi_seq_sph[max_key]
                del combi_seq_sph['bid_pindex' + str(max_key)]
    return jobs_sph


def is_bid_best(sorted_bids_ibb, weight_ibb, current_bid_ibb, job_server_ibb):
    if len(current_bid_ibb[2]) < 2 or len(current_bid_ibb[2]) > len(sorted_bids_ibb) / 2:
        return True
    if len(current_bid_ibb) * 10.0 < len(sorted_bids_ibb[current_bid_ibb[2][0]]) * len(sorted_bids_ibb[current_bid_ibb[2][1]]):
        job_parts_ibb = 0 + current_bid_ibb[2][0]
    else:
        job_parts_ibb = 1 + current_bid_ibb[2][0]
    # result = is_pindex_highest(sorted_bids_ibb, weight_ibb, current_bid_ibb[2], current_bid_ibb[2])
    jobs_ibb = split_is_pindex_highest(sorted_bids_ibb, weight_ibb, current_bid_ibb[2],
                                       current_bid_ibb[1], job_server_ibb, job_parts_ibb)
    job_server_ibb.wait()
    for job_ibb in jobs_ibb:
        if not job_ibb():
            return False
    return True


def bid_removal(sorted_bids_br, weight_br, job_server_br):
    temp_sorted_bids = []
    for bids_br in sorted_bids_br:
        temp_bids_br = [bid for bid in bids_br if is_bid_best(sorted_bids_br, weight_br, bid, job_server_br)]
        temp_sorted_bids.append(temp_bids_br)
    return temp_sorted_bids


# Creates bid combinations
def find_combi(sorted_bids_fc, weight_fc, combi_seq_fc=None):
    if combi_seq_fc is None:
        combi_seq_fc = {}
    combinas = []  # Takes index in sorted_bids
    sort_counter = 0
    total_weight = sum(bid_weight for pack, bid_weight in weight_fc.iteritems())
    while True:
        current_bid_packs_fc = []

        if 'reverse' not in combi_seq_fc:
            try:
                new_max = max(key for key in combi_seq_fc.keys() if isinstance(key, int)) + 1
                current_bid_packs_fc = sorted_bids_fc[new_max]
                if not is_not_full(combi_seq_fc, [new_max], sorted_bids_fc):
                    combi_seq_fc[new_max] = None
                    combi_seq_fc['bid_pindex' + str(new_max)] = 0
                    continue
            except ValueError:
                current_bid_packs_fc = sorted_bids_fc[0]
                new_max = 0
            except IndexError:
                combi_seq_fc['pindex'] = sum(pin for key, pin in combi_seq_fc.iteritems()
                                             if str(key).startswith('bid_pindex')) / total_weight
                combinas.append(copy.deepcopy(combi_seq_fc))
                combi_seq_fc['reverse'] = True

                sort_counter = sort_counter + 1 if sort_counter < 1000000000 else 0
                if sort_counter % 100 == 0:
                    combinas.sort(key=lambda x: x['pindex'], reverse=True)
                    for i in xrange(len(combinas) - 1):
                        if combinas[i]['pindex'] != combinas[i + 1]['pindex']:
                            combinas = combinas[:i + 1]
                            break
            for i, bid_fc in enumerate(current_bid_packs_fc):
                if is_not_full(combi_seq_fc, bid_fc[2], sorted_bids_fc):
                    combi_seq_fc[new_max] = i
                    bid_sum_perf = sum(sorted_bids_fc[new_max][i][1] * weight_fc[pack_fc]
                                       for pack_fc in sorted_bids_fc[new_max][i][2])
                    combi_seq_fc['bid_pindex' + str(new_max)] = bid_sum_perf
                    break
        else:
            try:
                max_key = max(key for key in combi_seq_fc.keys() if isinstance(key, int))
                if combi_seq_fc.get('lock') == max_key:
                    break
            except ValueError:
                break

            try:
                in_jump = combi_seq_fc[max_key] + 1
                del combi_seq_fc[max_key]
                del combi_seq_fc['bid_pindex' + str(max_key)]
                current_bid_packs_fc = sorted_bids_fc[max_key]

                for i, bid_fc in enumerate(current_bid_packs_fc[in_jump:]):
                    if is_not_full(combi_seq_fc, bid_fc[2], sorted_bids_fc):
                        index = i + in_jump
                        combi_seq_fc[max_key] = index
                        bid_sum_perf = sum(sorted_bids_fc[max_key][index][1] * weight_fc[pack_fc]
                                           for pack_fc in sorted_bids_fc[max_key][index][2])
                        combi_seq_fc['bid_pindex' + str(max_key)] = bid_sum_perf
                        del combi_seq_fc['reverse']
                        break
            except TypeError:
                del combi_seq_fc[max_key]
                del combi_seq_fc['bid_pindex' + str(max_key)]

    combinas.sort(key=lambda x: x['pindex'], reverse=True)
    for key_combi in xrange(len(combinas) - 1):
        if combinas[key_combi]['pindex'] != combinas[key_combi + 1]['pindex']:
            combinas = combinas[:key_combi + 1]
            break
    return combinas


def split_find_combi(sorted_bids_sfc, weight_sfc, srv_sfc=None, job_parts_sfc=0):
    jobs_sfc = []
    combi_seq_sfc = {}  # Takes index in sorted_bids
    while True:
        if 'reverse' not in combi_seq_sfc:
            try:
                new_max = max(key for key in combi_seq_sfc.keys() if isinstance(key, int)) + 1
                current_bid_packs_sfc = sorted_bids_sfc[new_max]
                if not is_not_full(combi_seq_sfc, [new_max], sorted_bids_sfc):
                    combi_seq_sfc[new_max] = None
                    combi_seq_sfc['bid_pindex' + str(new_max)] = 0
            except ValueError:
                current_bid_packs_sfc = sorted_bids_sfc[0]
                new_max = 0

            for i, bid_sfc in enumerate(current_bid_packs_sfc):
                if is_not_full(combi_seq_sfc, bid_sfc[2], sorted_bids_sfc):
                    combi_seq_sfc[new_max] = i
                    bid_sum_perf = sum(sorted_bids_sfc[new_max][i][1] * weight_sfc[pack_sfc]
                                       for pack_sfc in sorted_bids_sfc[new_max][i][2])
                    combi_seq_sfc['bid_pindex' + str(new_max)] = bid_sum_perf
                    break
            if new_max == job_parts_sfc:
                combi_seq_sfc['lock'] = new_max
                jobs_sfc.append(srv_sfc.submit(func=find_combi, args=(sorted_bids_sfc, weight_sfc,
                                                                      copy.deepcopy(combi_seq_sfc)),
                                               depfuncs=(is_not_full,), modules=('copy',)))
                combi_seq_sfc['reverse'] = True
                del combi_seq_sfc['lock']
        else:
            try:
                max_key = max(key for key in combi_seq_sfc.keys() if isinstance(key, int))
            except ValueError:
                break

            try:
                in_jump = combi_seq_sfc[max_key] + 1
                del combi_seq_sfc[max_key]
                del combi_seq_sfc['bid_pindex' + str(max_key)]
                current_bid_packs_sfc = sorted_bids_sfc[max_key]

                for i, bid_sfc in enumerate(current_bid_packs_sfc[in_jump:]):
                    if is_not_full(combi_seq_sfc, bid_sfc[2], sorted_bids_sfc):
                        index = i + in_jump
                        combi_seq_sfc[max_key] = index
                        bid_sum_perf = sum(sorted_bids_sfc[max_key][index][1] * weight_sfc[pack_sfc]
                                           for pack_sfc in sorted_bids_sfc[max_key][index][2])
                        combi_seq_sfc['bid_pindex' + str(max_key)] = bid_sum_perf
                        del combi_seq_sfc['reverse']
                        if max_key == job_parts_sfc:
                            combi_seq_sfc['lock'] = max_key
                            jobs_sfc.append(srv_sfc.submit(func=find_combi,
                                                           args=(sorted_bids_sfc, weight_sfc,
                                                                 copy.deepcopy(combi_seq_sfc)),
                                                           depfuncs=(is_not_full,), modules=('copy',)))
                            combi_seq_sfc['reverse'] = True
                            del combi_seq_sfc['lock']
                        break
            except TypeError:
                del combi_seq_sfc[max_key]
                del combi_seq_sfc['bid_pindex' + str(max_key)]
    return jobs_sfc


def save_solution(combi_list_ss, sorted_bids_ss, r="result.txt", w="w"):
    with open(r, w) as file_:
        best = []
        for i in xrange(len(combi_list_ss) - 1):
            if combi_list_ss[i]['pindex'] != combi_list_ss[i + 1]['pindex']:
                for j in combi_list_ss[:i + 1]:
                    combination = ['%s: %s' % (['%s%s' % (sorted_bids_ss[key][value][0], sorted_bids_ss[key][value][2])
                                                for key, value in j.iteritems() if isinstance(key, int) and
                                                isinstance(value, int)], j['pindex'])]
                    combination[0] = combination[0].replace("'", "")
                    best += combination
                break
        else:
            for j in combi_list_ss:
                combination = ['%s: %s' % (['%s%s' % (sorted_bids_ss[key][value][0], sorted_bids_ss[key][value][2])
                                            for key, value in j.iteritems() if isinstance(key, int) and
                                            isinstance(value, int)], j['pindex'])]
                combination[0] = combination[0].replace("'", "")
                best += combination
        file_.write(str(best))
        return best


ppservers = ("*",)

# Parse args
parser = argparse.ArgumentParser(description='Exact cover solver')
parser.add_argument('--ncpus', '-n', metavar='N',
                    type=int, default=0,
                    help='Number of CPU cores to use (default all)')
parser.add_argument('--input', '-i', metavar='INPUT',
                    type=str, default='data.txt',
                    help='Input file (default: %(default)s)')
parser.add_argument('--output', '-o', metavar='OUTPUT',
                    type=str, default=None,
                    help='Output file (default: input filename appended with .out)')
args = parser.parse_args()

if not os.path.isfile(args.input):
    parser.error('Input file not found: %r' % args.input)
if args.ncpus < 0:
    parser.error('--ncpus cannot be negative')
if not args.output:
    args.output = args.input + '.out'

if args.ncpus:
    # Creates jobserver with ncpus workers
    job_server = pp.Server(args.ncpus, ppservers=ppservers)
else:
    # Creates jobserver with automatically detected number of workers
    job_server = pp.Server(ppservers=ppservers)

RESULT = (os.path.basename(args.input),)
try:
    RESULT += tuple(map(int, args.input.replace('.', '-').split('-')[1:-1]))
    print tuple(map(int, args.input.replace('.', '-').split('-')[1:-1]))
except ValueError:
    pass

print "Starting pp with", job_server.get_ncpus(), "workers"

bids_0, weight = get_data(args.input)

start_time = time.time()

bids_1 = sort_packages(bids_0)

print "Bids first: " + str(len(bids_1))
RESULT += (len(bids_1),)

bids_2 = repeated_bids(bids_1)

single_dict = single_packs(bids_2)

print 'Single dict %s' % single_dict

print "Bids second: " + str(len(bids_2))
RESULT += (len(bids_2),)

bids_3 = is_single_best(bids_2, single_dict, weight)

print "Bids third: " + str(len(bids_3))
RESULT += (len(bids_3),)

sorted_bids_0 = sort_bids_list(bids_3)

sorted_bids_1 = bid_removal(sorted_bids_0, weight, job_server)

print 'Length of first in sorted: %s' % len(sorted_bids_1[0])

if len(sorted_bids_1) * 10.0 < len(sorted_bids_1[0]) * len(sorted_bids_1[1]):
    job_parts = 0
else:
    job_parts = 1

print "Job parts: " + str(job_parts)

split_time_begin = time.time()

jobs = split_find_combi(sorted_bids_sfc=sorted_bids_1, weight_sfc=weight, srv_sfc=job_server, job_parts_sfc=job_parts)

split_time_end = time.time()

print "Split time: " + str(split_time_end - split_time_begin)

combi_list = []

job_time_begin = time.time()
print "Number of jobs: " + str(len(jobs))

for job in jobs:
    job_time = time.time()
    combi_list += job()
    # print "Job time: " + str(time.time()-job_time)

print "Job time: " + str(time.time() - job_time_begin)

combi_list.sort(key=lambda x: x['pindex'], reverse=True)

end_time = time.time()

spend = end_time - start_time

job_server.print_stats()

print "Time: " + str(spend)
RESULT += (spend,)

best_bids = save_solution(combi_list, sorted_bids_1, args.output)
print 'Output saved in', args.output
print

for best_bid in best_bids:
    print "Best: " + str(best_bid)

print
print 'RESULT;', '; '.join(map(str, RESULT))
print
