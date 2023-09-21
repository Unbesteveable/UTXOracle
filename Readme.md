# UTXOracle

This python program estimates the daily USD price of bitcoin using only your bitcoin Core full node. It will work even while you are disconnected 
from the internet because it only reads blocks from your machine. 

It does not save files, write cookies, or access any wallet information. It only reads blocks, analyzes output patterns, and estimates a daily average a USD price of bitcoin. 

The call to your node is the standard "bitcoin-cli". The date and price ranges expected to work for this version are from 2020-7-26 and from $10,000 to $100,000

### Run?
* Have a bitcoin node. You'll need to configure your RPC settings somewhere like `~/.bitcoin/bitcoin.conf`
* `python UTXOracle.py` or `python3 UTXOracle.py`

# LastPrice.py

## What is this?

It leverages @SteveSimple's good work with [utxo.live](https://utxo.live/oracle/). Instead of looking at a full set of blocks for a given day, it just looks at the last block. 

## What's it do?

>TLDR: It analyzes the last block in your node, and infers a USD price for bitcoin based on assumptions made that people transact generally in round-USD amounts.

### Details
* Gets your last block on your node.
* Walks through transactions in the last block.
* Fancy bell curve thingees.
* Throws out some edge cases.
* Builds a template of sorts of USD/BTC things.
* Lays that template across the array.
* Infers a price.

### Run?
* Have a bitcoin node. You'll need to configure your RPC settings somewhere like `~/.bitcoin/bitcoin.conf`
* `python3 LastPrice.py`

### FAQ
* Is this accurate? 
  * I have no idea. Seems to be with 1/2% of coingecko, etc. 
* How does this work?
  * @SteveSimple is smarter than me; did some fancy math and bell curves and whatnot. Basically, finds the `val` of each transaction in a given block, and throws out even BTC numbers, assumes some round dollar amounts and clustering, and spits out a number.
* Is there any license?
  * Probably should be an MIT or Apache2 or something. I'll update this if/when I can find the original.
* Why is this in _your_ github, and not @SteveSimple? 
  * I couldn't find the original repo, but the original python file is located [here](https://utxo.live/oracle/UTXOracle.py). I also included that file in this repo. NOTE: if/when I find the original repo, I'll collapse/delete this one, and fork the original, and do a proper Pull Request into the original.
* Why didn't you just modify @SteveSimple's original code?
  * Frankly, I don't understand the math. I have a working knowledge of Python, and wanted to see if I could just pick up the _last_ block in my node, and infer a price. 