"""Safety and risk management features for the RUGS.FUN Trading Bot."""
import time
import logging
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timedelta

from . import config

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    """Represents a single trade."""
    entry_time: float
    entry_price: float
    stake_amount: float
    bet_id: Optional[str] = None
    exit_time: Optional[float] = None
    exit_price: Optional[float] = None
    profit: Optional[float] = None
    is_active: bool = True


@dataclass
class SafetyManager:
    """Manages safety features and risk controls."""
    
    # Daily tracking
    daily_start_time: float = field(default_factory=time.time)
    daily_profit: float = 0.0
    daily_loss: float = 0.0
    
    # Consecutive losses tracking
    consecutive_losses: int = 0
    consecutive_wins: int = 0
    
    # Trade history
    trades: List[Trade] = field(default_factory=list)
    
    # Current trade
    current_trade: Optional[Trade] = None
    
    # Emergency stop flag
    emergency_stop: bool = False
    stop_reason: Optional[str] = None
    
    def should_place_bet(self, current_price: float) -> tuple[bool, str]:
        """Check if it's safe to place a bet.
        
        Args:
            current_price: Current market price
            
        Returns:
            Tuple of (should_place, reason)
        """
        # Check emergency stop
        if self.emergency_stop:
            return False, f"Emergency stop active: {self.stop_reason}"
        
        # Check if already in position
        if self.current_trade and self.current_trade.is_active:
            return False, "Already in an active position"
        
        # Check daily loss limit
        if self.daily_loss >= config.MAX_DAILY_LOSS:
            self.trigger_emergency_stop(f"Daily loss limit reached: {self.daily_loss:.6f} SOL")
            return False, f"Daily loss limit reached: {self.daily_loss:.6f} SOL"
        
        # Check consecutive losses
        if self.consecutive_losses >= config.MAX_CONSECUTIVE_LOSSES:
            self.trigger_emergency_stop(f"Max consecutive losses reached: {self.consecutive_losses}")
            return False, f"Max consecutive losses reached: {self.consecutive_losses}"
        
        # Check if we're in dry run mode
        if config.DRY_RUN:
            logger.info("🧪 DRY RUN: Would place bet but simulating only")
        
        return True, "Safe to place bet"
    
    def should_sell_position(self, current_price: float) -> tuple[bool, str]:
        """Check if we should sell the current position.
        
        Args:
            current_price: Current market price
            
        Returns:
            Tuple of (should_sell, reason)
        """
        if not self.current_trade or not self.current_trade.is_active:
            return False, "No active position"
        
        current_time = time.time()
        entry_price = self.current_trade.entry_price
        entry_time = self.current_trade.entry_time
        
        # Calculate current profit multiplier
        profit_multiplier = current_price / entry_price
        
        # Check profit target
        if profit_multiplier >= config.PER_TRADE_PROFIT_MULTIPLIER_TARGET:
            return True, f"Profit target reached: {profit_multiplier:.4f}x"
        
        # Check stop loss
        if profit_multiplier <= config.STOP_LOSS_MULTIPLIER:
            return True, f"Stop loss triggered: {profit_multiplier:.4f}x"
        
        # Check maximum position time
        position_time = current_time - entry_time
        if position_time >= config.MAX_POSITION_TIME_SECONDS:
            return True, f"Max position time reached: {position_time:.0f}s"
        
        # Check emergency stop
        if self.emergency_stop:
            return True, f"Emergency stop: {self.stop_reason}"
        
        return False, f"Hold position (current: {profit_multiplier:.4f}x)"
    
    def start_trade(self, entry_price: float, stake_amount: float, bet_id: str = None) -> Trade:
        """Start a new trade.
        
        Args:
            entry_price: Entry price for the trade
            stake_amount: Amount staked
            bet_id: Optional bet ID from the exchange
            
        Returns:
            The created Trade object
        """
        if self.current_trade and self.current_trade.is_active:
            logger.warning("Starting new trade while previous trade is still active!")
        
        self.current_trade = Trade(
            entry_time=time.time(),
            entry_price=entry_price,
            stake_amount=stake_amount,
            bet_id=bet_id
        )
        
        self.trades.append(self.current_trade)
        
        if config.DRY_RUN:
            logger.info(f"🧪 DRY RUN: Simulated trade started - Entry: {entry_price:.6f}, Stake: {stake_amount:.6f}")
        else:
            logger.info(f"💰 Trade started - Entry: {entry_price:.6f}, Stake: {stake_amount:.6f}, ID: {bet_id}")
        
        return self.current_trade
    
    def close_trade(self, exit_price: float, payout: float = None) -> Optional[Trade]:
        """Close the current trade.
        
        Args:
            exit_price: Exit price for the trade
            payout: Total payout received (optional)
            
        Returns:
            The closed Trade object or None if no active trade
        """
        if not self.current_trade or not self.current_trade.is_active:
            logger.warning("Attempting to close trade but no active trade found")
            return None
        
        # Calculate profit
        if payout is not None:
            profit = payout - self.current_trade.stake_amount
        else:
            # Calculate profit based on price difference
            profit_multiplier = exit_price / self.current_trade.entry_price
            profit = self.current_trade.stake_amount * (profit_multiplier - 1)
        
        # Update trade
        self.current_trade.exit_time = time.time()
        self.current_trade.exit_price = exit_price
        self.current_trade.profit = profit
        self.current_trade.is_active = False
        
        # Update daily tracking
        if profit > 0:
            self.daily_profit += profit
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        else:
            self.daily_loss += abs(profit)
            self.consecutive_losses += 1
            self.consecutive_wins = 0
        
        # Log trade result
        trade_duration = self.current_trade.exit_time - self.current_trade.entry_time
        profit_multiplier = exit_price / self.current_trade.entry_price
        
        if config.DRY_RUN:
            logger.info(f"🧪 DRY RUN: Simulated trade closed")
        
        if profit > 0:
            logger.info(f"✅ Trade PROFIT: {profit:.6f} SOL ({profit_multiplier:.4f}x) in {trade_duration:.1f}s")
        else:
            logger.info(f"❌ Trade LOSS: {profit:.6f} SOL ({profit_multiplier:.4f}x) in {trade_duration:.1f}s")
        
        # Update stats
        self._log_stats()
        
        completed_trade = self.current_trade
        self.current_trade = None
        
        return completed_trade
    
    def trigger_emergency_stop(self, reason: str):
        """Trigger emergency stop with reason."""
        self.emergency_stop = True
        self.stop_reason = reason
        logger.error(f"🚨 EMERGENCY STOP TRIGGERED: {reason}")
    
    def reset_daily_stats(self):
        """Reset daily statistics (call at start of new day)."""
        current_time = time.time()
        if current_time - self.daily_start_time >= 86400:  # 24 hours
            logger.info("📅 Resetting daily statistics")
            self.daily_start_time = current_time
            self.daily_profit = 0.0
            self.daily_loss = 0.0
    
    def _log_stats(self):
        """Log current trading statistics."""
        total_trades = len(self.trades)
        if total_trades == 0:
            return
        
        profitable_trades = sum(1 for t in self.trades if t.profit and t.profit > 0)
        win_rate = (profitable_trades / total_trades) * 100
        
        net_profit = self.daily_profit - self.daily_loss
        
        logger.info(f"📊 Session Stats: {total_trades} trades, {win_rate:.1f}% win rate, "
                   f"Net P&L: {net_profit:.6f} SOL")
        logger.info(f"🔥 Consecutive: {self.consecutive_wins} wins, {self.consecutive_losses} losses")
    
    def get_daily_stats(self) -> dict:
        """Get daily statistics summary."""
        total_trades = len([t for t in self.trades if t.entry_time >= self.daily_start_time])
        profitable_trades = len([t for t in self.trades 
                               if t.entry_time >= self.daily_start_time and t.profit and t.profit > 0])
        
        win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
        net_profit = self.daily_profit - self.daily_loss
        
        return {
            "total_trades": total_trades,
            "profitable_trades": profitable_trades,
            "win_rate": win_rate,
            "daily_profit": self.daily_profit,
            "daily_loss": self.daily_loss,
            "net_profit": net_profit,
            "consecutive_wins": self.consecutive_wins,
            "consecutive_losses": self.consecutive_losses,
            "emergency_stop": self.emergency_stop,
            "stop_reason": self.stop_reason,
        } 