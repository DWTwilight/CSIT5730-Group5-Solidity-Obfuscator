// SPDX-License-Identifier: MIT

pragma solidity ^0.8.26;

contract ControlFlowExample {
    function loop() public pure returns (uint256, uint256) {
        
        uint256 s = 1;
        {
    uint256 i = 0;
    uint256 y8793a06a75cb = 929482113;
    while (true) {
        if (y8793a06a75cb == 929482113) { y8793a06a75cb = ( i < 10) ? 470393626 : 1075398675; }
        else if (y8793a06a75cb == 470393626) {
            if (i == 3) {
                s += i;
                y8793a06a75cb = 151609646; continue;
            }
            if (i == 5) {
                s -= i;
                y8793a06a75cb = 1075398675; continue;
            }
         y8793a06a75cb = 151609646; }
        else if (y8793a06a75cb == 1075398675) {break; }
        else if (y8793a06a75cb == 151609646) {  i++; y8793a06a75cb = 929482113; }
}}

        if (s > 5) {
            s -= 5;
        }

        
        uint256 j = 0;
        {
    uint256 y23ca9f43c19a = 139950449;
    while (true) {
        if (y23ca9f43c19a == 139950449) { y23ca9f43c19a = (j <= 10) ? 1360346990 : 496739134; }
        else if (y23ca9f43c19a == 1360346990) {
            j++;
         y23ca9f43c19a = 139950449; }
        else if (y23ca9f43c19a == 496739134) {break; }
}}

        
        uint256 k = 0;
        {
    uint256 L476545fb61d3 = 1866638845;
    while (true) {
        if (L476545fb61d3 == 1669165175) { L476545fb61d3 = (k <= 20) ? 1866638845 : 1357429079; }
        else if (L476545fb61d3 == 1866638845) {
            k++;
         L476545fb61d3 = 1669165175; }
        else if (L476545fb61d3 == 1357429079) {break; }
}}

        
        if (j >= 20) {
            j += 9;
        } else if (j >= 10) {
            j += 5;
        } else {
            j += 1;
        }
        
        return (s, j);
    }
}