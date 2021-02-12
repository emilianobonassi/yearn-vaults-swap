import brownie
import pytest
from brownie import chain


def test_swap_v1_not_registered_vault(
    vaultFactory,
    vaultFactoryV1,
    controllerFactoryV1,
    Token,
    StrategyDForceDAI,
    user,
    TrustedVaultSwap,
    gov,
    accounts,
):
    # Registry
    registry = "0xe15461b18ee31b7379019dc523231c57d1cbc18c"
    vaultSwap = gov.deploy(TrustedVaultSwap, registry)

    token = Token.at("0x6B175474E89094C44Da98b954EedeAC495271d0F")  # DAI
    tokenOwner = accounts.at(
        "0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643", force=True
    )  # whale for DAI

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

    with brownie.reverts("Target vault should be the latest for token"):
        vaultSwap.swap(vaultA, vaultB, {"from": user})


def test_swap_v1_registered_vault(
    interface,
    vaultFactoryV1,
    controllerFactoryV1,
    Token,
    StrategyDForceDAI,
    user,
    TrustedVaultSwap,
    gov,
    accounts,
):
    # Registry
    registry = "0xe15461b18ee31b7379019dc523231c57d1cbc18c"
    vaultSwap = gov.deploy(TrustedVaultSwap, registry)

    token = Token.at("0x6B175474E89094C44Da98b954EedeAC495271d0F")  # DAI
    tokenOwner = accounts.at(
        "0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643", force=True
    )  # whale for DAI

    # Create a V1 Vault
    controller = controllerFactoryV1()
    strategy = gov.deploy(StrategyDForceDAI, controller)
    # setting to get even calculations
    strategy.setWithdrawalFee(0, {"from": gov})
    vaultA = vaultFactoryV1(token, controller)
    controller.setStrategy(token, strategy, {"from": gov})

    # Create target V2 vault
    vaultB = interface.IVaultAPI(interface.IRegistry(registry).latestVault(token))

    # Give user some funds
    tokenAmount = "10 ether"
    token.transfer(user, tokenAmount, {"from": tokenOwner})

    # Deposit in vaultA
    token.approve(vaultA, tokenAmount, {"from": user})
    vaultA.deposit(tokenAmount, {"from": user})

    assert vaultB.balanceOf(user) == 0

    # Migrate in vaultB
    balanceVaultA = vaultA.balanceOf(user)
    balanceVaultBbefore = token.balanceOf(vaultB)

    vaultA.approve(vaultSwap, balanceVaultA, {"from": user})
    print(f"Vault A balance '{vaultA.balanceOf(user)}' before")
    print(f"Vault B Token balance '{token.balanceOf(vaultB)}' before")
    vaultSwap.swap(vaultA, vaultB, {"from": user})

    assert vaultA.balanceOf(user) == 0
    print(f"Vault B balance '{vaultB.balanceOf(user)}' after")
    print(f"Vault B Token balance '{token.balanceOf(vaultB)}' after")
    assert vaultB.balanceOf(user) > 0
    assert token.balanceOf(vaultB) > balanceVaultBbefore
    print(f"difference '{token.balanceOf(vaultB) - balanceVaultBbefore}' DAI")
    assert token.balanceOf(vaultB) - balanceVaultBbefore == tokenAmount
