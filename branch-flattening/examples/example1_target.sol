// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

contract ControlFlowExample {
    function loop() public pure returns (uint256, uint256) {
        // for loop
        uint256 s = 1;

        {
            uint256 state_var = 0; // 0 for condition, 1 for body, 2 for break, 3 for post
            uint256 i = 0;
            while (true) {
                if (state_var == 0) {
                    state_var = i < 10 ? 1 : 2;
                } else if (state_var == 1) {
                    // begin "body"
                    if (i == 3) {
                        s += i;
                        // begin "continue"
                        state_var = 0;
                        continue;
                        // end "continue"
                    } else if (i == 5) {
                        s -= i;
                        // begin "break"
                        state_var = 2;
                        continue;
                        // end "break"
                    }
                    // end "body", go to "post"
                    state_var = 3;
                } else if (state_var == 2) {
                    break;
                } else if (state_var == 3) {
                    i++;
                    state_var = 0;
                }
            }
        }

        if (s > 5) {
            s -= 5;
        }

        uint256 j = 0;
        // while loop
        {
            uint256 state_var = 0; // 0 for condition, 1 for body, 2 for break
            
            while (true) {
                if (state_var == 0) {
                    state_var = j <= 10 ? 1 : 2;
                } else if (state_var == 1) {
                    j++;
                    state_var = 0;
                } else if (state_var == 2) {
                    break;
                }
            }
        }

        // do-while loop
        uint256 k = 0;
        {
            uint256 state_var = 1; // 0 for condition, 1 for body, 2 for break
            while (true) {
                if (state_var == 0) {
                    state_var = k <= 20 ? 1 : 2;
                } else if (state_var == 1) {
                    k++;
                    state_var = 0;
                } else if (state_var == 2) {
                    break;
                }
            }
        }

        // multiple if-else statements
        {

            if (j >= 20) {
                j += 9;
            } else if (j >= 10) {
                j += 5;
            } else {
                j += 1;
            }
        }

        return (s, j);
    }
}
