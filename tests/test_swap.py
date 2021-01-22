import brownie
import pytest
from brownie import chain
from eth_account import Account
from eth_account.messages import encode_structured_data

def generate_permit(vault, owner: Account, spender: Account, value, nonce, deadline):
    name = "Yearn Vault"
    version = vault.apiVersion()
    chain_id = 1  # ganache bug https://github.com/trufflesuite/ganache/issues/1643
    contract = str(vault)
    data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "Permit": [
                {"name": "owner", "type": "address"},
                {"name": "spender", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "nonce", "type": "uint256"},
                {"name": "deadline", "type": "uint256"},
            ],
        },
        "domain": {
            "name": name,
            "version": version,
            "chainId": chain_id,
            "verifyingContract": contract,
        },
        "primaryType": "Permit",
        "message": {
            "owner": owner.address,
            "spender": spender.address,
            "value": value,
            "nonce": nonce,
            "deadline": deadline,
        },
    }

    return encode_structured_data(data)

def test_swap_v1(vaultFactory, vaultFactoryV1, controllerFactoryV1, Token, StrategyDForceDAI, user, vaultSwap, gov, accounts):
    token = Token.at("0x6B175474E89094C44Da98b954EedeAC495271d0F") # DAI
    tokenOwner = accounts.at("0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643", force=True) # whale for DAI

    # Create a V1 Vault
    controller = controllerFactoryV1()
    strategy = gov.deploy(StrategyDForceDAI, controller)
    vaultA = vaultFactoryV1(token, controller)
    controller.setStrategy(token, strategy, {"from": gov})

    # Create target V2 vault
    vaultB = vaultFactory(token)

    # Give user some funds
    tokenAmount = "10 ether"
    token.transfer(user, tokenAmount, {"from": tokenOwner})

    # Deposit in vaultA
    token.approve(vaultA, tokenAmount, {"from": user})
    vaultA.deposit(tokenAmount, {"from": user})

    # Migrate in vaultB
    balanceVaultA = vaultA.balanceOf(user)

    vaultA.approve(vaultSwap, balanceVaultA, {"from": user})
    vaultSwap.swap(vaultA, vaultB, {"from": user})

    assert vaultA.balanceOf(user) == 0
    assert vaultB.balanceOf(user) > 0

def test_swap_approve(vaultFactory, tokenFactory, tokenOwner, user, vaultSwap):
    token = tokenFactory()
    vaultA = vaultFactory(token)
    vaultB = vaultFactory(token)

    # Give user some funds
    tokenAmount = "10 ether"
    token.transfer(user, tokenAmount, {"from": tokenOwner})

    # Deposit in vaultA
    token.approve(vaultA, tokenAmount, {"from": user})
    vaultA.deposit({"from": user})

    # Migrate in vaultB
    balanceVaultA = vaultA.balanceOf(user)
    
    vaultA.approve(vaultSwap, balanceVaultA, {"from": user})
    vaultSwap.swap(vaultA, vaultB, {"from": user})

    assert vaultA.balanceOf(user) == 0
    assert vaultB.balanceOf(user) > 0

    
def test_swap_permit(vaultFactory, tokenFactory, tokenOwner, vaultSwap, chain, accounts):
    userForSignature = Account.create()
    user = accounts.at(userForSignature.address, force=True)

    token = tokenFactory()
    vaultA = vaultFactory(token)
    vaultB = vaultFactory(token)

    # Give user some funds
    tokenAmount = "10 ether"
    token.transfer(user, tokenAmount, {"from": tokenOwner})

    # Deposit in vaultA
    token.approve(vaultA, tokenAmount, {"from": user})
    vaultA.deposit({"from": user})

    # Migrate in vaultB
    balanceVaultA = vaultA.balanceOf(user)

    deadline = chain[-1].timestamp + 3600
    permit = generate_permit(vaultA, userForSignature, vaultSwap, balanceVaultA, vaultA.nonces(user), deadline)
    signature = userForSignature.sign_message(permit).signature

    vaultSwap.swap(vaultA, vaultB, deadline, signature, {"from": user})

    assert vaultA.balanceOf(user) == 0
    assert vaultB.balanceOf(user) > 0

def test_swap_wrong_vaults(vaultFactory, tokenFactory, tokenOwner, user, vaultSwap):
    token = tokenFactory()
    tokenWrong = tokenFactory()
    vaultA = vaultFactory(token)
    vaultB = vaultFactory(tokenWrong)

    # Give user some funds
    tokenAmount = "10 ether"
    token.transfer(user, tokenAmount, {"from": tokenOwner})

    # Deposit in vaultA
    token.approve(vaultA, tokenAmount, {"from": user})
    vaultA.deposit({"from": user})

    # Migrate in vaultB
    balanceVaultA = vaultA.balanceOf(user)
    
    vaultA.approve(vaultSwap, balanceVaultA, {"from": user})

    with brownie.reverts("Vaults must have the same token"):
        vaultSwap.swap(vaultA, vaultB, {"from": user})
