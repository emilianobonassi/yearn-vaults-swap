from pathlib import Path

from brownie import TrustedVaultSwap, accounts, config, network, project, web3
from brownie.network.account import PublicKeyAccount
from eth_utils import is_checksum_address


def main():
    print(f"You are using the '{network.show_active()}' network")
    dev = accounts.load("dev")
    print(f"You are using: 'dev' [{dev.address}]")

    if input("Deploy TrustedVaultSwap? y/[N]: ").lower() != "y":
        return

    vaultSwap = TrustedVaultSwap.deploy(PublicKeyAccount("v2.registry.ychad.eth").address, {"from": dev})
