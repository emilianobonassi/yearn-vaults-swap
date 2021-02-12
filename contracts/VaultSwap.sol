// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.6.12;

import "../interfaces/IVaultAPI.sol";

import {
    SafeERC20,
    SafeMath,
    IERC20
} from "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";

contract VaultSwap {
    using SafeMath for uint256;
    using SafeERC20 for IERC20;
    using SafeERC20 for IVaultAPI;

    modifier onlyCompatibleVaults(address vaultA, address vaultB) {
        require(
            IVaultAPI(vaultA).token() == IVaultAPI(vaultB).token(),
            "Vaults must have the same token"
        );
        _;
    }

    function swap(address vaultFrom, address vaultTo) external {
        _swap(vaultFrom, vaultTo, IVaultAPI(vaultFrom).balanceOf(msg.sender));
    }

    function swap(
        address vaultFrom,
        address vaultTo,
        uint256 shares
    ) external {
        _swap(vaultFrom, vaultTo, shares);
    }

    function swap(
        address vaultFrom,
        address vaultTo,
        uint256 deadline,
        bytes calldata signature
    ) external {
        uint256 shares = IVaultAPI(vaultFrom).balanceOf(msg.sender);

        _permit(vaultFrom, shares, deadline, signature);
        _swap(vaultFrom, vaultTo, shares);
    }

    function swap(
        address vaultFrom,
        address vaultTo,
        uint256 shares,
        uint256 deadline,
        bytes calldata signature
    ) external {
        _permit(vaultFrom, shares, deadline, signature);
        _swap(vaultFrom, vaultTo, shares);
    }

    function _permit(
        address vault,
        uint256 value,
        uint256 deadline,
        bytes calldata signature
    ) internal {
        require(
            IVaultAPI(vault).permit(
                msg.sender,
                address(this),
                value,
                deadline,
                signature
            ),
            "Unable to permit on vault"
        );
    }

    function _swap(
        address vaultFrom,
        address vaultTo,
        uint256 shares
    ) internal virtual onlyCompatibleVaults(vaultFrom, vaultTo) {
        // Transfer in vaultFrom shares
        IVaultAPI vf = IVaultAPI(vaultFrom);

        uint256 preBalanceVaultFrom = vf.balanceOf(address(this));

        vf.safeTransferFrom(msg.sender, address(this), shares);

        uint256 balanceVaultFrom =
            vf.balanceOf(address(this)).sub(preBalanceVaultFrom);

        // Withdraw token from vaultFrom
        IERC20 token = IERC20(vf.token());

        uint256 preBalanceToken = token.balanceOf(address(this));

        vf.withdraw(balanceVaultFrom);

        uint256 balanceToken =
            token.balanceOf(address(this)).sub(preBalanceToken);

        // Deposit new vault
        token.safeIncreaseAllowance(vaultTo, balanceToken);

        IVaultAPI(vaultTo).deposit(balanceToken, msg.sender);
    }
}
