// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

contract Loop {
    uint256 constant l1 = 10;
    uint256 constant l2 = 20;
    uint256 constant l3 = l1 / l2;
    uint256 constant p = l1 * l2 % 20 + 3 ** l3;
    bool constant abcd = true;
    uint256[p] public value_1;
    uint256[(((l1)+l2))] public value_2;
    uint256[p][l1][l1+l2+p-p+1] public multi_array;
    uint256[10] public value_3 = [1,2,3,4,5,6,7,8,9,10];
    function loop() public pure returns (uint256, uint256) {
        // for loop
        uint256 s;
        for (uint256 i = 0; i < 10; i++) {
            if (i == 3) {
                // Skip to next iteration with continue
                s += i;
                continue;
            }
            if (i == 5) {
                // Exit loop with break
                s -= i;
                break;
            }
        }

        if (s > 5) {
            s -= 5;
        }

        // while loop
        uint256 j;
        while (j <= 10) {
            j++;
        }

        if (j >= 20) {
            j += 9;
        }
        return (s, j);
    }
    function set_value(uint256 _value, uint128 idx) public {
        if(idx < value_1.length - 1){
            value_1[idx] = _value + p + value_3[4];
        }
        
    }

    function get_value(uint128 idx) public view returns (uint256){
        if(value_3.length > 5)
            return value_1[idx] * l3;
        else
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
