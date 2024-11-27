// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MyContract{
    uint256 constant l1 = 10;
    uint256 constant l2 = 20;
int128 f885b3ab739b5ff7 = 217012;
int128 w0a6099 = 321084;
    uint256 constant p = l1 * l2 % 20 + 3 ** l2;
bool aa6d436d59343 = true;
bool b6b5a = true;
    bool constant abcd = true;
    uint256[p] public value_1;
    uint256[(((l1)+l2))] public value_2;
    uint256[p][l1][l1+l2+p-p+1] public multi_array;
    uint256[10] public value_3 = [1,2,3,4,5,6,7,8,9,10];
bool s7cfda3 = true;
    uint256[] public dynamic_value;

    function set_value(uint256 _value, uint128 idx) public {
        if(idx < value_1.length - 1){
            value_1[idx] = _value + p + value_3[4];
        }
        dynamic_value.push(_value);
    }

    function get_value(uint128 idx) public returns (uint256){
        if(value_3.length > 5)
            return value_1[idx] * l2;
        else
f885b3ab739b5ff7 = int128(664140);
w0a6099 = int128(122034);
            return value_1[idx];
    }

    function replace_value(uint[10] memory data, uint idx) public returns (uint256[10] memory){
        value_1[idx] = data[idx];
        data[idx-1] = value_1[idx-1];
        return data;
    }

    function add_value(uint[] memory data, uint idx) public returns (uint[11] memory){
        uint[11] memory new_data;

        for(uint i=0; (i< new_data.length-1) && (i < data.length); i++)
        {
            new_data[i] = data[i];
        }
        new_data[new_data.length-1] = value_1[idx];
        return new_data;
    }
}