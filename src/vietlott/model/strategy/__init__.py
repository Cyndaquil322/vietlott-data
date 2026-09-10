"""
Lottery prediction strategies module (Legacy Shim).

This module contains various strategies for predicting lottery numbers,
along with backtesting and parameter tuning capabilities.
Re-exports from vietlott.model.legacy_strategies for full backward compatibility.
"""

try:
    from vietlott.model.legacy_strategies import (
        BacktestResult,
        ColdNumbersStrategy,
        FrequencyStrategy,
        HotNumbersStrategy,
        NotRepeatStrategy,
        ParameterTuner,
        PatternStrategy,
        PredictModel,
        RandomModel,
        StrategyBacktester,
        StrategyComparator,
    )
except ImportError:
    try:
        from src.vietlott.model.legacy_strategies import (
            BacktestResult,
            ColdNumbersStrategy,
            FrequencyStrategy,
            HotNumbersStrategy,
            NotRepeatStrategy,
            ParameterTuner,
            PatternStrategy,
            PredictModel,
            RandomModel,
            StrategyBacktester,
            StrategyComparator,
        )
    except ImportError:
        from .backtest import BacktestResult, ParameterTuner, StrategyBacktester, StrategyComparator
        from .base import PredictModel
        from .frequency import ColdNumbersStrategy, FrequencyStrategy, HotNumbersStrategy
        from .not_repeat import NotRepeatStrategy
        from .pattern import PatternStrategy
        from .random_strategy import RandomModel

__all__ = [
    # Base classes
    "PredictModel",
    # Strategy implementations
    "RandomModel",
    "NotRepeatStrategy",
    "FrequencyStrategy",
    "HotNumbersStrategy",
    "ColdNumbersStrategy",
    "PatternStrategy",
    # Backtesting and tuning
    "StrategyBacktester",
    "ParameterTuner",
    "StrategyComparator",
    "BacktestResult",
]
