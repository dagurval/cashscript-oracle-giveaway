#!/usr/bin/env python3
import qrcode
import asyncio
import time

from bitcoincash.core import b2x, lx, COutPoint, CMutableTxOut, CMutableTxIn, \
                            CMutableTransaction
from bitcoincash.core.script import *
from bitcoincash.wallet import CBitcoinAddress
from bitcoincash.electrum import Electrum

OP_CHECKDATASIGVERIFY = CScriptOp(0xbb)
OP_SPLIT = CScriptOp(0x7f)
OP_BIN2NUM = CScriptOp(0x81)

# Put your address here. Where to claim the giveaway to.
REDEEM_ADDRESS = CBitcoinAddress("bitcoincash:qzxqjtkze0vy96y5xtru2w65mvaftryr55yzmhy8sl")

# Keep this comment short, if it exceeds OP_RETURN push limit, the tx is invalid.
# The comment will be public for everyone to view on-chain forever.
REDEEM_COMMENT = "Short optional comment"

UNLOCKING_SCRIPT = [
    # Put the oracle signature.
    bytes.fromhex("e1c627d66e808546da95417be12fb3dc0504c3ef84c835db4e1521a4d32d3622b22bd7fec15513714ca8f47d228e53bd1b6dbad8bb7c90157861106c3d22d0e4"),
    # Put the oracle message here.
    bytes.fromhex("4a55b062a470010079700100ed2f0000"),
]

REDEEM_SCRIPT = CScript([
    # Oracle pubkey
    bytes.fromhex("02d3c1de9d4bc77d6c3608cbe44d10138c7488e592dc2b1e10a6cf0e92c2ecb047"),
    OP_ROT, OP_2, OP_PICK, OP_ROT, OP_CHECKDATASIGVERIFY, OP_DUP, OP_8,
    OP_SPLIT, OP_NIP, OP_4, OP_SPLIT, OP_DROP, OP_BIN2NUM,
    bytes.fromhex("306f01"), # Sequence
    OP_GREATERTHAN, OP_VERIFY, OP_12, OP_SPLIT, OP_NIP, OP_BIN2NUM,
    bytes.fromhex("a861"), # Dollar value
    OP_GREATERTHAN
])

async def main():
    cli = Electrum()
    await cli.connect()

    locking_script = REDEEM_SCRIPT.to_p2sh_scriptPubKey();
    contract_address = CBitcoinAddress.from_scriptPubKey(locking_script);

    # Output a QR code for the address in the terminal
    qr = qrcode.QRCode()
    qr.add_data(str(contract_address))
    qr.print_ascii()
    print(contract_address)

    try:
        while True:
            if (await main_loop(cli, contract_address, locking_script)):
                return
            time.sleep(1)
    finally:
        await cli.close()

def spend_input(coin_in, address, locking_script):
    tx_input = CMutableTxIn(COutPoint(lx(coin_in['tx_hash']), coin_in['tx_pos']))
    tx_input.scriptSig = CScript(UNLOCKING_SCRIPT + [REDEEM_SCRIPT])

    tx_output = CMutableTxOut(
            nValue = -1, # we will set this after calcualting fee
            scriptPubKey = REDEEM_ADDRESS.to_scriptPubKey())

    tx = CMutableTransaction()
    tx.vin = [tx_input]
    tx.vout = [tx_output]

    tx.vout.append(CMutableTxOut(nValue = 0, scriptPubKey = CScript(
                [OP_RETURN, REDEEM_COMMENT.encode('utf-8')])))

    fee = len(tx.serialize())
    output_value = coin_in['value'] - fee

    if output_value < 546:
        # Below dust, unspendable
        return None

    tx.vout[0].nValue = output_value
    tx_hex = b2x(tx.serialize())
    print(f"Transaction debug: meep debug -a {tx.vout[0].nValue} -s {b2x(locking_script)} -t {tx_hex}")
    return tx

async def broadcast(cli, tx):
    tx_hex = b2x(tx.serialize())
    await cli.RPC('blockchain.transaction.broadcast', tx_hex)

async def main_loop(cli, address, locking_script):
    # Get list of spendable coins in address

    print("")
    print("Press enter when contract has been funded...")
    input("")

    coins = await cli.RPC('blockchain.address.listunspent', str(address))

    tx = CMutableTransaction()
    tx.nLockTime = 1

    broadcasts = []

    while len(coins):
        tx = spend_input(coins.pop(), address, locking_script)
        if tx is None:
            continue

        broadcasts.append(broadcast(cli, tx))
        print(".", end = "", flush = True)

    print(f"Broadcasting {len(broadcasts)} transactions")
    await asyncio.gather(*broadcasts)
    return True

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()

