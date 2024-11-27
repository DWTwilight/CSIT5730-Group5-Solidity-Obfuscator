// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

contract ControlFlowExample {
    function loop() public pure returns (uint256, uint256) {
        // for loop
        uint256 s = 1;
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
        uint256 j = 0;
        while (j <= 10) {
            j++;
        }

        // do-while loop
        uint256 k = 0;
        do {
            k++;
        } while (k <= 20);

        // multiple if-else statements
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