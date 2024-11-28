// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleVotingSystem {

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
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }

    modifier contractActive() {
        require(isActive, "Contract is not active");
        _;
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
        require(candidateVotes[candidateHash] > 0 || candidateHash == keccak256(abi.encodePacked(candidates[0])), "Candidate does not exist");

        candidateVotes[candidateHash] += 1;
        hasVoted[msg.sender] = true; 
    }

    function getVotes(string memory candidateName) public view returns (uint256) {
        bytes32 candidateHash = keccak256(abi.encodePacked(candidateName));
        require(candidateVotes[candidateHash] > 0 || candidateHash == keccak256(abi.encodePacked(candidates[0])), "Candidate does not exist");
        return candidateVotes[candidateHash];
    }

    function getAllResults() public view onlyAdmin returns (bytes32[] memory, uint256[] memory) {
        uint256[] memory results = new uint256[](candidates.length);

        for (uint256 i = 0; i < candidates.length; i++) {
            results[i] = candidateVotes[candidates[i]];
        }

        return (candidates, results);
    }

    function getRemainingTime() public view returns (uint256) {
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
