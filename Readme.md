# UTXOracle

This python program estimates the daily USD price of bitcoin using only your bitcoin Core full node. It will work even while you are disconnected 
from the internet because it only reads blocks from your machine. 

It does not save files, write cookies, or access any wallet information. It only reads blocks, analyzes output patterns, and estimates a daily average a USD price of bitcoin. 

The call to your node is the standard "bitcoin-cli". The date and price ranges expected to work for this version are from 2020-7-26 and from $10,000 to $100,000

>TLDR: It analyzes a day's worth of blocks in your node, and infers a USD price for bitcoin based on assumptions made that people transact generally in round-USD amounts.

## Run?
* Have a bitcoin node. You'll need to configure your RPC settings somewhere like `~/.bitcoin/bitcoin.conf`
* `python UTXOracle.py` or `python3 UTXOracle.py`. Follow the instructions on the screen.
* Conversely, for a "last block", set an envvar, and run: `LASTRUN=true python3 UTXOracle.py` for example.

### LastPrice
>TLDR: It analyzes the last block in your node, and infers a USD price for bitcoin based on assumptions made that people transact generally in round-USD amounts.
* For "last block price", set an envvar, and run: `LASTRUN=true python3 UTXOracle.py` for example.

* It leverages @SteveSimple's good work with [utxo.live](https://utxo.live/oracle/). Instead of looking at a full set of blocks for a given day, it just looks at the last block. 

## Details
* Gets your last block (or a day's worth of blocks) on your node.
* Walks through transactions in the last block/s.
* Fancy bell curve thingees.
* Throws out some edge cases.
* Builds a template of sorts of USD/BTC things.
* Lays that template across the array.
* Infers a price.
