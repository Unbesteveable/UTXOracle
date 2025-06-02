<p align="center">
  <img src="https://utxo.live/oracle/oracle_yesterday.png" alt="UTXOracle Chart" width="100%">
</p>

# UTXOracle

**UTXOracle** is a Bitcoin-native, exchange-free price oracle that calculates the market price of Bitcoin directly from the blockchain.

Unlike traditional oracles that rely on exchange APIs, UTXOracle identifies the most statistically probable BTC/USD exchange rate by analyzing recent transactions on-chain — no external price feeds required.

> ⚡ Pure Python. No dependencies. No assumptions. Just Bitcoin data.

---

## 🔍 How It Works

UTXOracle analyzes confirmed Bitcoin transactions and uses statistical clustering to isolate a "canonical" price point:
- Filters out coinbase, self-spends, and spam transactions.
- Focuses on economically meaningful outputs (within a dynamic BTC range).
- Calculates a volume-weighted median from clustered prices across a recent window of blocks.

The result is a Bitcoin price **derived from actual usage**, not speculative trading.

---

## 🧠 Why It Matters

- 🛑 **Exchange Independence**: Trust the chain, not custodians.
- 🔎 **Transparency**: Every price is reproducible from public block data.
- 🎯 **On-Chain Signal**: Derived from organic BTC/USD activity.
- 🐍 **Minimalism**: The core logic fits in a single, readable Python file.

---

## 📦 Getting Started

Clone the repo and run the reference script:

```bash
git clone https://github.com/Unbesteveable/UTXOracle.git
cd UTXOracle
python3 UTXOracle.py
```

This will connect to your local `bitcoind` node and print the current UTXOracle price.

**Requirements:**
- A running Bitcoin Core node (RPC enabled)
- Python 3.8+

---

## 🌐 Live Example

Check the live visual version of UTXOracle here:  
📺 **https://utxo.live**

- Includes historical charts and real-time YouTube stream
- Based entirely on the same logic as the reference script

---

## 🛠 Structure

- `UTXOracle.py` – The main reference implementation
- `v8/`, `v9/` – Previous algorithm versions
- `start9/` – Packaging for Start9 node integration

---

## ⚖️ License

UTXOracle is licensed under the [Blue Oak Model License 1.0.0](./LICENSE), a permissive open-source license designed to be simple, fair, and developer-friendly.

You are free to use, modify, and distribute this software with very few restrictions.

---

## 🙏 Credits

Created by [@Unbesteveable](https://github.com/Unbesteveable)  
Inspired by the idea that **Bitcoin's price should come from Bitcoin itself.**

---

<p align="center">
  <i>Signal from noise.</i>
</p>
