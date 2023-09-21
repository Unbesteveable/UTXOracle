###############################################################################

#             Introduction This was copied from UTXOracle.py, and stripped down
# - Credit to @SteveSimple on Twitter: https://twitter.com/SteveSimple/status/1704864674431332503

###############################################################################


# This python program estimates the daily USD price of bitcoin using only
# your bitcoin Core full node. It will work even while you are disconnected
# from the internet because it only reads blocks from your machine. It does not
# save files, write cookies, or access any wallet information. It only reads
# blocks, analyzes output patterns, and estimates a daily average a USD
# price of bitcoin. The call to your node is the standard "bitcoin-cli". The
# date and price ranges expected to work for this version are from 2020-7-26
# and from $10,000 to $100,000

print("LastPrice version 1\n")

###############################################################################

#                        Quick Start

###############################################################################


# 1. Make sure you have python3 and bitcoin-cli installed
# 2. Make sure "server = 1" is in bitcoin.conf
# 3. Run this file as "python3 LastPrice.py"

# If this isn't working for you, you'll likely need to explore the
# bitcon-cli configuration options below:


# configuration options for bitcoin-cli
datadir = ""
rpcuser = ""
rpcpassword = ""
rpcookiefile = ""
rpcconnect = ""
rpcport = ""
conf = ""

# add the configuration options to the bitcoin-cli call
bitcoin_cli_options = []
if datadir != "":
    bitcoin_cli_options.append('-datadir=' + datadir)
if rpcuser != "":
    bitcoin_cli_options.append("-rpcuser=" + rpcuser)
if rpcpassword != "":
    bitcoin_cli_options.append("-rpcpassword=" + rpcpassword)
if rpcookiefile != "":
    bitcoin_cli_options.append("-rpcookiefile=" + rpcookiefile)
if rpcconnect != "":
    bitcoin_cli_options.append("-rpcconnect=" + rpcconnect)
if rpcport != "":
    bitcoin_cli_options.append("-rpcport=" + rpcport)
if conf != "":
    bitcoin_cli_options.append("-conf=" + conf)

###############################################################################

#  Part 1) Defining a shortcut function to call your node

###############################################################################

# Here we define define a shortcut (a function) for calling the node as we do
# this many times through out the program. The function will return the
# answer it gets from your node with the "command" that you asked it for.
# If we don't get an answer, the problem is likely that you don't have
# sever=1 in your bitcoin conf file.


import subprocess  # a built in python library for sending command line commands


def Ask_Node(command):
    # 'bitcoin-cli' is how the command window calls your node so
    # it needs to be the first word in any request for data from the node
    # other options are added if given
    for o in bitcoin_cli_options:
        command.insert(0, o)
    command.insert(0, "bitcoin-cli")

    # get the answer from the node and return it to the program
    answer = None
    try:  # python try is used when we need to deal with errors after
        answer = subprocess.check_output(command)
    except Exception as e:
        # something went wrong while getting the answer
        print("Error connecting to your node. Trouble shooting steps:\n")
        print("\t 1) Make sure bitcoin-cli is working. Try command 'bitcoin-cli getblockcount'")
        print("\t 2) Make sure config file bitcoin.conf has server=1")
        print("\t 3) Explore the bitcoin-cli options in UTXOracle.py (line 38)")
        print("\nThe command was:" + str(command))
        print("\nThe error from bitcoin-cli was:\n")
        print(e)
        exit()

    # answer received, return this answer to the program
    return answer


###############################################################################

# Part 2)  Get the latest block from the node

###############################################################################

# The first request to the node is to ask it how many blocks it has. This
# let's us know the maximum possible day for which we can request a
# btc price estimate. The time information of blocks is listed in the block
# header, so we ask for the header only when we just need to know the time.


# get current block height from local node and exit if connection not made
block_count_b = Ask_Node(['getblockcount'])
block_count = int(block_count_b)  # convert text to integer

# get block header from current block height
block_hash_b = Ask_Node(['getblockhash', block_count_b])
block_header_b = Ask_Node(['getblockheader', block_hash_b[:64], 'true'])
import json  # a built in tool for deciphering lists of embedded lists

block_header = json.loads(block_header_b)
print("Connected to local node at block #:\t" + str(block_count))

# ###############################################################################
#
# # Part 3)  Ask for the desired date to estimate the price
#
# ###############################################################################
#  NOTE: see original UTXOracle.py; I removed that
# ##############################################################################
#
# # Part 4)  Hunt through blocks to find the first block on the target day
#
# ##############################################################################
#  NOTE: see original UTXOracle.py; I removed that
#
##############################################################################

#  Part 5) Build the container to hold the output amounts bell curve

##############################################################################

# In pure math a bell curve can be perfectly smooth. But to make a bell curve
# from a sample of data, one must specifiy a series of buckets, or bins, and then
# count how many samples are in each bin. If the bin size is too large, say just one
# large bin, a bell curve can't appear because it will have only one bar. The bell
# curve also doesn't appear if the bin size is too small because then there will
# only be one sample in each bin and we'd fail to have a distribution of bin heights.

# Although several bin sizes would work, I have found over many years, that 200 bins
# for every 10x of bitcoin amounts works very well. We use 'every 10x' because just
# like a long term bitcoin price chart, viewing output amounts in log scale provides
# a more comprehensive and detailed overview of the amounts being analyzed.


# Define the maximum and minimum values (in log10) of btc amounts to use
first_bin_value = -6
last_bin_value = 6  # python -1 means last in list
range_bin_values = last_bin_value - first_bin_value

# create a list of output_bell_curve_bins and add zero sats as the first bin
output_bell_curve_bins = [0.0]  # a decimal tells python the list will contain decimals

# calculate btc amounts of 200 samples in every 10x from 100 sats (1e-6 btc) to 100k (1e5) btc
for exponent in range(-6, 6):  # python range uses 'less than' for the big number

    # add 200 bin_width increments in this 10x to the list
    for b in range(0, 200):
        bin_value = 10 ** (exponent + b / 200)
        output_bell_curve_bins.append(bin_value)

# Create a list the same size as the bell curve to keep the count of the bins
number_of_bins = len(output_bell_curve_bins)
output_bell_curve_bin_counts = []
for n in range(0, number_of_bins):
    output_bell_curve_bin_counts.append(float(0.0))

##############################################################################

#  Part 6) Get all output amounts from last block

##############################################################################

from math import log10  # built in math functions needed logarithms

# get the full data of the first target day block from the node
print("Loading in the data #:\t" + str(block_count))
block_height = block_count
block_hash_b = Ask_Node(['getblockhash', str(block_height)])
block_b = Ask_Node(['getblock', block_hash_b[:64], '2'])
block = json.loads(block_b)

# go through all the txs in the block which are stored in a list called 'tx'
for tx in block['tx']:
    # txs have more than one output which are stored in a list called 'vout'
    outputs = tx['vout']
    # go through all outputs in the tx
    for output in outputs:

        # the bitcoin output amount is called 'value' in Core, add this to the list
        amount = float(output['value'])

        # tiny and huge amounts aren't used by the USD price finder
        if 1e-6 < amount < 1e6:
            # take the log
            amount_log = log10(amount)
            # find the right output amount bin to increment
            percent_in_range = (amount_log - first_bin_value) / range_bin_values
            bin_number_est = int(percent_in_range * number_of_bins)

            # search for the exact right bin (won't be less than)
            while output_bell_curve_bins[bin_number_est] <= amount:
                bin_number_est += 1
            bin_number = bin_number_est - 1

            # increment the output bin
            output_bell_curve_bin_counts[bin_number] += 1.0  # += means increment

##############################################################################

#  Part 7) Remove non-usd related output amounts from the bell curve

##############################################################################


# This sections aims to remove non-usd denominated samples from the bell curve
# of outputs. The two primary steps are to remove very large/small outputs
# and then to remove round btc amounts. We don't set the round btc amounts
# to zero because if the USD price of bitcoin is also round, then round
# btc amounts will co-align with round usd amounts. There are many ways to deal
# with this. One way we've found to work is to smooth over the round btc amounts
# using the neighboring amounts in the bell curve. The last step is to normalize
# the bell curve. Normalizing is done by dividing the entire curve by the sum
# of the curve, and then removing extreme values.

# remove ouputs below 1k sats
for n in range(0, 201):
    output_bell_curve_bin_counts[n] = 0

# remove outputs above ten btc
for n in range(1601, number_of_bins):
    output_bell_curve_bin_counts[n] = 0

# create a list of round btc bin numbers
round_btc_bins = [
    201,  # 1k sats
    401,  # 10k
    461,  # 20k
    496,  # 30k
    540,  # 50k
    601,  # 100k
    661,  # 200k
    696,  # 300k
    740,  # 500k
    801,  # 0.01 btc
    861,  # 0.02
    896,  # 0.03
    940,  # 0.04
    1001,  # 0.1
    1061,  # 0.2
    1096,  # 0.3
    1140,  # 0.5
    1201  # 1 btc
]

# smooth over the round btc amounts
for r in round_btc_bins:
    amount_above = output_bell_curve_bin_counts[r + 1]
    amount_below = output_bell_curve_bin_counts[r - 1]
    output_bell_curve_bin_counts[r] = .5 * (amount_above + amount_below)

# get the sum of the curve
curve_sum = 0.0
for n in range(201, 1601):
    curve_sum += output_bell_curve_bin_counts[n]

# normalize the curve by dividing by it's sum and removing extreme values
for n in range(201, 1601):
    output_bell_curve_bin_counts[n] /= curve_sum

    # remove extremes (the iterative process mentioned below found 0.008 to work)
    if output_bell_curve_bin_counts[n] > 0.008:
        output_bell_curve_bin_counts[n] = 0.008

##############################################################################

#  Part 8) Construct the USD price finder stencil

##############################################################################

# We now have a bell curve of outputs which should contain round USD outputs
# as it's prominent features. To expose these prominent features even more,
# and estimate a usd price, we slide a stencil over the bell curve and look
# for where the slide location is maximized. There are several stencil designs
# and maximization strategies which could accomplish this. The one used here
# is a stencil whose locations and heights have been found using the averages of
# running this algorithm iteratively over the years 2020-2023. The stencil is
# centered around 0.01 btc = $10,00 as this was the easiest mark to identify.
# The result of this process has produced the following stencil design:


# create an empty stencil the same size as the bell curve
round_usd_stencil = []
for n in range(0, number_of_bins):
    round_usd_stencil.append(0.0)

# fill the round usd stencil with the values found by the process mentioned above
round_usd_stencil[401] = 0.0005957955691168063  # $1
round_usd_stencil[402] = 0.0004454790662303128  # (next one for tx/atm fees)
round_usd_stencil[429] = 0.0001763099393598914  # $1.50
round_usd_stencil[430] = 0.0001851801497144573
round_usd_stencil[461] = 0.0006205616481885794  # $2
round_usd_stencil[462] = 0.0005985696860584984
round_usd_stencil[496] = 0.0006919505728046619  # $3
round_usd_stencil[497] = 0.0008912933078342840
round_usd_stencil[540] = 0.0009372916238804205  # $5
round_usd_stencil[541] = 0.0017125522985034724  # (larger needed range for fees)
round_usd_stencil[600] = 0.0021702347223143030
round_usd_stencil[601] = 0.0037018622326411380  # $10
round_usd_stencil[602] = 0.0027322168706743802
round_usd_stencil[603] = 0.0016268322583097678  # (larger needed range for fees)
round_usd_stencil[604] = 0.0012601953416497664
round_usd_stencil[661] = 0.0041425242880295460  # $20
round_usd_stencil[662] = 0.0039247767475640830
round_usd_stencil[696] = 0.0032399441632017228  # $30
round_usd_stencil[697] = 0.0037112959007355585
round_usd_stencil[740] = 0.0049921908828370000  # $50
round_usd_stencil[741] = 0.0070636869018197105
round_usd_stencil[801] = 0.0080000000000000000  # $100
round_usd_stencil[802] = 0.0065431388282424440  # (larger needed range for fees)
round_usd_stencil[803] = 0.0044279509203361735
round_usd_stencil[861] = 0.0046132440551747015  # $200
round_usd_stencil[862] = 0.0043647851395531140
round_usd_stencil[896] = 0.0031980892880846567  # $300
round_usd_stencil[897] = 0.0034237641632481910
round_usd_stencil[939] = 0.0025995335505435034  # $500
round_usd_stencil[940] = 0.0032631930982226645  # (larger needed range for fees)
round_usd_stencil[941] = 0.0042753262790881080
round_usd_stencil[1001] = 0.0037699501474772350  # $1,000
round_usd_stencil[1002] = 0.0030872891064215764  # (larger needed range for fees)
round_usd_stencil[1003] = 0.0023237040836798163
round_usd_stencil[1061] = 0.0023671764210889895  # $2,000
round_usd_stencil[1062] = 0.0020106877104798474
round_usd_stencil[1140] = 0.0009099214128654502  # $3,000
round_usd_stencil[1141] = 0.0012008546799361498
round_usd_stencil[1201] = 0.0007862586076341524  # $10,000
round_usd_stencil[1202] = 0.0006900048077192579

##############################################################################

#  Part 9) Slide the stencil over the output bell curve to find the best fit

##############################################################################

# This is the final step. We slide the stencil over the bell curve and see
# where it fits the best. The best fit location and it's neighbor are used
# in a weighted average to estimate the best fit USD price


# set up scores for sliding the stencil
best_slide = 0
best_slide_score = 0.0
total_score = 0.0
number_of_scores = 0

# upper and lower limits for sliding the stencil
min_slide = -200
max_slide = 200

# slide the stencil and calculate slide score
for slide in range(min_slide, max_slide):

    # shift the bell curve by the slide
    shifted_curve = output_bell_curve_bin_counts[201 + slide:1401 + slide]

    # score the shift by multiplying the curve by the stencil
    slide_score = 0.0
    for n in range(0, len(shifted_curve)):
        slide_score += shifted_curve[n] * round_usd_stencil[n + 201]

    # increment total and number of scores
    total_score += slide_score
    number_of_scores += 1

    # see if this score is the best so far
    if slide_score > best_slide_score:
        best_slide_score = slide_score
        best_slide = slide

# estimate the usd price of the best slide
usd100_in_btc_best = output_bell_curve_bins[801 + best_slide]
btc_in_usd_best = 100 / (usd100_in_btc_best)

# find best slide neighbor up
neighbor_up = output_bell_curve_bin_counts[201 + best_slide + 1:1401 + best_slide + 1]
neighbor_up_score = 0.0
for n in range(0, len(neighbor_up)):
    neighbor_up_score += neighbor_up[n] * round_usd_stencil[n + 201]

# find best slide neighbor down
neighbor_down = output_bell_curve_bin_counts[201 + best_slide - 1:1401 + best_slide - 1]
neighbor_down_score = 0.0
for n in range(0, len(neighbor_down)):
    neighbor_down_score += neighbor_down[n] * round_usd_stencil[n + 201]

# get best neighbor
best_neighbor = +1
neighbor_score = neighbor_up_score
if neighbor_down_score > neighbor_up_score:
    best_neighbor = -1
    neighbor_score = neighbor_down_score

# get best neighbor usd price
usd100_in_btc_2nd = output_bell_curve_bins[801 + best_slide + best_neighbor]
btc_in_usd_2nd = 100 / (usd100_in_btc_2nd)

# weight average the two usd price estimates
avg_score = total_score / number_of_scores
a1 = best_slide_score - avg_score
a2 = abs(neighbor_score - avg_score)  # theoretically possible to be negative
w1 = a1 / (a1 + a2)
w2 = a2 / (a1 + a2)
price_estimate = int(w1 * btc_in_usd_best + w2 * btc_in_usd_2nd)

# report the price estimate
print("\nThe btc price estimate is: $" + f'{price_estimate:,}')














