# Import dependencies
import subprocess
import json
from dotenv import load_dotenv
import os

# Load and set environment variables
load_dotenv()
mnemonic=os.getenv("mnemonic")


# Import constants.py and necessary functions from bit and web3
import constants
from web3 import Web3
from web3.middleware import geth_poa_middleware
from bit import PrivateKeyTestnet, network
from eth_account import Account

# This is just the manual process for testing the symbolic linking for the hdwallet

# export MSYS=winsymlinks:nativestrict
# note to remove a symbolic link, we can just delete the file from the directory
# ./hd-wallet-derive/hd-wallet-derive.php --key=xprv9zbB6Xchu2zRkf6jSEnH9vuy7tpBuq2njDRr9efSGBXSYr1QtN8QHRur28QLQvKRqFThCxopdS1UD61a5q6jGyuJPGLDV9XfYHQto72DAE8 --cols=path,address --coin=ZEC --numderive=3 -g
# ln -s hd-wallet-derive/hd-wallet-derive.php derive
# ./derive --key=xprv9zbB6Xchu2zRkf6jSEnH9vuy7tpBuq2njDRr9efSGBXSYr1QtN8QHRur28QLQvKRqFThCxopdS1UD61a5q6jGyuJPGLDV9XfYHQto72DAE8 --cols=path,address --coin=ZEC --numderive=3 -g


#w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
#w3.middleware_onion.inject(geth_poa_middleware, layer=0)
 
# Create a function called `derive_wallets`
def derive_wallets(mnemonic, coin, numderive):
    """
    This is a function to derive the wallet addresses
    
    """
    command = f'php derive -g --mnemonic="{mnemonic}" --cols=path,address,privkey,pubkey --coin={coin} --numderive={numderive} --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    return json.loads(output)

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {}
crypto = [constants.ETH, constants.BTCTEST]
for c in crypto:
    coins[c] = derive_wallets(mnemonic, c, 3)
    

    


def priv_key_to_account(coin, priv_key):
    """
    This is a function that converts privkey strings to account objects.
    parameters: coin     = name of coin
                priv_key = private key for the coin
    """
    if coin == 'eth':
        return Account.privateKeyToAccount(priv_key)
    elif coin == 'btc-test':
        return PrivateKeyTestnet(priv_key)

    
    
    
# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, to, amount):
    if coin == 'eth':
        gasEstimate = w3.eth.estimateGas({"from": account.address, "to": to, "value": amount})
        return {
        "from": account.address,
        "to": to,
        "value": amount,
        "gasPrice": w3.eth.gasPrice,
        "gas": gasEstimate,
        "nonce": w3.eth.getTransactionCount(account.address),
        }
    elif coin == 'btc-test':
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, 'btc')])

    
# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, to, amount):
    if coin == 'eth':
        raw_tx = create_tx(coin, account, to, amount)
        signed_tx = account.sign_transaction(raw_tx)
        return w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    elif coin == 'btc-test':
        raw_tx = create_tx(coin, account, to, amount)
        signed_tx = account.sign_transaction(raw_tx)
        return network.NetworkAPI.broadcast_tx_testnet(signed_tx)    
    
    
# connect to geth local host
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    
btc_test = constants.BTCTEST
priv = coins['btc-test'][0]['privkey']
account = priv_key_to_account(btc_test, priv)


print(f"mnemonic = {mnemonic}")
print(btc_test)
print(f"account: {account}")
print(f"privateKey: {priv}")





# Perform Transfer of 0.00001BTC Back to the depositing address
to = 'tb1qy9tzfnf37676y69ecmk2kt9cyhw4ex6yzufk86'
transfer = send_tx(btc_test, account, to, 0.00001)





eth = constants.ETH
eth_priv = coins['eth'][0]['privkey']
eth_account = priv_key_to_account(eth, eth_priv)

print(eth)
print(f"account: {eth_account}")
print(f"privateKey: {eth_priv}")




to = '0xd55394285f4170f34d7dFEA17274E7A98ca75e35'
send_tx(eth, eth_account, to, 5000000000000000000)