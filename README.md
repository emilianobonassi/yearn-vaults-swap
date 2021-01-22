<h1 align=center><code>Yearn V2 Vaults Swap</code></h1>

**Yearn V2 Vaults Swap** is a collection of smart contracts to simplify Yearn V2 Vaults swap (or migration from v2 or v1).

## How it works

It simplifies the swap between Yearn V2 Vaults with the same token (underlying).

It supports migration from v1 to v2 too!

It supports `permit` to allow 1-tx operations (only from v2 to v2).

## Usage

You have the following methods available:
- `swap(address vaultFrom, address vaultTo)`, swap full balance from vaultFrom to vaultTo. Requires `approve` tx.
- `swap(address vaultFrom, address vaultTo, uint256 deadline, bytes calldata signature)`, like the previous but using permit (v2 to v2 only).
- `swap(address vaultFrom, address vaultTo, uint256 shares)`, swap a specific amount of `shares` from vaultFrom to vaultTo. Requires `approve` tx.
- `swap(address vaultFrom, address vaultTo, uint256 shares, uint256 deadline, bytes calldata signature)`, like the previous but using permit (v2 to v2 only).

Currently, it's a developer tool, use at your own risk, no audit!