// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

contract Loop {
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
}
