// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.6.12;

import "./VaultSwap.sol";

import "../interfaces/IRegistry.sol";

contract TrustedVaultSwap is VaultSwap {

    address public immutable registry;

    modifier onlyRegisteredVault(address vault) {
        require(
            IRegistry(registry)
                .latestVault(IVaultAPI(vault).token()) == vault
            , "Target vault should be the latest for token");
        _;
    } 

    constructor(address _registry) VaultSwap() public {
        require(_registry != address(0), "Registry cannot be 0");

        registry = _registry;
    }

    function _swap(
        address vaultFrom,
        address vaultTo,
        uint256 shares
    ) onlyRegisteredVault(vaultTo) override internal {
        super._swap(vaultFrom, vaultTo, shares);
    }
}