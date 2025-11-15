#!/usr/bin/env python3
"""
AI Trading System Simulation
Test both Qwen and DeepSeek models on historical data
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from market_data_manager import MarketDataManager
from core.trading_engine import TradingEngine
from models.database import TradingAccount, create_database_engine, create_session_factory
from config.settings import get_settings, INDIAN_STOCKS

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TradingSimulation:
    """Run AI trading simulation on historical data"""
    
    def __init__(self):
        self.settings = get_settings()
        self.symbols = list(INDIAN_STOCKS.keys())
        
        # Market data manager
        self.market_manager = MarketDataManager(self.symbols)
        
        # Trading engine
        self.trading_engine = None
        
        # Simulation results
        self.results = {
            "qwen": {"trades": [], "pnl": 0, "capital": 10000},
            "deepseek": {"trades": [], "pnl": 0, "capital": 10000}
        }
        
    async def setup(self):
        """Setup simulation environment"""
        logger.info("Setting up simulation environment...")
        
        # Initialize trading engine
        self.trading_engine = TradingEngine()
        await self.trading_engine.initialize()
        
        logger.info("Simulation setup completed")
    
    def fetch_historical_data(self, days: int = 7):
        """Step 1: Fetch and save historical data"""
        logger.info(f"=== Fetching {days} days of historical data ===")
        self.market_manager.fetch_and_save_historical_data(days)
        logger.info("Historical data saved to CSV files")
    
    def start_simulation(self):
        """Step 2: Start simulation mode"""
        logger.info("=== Starting simulation mode ===")
        self.market_manager.start_simulation_mode()
        
        # Print simulation stats
        progress = self.market_manager.get_simulation_progress()
        current_time = self.market_manager.get_current_simulation_time()
        
        logger.info(f"Simulation progress: {progress:.1f}%")
        logger.info(f"Current simulation time: {current_time}")
    
    async def run_simulation(self, max_iterations: int = 100):
        """Step 3: Run the actual simulation"""
        logger.info(f"=== Running simulation ({max_iterations} iterations) ===")
        
        # Get trading accounts (create mock accounts for simulation)
        accounts = await self._get_simulation_accounts()
        
        iteration = 0
        
        while iteration < max_iterations:
            current_time = self.market_manager.get_current_simulation_time()
            progress = self.market_manager.get_simulation_progress()
            
            if progress >= 99.0:  # Simulation complete
                logger.info("Simulation completed - reached end of historical data")
                break
            
            logger.info(f"\n--- Iteration {iteration + 1} ---")
            logger.info(f"Simulation time: {current_time}")
            logger.info(f"Progress: {progress:.1f}%")
            
            # Process each account (like real trading engine)
            for account in accounts:
                try:
                    # This will use simulation data instead of live data
                    await self.trading_engine.process_account(account)
                    logger.info(f"Processed {account.name}")
                    
                except Exception as e:
                    logger.error(f"Error processing {account.name}: {e}")
            
            # Advance simulation by 5 minutes
            self.market_manager.advance_simulation(5)
            
            iteration += 1
            
            # Brief pause to see progress
            await asyncio.sleep(0.1)
        
        logger.info("Simulation run completed")
    
    async def _get_simulation_accounts(self):
        """Create mock trading accounts for simulation"""
        # Mock accounts for testing
        qwen_account = TradingAccount(
            id="sim_qwen",
            name="Qwen_Simulation",
            model_name="qwen/qwen3-235b-a22b-2507",
            dhan_client_id="mock_client",
            dhan_access_token="mock_token",
            account_id="mock_account",
            capital_allocation=10000,
            allocation_percentage=50,
            is_active=True
        )
        
        deepseek_account = TradingAccount(
            id="sim_deepseek", 
            name="DeepSeek_Simulation",
            model_name="deepseek/deepseek-v3.2-exp",
            dhan_client_id="mock_client",
            dhan_access_token="mock_token", 
            account_id="mock_account",
            capital_allocation=10000,
            allocation_percentage=50,
            is_active=True
        )
        
        return [qwen_account, deepseek_account]
    
    def print_simulation_results(self):
        """Print final simulation results"""
        logger.info("\n" + "="*60)
        logger.info("SIMULATION RESULTS")
        logger.info("="*60)
        
        for model_name, results in self.results.items():
            logger.info(f"\n{model_name.upper()} Model:")
            logger.info(f"  Final Capital: ₹{results['capital']:,.2f}")
            logger.info(f"  Total P&L: ₹{results['pnl']:,.2f}")
            logger.info(f"  Return: {(results['pnl']/10000)*100:.2f}%")
            logger.info(f"  Total Trades: {len(results['trades'])}")
        
        # Compare performance
        qwen_return = (self.results['qwen']['pnl']/10000)*100
        deepseek_return = (self.results['deepseek']['pnl']/10000)*100
        
        logger.info(f"\n🏆 PERFORMANCE COMPARISON:")
        logger.info(f"Qwen 3 235B:     {qwen_return:+.2f}%")
        logger.info(f"DeepSeek v3.2:   {deepseek_return:+.2f}%")
        
        if qwen_return > deepseek_return:
            logger.info("🥇 Winner: Qwen 3 235B")
        elif deepseek_return > qwen_return:
            logger.info("🥇 Winner: DeepSeek v3.2") 
        else:
            logger.info("🤝 Tie!")

async def main():
    """Main simulation runner"""
    simulation = TradingSimulation()
    
    try:
        # Step 1: Fetch historical data
        logger.info("Step 1: Fetching historical data...")
        simulation.fetch_historical_data(days=7)
        
        # Step 2: Setup simulation
        logger.info("Step 2: Setting up simulation...")
        await simulation.setup()
        simulation.start_simulation()
        
        # Step 3: Run simulation
        logger.info("Step 3: Running simulation...")
        await simulation.run_simulation(max_iterations=200)  # ~16 hours of trading simulation
        
        # Step 4: Results
        logger.info("Step 4: Displaying results...")
        simulation.print_simulation_results()
        
        logger.info("\n🎉 Simulation completed successfully!")
        
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        raise

if __name__ == "__main__":
    print("🚀 AI Trading System Simulation")
    print("Testing Qwen vs DeepSeek on last 7 days of data")
    print("="*60)
    
    asyncio.run(main())