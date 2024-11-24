// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MyContract{
    uint256 constant l1 = 10;
    uint256 constant l2 = 20;
    uint256 constant l3 = l2;
    uint256 constant p = l1 * l2 + l1 / l3 - (l2 - (l3 - l1)) % 20 + 3 ** l3;
    
    uint256[p] public value_1;
    uint256[(((l1)+l2))] public value_2;
    uint256[10] public value_3;
    uint256[] public dynamic_value;

    function set_value(uint256 _value, uint128 idx) public {
        if(idx < value_1.length - 1){
            value_1[idx] = _value;
        }
        dynamic_value.push(_value);
        
    }

    function get_value(uint128 idx) public view returns (uint256){
        return value_1[idx];
    }

    function replace_value(uint[10] memory data, uint idx) public returns (uint256[10] memory){
        value_1[idx] = data[idx];
        data[idx-1] = value_1[idx-1];
        return data;
    }

    function add_value(uint[] memory data, uint idx) public view returns (uint[11] memory){
        uint[11] memory new_data;

        for(uint i=0; (i< new_data.length-1) && (i < data.length); i++)
        {
            new_data[i] = data[i];
        }
        new_data[new_data.length-1] = value_1[idx];
        return new_data;
    }
}