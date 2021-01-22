// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.6.12;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface IVaultAPI is IERC20 {
    function deposit(uint256 _amount, address recipient) external returns (uint256 shares);
    
    function withdraw(uint256 _shares) external returns (uint256 value);
    
    function token() external view returns (address);

    function permit(address owner, address spender, uint256 value, uint256 deadline, bytes calldata signature) external returns (bool);
}