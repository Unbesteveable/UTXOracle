
#########################################################################################  
#                                                                                       #
#   /$$   /$$ /$$$$$$$$ /$$   /$$  /$$$$$$                               /$$            #
#  | $$  | $$|__  $$__/| $$  / $$ /$$__  $$                             | $$            #
#  | $$  | $$   | $$   |  $$/ $$/| $$  \ $$  /$$$$$$  /$$$$$$   /$$$$$$$| $$  /$$$$$$   #
#  | $$  | $$   | $$    \  $$$$/ | $$  | $$ /$$__  $$|____  $$ /$$_____/| $$ /$$__  $$  #
#  | $$  | $$   | $$     >$$  $$ | $$  | $$| $$  \__/ /$$$$$$$| $$      | $$| $$$$$$$$  #
#  | $$  | $$   | $$    /$$/\  $$| $$  | $$| $$      /$$__  $$| $$      | $$| $$_____/  #
#  |  $$$$$$/   | $$   | $$  \ $$|  $$$$$$/| $$     |  $$$$$$$|  $$$$$$$| $$|  $$$$$$$  #
#   \______/    |__/   |__/  |__/ \______/ |__/      \_______/ \_______/|__/ \_______/  #
#                                                                                       #
#########################################################################################  
#                     Version 9.1 RPC Only






###############################################################################  

#  Introduction

###############################################################################  

 # Thank you for taking the time to open this. Computer programs have two functions:
 # one for the computer and one for the human. This might be the first time you've
 # attempted to read a computer program. If so, these lines starting with the hash tag
 # are for you. They’ll tell you what the code is doing at all times. The non–hash-tag
 # lines are used by the computer, though if you spend a few seconds with them, 
 # you’ll be able to understand exactly what they’re doing.

 # Since you opened this, you probably already have a good idea of what UTXOracle
 # does. It finds the price of Bitcoin using data only from your own node. It doesn’t
 # contact any third parties. The code also has no third-party dependencies. It runs
 # on the most basic version of Python 3 that you can find. Many operating systems
 # have Python 3 built in, but many don’t. You’ll also need to know how to open a
 # terminal window on your computer. To see if you already have Python 3 installed,
 # open a terminal window and type python3 --version, then hit Enter. If it doesn’t
 # show you a version number, you’ll need to download and install it from python.org.

 # If you’re reading this from a file on your computer, then you already have the
 # program. If you’re reading this off a website, you need to download it to your
 # computer. You can do this by simply typing:

 # If you’re an experienced coder, you’re probably already annoyed by this
 # introduction. That’s because this program is not written for you. This program
 # violates the most basic coder principles. It is a single file that runs top to bottom. 
 # It doesn’t not make use of advanced libraries that would make the code more
 # efficient at the cost of third party dependence. It repeats code for clarity instead of
 # defining functions where the user has to constantly scroll up and down and to
 # other files to see how the function works. The purpose of this code is not for
 # efficiency, or for corporate team implementations. The purpose is to explain how
 # the UTXOracle algorithm works side by side with the code.

 # The code proceeds by completing the following 12 steps in order. Approximate line
 # numbers of the steps are listed for the user to jump directly there if desired.
 
# Step 1 - Configuration Options...................Line 78
# Step 2 - Establish RPC Connection................Line 206
# Step 3 - Check Dates.............................Line 315
# Step 4 - Find Block Hashes.......................Line 409
# Step 5 - Initial Histogram.......................Line 589
# Step 6 - Load Histogram from Transaction Data....Line 646
# Step 7 - Remove Round Bitcoin Amounts............Line 889
# Step 8 - Construct the Price Finding Stencil.....Line 971
# Step 9 - Estimate a Rough Price..................Line 1049
# Step 10 - Create Intraday Price Points...........Line 1160
# Step 11 - Find the Exact Average Price...........Line 1260
# Step 12 - Generate a Price Plot HTML Page........Line 1377




###############################################################################  

# Step 1 - Configuation Options

############################################################################### 

# The way UTXOracle connects to your Bitcoin node depends on your operating
# system and the settings in your bitcoin.conf file. First, the program determines
# your operating system to make an initial guess at the default location of your
# primary Bitcoin directory. If you're not using the default directory, use the -p option
# when running the program to specify the correct block directory.

# Other options let you specify the historical date you want to run (-h) or request the
# price from the most recent 144 blocks (-rb). If you're an advanced user with
# custom settings overriding the default RPC connection, the program will read your
# bitcoin.conf file to use them. Otherwise, it will use the autogenerated cookie file for
# authentication.


# set platform dependent data paths
import platform
import os
data_dir = []
system = platform.system()
if system == "Darwin":  # macOS
    data_dir = os.path.expanduser("~/Library/Application Support/Bitcoin")
elif system == "Windows":
    data_dir = os.path.join(os.environ.get("APPDATA", ""), "Bitcoin")
else:  # Linux or others
    data_dir = os.path.expanduser("~/.bitcoin")

# initialize variables for blocks and dates
date_entered = ""
date_mode = True
block_mode = False
block_start_num = 0
block_finish_num = 0
block_nums_needed = []
block_hashes_needed = []
block_times_needed = []

#print help text for the user if needed
import sys
def print_help():
    help_text = """
Usage: python script.py [options]

Options:
  -h               Show this help message
  -d YYYY/MM/DD    Specify a UTC date to evaluate
  -p /path/to/dir  Specify the data directory for blk files
  -rb              Use last 144 recent blocks instead of date mode
"""
    print(help_text)
    sys.exit(0)

#did use ask for help
if "-h" in sys.argv:
    print_help()
    
#did user specify a date?
if "-d" in sys.argv:
    h_index = sys.argv.index("-d")
    if h_index + 1 < len(sys.argv):
        date_entered = sys.argv[h_index + 1]

#did user specify a data path?
if "-p" in sys.argv:
    d_index = sys.argv.index("-p")
    if d_index + 1 < len(sys.argv):
        data_dir = sys.argv[d_index + 1]

#did user specify blocks instead of a date?
if "-rb" in sys.argv:
    date_mode = False
    block_mode = True

# Look for bitcoin.conf or bitcoin_rw.conf
conf_path = None
conf_candidates = ["bitcoin.conf", "bitcoin_rw.conf"]
for fname in conf_candidates:
    path = os.path.join(data_dir, fname)
    if os.path.exists(path):
        conf_path = path
        break
if not conf_path:
    print(f"Invalid Bitcoin data directory: {data_dir}")
    print("Expected to find 'bitcoin.conf' or 'bitcoin_rw.conf' in this directory.")
    sys.exit(1)

# Parse the conf file
conf_settings = {}
with open(conf_path, 'r') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            conf_settings[key.strip()] = value.strip().strip('"')

# Set blocks directory
blocks_dir = os.path.expanduser(conf_settings.get("blocksdir", os.path.join(data_dir, "blocks")))

# Prepare RPC parameters
rpc_user = conf_settings.get("rpcuser")
rpc_password = conf_settings.get("rpcpassword")
cookie_path = conf_settings.get("rpccookiefile", os.path.join(data_dir, ".cookie"))
rpc_host = conf_settings.get("rpcconnect", "127.0.0.1")
rpc_port = int(conf_settings.get("rpcport", "8332"))

# Prepare bitcoin-cli fallback options (if needed elsewhere)
bitcoin_cli_options = []
if rpc_user and rpc_password:
    bitcoin_cli_options.append(f"-rpcuser={rpc_user}")
    bitcoin_cli_options.append(f"-rpcpassword={rpc_password}")
else:
    if os.path.exists(cookie_path):
        bitcoin_cli_options.append(f"-rpccookiefile={cookie_path}")

if rpc_host:
    bitcoin_cli_options.append(f"-rpcconnect={rpc_host}")
if "rpcport" in conf_settings:
    bitcoin_cli_options.append(f"-rpcport={conf_settings['rpcport']}")




###############################################################################  

#  Step 2 - Establish RPC Connection

###############################################################################  

# Community consensus has established that RPC should be the standard front door
# through which other programs communicate with your Bitcoin node. Since we'll be
# making repeated requests to the node, we define a general function that attaches
# the necessary RPC credentials to any command we send and returns the
# response to where it's needed in the program. If this is the first time you've used
# RPC, the function will create the RPC cookie file using the node's default method.
# Otherwise, it simply returns the result of the command and prints any errors
# encountered. After defining the Ask_Node function, we test it by requesting the
# latest block the node has received.


print("\nCurrent operation  \t\t\t\tTotal Completion",flush=True)
print("\nConnecting to node...",flush=True)
print("0%..", end="",flush=True)

# define the node communication function
import http.client
import json
import base64

def Ask_Node(command, cred_creation):
    method = command[0]
    params = command[1:]

    # Handle authentication
    rpc_u = rpc_user
    rpc_p = rpc_password

    if not rpc_u or not rpc_p:
        try:
            with open(cookie_path, "r") as f:
                cookie = f.read().strip()
                rpc_u, rpc_p = cookie.split(":", 1)
        except Exception as e:
            print("Error reading .cookie file for RPC authentication.")
            print("Details:", e)
            sys.exit(1)

    # Prepare JSON-RPC payload
    payload = json.dumps({
        "jsonrpc": "1.0",
        "id": "utxoracle",
        "method": method,
        "params": params
    })

    # Basic auth header
    auth_header = base64.b64encode(f"{rpc_u}:{rpc_p}".encode()).decode()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {auth_header}"
    }

    try:
        conn = http.client.HTTPConnection(rpc_host, rpc_port)
        conn.request("POST", "/", payload, headers)
        response = conn.getresponse()
        if response.status != 200:
            raise Exception(f"HTTP error {response.status} {response.reason}")
        raw_data = response.read()
        conn.close()

        # Extract result and mimic `subprocess.check_output` return (as bytes)
        parsed = json.loads(raw_data)
        if parsed.get("error"):
            raise Exception(parsed["error"])
        result = parsed["result"]
        if isinstance(result, (dict, list)):
            return json.dumps(result, indent=2).encode()  # pretty-print like CLI
        else:
            return str(result).encode()

    except Exception as e:
        if not cred_creation:
            print("Error connecting to your node via RPC. Troubleshooting steps:\n")
            print("\t1) Ensure bitcoind or bitcoin-qt is running with server=1.")
            print("\t2) Check rpcuser/rpcpassword or .cookie.")
            print("\t3) Verify RPC port/host settings.")
            print("\nThe attempted RPC method was:", method)
            print("Parameters:", params)
            print("\nThe error was:\n", e)
            sys.exit(1)


#get current block height from local node and exit if connection not made
print("20%..", end="",flush=True)
Ask_Node(['getblockcount'], True) #create RPC creds if necessary
block_count_b = Ask_Node(['getblockcount'], False)
print("40%..", end="",flush=True)
block_count = int(block_count_b)             #convert text to integer
block_count_consensus = block_count-6

#get block header from current block height
#block_hash = Ask_Node(['getblockhash', str(block_count_consensus)]).decode().strip()
block_hash = Ask_Node(['getblockhash',block_count_consensus], False).decode().strip()
print("60%..", end="",flush=True)
block_header_b = Ask_Node(['getblockheader', block_hash, True], False)
block_header = json.loads(block_header_b)
print("80%..", end="",flush=True)




###############################################################################  

# Step 3 - Check Dates  

############################################################################### 

# The Bitcoin price does not exist instantaneously on-chain. A single block often
# does not contain enough transaction data to determine the price—and in some
# cases, may contain no transactions at all. For this reason, a time-averaging
# window is required to accumulate sufficient data to estimate the price accurately.

# While many averaging windows could work, a single day is both a natural human
# time scale and typically includes enough transaction activity. For accounting and
# historical purposes, daily resolution is also a commonly used standard. Therefore, 
# UTXOracle uses the daily average as its default time window for determining price.

# This means UTXOracle must know two things: (1) the most recent date covered by 
# the node’s block data, and (2) the date the user is requesting the price for. If the 
# requested date is too far in the past or future relative to the available data, an error 
# message will be displayed. The earliest supported date depends on how far back 
# the current version of UTXOracle has been tested.



#import built in tools for dates/times and json style lists
from datetime import datetime, timezone, timedelta



#get the date and time of the current block height
latest_time_in_seconds = block_header['time']
time_datetime = datetime.fromtimestamp(latest_time_in_seconds,tz=timezone.utc)

#get the date/time of utc midnight on the latest day
latest_year  = int(time_datetime.strftime("%Y"))
latest_month = int(time_datetime.strftime("%m"))
latest_day   = int(time_datetime.strftime("%d"))
latest_utc_midnight = datetime(latest_year,latest_month,latest_day,0,0,0,tzinfo=timezone.utc)

#assign the day before as the latest possible price date
seconds_in_a_day = 60*60*24
yesterday_seconds = latest_time_in_seconds - seconds_in_a_day
latest_price_day = datetime.fromtimestamp(yesterday_seconds,tz=timezone.utc)
latest_price_date = latest_price_day.strftime("%Y-%m-%d")
print("100%", end="",flush=True)

#print completion update
print("\t\t\t5% done",flush=True)


# If running in date mode, make sure that the date requested is in the
if date_mode:

    # run latest day if hit enter
    if (date_entered == ""):
        datetime_entered = latest_utc_midnight + timedelta(days=-1)
        
    #user entered a specific date
    else:
        
        #check to see if this is a good date
        try:
            year  = int(date_entered.split('/')[0])
            month = int(date_entered.split('/')[1])
            day = int(date_entered.split('/')[2])
            
            #make sure this date is less than the max date
            datetime_entered = datetime(year,month,day,0,0,0,tzinfo=timezone.utc)
            if datetime_entered.timestamp() >= latest_utc_midnight.timestamp():
                print("\nDate is after the latest avaiable. We need 6 blocks after UTC midnight.")
                print("Run UTXOracle.py -rb for the most recent blocks")
                
                sys.exit()
            
            #make sure this date is after the min date
            dec_15_2023 = datetime(2023,12,15,0,0,0,tzinfo=timezone.utc)
            if datetime_entered.timestamp() < dec_15_2023.timestamp():
                print("\nThe date entered is before 2023-12-15, please try again")
                sys.exit()
        
        except:
            print("\nError interpreting date. Please try again. Make sure format is YYYY/MM/DD")
            sys.exit()
    
    
    #get the seconds and printable date string of date entered
    price_day_seconds = int(datetime_entered.timestamp())
    price_day_date_utc = datetime_entered.strftime("%b %d, %Y")
    price_date_dash = datetime_entered.strftime("%Y-%m-%d")
    




##############################################################################  

# Step 4 - Find Block Hashes

##############################################################################  

# Bitcoin nodes don’t store blocks by date—or even by block height. Instead, they 
# store blocks by their hash. This has two implications: first, we need to know which 
# block heights we're looking for, and second, we must retrieve the corresponding 
# block hashes for those heights.

# The task is simpler when running in block mode (-rb), where we determine the 
# needed blocks by subtracting 144 from the most recent block height. In date mode, 
# however, the process is more involved, as we must enter a guess-and-check loop 
# to determine which blocks correspond to the desired calendar day.

# Since blocks are mined roughly every ten minutes, we can use that as a guideline. 
# When a user enters a date, we first estimate how many blocks ago that date 
# occurred. We then check block timestamps starting from our estimate, moving 
# forward to find the last block of that day, and backward to find the first block.

# Once we’ve identified all the relevant block heights, we store the hashes of each 
# block in a list so that we can retrieve them one by one in the next step.



#define a shortcut for getting the block time from the block number
def get_block_time(height):
    block_hash_b = Ask_Node(['getblockhash',height], False)
    #block_header_b = Ask_Node(['getblockheader',block_hash_b[:64],True])
    block_header_b = Ask_Node(['getblockheader', block_hash_b.decode().strip(), True], False)

    block_header = json.loads(block_header_b)
    return(block_header['time'], block_hash_b[:64].decode())

#define a shortcut for getting the day of money from a time in seconds
def get_day_of_month(time_in_seconds):
    time_datetime = datetime.fromtimestamp(time_in_seconds,tz=timezone.utc)
    return(int(time_datetime.strftime("%d")))

#if block mode add the blocks and hashes to a list
if block_mode:
    
    print("\nFinding the last 144 blocks",flush=True)
    
    #get the last block number of the day
    block_finish_num = block_count
    block_start_num = block_finish_num - 144
    
    #append needed block nums and hashes needed
    block_num = block_start_num
    time_in_seconds, hash_end = get_block_time(block_start_num)
    print_every = 0
    while block_num < block_finish_num:
        
        #print update
        if (block_num-block_start_num)/144*100 > print_every and print_every < 100:
            print(str(print_every)+"%..",end="",flush=True)
            print_every += 20
        block_nums_needed.append(block_num)
        block_hashes_needed.append(hash_end)
        block_times_needed.append(time_in_seconds)
        block_num += 1
        time_in_seconds, hash_end = get_block_time(block_num)
        
    print("100%\t\t\t25% done",flush=True)

#if date mode search for all the blocks on this day
elif date_mode:
    
    print("\nFinding first blocks on "+datetime_entered.strftime("%b %d, %Y"),flush=True)
    print("0%..",end="", flush=True)
    #first estimate of the block height of the price day
    seconds_since_price_day = latest_time_in_seconds - price_day_seconds
    blocks_ago_estimate = round(144*float(seconds_since_price_day)/float(seconds_in_a_day))
    price_day_block_estimate = block_count_consensus - blocks_ago_estimate
    
    #check the time of the price day block estimate
    time_in_seconds, hash_end = get_block_time(price_day_block_estimate) 
    
    #get new block estimate from the seconds difference using 144 blocks per day
    print("20%..",end="",flush=True)
    seconds_difference = time_in_seconds - price_day_seconds
    block_jump_estimate = round(144*float(seconds_difference)/float(seconds_in_a_day))
    
    #iterate above process until it oscillates around the correct block
    last_estimate = 0
    last_last_estimate = 0
    
    print("40%..",end="",flush=True)
    while block_jump_estimate >6 and block_jump_estimate != last_last_estimate:
        
        #when we oscillate around the correct block, last_last_estimate = block_jump_estimate
        last_last_estimate = last_estimate
        last_estimate = block_jump_estimate
        
        #get block header or new estimate
        price_day_block_estimate = price_day_block_estimate-block_jump_estimate
        
        #check time of new block and get new block jump estimate
        time_in_seconds, hash_end = get_block_time(price_day_block_estimate) 
        seconds_difference = time_in_seconds - price_day_seconds
        block_jump_estimate = round(144*float(seconds_difference)/float(seconds_in_a_day))
    
    print("60%..",end="",flush=True)
    #the oscillation may be over multiple blocks so we add/subtract single blocks 
    #to ensure we have exactly the first block of the target day
    if time_in_seconds > price_day_seconds:
        
        # if the estimate was after price day look at earlier blocks
        while time_in_seconds > price_day_seconds:
            
            #decrement the block by one, read new block header, check time
            price_day_block_estimate = price_day_block_estimate-1
            time_in_seconds, hash_end = get_block_time(price_day_block_estimate) 
            
        #the guess is now perfectly the first block before midnight
        price_day_block_estimate = price_day_block_estimate + 1
        
    # if the estimate was before price day look for later blocks
    elif time_in_seconds < price_day_seconds:
        
        while time_in_seconds < price_day_seconds:
            
            #increment the block by one, read new block header, check time
            price_day_block_estimate = price_day_block_estimate+1
            time_in_seconds, hash_end = get_block_time(price_day_block_estimate) 
    
    print("80%..",end="",flush=True)
    #assign the estimate as the price day block since it is correct now    
    price_day_block = price_day_block_estimate
    
    #get the day of the month 
    time_in_seconds, hash_start = get_block_time(price_day_block)
    day1 = get_day_of_month(time_in_seconds)
    
    #get the last block number of the day
    price_day_block_end = price_day_block 
    time_in_seconds, hash_end = get_block_time(price_day_block_end)
    day2 = get_day_of_month(time_in_seconds)
    
    print("100%\t\t\t25% done",flush=True)
    print("\nFinding last blocks on "+datetime_entered.strftime("%b %d, %Y"),flush=True)
    
    #load block nums and hashes needed
    block_num = 0
    print_next = 0
    while day1 == day2:
        
        #print progress update
        block_num+=1
        if block_num/144 * 100 > print_next:
            if print_next < 100:
                print(str(print_next)+"%..",end="",flush=True)
                print_next +=20
        
        #append needed block
        block_nums_needed.append(price_day_block_end)
        block_hashes_needed.append(hash_end)
        block_times_needed.append(time_in_seconds)
        price_day_block_end += 1 #assume 30+ blocks this day
        time_in_seconds, hash_end = get_block_time(price_day_block_end)
        day2 = get_day_of_month(time_in_seconds)
    
    #complete print update status
    while print_next<100:
        print(str(print_next)+"%..",end="",flush=True)
        print_next +=20
    
    #set start and end block numbers
    block_start_num = price_day_block
    block_finish_num = price_day_block_end

    print("100%\t\t\t50% done",flush=True)






##############################################################################

# Step 5 - Initial histogram

##############################################################################

# Just as the price of Bitcoin does not exist at a single instant in time, it also does not 
# exist at a single satoshi amount. The on-chain price emerges because users tend 
# to spend Bitcoin in round fiat amounts. To detect this, we create a histogram that 
# reveals clusters of satoshi values where round fiat amounts are most likely to 
# occur.

# We divide the BTC value range into intervals and count how many transaction 
# outputs fall into each interval. This allows us to visualize where spending patterns 
# cluster. If the intervals are too small, the data becomes noisy; if they’re too large, 
# important detail is lost. A rough estimate of the ideal interval width is the average 
# daily fiat volatility, which we’ve found to be around 0.5%—corresponding to roughly 
# 200 intervals between each power of ten in BTC.

# We must also define the upper and lower bounds of the histogram: the smallest 
# and largest BTC amounts likely to capture typical round fiat values. This range will 
# evolve as Bitcoin’s purchasing power changes and may need to be updated in 
# future versions of UTXOracle. From 2020 to 2025, we’ve found that most round fiat 
# amounts fall within the range of 10^-6 to 10^6 BTC.

# Once the range and interval size are established, we generate arrays representing 
# the edges of each interval and initialize a corresponding array of zeros to count 
# how many transaction outputs fall into each bucket.


# Define the maximum and minimum values (in log10) of btc amounts to use
first_bin_value = -6
last_bin_value = 6  #python -1 means last in list
range_bin_values = last_bin_value - first_bin_value 

# create a list of output_histogram_bins and add zero sats as the first bin
output_histogram_bins = [0.0] #a decimal tells python the list will contain decimals

# calculate btc amounts of 200 samples in every 10x from 100 sats (1e-6 btc) to 100k (1e5) btc
for exponent in range(-6,6): #python range uses 'less than' for the big number 
    
    #add 200 bin_width increments in this 10x to the list
    for b in range(0,200):
        
        bin_value = 10 ** (exponent + b/200)
        output_histogram_bins.append(bin_value)

# Create a list the same size as the bell curve to keep the count of the bins
number_of_bins = len(output_histogram_bins)
output_histogram_bin_counts = []
for n in range(0,number_of_bins):
    output_histogram_bin_counts.append(float(0.0))





##############################################################################

#  Step 6 -  Load Transaction Data

##############################################################################

# This section of the algorithm is the most time-consuming because it reads every 
# transaction from the range of blocks requested by the user. We typically need 
# around 144 blocks, and since each block is roughly 1MB, this means processing 
# about 144 MB of data.

# To improve efficiency, we request the raw binary block data and manually convert it 
# into integers and strings. This requires defining functions that translate binary data 
# into integers, such as read_varint and encode_varint. We also compute the txid 
# manually, since binary Bitcoin blocks do not store it directly.

# After defining these functions, we loop through the list of required block hashes 
# and extract transaction output amounts to place into histogram bins. We apply 
# several filters to exclude transactions that are unlikely to reflect meaningful price 
# information.

# Through years of testing we decided to filter out transactions containing: more than 
# 5 inputs, more than 2 outputs, coinbase outputs, op_return outputs, large witness 
# scripts, and same day inputs. If the output passes the filters, it is inserted into the 
# histogram bin according to the bitcoin amount of the output.


print("\nLoading every transaction from every block",flush=True)



# #initialize output lists and variables
from struct import unpack
import binascii
todays_txids = set()
raw_outputs = []
block_heights_dec = []
block_times_dec = []
print_next = 0
block_num = 0


#shortcut for reading bytes of data from the block file
import struct
from math import log10 
import hashlib
def read_varint(f):
    i = f.read(1)
    if not i:
        return 0
    i = i[0]
    if i < 0xfd:
        return i
    elif i == 0xfd:
        val = struct.unpack("<H", f.read(2))[0]
    elif i == 0xfe:
        val = struct.unpack("<I", f.read(4))[0]
    else:
        val = struct.unpack("<Q", f.read(8))[0]
    return val

#shortcut for encoding variable size integers to bytes
from io import BytesIO
def encode_varint(i: int) -> bytes:
    assert i >= 0
    if i < 0xfd:
        return i.to_bytes(1, 'little')
    elif i <= 0xffff:
        return b'\xfd' + i.to_bytes(2, 'little')
    elif i <= 0xffffffff:
        return b'\xfe' + i.to_bytes(4, 'little')
    else:
        return b'\xff' + i.to_bytes(8, 'little')

#shortcut for computing the txid because blk files don't store txids
def compute_txid(raw_tx_bytes: bytes) -> bytes:
    
    stream = BytesIO(raw_tx_bytes)

    # Read version
    version = stream.read(4)

    # Peek at marker/flag to detect SegWit
    marker = stream.read(1)
    flag = stream.read(1)
    is_segwit = (marker == b'\x00' and flag == b'\x01')

    if not is_segwit:
        # Legacy tx: rewind and hash full raw tx
        stream.seek(0)
        stripped_tx = stream.read()
    else:
        # Start stripped tx with version
        stripped_tx = bytearray()
        stripped_tx += version

        # Inputs
        input_count = read_varint(stream)
        stripped_tx += encode_varint(input_count)
        for _ in range(input_count):
            stripped_tx += stream.read(32)  # prev txid
            stripped_tx += stream.read(4)   # vout index
            script_len = read_varint(stream)
            stripped_tx += encode_varint(script_len)
            stripped_tx += stream.read(script_len)
            stripped_tx += stream.read(4)   # sequence

        # Outputs
        output_count = read_varint(stream)
        stripped_tx += encode_varint(output_count)
        for _ in range(output_count):
            stripped_tx += stream.read(8)   # value
            script_len = read_varint(stream)
            stripped_tx += encode_varint(script_len)
            stripped_tx += stream.read(script_len)

        # Skip witness data
        for _ in range(input_count):
            stack_count = read_varint(stream)
            for _ in range(stack_count):
                item_len = read_varint(stream)
                stream.read(item_len)

        # Locktime
        stripped_tx += stream.read(4)

    return hashlib.sha256(hashlib.sha256(stripped_tx).digest()).digest()[::-1]


# read in all blocks needed
for bh in block_hashes_needed:
    block_num += 1
    print_progress = block_num / len(block_hashes_needed) * 100
    if print_progress > print_next and print_next < 100:
        #print(f"{int(print_next)}% ", end="", flush=True)
        print(f"{int(print_next)}%..",end="",flush=True)
        print_next += 1
        if print_next % 7 == 0:
            print("\n", end="")

    # Get raw block hex using RPC
    raw_block_hex = Ask_Node(["getblock", bh, 0], False).decode().strip()
    raw_block_bytes = binascii.unhexlify(raw_block_hex)
    stream = BytesIO(raw_block_bytes)

    # Read header (skip 80 bytes)
    stream.read(80)
    tx_count = read_varint(stream)
    
    # loop through all txs in this block
    txs_to_add = []
    for tx_index in range(tx_count):
        start_tx = stream.tell()
        version = stream.read(4)

        # Check for SegWit
        marker_flag = stream.read(2)
        is_segwit = marker_flag == b'\x00\x01'
        if not is_segwit:
            stream.seek(start_tx + 4)

        # Read inputs
        input_count = read_varint(stream)
        inputs = []
        has_op_return = False
        witness_exceeds = False
        is_coinbase = False
        input_txids = []
        for _ in range(input_count):
            prev_txid = stream.read(32)
            prev_index = stream.read(4)
            script_len = read_varint(stream)
            script = stream.read(script_len)
            stream.read(4)
            input_txids.append(prev_txid[::-1].hex())
            if prev_txid == b'\x00' * 32 and prev_index == b'\xff\xff\xff\xff':
                is_coinbase = True
            inputs.append({"script": script})

        #read outputs
        output_count = read_varint(stream)
        output_values = []
        for _ in range(output_count):
            value_sats = unpack("<Q", stream.read(8))[0]
            script_len = read_varint(stream)
            script = stream.read(script_len)
            if script and script[0] == 0x6a:
                has_op_return = True
            value_btc = value_sats / 1e8
            if 1e-5 < value_btc < 1e5:
                output_values.append(value_btc)

        # check witness data
        if is_segwit:
            for input_data in inputs:
                stack_count = read_varint(stream)
                total_witness_len = 0
                for _ in range(stack_count):
                    item_len = read_varint(stream)
                    total_witness_len += item_len
                    stream.read(item_len)
                    if item_len > 500 or total_witness_len > 500:
                        witness_exceeds = True

        #comput txid
        stream.read(4)
        end_tx = stream.tell()
        stream.seek(start_tx)
        raw_tx = stream.read(end_tx - start_tx)
        txid = compute_txid(raw_tx)
        todays_txids.add(txid.hex())

        #check same day tx
        is_same_day_tx = any(itxid in todays_txids for itxid in input_txids)

        # apply filter and add output to bell curve
        if (input_count <= 5 and output_count == 2 and not is_coinbase and
            not has_op_return and not witness_exceeds and not is_same_day_tx):
            for amount in output_values:
                amount_log = log10(amount)
                percent_in_range = (amount_log - first_bin_value) / range_bin_values
                bin_number_est = int(percent_in_range * number_of_bins)
                while output_histogram_bins[bin_number_est] <= amount:
                    bin_number_est += 1
                bin_number = bin_number_est - 1
                output_histogram_bin_counts[bin_number] += 1.0
                txs_to_add.append(amount)

    # add outputs to raw outputs
    if len(txs_to_add) > 0:
        bkh = block_nums_needed[block_num - 1]
        tm = block_times_needed[block_num - 1]
        for amt in txs_to_add:
            raw_outputs.append(amt)
            block_heights_dec.append(bkh)
            block_times_dec.append(tm)


print("100%",flush=True)
print("\t\t\t\t\t\t95% done",flush=True)

            

##############################################################################

#  Step 7 - Remove Round Bitcoin Amounts

##############################################################################

# Although most transaction amounts are related to fiat purchasing power, spending 
# round Bitcoin amounts is still common. This makes it difficult to determine whether 
# a histogram interval is truly capturing a round fiat value or simply reflecting a round 
# BTC amount.

# We can't completely remove round BTC amounts, because when the fiat price of 
# Bitcoin is near a round number, round BTC and round fiat values can overlap. 
# Instead of removing these intervals, we smooth them by averaging the values of 
# the histogram bins directly above and below the round BTC amounts.

# After smoothing, we normalize the histogram by dividing each bin by the total sum. 
# This converts the histogram into percentages rather than raw counts. Percentages 
# are more stable across days with unusually high or low transaction volume, making 
# the resulting signal more consistent.



# print update
print("\nFinding prices and rendering plot",flush=True)
print("0%..",end="",flush=True)

#remove outputs below 10k sat (increased from 1k sat in v6)
for n in range(0,201):
    output_histogram_bin_counts[n]=0

#remove outputs above ten btc
for n in range(1601,len(output_histogram_bin_counts)):
    output_histogram_bin_counts[n]=0

#create a list of round btc bin numbers
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
1001, # 0.1 
1061, # 0.2
1096, # 0.3
1140, # 0.5
1201  # 1 btc
]

#smooth over the round btc amounts
for r in round_btc_bins:
    amount_above = output_histogram_bin_counts[r+1]
    amount_below = output_histogram_bin_counts[r-1]
    output_histogram_bin_counts[r] = .5*(amount_above+amount_below)

#get the sum of the curve
curve_sum = 0.0
for n in range(201,1601):
    curve_sum += output_histogram_bin_counts[n]

#normalize the curve by dividing by it's sum and removing extreme values
for n in range(201,1601):
    output_histogram_bin_counts[n] /= curve_sum
    
    #remove extremes (0.008 chosen by historical testing)
    if output_histogram_bin_counts[n] > 0.008:
        output_histogram_bin_counts[n] = 0.008

#print update    
print("20%..",end="",flush=True)




##############################################################################

#  Step 8 - Construct the Price Finding Stencil

##############################################################################

# Users don’t just send round fiat amounts, they also tend to send them in 
# predictable proportions depending on the amount. For example, users spend $100 
# far more often than they send $10,000. We use this proportionality both to lock 
# onto round fiat amounts and to determine which amount is which.

# Through historical testing, we’ve measured the average histogram bin counts for 
# each common round fiat amount and hard-code these values into what we call a 
# price-finding stencil. The most common and heavily weighted amount in the stencil 
# is $100. Less frequently used fiat amounts are assigned lower weights, since we 
# expect to see them transacted less often.

# Even when users are not transacting at a perfectly round fiat amount, their 
# behavior is still influenced by Bitcoin’s long-term rise in purchasing power. For 
# example, if we plot a bell curve of output amounts, we find that the center of the 
# curve shifts toward smaller BTC amounts over time.

# This provides additional information we can use. We first apply a smooth stencil to 
# estimate a center of gravity for the price within a broad 20% range. Then, we apply 
# a spike stencil based on perfectly round USD amounts to refine the price estimate 
# to within about 0.5%.


# Parameters
num_elements = 803
mean = 411 #(num_elements - 1) / 2  # Center of the array
std_dev = 201

#contstruct the smooth stencil
smooth_stencil = []
for x in range(num_elements):
    exp_part = -((x - mean) ** 2) / (2 * (std_dev ** 2))
    smooth_stencil.append( (.00150 * 2.718281828459045 ** exp_part) + (.0000005 * x) )

# Load the spike stencil that fine tunes the alignment on popular usd amounts

spike_stencil = []
for n in range(0,803):
    spike_stencil.append(0.0)
    
#round usd bin location   #popularity    #usd amount  
spike_stencil[40] = 0.001300198324984352  # $1
spike_stencil[141]= 0.001676746949820743  # $5
spike_stencil[201]= 0.003468805546942046  # $10
spike_stencil[202]= 0.001991977522512513  # 
spike_stencil[236]= 0.001905066647961839  # $15
spike_stencil[261]= 0.003341772718156079  # $20
spike_stencil[262]= 0.002588902624584287  # 
spike_stencil[296]= 0.002577893841190244  # $30
spike_stencil[297]= 0.002733728814200412  # 
spike_stencil[340]= 0.003076117748975647  # $50
spike_stencil[341]= 0.005613067550103145  # 
spike_stencil[342]= 0.003088253178535568  # 
spike_stencil[400]= 0.002918457489366139  # $100
spike_stencil[401]= 0.006174500465286022  # 
spike_stencil[402]= 0.004417068070043504  # 
spike_stencil[403]= 0.002628663628020371  # 
spike_stencil[436]= 0.002858828161543839  # $150
spike_stencil[461]= 0.004097463611984264  # $200
spike_stencil[462]= 0.003345917406120509  # 
spike_stencil[496]= 0.002521467726855856  # $300
spike_stencil[497]= 0.002784125730361008  # 
spike_stencil[541]= 0.003792850444811335  # $500
spike_stencil[601]= 0.003688240815848247  # $1000
spike_stencil[602]= 0.002392400117402263  # 
spike_stencil[636]= 0.001280993059008106  # $1500
spike_stencil[661]= 0.001654665137536031  # $2000
spike_stencil[662]= 0.001395501347054946  # 
spike_stencil[741]= 0.001154279140906312  # $5000
spike_stencil[801]= 0.000832244504868709  # $10000



##############################################################################

#  Step 9 - Estimate a Rough Price

##############################################################################

# To find where the smooth and spiked stencils fit best over the output histogram, we 
# slide the stencils across the histogram and calculate a score at each position. 
# There are several ways to do this, but the method we have found most effective is 
# to multiply the stencil heights by the histogram values at each point and sum the 
# result.

# We define upper and lower bounds for the slide range, which set the maximum and 
# minimum possible prices. These limits will need to be updated in future versions of 
# UTXOracle as Bitcoin’s purchasing power changes. We also assign a relative 
# weight to the smooth stencil compared to the spiked stencil. Historical testing has 
# shown that a weighting ratio of 0.65 to 1 gives the best results.

# Once the stencils have been slid across the full range, we identify the position with 
# the highest score. This gives us a rough estimate of the price, accurate to within 
# about 0.5 percent.



# set up scores for sliding the stencil
best_slide        = 0
best_slide_score  = 0
total_score       = 0

#weighting of the smooth and spike slide scores
smooth_weight     = 0.65
spike_weight      = 1

#establish the center slide such that if zero slide then 0.001 btc is $100 ($100k price)
center_p001 = 601   # 601 is where 0.001 btc is in the output bell curve
left_p001   = center_p001 - int((len(spike_stencil) +1)/2)
right_p001  = center_p001 + int((len(spike_stencil) +1)/2)

#upper and lower limits for sliding the stencil
min_slide = -141   # $500k
max_slide =  201   # $5k
    
#slide the stencil and calculate slide score
for slide in range(min_slide,max_slide):
    
    #shift the bell curve by the slide
    shifted_curve = output_histogram_bin_counts[left_p001+slide:right_p001+slide]
    
    #score the smoothslide by multiplying the curve by the stencil
    slide_score_smooth = 0.0
    for n in range(0,len(smooth_stencil)):
        slide_score_smooth += shifted_curve[n]*smooth_stencil[n]
    
    #score the spiky slide by multiplying the curve by the stencil
    slide_score = 0.0
    for n in range(0,len(spike_stencil)):
        slide_score += shifted_curve[n]*spike_stencil[n]
    
    # add the spike and smooth slide scores, neglect smooth slide over wrong regions
    if slide < 150:
        slide_score = slide_score + slide_score_smooth*.65
        
    # see if this score is the best so far
    if slide_score > best_slide_score:
        best_slide_score = slide_score
        best_slide = slide
    
    # increment the total score
    total_score += slide_score
        
# estimate the usd price of the best slide
usd100_in_btc_best = output_histogram_bins[center_p001+best_slide]
btc_in_usd_best = 100/(usd100_in_btc_best)

#find best slide neighbor up
neighbor_up = output_histogram_bin_counts[left_p001+best_slide+1:right_p001+best_slide+1]
neighbor_up_score = 0.0
for n in range(0,len(spike_stencil)):
    neighbor_up_score += neighbor_up[n]*spike_stencil[n]

#find best slide neighbor down
neighbor_down = output_histogram_bin_counts[left_p001+best_slide-1:right_p001+best_slide-1]
neighbor_down_score = 0.0
for n in range(0,len(spike_stencil)):
    neighbor_down_score += neighbor_down[n]*spike_stencil[n]

#get best neighbor
best_neighbor = +1
neighbor_score = neighbor_up_score
if neighbor_down_score > neighbor_up_score:
    best_neighbor = -1
    neighbor_score = neighbor_down_score

#get best neighbor usd price
usd100_in_btc_2nd = output_histogram_bins[center_p001+best_slide+best_neighbor]
btc_in_usd_2nd = 100/(usd100_in_btc_2nd)

#weight average the two usd price estimates
avg_score = total_score/len(range(min_slide,max_slide))
a1 = best_slide_score - avg_score
a2 = abs(neighbor_score - avg_score)
w1 = a1/(a1+a2)
w2 = a2/(a1+a2)
rough_price_estimate = int(w1*btc_in_usd_best + w2*btc_in_usd_2nd)

# Print update
print("40%..",end="",flush=True)




##############################################################################

#  Step 10 - Create Intraday Price Points

##############################################################################

# Using the rough price estimate and the known common fiat spending amounts, we 
# create a window and assign a rough fiat price to every Bitcoin output. The rough 
# price does not need to be exact, because the center of mass within this window 
# shows how the estimate needs to be refined in order to calculate the precise 
# average.

# We set the maximum allowed range of price refinement to 25 percent in either 
# direction. This range accounts for possible errors in the rough estimate, especially 
# on highly volatile fiat price days. Note that this does not mean UTXOracle can only 
# handle 25 percent daily price swings. The rough price estimate already captures 
# most of the daily volatility, so the remaining error is usually much smaller.

# As we did when finding the rough estimate, we need to remove round BTC 
# amounts before refining. However, since we are not inserting outputs into a 
# histogram at this stage, we cannot simply smooth over histogram bins. Instead, we 
# identify and exclude round BTC amounts by checking whether an output falls within 
# a narrow range around common round BTC values.



# list of round USD prices to collect outputs from
usds = [5,10,15,20,25,30,40,50,100,150,200,300,500,1000]

# pct of price increase of decrease to include
pct_range_wide = .25

# filter for micro round satoshi amounts
micro_remove_list = []
i = .00005000
while i<.0001:
    micro_remove_list.append(i)
    i += .00001
i = .0001
while i<.001:
    micro_remove_list.append(i)
    i += .00001
i = .001
while i<.01:
    micro_remove_list.append(i)
    i += .0001
i = .01
while i<.1:
    micro_remove_list.append(i)
    i += .001
i = .1
while i<1:
    micro_remove_list.append(i)
    i += .01
pct_micro_remove = .0001

# init output prices list
output_prices = []
output_blocks = []
output_times = []

#loop through all outputs
for i in range (0,len(raw_outputs)):
    
    #get the amount, height and time of the next output
    n = raw_outputs[i]
    b = block_heights_dec[i]
    t = block_times_dec[i]
    
    #loop throughll usd amounts possible
    for usd in usds:
        
        #calculate the upper and lower bounds for the USD range
        avbtc = usd/rough_price_estimate
        btc_up = avbtc + pct_range_wide * avbtc 
        btc_dn = avbtc - pct_range_wide * avbtc
    
        # check if inside price bounds
        if btc_dn < n < btc_up:
            append = True
            
            #remove perfectly round sats
            for r in micro_remove_list:
                
                rm_dn = r - pct_micro_remove * r
                rm_up = r + pct_micro_remove * r
                if rm_dn < n < rm_up:
                    append = False
            
            # if in price range and not perfectly round sat, add to list
            if append:
                output_prices.append(usd/n)
                output_blocks.append(b)
                output_times.append(t)

print("60%..",end="",flush=True)




##############################################################################

#  Step 11 - Find the Exact Average Price

##############################################################################

# We find the exact average price using an iterative procedure that locates the 
# central output within the cluster of rough intraday price points. The algorithm 
# calculates the center of mass of the intraday price points and shifts the price 
# estimate toward this center.

# As the window shifts, price points drop out on one side and new ones are added on 
# the other. This changes the distribution, so the center of mass must be recalculated 
# each time. By repeating this process, one of two outcomes will occur: either the 
# center price will converge to a single stable value, or it will begin to oscillate in a 
# repeating pattern, shifting up and down by fixed amounts.

# The final exact price is determined by one of two conditions: A) the converged 
# center price, or B) the first central value where stable oscillation begins.


# define an algorithm for finding the central price point and avg deviation
def find_central_output(r2, price_min, price_max):
    
    #sort the list of prices
    r6 = [r for r in r2 if price_min < r < price_max]
    outputs = sorted(r6)
    n = len(outputs)

    # Prefix sums
    prefix_sum = []
    total = 0
    for x in outputs:
        total += x
        prefix_sum.append(total)

    # count the number of point left and right
    left_counts = list(range(n))
    right_counts = [n - i - 1 for i in left_counts]
    left_sums = [0] + prefix_sum[:-1]
    right_sums = [total - x for x in prefix_sum]

    # find the total distance to other points
    total_dists = []
    for i in range(n):
        dist = (outputs[i] * left_counts[i] - left_sums[i]) + (right_sums[i] - outputs[i] * right_counts[i])
        total_dists.append(dist)

    # find the Most central output
    min_index, _ = min(enumerate(total_dists), key=lambda x: x[1])
    best_output = outputs[min_index]

    # Median absolute deviation
    deviations = [abs(x - best_output) for x in outputs]
    deviations.sort()
    m = len(deviations)
    if m % 2 == 0:
        mad = (deviations[m//2 - 1] + deviations[m//2]) / 2
    else:
        mad = deviations[m//2]

    return best_output, mad


# use a tight pct range to find the first central price
pct_range_tight = .05
price_up = rough_price_estimate + pct_range_tight * rough_price_estimate 
price_dn = rough_price_estimate - pct_range_tight * rough_price_estimate
central_price, av_dev = find_central_output(output_prices,price_dn,price_up)

# find the deviation as a percentage of the price range
price_range = price_up - price_dn
dev_pct = av_dev/price_range

# iteratively re-center the bounds and find a new center price until convergence
avs = set()
avs.add(central_price)
while central_price not in avs:
    avs.add(central_price)
    price_up = central_price + pct_range_tight * central_price 
    price_dn = central_price - pct_range_tight * central_price
    central_price, av_dev = find_central_output(output_prices,price_dn,price_up)
    price_range = price_up - price_dn
    dev_pct = av_dev/price_range

#print update
print("80%..",end="",flush=True)

#because price flutucation may exceed bounds, check a wide ranger for the devation
pct_range_med = .1
price_up = central_price + pct_range_med * central_price 
price_dn = central_price - pct_range_med * central_price
price_range = price_up - price_dn
unused_price, av_dev = find_central_output(output_prices,price_dn,price_up)
dev_pct = av_dev/price_range

# use the pct deviation of data to set y axis range
map_dev_axr = (.15-.05)/(.20-.17)
ax_range = .05+ (dev_pct-.17)*map_dev_axr

#set max and min y axis ranges
if ax_range < .05:
    ax_range = .05
if ax_range > .2:
    ax_range = .2
price_up = central_price + ax_range * central_price 
price_dn = central_price - ax_range * central_price


# print update
print("100%\t\t\tdone",flush=True)
if date_mode:
    print("\n\n\t\t"+price_day_date_utc+" price: $"+f"{int(central_price):,}\n\n",flush=True)




##############################################################################

# Step 12 - Generate a Price Plot HTML Page

##############################################################################

# To display the results, we create a local webpage and serve an intraday plot using 
# an HTML <canvas> element rendered in the user's browser. This is accomplished 
# by generating a string that follows HTML and JavaScript syntax, defining the 
# canvas and drawing the intraday price points as (x, y) elements.

# The resulting string is saved as a local HTML file, which should automatically open 
# in the user’s default web browser using the webbrowser.open() command.


# geometric layout of webpage and chart
width = 1000   # canvas width (px)
height = 660  # canvas height (px)
margin_left = 120
margin_right = 90
margin_top = 100
margin_bottom = 120

# #get linear block hieghts on x axis
start = block_nums_needed[0]
end = block_nums_needed[-1]
count = len(output_prices)
step = (end - start) / (count - 1) if count > 1 else 0
b3 = [start + i * step for i in range(count)]

#Prepare python prices, heights, and timestamps for sending to html
heights = []
heights_smooth = []
timestamps = []
prices = []
for i in range(len(output_prices)):
    if price_dn < output_prices[i] < price_up:
        heights.append(output_blocks[i])
        heights_smooth.append(b3[i])
        timestamps.append(output_times[i])
        prices.append(output_prices[i])

# Sort by timestamps (optional, looks nicer)
heights_smooth, prices = zip(*sorted(zip(heights_smooth, prices)))

# set x tick locations
num_ticks = 5
n = len(heights_smooth)
tick_indxs = [round(i * (n - 1) / (num_ticks - 1)) for i in range(num_ticks)]

# Set the x tick labels 
xtick_positions = []
xtick_labels = []
for tk in tick_indxs:
    xtick_positions.append(heights_smooth[tk])
    block_height = heights[tk]
    timestamp = timestamps[tk]
    dt = datetime.utcfromtimestamp(timestamp)
    time_label = f"{dt.hour:02}:{dt.minute:02} UTC"
    label = f"{block_height}\n{time_label}"  # comma after 3 digits
    xtick_labels.append(label)

# Calculate avg price
avg_price = central_price

#set the plot annotations
plot_title_left = ""
plot_title_right = ""
bottom_note1 = ""
bottom_note2 = ""
if date_mode:
    plot_title_left = price_day_date_utc+" blocks from local node"
    plot_title_right ="UTXOracle Consensus Price $"+f"{int(central_price):,} "#+test_price
    bottom_note1 = "Consensus Data:"
    bottom_note2 = "this plot is identical and immutable for every bitcoin node"
if block_mode:
    plot_title_left = "Local Node Blocks "+str(block_start_num)+"-"+str(block_finish_num)
    plot_title_right ="UTXOracle Block Window Price $"+f"{int(central_price):,}"
    bottom_note1 = "* Block Window Price "
    bottom_note2 = "may have node dependent differences data on the chain tip"


# Write the HTML code for the chart
html_content = f'''<!DOCTYPE html>

<html>
<head>
<title>UTXOracle Local</title>
<style>
    body {{
        background-color: black;
        margin: 0;
        color: #CCCCCC;
        font-family: Arial, sans-serif;
        text-align: center;
    }}
    canvas {{
        background-color: black;
        display: block;
        margin: auto;
    }}
    
    
</style>
</head>
<body>



<div id="tooltip" style="
    position: absolute;
    background-color: black;
    color: cyan;
    border: 1px solid cyan;
    padding: 8px;
    font-size: 14px;
    border-radius: 5px;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.2s;
    text-align: left;
    z-index: 10;
"></div>

<div style="position: relative; width: 95%; max-width: 1000px; margin: auto;">
    
    <canvas id="myCanvas" style="width: 100%; height: auto;" width="{width}" height="{height}"></canvas>
    
    <button id="downloadBtn" style="
        position: absolute;
        bottom: 5%;
        right: 2%;
        font-size: 14px;
        padding: 6px 10px;
        background-color: black;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        opacity: 0.85;
    ">
    Save PNG
    </button>

</div>



<script>
const canvas = document.getElementById('myCanvas');
const ctx = canvas.getContext('2d');

const width = {width};
const height = {height};

const marginLeft = {margin_left};
const marginRight = {margin_right};
const marginTop = {margin_top};
const marginBottom = {margin_bottom};

const plotWidth = width - marginLeft - marginRight;
const plotHeight = height - marginTop - marginBottom;

// Data
const heights_smooth = {list(heights_smooth)};
const prices = {list(prices)};
const heights = {list(heights)};
const timestamps = {list(timestamps)};


const ymin = Math.min(...prices);
const ymax = Math.max(...prices);
const xmin = Math.min(...heights_smooth);
const xmax = Math.max(...heights_smooth);

// xticks
const xtick_positions = {xtick_positions};
const xtick_labels = {xtick_labels};


// Scaling functions
function scaleX(t) {{
    return marginLeft + (t - xmin) / (xmax - xmin) * plotWidth;
}}

function scaleY(p) {{
    return marginTop + (1 - (p - ymin) / (ymax - ymin)) * plotHeight;
}}

// Background
ctx.fillStyle = "black";
ctx.fillRect(0, 0, width, height);


// UTXOracle Local Title
ctx.font = "bold 36px Arial";
ctx.textAlign = "center";
ctx.fillStyle = "cyan";
ctx.fillText("UTXOracle", width / 2 - 60, 40);  // Slight left shift for spacing

ctx.fillStyle = "lime";
ctx.fillText("Local", width / 2 + 95, 40);  // Slight right shift

// Plot Date and Consensus Price
ctx.font = "24px Arial";
ctx.textAlign = "right";
ctx.fillStyle = "white";
ctx.fillText("{plot_title_left}", width /2, 80);
ctx.textAlign = "left";
ctx.fillStyle = "lime";
ctx.fillText("{plot_title_right}", width/2 +10, 80);





// Draw axes
ctx.strokeStyle = "white";
ctx.lineWidth = 1;

// Y axis
ctx.beginPath();
ctx.moveTo(marginLeft, marginTop);
ctx.lineTo(marginLeft, marginTop + plotHeight);
ctx.stroke();

// X axis
ctx.beginPath();
ctx.moveTo(marginLeft, marginTop + plotHeight);
ctx.lineTo(marginLeft + plotWidth, marginTop + plotHeight);
ctx.stroke();

// Right spine
ctx.beginPath();
ctx.moveTo(marginLeft + plotWidth, marginTop);
ctx.lineTo(marginLeft + plotWidth, marginTop + plotHeight);
ctx.stroke();

// Top spine
ctx.beginPath();
ctx.moveTo(marginLeft, marginTop);
ctx.lineTo(marginLeft + plotWidth, marginTop);
ctx.stroke();


// Draw ticks and labels
ctx.fillStyle = "white";
ctx.font = "20px Arial";

// Y axis ticks
const yticks = 5;
for (let i = 0; i <= yticks; i++) {{
    let p = ymin + (ymax - ymin) * i / yticks;
    let y = scaleY(p);
    ctx.beginPath();
    ctx.moveTo(marginLeft - 5, y);
    ctx.lineTo(marginLeft, y);
    ctx.stroke();
    ctx.textAlign = "right";
    ctx.fillText(Math.round(p).toLocaleString(), marginLeft - 10, y + 4);
}}

// X axis ticks
ctx.textAlign = "center";
ctx.font = "16px Arial";

for (let i = 0; i < xtick_positions.length; i++) {{
    let x = scaleX(xtick_positions[i]);
    ctx.beginPath();
    ctx.moveTo(x, marginTop + plotHeight);
    ctx.lineTo(x, marginTop + plotHeight + 5);
    ctx.stroke();

    // Split label into two lines
    let parts = xtick_labels[i].split("\\n");
    ctx.fillText(parts[0], x, marginTop + plotHeight + 20);   // Block height
    ctx.fillText(parts[1], x, marginTop + plotHeight + 40);   // Time
}}


// Axis labels
ctx.fillStyle = "white";
ctx.font = "20px Arial";
ctx.textAlign = "center";
ctx.fillText("Block Height and UTC Time", marginLeft + plotWidth/2, height - 48);
ctx.save();
ctx.translate(20, marginTop + plotHeight/2);
ctx.rotate(-Math.PI / 2);
ctx.fillText("BTC Price ($)", 0, 0);
ctx.restore();

// Plot points
ctx.fillStyle = "cyan";
for (let i = 0; i < heights_smooth.length; i++) {{
    let x = scaleX(heights_smooth[i]);
    let y = scaleY(prices[i]);
    ctx.fillRect(x, y, .75, .75);
}}

// Annotation for average price
ctx.fillStyle = "cyan";
ctx.font = "20px Arial";
ctx.textAlign = "left";
ctx.fillText("- {int(avg_price):,}", marginLeft + plotWidth + 1, scaleY({avg_price}) +0);


// Annotate bottom chart note

ctx.font = "24px Arial";
ctx.fillStyle = "lime";
ctx.textAlign = "right";
ctx.fillText("{bottom_note1}", 320, height-10);
ctx.font = "24px Arial";
ctx.fillStyle = "white";
ctx.textAlign = "left";
ctx.fillText("{bottom_note2}", 325, height-10);


// === MOUSEOVER INFO ===

const tooltip = document.getElementById('tooltip');

canvas.addEventListener('mousemove', function(event) {{
const rect = canvas.getBoundingClientRect();
const scaleX = canvas.width / rect.width;
const scaleY = canvas.height / rect.height;
const mouseX = (event.clientX - rect.left) * scaleX;
const mouseY = (event.clientY - rect.top) * scaleY;

if (mouseX >= marginLeft && mouseX <= width - marginRight &&
    mouseY >= marginTop && mouseY <= marginTop + plotHeight) {{

    const fractionAcross = (mouseX - marginLeft) / plotWidth;
    let index = Math.round(fractionAcross * (heights.length - 1));
    index = Math.max(0, Math.min(index, heights.length - 1));

    const price = ymax - (mouseY - marginTop) / plotHeight * (ymax - ymin);
    const blockHeight = heights[index];
    const timestamp = timestamps[index];

    const date = new Date(timestamp * 1000);
    const hours = date.getUTCHours().toString().padStart(2, '0');
    const minutes = date.getUTCMinutes().toString().padStart(2, '0');
    const utcTime = `${{hours}}:${{minutes}} UTC`;

    tooltip.innerHTML = `
        Price: $${{Math.round(price).toLocaleString()}}<br>
        Block: ${{blockHeight.toLocaleString()}}<br>
        Time: ${{utcTime}}
    `;

    tooltip.style.left = (event.clientX + 5) + 'px';
    tooltip.style.top = (event.clientY + window.scrollY - 75) + 'px';
    tooltip.style.opacity = 1;
}} else {{
    tooltip.style.opacity = 0;
}}
}});




</script>


<script>
// Download canvas as PNG
const downloadBtn = document.getElementById('downloadBtn');
downloadBtn.addEventListener('click', function() {{
    const link = document.createElement('a');
    link.download = 'UTXOracle_Local_Node_Price.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
}});
</script>

<br>
<br>


<h2 style="margin-top:10px; font-size:24px;">
Want a 
<span style="color:orange; font-size:24px;">Live Updating Oracle</span>
  with New Mempool Transactions? 
</h2>


<iframe
    width="{width}"
    height="{height}"
    src="https://www.youtube.com/embed/live_stream?channel=UCXN7Xa_BF7dqLErzOmS-B7Q&autoplay=1&mute=1"
    frameborder="0"
    allow="autoplay; encrypted-media"
    allowfullscreen
    
</iframe>



<br>

</body>
</html>
'''


# name the file with dates or blocks
filename = ".html"
if date_mode:
    filename = "UTXOracle_"+price_date_dash+filename
if block_mode:
    filename = "UTXOracle_"+str(block_start_num)+"-"+str(block_finish_num)+filename


# Write file locally and serve to browser
import webbrowser
with open(filename, "w") as f:
    f.write(html_content)
webbrowser.open('file://' + os.path.realpath(filename))




