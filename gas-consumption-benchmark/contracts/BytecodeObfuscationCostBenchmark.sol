// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

contract BytecodeObfuscation {
    uint256 public res;

    function loop() public {
        // for loop
        uint256 s;
        for (uint256 i = 0; i < 10; i++) {
            if (i > 3) {
                s += i;
                continue;
            }
            if (i >= 5) {
                s += i;
            }
        }
        uint256 j;
        while (j <= 10) {
            j++;
        }
        res = s + j;
    }

    function cond() public {
        uint256 s = 5;
        if (s > 4) {
            s += 1;
        }
        if (s <= 6) {
            s -= 1;
        }
        res = s;
    }

    function arithmetic() public {
        uint256 a = 1;
        uint256 b = 2;
        a += b;
        a *= b;
        a -= b;
        a /= b;
        res = (a + b);
    }
}
