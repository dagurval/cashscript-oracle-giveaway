# Oracle Giveaway Contract

Example of a "giveaway contract", where anyone can claim the coins in the
if Bitcoin Cash reaches a certain USD marked value.

This contract uses an external oracle: https://oracles.cash/

In this example, the contract can be spent from when Bitcoin Cash reaches
marked value of 1 BCH >= $250.

Use at own risk.

### Usage

Open `giveaway.py`, update values in `REDEEM_ADDRESS` and `UNLOCKING_SCRIPT`.

```
pip3 bitcoincash
python3 giveaway.py
```

#### Changing `contract.cash`

Install `cashc` via npm to the CashScript compiler. Run `cashc contract.cash`
to produce new bytecode of the changes you make.
