// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.6.12;

interface IRegistry {
    function latestVault(address token) external view returns (address);
}