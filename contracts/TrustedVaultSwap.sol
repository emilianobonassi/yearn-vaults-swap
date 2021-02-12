// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.6.12;

import "./VaultSwap.sol";
import "./Governable.sol";

import "../interfaces/IRegistry.sol";

contract TrustedVaultSwap is VaultSwap, Governable {
    address public registry;

    modifier onlyRegisteredVault(address vault) {
        require(
            IRegistry(registry).latestVault(IVaultAPI(vault).token()) == vault,
            "Target vault should be the latest for token"
        );
        _;
    }

    constructor(address _registry)
        public
        VaultSwap()
        Governable(address(0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52))
    {
        require(_registry != address(0), "Registry cannot be 0");

        registry = _registry;
    }

    function _swap(
        address vaultFrom,
        address vaultTo,
        uint256 shares
    ) internal override onlyRegisteredVault(vaultTo) {
        super._swap(vaultFrom, vaultTo, shares);
    }

    function sweep(address _token) external onlyGovernance {
        IERC20(_token).safeTransfer(
            governance,
            IERC20(_token).balanceOf(address(this))
        );
    }

    // setters
    function setRegistry(address _registry) external onlyGovernance {
        require(_registry != address(0), "Registry cannot be 0");
        registry = _registry;
    }
}
