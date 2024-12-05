

from ta.momentum import rsi as RSI
from ta.volatility import average_true_range as ATR
from ta.trend import cci as CCI, adx as ADX, ema_indicator as EMA, sma_indicator as SMA
import pandas as pd




class EMAIndicator(IndicatorMixin):
    """EMA - Exponential Moving Average

    Args:
        close(pandas.Series): dataset 'Close' column.
        window(int): n period.
        fillna(bool): if True, fill nan values.
    """

    def __init__(self, close: pd.Series, window: int = 14, fillna: bool = False):
        self._close = close
        self._window = window
        self._fillna = fillna

    def ema_indicator(self) -> pd.Series:
        """Exponential Moving Average (EMA)

        Returns:
            pandas.Series: New feature generated.
        """
        ema_ = _ema(self._close, self._window, self._fillna)
        return pd.Series(ema_, name=f"ema_{self._window}")


# class SMAIndicator(IndicatorMixin):
#     """SMA - Simple Moving Average

#     Args:
#         close(pandas.Series): dataset 'Close' column.
#         window(int): n period.
#         fillna(bool): if True, fill nan values.
#     """

#     def __init__(self, close: pd.Series, window: int, fillna: bool = False):
#         self._close = close
#         self._window = window
#         self._fillna = fillna

#     def sma_indicator(self) -> pd.Series:
#         """Simple Moving Average (SMA)

#         Returns:
#             pandas.Series: New feature generated.
#         """
#         sma_ = _sma(self._close, self._window, self._fillna)
#         return pd.Series(sma_, name=f"sma_{self._window}")




# class CCIIndicator(IndicatorMixin):
#     """Commodity Channel Index (CCI)

#     CCI measures the difference between a security's price change and its
#     average price change. High positive readings indicate that prices are well
#     above their average, which is a show of strength. Low negative readings
#     indicate that prices are well below their average, which is a show of
#     weakness.

#     http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:commodity_channel_index_cci

#     Args:
#         high(pandas.Series): dataset 'High' column.
#         low(pandas.Series): dataset 'Low' column.
#         close(pandas.Series): dataset 'Close' column.
#         window(int): n period.
#         constant(int): constant.
#         fillna(bool): if True, fill nan values.
#     """

#     def __init__(
#         self,
#         high: pd.Series,
#         low: pd.Series,
#         close: pd.Series,
#         window: int = 20,
#         constant: float = 0.015,
#         fillna: bool = False,
#     ):
#         self._high = high
#         self._low = low
#         self._close = close
#         self._window = window
#         self._constant = constant
#         self._fillna = fillna
#         self._run()

#     def _run(self):
#         def _mad(x):
#             return np.mean(np.abs(x - np.mean(x)))

#         min_periods = 0 if self._fillna else self._window
#         typical_price = (self._high + self._low + self._close) / 3.0
#         self._cci = (
#             typical_price
#             - typical_price.rolling(self._window, min_periods=min_periods).mean()
#         ) / (
#             self._constant
#             * typical_price.rolling(self._window, min_periods=min_periods).apply(
#                 _mad, True
#             )
#         )

#     def cci(self) -> pd.Series:
#         """Commodity Channel Index (CCI)

#         Returns:
#             pandas.Series: New feature generated.
#         """
#         cci_series = self._check_fillna(self._cci, value=0)
#         return pd.Series(cci_series, name="cci")
    
    
    
    
# class ADXIndicator(IndicatorMixin):
#     """Average Directional Movement Index (ADX)

#     The Plus Directional Indicator (+DI) and Minus Directional Indicator (-DI)
#     are derived from smoothed averages of these differences, and measure trend
#     direction over time. These two indicators are often referred to
#     collectively as the Directional Movement Indicator (DMI).

#     The Average Directional Index (ADX) is in turn derived from the smoothed
#     averages of the difference between +DI and -DI, and measures the strength
#     of the trend (regardless of direction) over time.

#     Using these three indicators together, chartists can determine both the
#     direction and strength of the trend.

#     http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:average_directional_index_adx

#     Args:
#         high(pandas.Series): dataset 'High' column.
#         low(pandas.Series): dataset 'Low' column.
#         close(pandas.Series): dataset 'Close' column.
#         window(int): n period.
#         fillna(bool): if True, fill nan values.
#     """

#     def __init__(
#         self,
#         high: pd.Series,
#         low: pd.Series,
#         close: pd.Series,
#         window: int = 14,
#         fillna: bool = False,
#     ):
#         self._high = high
#         self._low = low
#         self._close = close
#         self._window = window
#         self._fillna = fillna
#         self._run()

#     def _run(self):
#         if self._window == 0:
#             raise ValueError("window may not be 0")

#         close_shift = self._close.shift(1)

#         pdm = _get_min_max(self._high, close_shift, "max")
#         pdn = _get_min_max(self._low, close_shift, "min")

#         diff_directional_movement = pdm - pdn

#         self._trs_initial = np.zeros(self._window - 1)
#         self._trs = np.zeros(len(self._close) - (self._window - 1))
#         self._trs[0] = diff_directional_movement.dropna().iloc[0 : self._window].sum()
#         diff_directional_movement = diff_directional_movement.reset_index(drop=True)

#         for i in range(1, len(self._trs) - 1):
#             self._trs[i] = (
#                 self._trs[i - 1]
#                 - (self._trs[i - 1] / float(self._window))
#                 + diff_directional_movement[self._window + i]
#             )

#         diff_up = self._high - self._high.shift(1)
#         diff_down = self._low.shift(1) - self._low

#         pos = abs(((diff_up > diff_down) & (diff_up > 0)) * diff_up)
#         neg = abs(((diff_down > diff_up) & (diff_down > 0)) * diff_down)

#         self._dip = np.zeros(len(self._close) - (self._window - 1))
#         self._dip[0] = pos.dropna().iloc[0 : self._window].sum()

#         pos = pos.reset_index(drop=True)

#         for i in range(1, len(self._dip) - 1):
#             self._dip[i] = (
#                 self._dip[i - 1]
#                 - (self._dip[i - 1] / float(self._window))
#                 + pos[self._window + i]
#             )

#         self._din = np.zeros(len(self._close) - (self._window - 1))
#         self._din[0] = neg.dropna().iloc[0 : self._window].sum()

#         neg = neg.reset_index(drop=True)

#         for i in range(1, len(self._din) - 1):
#             self._din[i] = (
#                 self._din[i - 1]
#                 - (self._din[i - 1] / float(self._window))
#                 + neg[self._window + i]
#             )

#     def adx(self) -> pd.Series:
#         """Average Directional Index (ADX)

#         Returns:
#             pandas.Series: New feature generated.tr
#         """
#         dip = np.zeros(len(self._trs))

#         for idx, value in enumerate(self._trs):
#             if value != 0:
#                 dip[idx] = 100 * (self._dip[idx] / value)

#             else:
#                 dip[idx] = 0

#         din = np.zeros(len(self._trs))

#         for idx, value in enumerate(self._trs):
#             if value != 0:
#                 din[idx] = 100 * (self._din[idx] / value)

#             else:
#                 din[idx] = 0

#         directional_index = np.zeros(len(self._trs))

#         for idx in range(len(self._trs)):
#             if dip[idx] + din[idx] != 0:
#                 directional_index[idx] = 100 * np.abs(
#                     (dip[idx] - din[idx]) / (dip[idx] + din[idx])
#                 )

#             else:
#                 directional_index[idx] = 0

#         adx_series = np.zeros(len(self._trs))
#         adx_series[self._window] = directional_index[0 : self._window].mean()

#         for i in range(self._window + 1, len(adx_series)):
#             adx_series[i] = (
#                 (adx_series[i - 1] * (self._window - 1)) + directional_index[i - 1]
#             ) / float(self._window)

#         adx_series = np.concatenate((self._trs_initial, adx_series), axis=0)
#         adx_series = pd.Series(data=adx_series, index=self._close.index)
#         adx_series = self._check_fillna(adx_series, value=20)

#         return pd.Series(adx_series, name="adx")

#     def adx_pos(self) -> pd.Series:
#         """Plus Directional Indicator (+DI)

#         Returns:
#             pandas.Series: New feature generated.
#         """
#         dip = np.zeros(len(self._close))

#         for i in range(1, len(self._trs) - 1):
#             if self._trs[i] != 0:
#                 dip[i + self._window] = 100 * (self._dip[i] / self._trs[i])

#             else:
#                 dip[i + self._window] = 0

#         adx_pos_series = self._check_fillna(
#             pd.Series(dip, index=self._close.index), value=20
#         )

#         return pd.Series(adx_pos_series, name="adx_pos")

#     def adx_neg(self) -> pd.Series:
#         """Minus Directional Indicator (-DI)

#         Returns:
#             pandas.Series: New feature generated.
#         """
#         din = np.zeros(len(self._close))

#         for i in range(1, len(self._trs) - 1):
#             if self._trs[i] != 0:
#                 din[i + self._window] = 100 * (self._din[i] / self._trs[i])

#             else:
#                 din[i + self._window] = 0

#         adx_neg_series = self._check_fillna(
#             pd.Series(din, index=self._close.index), value=20
#         )

#         return pd.Series(adx_neg_series, name="adx_neg")




# def average_true_range(high, low, close, window=14, fillna=False):
#     """Average True Range (ATR)

#     The indicator provide an indication of the degree of price volatility.
#     Strong moves, in either direction, are often accompanied by large ranges,
#     or large True Ranges.

#     http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:average_true_range_atr

#     Args:
#         high(pandas.Series): dataset 'High' column.
#         low(pandas.Series): dataset 'Low' column.
#         close(pandas.Series): dataset 'Close' column.
#         window(int): n period.
#         fillna(bool): if True, fill nan values.

#     Returns:
#         pandas.Series: New feature generated.
#     """
#     indicator = AverageTrueRange(
#         high=high, low=low, close=close, window=window, fillna=fillna
#     )
#     return indicator.average_true_range()



# def rsi(close, window=14, fillna=False) -> pd.Series:
#     """Relative Strength Index (RSI)

#     Compares the magnitude of recent gains and losses over a specified time
#     period to measure speed and change of price movements of a security. It is
#     primarily used to attempt to identify overbought or oversold conditions in
#     the trading of an asset.

#     https://www.investopedia.com/terms/r/rsi.asp

#     Args:
#         close(pandas.Series): dataset 'Close' column.
#         window(int): n period.
#         fillna(bool): if True, fill nan values.

#     Returns:
#         pandas.Series: New feature generated.
#     """
#     return RSIIndicator(close=close, window=window, fillna=fillna).rsi()