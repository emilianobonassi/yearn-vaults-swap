// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.6.12;

contract Governable {
    address public governance;
    address public pendingGovernance;

    constructor(address _governance) public {
        require(
            _governance != address(0),
            "governable::should-not-be-zero-address"
        );
        governance = _governance;
    }

    function setPendingGovernance(address _pendingGovernance)
        external
        onlyGovernance
    {
        pendingGovernance = _pendingGovernance;
    }

    function acceptGovernance() external onlyPendingGovernance {
        governance = msg.sender;
        pendingGovernance = address(0);
    }

    modifier onlyGovernance {
        require(msg.sender == governance, "governable::only-governance");
        _;
    }

    modifier onlyPendingGovernance {
        require(
            msg.sender == pendingGovernance,
            "governable::only-pending-governance"
        );
        _;
    }
}
