// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title PortfolioStorage
 * @dev Smart contract for storing portfolio allocations on Ethereum blockchain
 * @author Decentralized Portfolio Optimizer
 */
contract PortfolioStorage {
    
    // Portfolio allocation structure
    struct PortfolioAllocation {
        string[] assetIds;           // Array of asset IDs (e.g., "bitcoin", "ethereum")
        uint256[] allocations;       // Allocation percentages (in basis points, 10000 = 100%)
        uint256 totalInvestment;     // Total investment amount in USD (scaled by 10^18)
        uint256 timestamp;           // Timestamp when portfolio was stored
        string riskProfile;          // Risk profile ("low", "medium", "high")
        string[] sectors;            // Selected sectors (e.g., "DeFi", "Layer 1")
    }
    
    // Mapping from user address to array of portfolio indices
    mapping(address => uint256[]) public userPortfolioIndices;
    
    // Mapping from user address and portfolio index to portfolio data
    mapping(address => mapping(uint256 => PortfolioAllocation)) public userPortfolios;
    
    // Mapping from user address to portfolio count
    mapping(address => uint256) public userPortfolioCount;
    
    // Events
    event PortfolioStored(
        address indexed user,
        uint256 indexed portfolioIndex,
        uint256 totalInvestment,
        string riskProfile,
        uint256 timestamp
    );
    
    event PortfolioUpdated(
        address indexed user,
        uint256 indexed portfolioIndex,
        uint256 totalInvestment,
        string riskProfile,
        uint256 timestamp
    );
    
    /**
     * @dev Store a new portfolio allocation
     * @param _assetIds Array of asset IDs
     * @param _allocations Array of allocation percentages (in basis points)
     * @param _totalInvestment Total investment amount in USD (scaled by 10^18)
     * @param _riskProfile Risk profile string
     * @param _sectors Array of selected sectors
     */
    function storePortfolio(
        string[] memory _assetIds,
        uint256[] memory _allocations,
        uint256 _totalInvestment,
        string memory _riskProfile,
        string[] memory _sectors
    ) public {
        require(_assetIds.length > 0, "Asset IDs cannot be empty");
        require(_assetIds.length == _allocations.length, "Asset IDs and allocations must have same length");
        require(_totalInvestment > 0, "Total investment must be greater than 0");
        
        // Validate allocations sum to 100% (10000 basis points)
        uint256 totalAllocation = 0;
        for (uint256 i = 0; i < _allocations.length; i++) {
            totalAllocation += _allocations[i];
        }
        require(totalAllocation == 10000, "Allocations must sum to 100%");
        
        // Get current portfolio index for user
        uint256 portfolioIndex = userPortfolioCount[msg.sender];
        
        // Create portfolio allocation
        PortfolioAllocation memory newPortfolio = PortfolioAllocation({
            assetIds: _assetIds,
            allocations: _allocations,
            totalInvestment: _totalInvestment,
            timestamp: block.timestamp,
            riskProfile: _riskProfile,
            sectors: _sectors
        });
        
        // Store portfolio
        userPortfolios[msg.sender][portfolioIndex] = newPortfolio;
        userPortfolioIndices[msg.sender].push(portfolioIndex);
        userPortfolioCount[msg.sender]++;
        
        emit PortfolioStored(
            msg.sender,
            portfolioIndex,
            _totalInvestment,
            _riskProfile,
            block.timestamp
        );
    }
    
    /**
     * @dev Update an existing portfolio allocation
     * @param _portfolioIndex Index of portfolio to update
     * @param _assetIds Array of asset IDs
     * @param _allocations Array of allocation percentages
     * @param _totalInvestment Total investment amount
     * @param _riskProfile Risk profile string
     * @param _sectors Array of selected sectors
     */
    function updatePortfolio(
        uint256 _portfolioIndex,
        string[] memory _assetIds,
        uint256[] memory _allocations,
        uint256 _totalInvestment,
        string memory _riskProfile,
        string[] memory _sectors
    ) public {
        require(_portfolioIndex < userPortfolioCount[msg.sender], "Portfolio does not exist");
        require(_assetIds.length > 0, "Asset IDs cannot be empty");
        require(_assetIds.length == _allocations.length, "Asset IDs and allocations must have same length");
        require(_totalInvestment > 0, "Total investment must be greater than 0");
        
        // Validate allocations sum to 100%
        uint256 totalAllocation = 0;
        for (uint256 i = 0; i < _allocations.length; i++) {
            totalAllocation += _allocations[i];
        }
        require(totalAllocation == 10000, "Allocations must sum to 100%");
        
        // Update portfolio allocation
        PortfolioAllocation storage portfolio = userPortfolios[msg.sender][_portfolioIndex];
        portfolio.assetIds = _assetIds;
        portfolio.allocations = _allocations;
        portfolio.totalInvestment = _totalInvestment;
        portfolio.timestamp = block.timestamp;
        portfolio.riskProfile = _riskProfile;
        portfolio.sectors = _sectors;
        
        emit PortfolioUpdated(
            msg.sender,
            _portfolioIndex,
            _totalInvestment,
            _riskProfile,
            block.timestamp
        );
    }
    
    /**
     * @dev Get portfolio allocation by index
     * @param _user User address
     * @param _portfolioIndex Portfolio index
     * @return assetIds Array of asset IDs
     * @return allocations Array of allocation percentages
     * @return totalInvestment Total investment amount
     * @return timestamp Portfolio creation timestamp
     * @return riskProfile Risk profile string
     * @return sectors Array of selected sectors
     */
    function getPortfolio(address _user, uint256 _portfolioIndex) public view returns (
        string[] memory assetIds,
        uint256[] memory allocations,
        uint256 totalInvestment,
        uint256 timestamp,
        string memory riskProfile,
        string[] memory sectors
    ) {
        require(_portfolioIndex < userPortfolioCount[_user], "Portfolio does not exist");
        
        PortfolioAllocation memory portfolio = userPortfolios[_user][_portfolioIndex];
        return (
            portfolio.assetIds,
            portfolio.allocations,
            portfolio.totalInvestment,
            portfolio.timestamp,
            portfolio.riskProfile,
            portfolio.sectors
        );
    }
    
    /**
     * @dev Get user's portfolio count
     * @param _user User address
     * @return count Number of portfolios for user
     */
    function getUserPortfolioCount(address _user) public view returns (uint256) {
        return userPortfolioCount[_user];
    }
    
    /**
     * @dev Get all portfolio indices for a user
     * @param _user User address
     * @return indices Array of portfolio indices
     */
    function getUserPortfolioIndices(address _user) public view returns (uint256[] memory) {
        return userPortfolioIndices[_user];
    }
    
    /**
     * @dev Get portfolio timestamps for a user
     * @param _user User address
     * @return timestamps Array of portfolio timestamps
     */
    function getUserPortfolioTimestamps(address _user) public view returns (uint256[] memory) {
        uint256 count = userPortfolioCount[_user];
        uint256[] memory timestamps = new uint256[](count);
        
        for (uint256 i = 0; i < count; i++) {
            timestamps[i] = userPortfolios[_user][i].timestamp;
        }
        
        return timestamps;
    }
    
    /**
     * @dev Calculate total portfolio value for a user
     * @param _user User address
     * @return totalValue Total portfolio value across all portfolios
     */
    function getTotalPortfolioValue(address _user) public view returns (uint256) {
        uint256 totalValue = 0;
        uint256 count = userPortfolioCount[_user];
        
        for (uint256 i = 0; i < count; i++) {
            totalValue += userPortfolios[_user][i].totalInvestment;
        }
        
        return totalValue;
    }
    
    /**
     * @dev Get portfolio summary for a user
     * @param _user User address
     * @return portfolioCount Number of portfolios
     * @return totalValue Total portfolio value
     * @return latestTimestamp Timestamp of most recent portfolio
     */
    function getPortfolioSummary(address _user) public view returns (
        uint256 portfolioCount,
        uint256 totalValue,
        uint256 latestTimestamp
    ) {
        portfolioCount = userPortfolioCount[_user];
        totalValue = getTotalPortfolioValue(_user);
        
        if (portfolioCount > 0) {
            latestTimestamp = userPortfolios[_user][portfolioCount - 1].timestamp;
        }
        
        return (portfolioCount, totalValue, latestTimestamp);
    }
    
    /**
     * @dev Check if user has any portfolios
     * @param _user User address
     * @return hasPortfolios True if user has portfolios, false otherwise
     */
    function hasPortfolios(address _user) public view returns (bool) {
        return userPortfolioCount[_user] > 0;
    }
} 