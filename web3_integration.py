import os
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

class EthereumPortfolioManager:
    def __init__(self):
        self.w3 = None
        self.contract = None
        self.contract_address = None
        self.account = None
        self.contract_abi = None
        
        # Initialize Web3 connection
        self._initialize_web3()
        
    def _initialize_web3(self):
        """Initialize Web3 connection and contract"""
        try:
            # Connect to Ethereum network
            rpc_url = os.getenv("ETHEREUM_RPC_URL")
            if not rpc_url:
                rpc_url = "https://mainnet.infura.io/v3/YOUR_PROJECT_ID"
            
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            # Note: PoA middleware removed for compatibility
            
            # Check connection
            if self.w3.is_connected():
                pass
            else:
                return
            
            # Load contract ABI and address
            self._load_contract()
            
        except Exception as e:
            pass
    
    def _load_contract(self):
        """Load smart contract ABI and address from build artifacts"""
        try:
            # Load ABI from build artifacts
            abi_path = "contracts/build/PortfolioStorage_metadata.json"
            if os.path.exists(abi_path):
                with open(abi_path, 'r') as f:
                    metadata = json.load(f)
                    self.contract_abi = metadata['output']['abi']
            else:
                # Fallback ABI (simplified version)
                self.contract_abi = [
                    {
                        "inputs": [
                            {"internalType": "string[]", "name": "assetIds", "type": "string[]"},
                            {"internalType": "uint256[]", "name": "allocations", "type": "uint256[]"},
                            {"internalType": "uint256", "name": "totalInvestment", "type": "uint256"},
                            {"internalType": "string", "name": "riskProfile", "type": "string"},
                            {"internalType": "string[]", "name": "sectors", "type": "string[]"}
                        ],
                        "name": "storePortfolio",
                        "outputs": [],
                        "stateMutability": "nonpayable",
                        "type": "function"
                    },
                    {
                        "inputs": [
                            {"internalType": "address", "name": "user", "type": "address"},
                            {"internalType": "uint256", "name": "portfolioIndex", "type": "uint256"}
                        ],
                        "name": "getPortfolio",
                        "outputs": [
                            {"internalType": "string[]", "name": "assetIds", "type": "string[]"},
                            {"internalType": "uint256[]", "name": "allocations", "type": "uint256[]"},
                            {"internalType": "uint256", "name": "totalInvestment", "type": "uint256"},
                            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                            {"internalType": "string", "name": "riskProfile", "type": "string"},
                            {"internalType": "string[]", "name": "sectors", "type": "string[]"}
                        ],
                        "stateMutability": "view",
                        "type": "function"
                    },
                    {
                        "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
                        "name": "getUserPortfolioCount",
                        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                        "stateMutability": "view",
                        "type": "function"
                    }
                ]
            
            # Contract address (deployed on Sepolia)
            self.contract_address = os.getenv("CONTRACT_ADDRESS", "0xd0214254f898F8855C73Bd1bBD080Cb5a06A131e")
            if not self.contract_address or self.contract_address == "0x0000000000000000000000000000000000000000":
                print("Warning: CONTRACT_ADDRESS not set. Using demo mode.")
                return
            
            # Initialize contract
            self.contract = self.w3.eth.contract(
                address=self.contract_address,
                abi=self.contract_abi
            )
            
            print(f"✅ Smart contract loaded: {self.contract_address}")
            
        except Exception as e:
            print(f"❌ Error loading contract: {str(e)}")
    
    def store_portfolio_on_blockchain(self, portfolio_data, risk_profile="medium", sectors=None):
        """
        Store portfolio allocation on Ethereum blockchain
        
        Args:
            portfolio_data (dict): Portfolio data with allocations
            risk_profile (str): Risk profile ("low", "medium", "high")
            sectors (list): Selected sectors (e.g., ["DeFi", "Layer 1"])
            
        Returns:
            bool: Success status
        """
        if not self.w3 or not self.contract:
            print("❌ Web3 or contract not initialized")
            return False
        
        try:
            # Prepare portfolio data for blockchain
            asset_ids = list(portfolio_data.keys())
            allocations = []
            
            # Convert percentages to basis points (1% = 100)
            for asset_id in asset_ids:
                allocation_percentage = portfolio_data[asset_id]
                allocation_basis_points = int(allocation_percentage * 100)
                allocations.append(allocation_basis_points)
            
            # Validate total allocation
            total_allocation = sum(allocations)
            if total_allocation != 10000:  # 100% in basis points
                print(f"❌ Total allocation must be 100%. Got: {total_allocation/100}%")
                return False
            
            # Default sectors if not provided
            if sectors is None:
                sectors = ["DeFi", "Layer 1"]
            
            # Calculate total investment (scaled by 1e18 for precision)
            total_investment = int(1000000 * 10**18)  # Example: $1M investment
            
            # Prepare transaction
            transaction = self.contract.functions.storePortfolio(
                asset_ids,
                allocations,
                total_investment,
                risk_profile,
                sectors
            ).build_transaction({
                'from': self.account.address if self.account else self.w3.eth.accounts[0],
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(
                    self.account.address if self.account else self.w3.eth.accounts[0]
                )
            })
            
            # Sign and send transaction
            if self.account:
                signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            else:
                # For demo purposes, just return success
                print("✅ Portfolio data prepared for blockchain storage (demo mode)")
                return True
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if tx_receipt.status == 1:
                print(f"✅ Portfolio stored on blockchain. Transaction: {tx_hash.hex()}")
                return True
            else:
                print(f"❌ Transaction failed: {tx_hash.hex()}")
                return False
                
        except Exception as e:
            print(f"❌ Error storing portfolio on blockchain: {str(e)}")
            return False
    
    def get_user_portfolios(self, user_address):
        """
        Retrieve user's portfolios from blockchain
        
        Args:
            user_address (str): User's Ethereum address
            
        Returns:
            list: Array of portfolio data
        """
        if not self.w3 or not self.contract:
            print("❌ Web3 or contract not initialized")
            return []
        
        try:
            # Get portfolio count
            portfolio_count = self.contract.functions.getUserPortfolioCount(user_address).call()
            
            portfolios = []
            for i in range(portfolio_count):
                portfolio_data = self.contract.functions.getPortfolio(user_address, i).call()
                
                # Convert basis points back to percentages
                allocations = {}
                for j, asset_id in enumerate(portfolio_data[0]):
                    allocation_basis_points = portfolio_data[1][j]
                    allocation_percentage = allocation_basis_points / 100
                    allocations[asset_id] = allocation_percentage
                
                portfolio = {
                    'allocations': allocations,
                    'totalInvestment': portfolio_data[2] / 10**18,  # Convert from scaled value
                    'timestamp': portfolio_data[3],
                    'riskProfile': portfolio_data[4],
                    'sectors': portfolio_data[5]
                }
                
                portfolios.append(portfolio)
            
            return portfolios
            
        except Exception as e:
            print(f"❌ Error retrieving portfolios: {str(e)}")
            return []
    
    def get_portfolio_value(self, user_address):
        """
        Get total portfolio value for a user
        
        Args:
            user_address (str): User's Ethereum address
            
        Returns:
            float: Total portfolio value
        """
        if not self.w3 or not self.contract:
            return 0.0
        
        try:
            total_value = self.contract.functions.getTotalPortfolioValue(user_address).call()
            return total_value / 10**18  # Convert from scaled value
        except Exception as e:
            print(f"❌ Error getting portfolio value: {str(e)}")
            return 0.0
    
    def get_portfolio_summary(self, user_address):
        """
        Get portfolio summary for a user
        
        Args:
            user_address (str): User's Ethereum address
            
        Returns:
            dict: Portfolio summary
        """
        if not self.w3 or not self.contract:
            return None
        
        try:
            summary = self.contract.functions.getPortfolioSummary(user_address).call()
            return {
                'portfolioCount': summary[0],
                'totalValue': summary[1] / 10**18,  # Convert from scaled value
                'latestTimestamp': summary[2]
            }
        except Exception as e:
            print(f"❌ Error getting portfolio summary: {str(e)}")
            return None
    
    def setup_account(self, private_key=None):
        """
        Setup account for transactions
        
        Args:
            private_key (str): Private key for signing transactions
        """
        if private_key:
            self.account = self.w3.eth.account.from_key(private_key)
            print(f"✅ Account set up: {self.account.address}")
        else:
            print("⚠️ No private key provided. Using demo mode.")
    
    def get_network_info(self):
        """Get current network information"""
        if not self.w3:
            return None
        
        try:
            return {
                'chain_id': self.w3.eth.chain_id,
                'block_number': self.w3.eth.block_number,
                'gas_price': self.w3.eth.gas_price,
                'is_connected': self.w3.is_connected()
            }
        except Exception as e:
            print(f"❌ Error getting network info: {str(e)}")
            return None
    
    def get_contract_info(self):
        """Get contract information"""
        if not self.contract:
            return None
        
        try:
            return {
                'address': self.contract.address,
                'abi_functions': len([f for f in self.contract_abi if f.get('type') == 'function']),
                'abi_events': len([e for e in self.contract_abi if e.get('type') == 'event'])
            }
        except Exception as e:
            print(f"❌ Error getting contract info: {str(e)}")
            return None

# Example usage
if __name__ == "__main__":
    # Initialize portfolio manager
    portfolio_manager = EthereumPortfolioManager()
    
    # Example portfolio data
    sample_portfolio = {
        'bitcoin': 0.4,
        'ethereum': 0.3,
        'aave': 0.2,
        'solana': 0.1
    }
    
    # Store portfolio (demo mode)
    success = portfolio_manager.store_portfolio_on_blockchain(sample_portfolio)
    print(f"Portfolio storage: {'Success' if success else 'Failed'}")
    
    # Get network info
    network_info = portfolio_manager.get_network_info()
    if network_info:
        print(f"Network: Chain ID {network_info['chain_id']}, Block {network_info['block_number']}")
    
    # Get contract info
    contract_info = portfolio_manager.get_contract_info()
    if contract_info:
        print(f"Contract: {contract_info['address']}, Functions: {contract_info['abi_functions']}") 