from pathlib import Path

from brownie import VaultSwap, accounts, config, network, project, web3
from eth_utils import is_checksum_address


def main():
    print(f"You are using the '{network.show_active()}' network")
    dev = accounts.load("dev")
    print(f"You are using: 'dev' [{dev.address}]")

    if input("Deploy VaultSwap? y/[N]: ").lower() != "y":
        return

    vaultSwap = VaultSwap.deploy({"from": dev})
