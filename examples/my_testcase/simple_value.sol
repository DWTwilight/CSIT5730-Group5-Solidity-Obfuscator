// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MyContract{
    uint256 public value;
    uint256 public trash;
    int256[10] public a;

    function set_value(uint256 _value) public {
        value = _value;
        uint256 x = 10;
        trash = value * x;
    }

    function get_value() public view returns (uint256){
        return value;
    }

    function get_trash() public view returns (uint256){
        uint104 x = 8;
        x = 8+8;
        return trash;
    }
}