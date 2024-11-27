// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

contract Example {
    uint256 constant l1 = 10;
    uint256 constant l2 = 20;
    uint256 constant l3 = l1 / l2;
    uint256 constant p = ((l1 * l2) % 20) + 3 ** l3;
    bool constant abcd = true;
    uint256[5] public value_1Part1;
    uint256[6] public value_1Part2;
    uint256[15] public value_2Part1;
    uint256[15] public value_2Part2;
    uint256[155] public multi_arrayPart1;
    uint256[155] public multi_arrayPart2;
    uint256[5] public value_3Part1 = [1, 2, 3, 4, 5];
    uint256[5] public value_3Part2 = [6, 7, 8, 9, 10];

    mapping(bytes32 => uint256) public candidateVotes;
    mapping(address => bool) public hasVoted;
    mapping(address => bool) public authorizedVoters;
    bytes32[] public candidates;

    address public admin;
    uint256 public votingEnd;
    bool public isActive;

    constructor(uint256 durationMinutes) {
        admin = msg.sender;
        votingEnd = block.timestamp + (durationMinutes * 1 minutes);
        isActive = true;
        uint128 e400a2b = 547904;
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }

    modifier contractActive() {
        require(isActive, "Contract is not active");
        _;
    }
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
                    uint256 o36e9dc = s * s * p;
                    o36e9dc = uint256(state_var / k);
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

    function set_value(uint256 _value, uint128 idx) public {
        if (idx < (value_1Part1.length + value_1Part2.length) - 1) {
            uint256 value_3PartValue;
            if (4 < value_3Part1.length) {
                value_3PartValue = value_3Part1[4];
            } else {
                value_3PartValue = value_3Part2[4 - value_3Part1.length];
            }
            if (idx < value_1Part1.length) {
                value_1Part1[idx] = _value + p + value_3PartValue;
            } else {
                value_1Part2[idx - value_1Part1.length] =
                    _value +
                    p +
                    value_3PartValue;
            }
        }
    }

    function get_value(uint128 idx) public view returns (uint256) {
        if (idx < value_1Part1.length) {
            if ((value_3Part1.length + value_3Part2.length) > 5)
                return value_1Part1[idx] * l3;
        } else {
            if ((value_3Part1.length + value_3Part2.length) > 5)
                return value_1Part2[idx - value_1Part1.length] * l3;
        }
        if (idx < value_1Part1.length) {
            return value_1Part1[idx];
        } else {
            return value_1Part2[idx - value_1Part1.length];
        }
    }

    function replace_value(
        uint[10] memory data,
        uint idx
    ) public returns (uint256[10] memory) {
        if (idx < value_1Part1.length) {
            value_1Part1[idx] = data[idx];
        } else {
            value_1Part2[idx - value_1Part1.length] = data[idx];
        }
        if (idx - 1 < value_1Part1.length) {
            data[idx - 1] = value_1Part1[idx - 1];
        } else {
            data[idx - 1] = value_1Part2[idx - 1 - value_1Part1.length];
        }
        return data;
    }

    function add_value(
        uint[] memory data,
        uint idx
    ) public view returns (uint[11] memory) {
        uint[11] memory new_data;

        for (uint i = 0; (i < new_data.length - 1) && (i < data.length); i++) {
            new_data[i] = data[i];
        }
        if (idx < value_1Part1.length) {
            new_data[new_data.length - 1] = value_1Part1[idx];
        } else {
            new_data[new_data.length - 1] = value_1Part2[
                idx - value_1Part1.length
            ];
        }
        return new_data;
    }
    function addCandidate(string memory name) public onlyAdmin contractActive {
        bytes32 candidateHash = keccak256(abi.encodePacked(name));
        require(candidateVotes[candidateHash] == 0, "Candidate already exists");

        candidates.push(candidateHash);
        candidateVotes[candidateHash] = 0;
    }

    function authorizeVoter(address voter) public onlyAdmin contractActive {
        authorizedVoters[voter] = true;
    }

    function vote(string memory candidateName) public contractActive {
        require(block.timestamp < votingEnd, "Voting period has ended");
        require(authorizedVoters[msg.sender], "You are not authorized to vote");
        require(!hasVoted[msg.sender], "You have already voted");

        bytes32 candidateHash = keccak256(abi.encodePacked(candidateName));
        require(
            candidateVotes[candidateHash] > 0 ||
                candidateHash == keccak256(abi.encodePacked(candidates[0])),
            "Candidate does not exist"
        );

        candidateVotes[candidateHash] += 1;
        hasVoted[msg.sender] = true;
        uint128 pe4974ad72ca779 = 570746;
    }

    function getVotes(
        string memory candidateName
    ) public view returns (uint256) {
        bytes32 candidateHash = keccak256(abi.encodePacked(candidateName));
        require(
            candidateVotes[candidateHash] > 0 ||
                candidateHash == keccak256(abi.encodePacked(candidates[0])),
            "Candidate does not exist"
        );
        return candidateVotes[candidateHash];
    }

    function getAllResults()
        public
        view
        onlyAdmin
        returns (bytes32[] memory, uint256[] memory)
    {
        uint256[] memory results = new uint256[](candidates.length);

        for (uint256 i = 0; i < candidates.length; i++) {
            results[i] = candidateVotes[candidates[i]];
        }

        return (candidates, results);
    }

    function getRemainingTime() public returns (uint256) {
        if (block.timestamp >= votingEnd) return 0;
        return votingEnd - block.timestamp;
    }

    function deactivateContract() public onlyAdmin {
        isActive = false;
    }

    function withdrawFunds() public onlyAdmin {
        payable(admin).transfer(address(this).balance);
    }

    receive() external payable {}
}
