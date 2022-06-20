# Oracle Giveaway Contract

Example of a "giveaway contract", where anyone can claim the coins in the
if Bitcoin Cash reaches a certain USD marked value.

This contract uses an external oracle: https://oracles.cash/

In this example, the contract can be spent from when Bitcoin Cash reaches
marked value of 1 BCH >= $250.

Use at own risk.

### Usage

Open `giveaway.py`, update values in `REDEEM_ADDRESS` and `UNLOCKING_SCRIPT`.

Oracle message and signature for the unlocking script can be found here:
https://oracles.cash/oracles/02d3c1de9d4bc77d6c3608cbe44d10138c7488e592dc2b1e10a6cf0e92c2ecb047

```
pip3 bitcoincash
python3 giveaway.py
```

#### Changing `contract.cash`

Install `cashc` via npm to the CashScript compiler. Run `cashc contract.cash`
to produce new bytecode of the changes you make.
