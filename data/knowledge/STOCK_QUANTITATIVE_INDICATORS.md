# 股票量化技术指标指南

## 基于Towards Data Science: Technical Indicators in Python

---

## 技术指标概览

### Technical Indicators List

| Indicator | Category | Purpose | Time Horizon |
|-----------|----------|---------|--------------|
| SMA (Simple Moving Average) | Trend | Identify trend | 5/15 days |
| ATR (Average True Range) | Volatility | Measure volatility | 5/15 days |
| ADX (Average Directional Index) | Trend Strength | Assess trend strength | 5/15 days |
| Stochastic Oscillator | Momentum | Identify overbought/oversold | Fast/Slow |
| RSI (Relative Strength Index) | Momentum | Quantify price changes | Fast/Slow |
| MACD | Trend | Trend analysis | 5/15 days |
| Bollinger Bands | Volatility | Identify overbought/oversold | 20 days |
| Rate of Change | Momentum | Price momentum | Variable |

---

## 1. Simple Moving Average (SMA)

### 指标说明

**定义**: 计算给定时间间隔的价格平均值

**用途**: 确定股票趋势方向

**参数**:
```
- Fast SMA: 5 days (short-term)
- Slow SMA: 15 days (long-term)
- 可自定义任意时间周期
```

---

### Python实现

```python
import pandas as pd
import numpy as np

def calculate_sma(data, window):
    """
    Calculate Simple Moving Average.
    
    Args:
        data: DataFrame with 'Close' column
        window: Moving average window (e.g., 5, 15)
    
    Returns:
        Series with SMA values
    """
    return data['Close'].rolling(window=window).mean()

# Calculate Fast and Slow SMA
data['SMA_5'] = calculate_sma(data, 5)   # Fast
data['SMA_15'] = calculate_sma(data, 15)  # Slow

# Calculate SMA relationship factor
data['SMA_ratio'] = data['SMA_15'] / data['SMA_5']
data['SMA_diff'] = data['SMA_15'] - data['SMA_5']
```

---

### Trading Strategy

**买入信号**:
```
✓ Fast SMA crosses above Slow SMA (Golden Cross)
✓ Price above SMA line
✓ SMA trending upward
```

**卖出信号**:
```
✓ Fast SMA crosses below Slow SMA (Death Cross)
✓ Price below SMA line
✓ SMA trending downward
```

---

### Feature Engineering

**衍生因子**:
```python
# Ratio factor (capture relationship)
sma_ratio = sma_slow / sma_fast

# Difference factor (capture distance)
sma_diff = sma_slow - sma_fast

# Both useful for Machine Learning models
```

---

## 2. Simple Moving Average Volume

### 指标说明

**定义**: 成交量的简单移动平均

**用途**: 提供信号强度洞察

---

### Python实现

```python
def calculate_sma_volume(data, window):
    """
    Calculate Simple Moving Average of Volume.
    
    Args:
        data: DataFrame with 'Volume' column
        window: Moving average window
    
    Returns:
        Series with SMA Volume values
    """
    return data['Volume'].rolling(window=window).mean()

# Calculate Volume SMA
data['SMA_Volume_5'] = calculate_sma_volume(data, 5)
data['SMA_Volume_15'] = calculate_sma_volume(data, 15)
```

---

## 3. Wilder's Smoothing

### 指标说明

**定义**: Wells Wilder引入的平滑方法

**特点**: 对近期事件赋予更高权重

**用途**: 用于多种技术指标计算

---

### Python实现

```python
def wilders_smoothing(data, window):
    """
    Calculate Wilder's Smoothing.
    
    Wilder's smoothing places more weight on recent events
    compared to simple moving average.
    
    Args:
        data: Series to smooth
        window: Smoothing window
    
    Returns:
        Series with Wilder's smoothing values
    """
    # Wilder's smoothing formula
    # Similar to EMA but with different alpha
    alpha = 1 / window
    
    smoothed = data.copy()
    
    for i in range(window, len(data)):
        smoothed[i] = smoothed[i-1] + alpha * (data[i] - smoothed[i-1])
    
    return smoothed
```

---

## 4. Average True Range (ATR)

### 指标说明

**定义**: 衡量市场波动性的指标

**用途**: 
```
✓ 识别何时退出或进入交易
✓ 不指示交易方向
✓ 更高ATR = 更高波动性
```

---

### True Range定义

**True Range = max(以下三项)**:
```
a. High - Low
b. abs(High - Previous Close)
c. abs(Low - Previous Close)
```

---

### Python实现

```python
def calculate_atr(data, window):
    """
    Calculate Average True Range.
    
    Args:
        data: DataFrame with 'High', 'Low', 'Close' columns
        window: ATR window (e.g., 5, 15)
    
    Returns:
        Series with ATR values
    """
    # Calculate True Range
    data['TR'] = np.maximum(
        data['High'] - data['Low'],
        np.maximum(
            abs(data['High'] - data['Close'].shift(1)),
            abs(data['Low'] - data['Close'].shift(1))
        )
    )
    
    # Calculate ATR using Wilder's smoothing
    atr = wilders_smoothing(data['TR'], window)
    
    return atr

# Calculate Fast and Slow ATR
data['ATR_5'] = calculate_atr(data, 5)   # Fast
data['ATR_15'] = calculate_atr(data, 15)  # Slow
```

---

### Trading Strategy

**高波动性** (ATR高):
```
- 市场不稳定
- 可能需要调整止损距离
- 谨慎交易
```

**低波动性** (ATR低):
```
- 市场稳定
- 可能处于盘整期
- 等待突破信号
```

---

## 5. Average Directional Index (ADX)

### 指标说明

**定义**: 评估股票价格趋势强度的指标

**用途**: 
```
✓ ADX ≥ 25: 强趋势
✓ ADX < 20: 弱趋势
```

**组件**:
```
+DI: 正方向指标 (上升趋势)
-DI: 负方向指标 (下降趋势)
```

---

### Python实现

```python
def calculate_adx(data, window):
    """
    Calculate Average Directional Index.
    
    Args:
        data: DataFrame with 'High', 'Low', 'Close' columns
        window: ADX window (e.g., 5, 15)
    
    Returns:
        Series with ADX values
    """
    # Calculate +DM and -DM
    data['+DM'] = np.maximum(
        data['High'] - data['High'].shift(1),
        0
    )
    
    data['-DM'] = np.maximum(
        data['Low'].shift(1) - data['Low'],
        0
    )
    
    # Smooth +DM and -DM
    data['+DM_smooth'] = wilders_smoothing(data['+DM'], window)
    data['-DM_smooth'] = wilders_smoothing(data['-DM'], window)
    
    # Calculate ATR
    atr = calculate_atr(data, window)
    
    # Calculate +DI and -DI
    data['+DI'] = 100 * (data['+DM_smooth'] / atr)
    data['-DI'] = 100 * (data['-DM_smooth'] / atr)
    
    # Calculate DX
    data['DX'] = 100 * abs(data['+DI'] - data['-DI']) / (data['+DI'] + data['-DI'])
    
    # Calculate ADX
    adx = wilders_smoothing(data['DX'], window)
    
    return adx

# Calculate ADX
data['ADX_5'] = calculate_adx(data, 5)   # Fast
data['ADX_15'] = calculate_adx(data, 15)  # Slow
```

---

### Trading Strategy

**趋势强度判断**:
```
✓ ADX > 25: Strong trend (buy/sell)
✓ ADX < 20: Weak trend (avoid trading)
✓ ADX rising: Trend strengthening
✓ ADX falling: Trend weakening
```

**趋势方向判断**:
```
✓ +DI > -DI: Uptrend
✓ +DI < -DI: Downtrend
✓ +DI crosses +DI: Trend reversal
```

---

## 6. Stochastic Oscillator

### 指标说明

**定义**: 动量指标，识别超买/超卖证券

**用途**: 
```
✓ 超买: %K > 80
✓ 超卖: %K < 20
```

---

### Python实现

```python
def calculate_stochastic(data, k_window, d_window):
    """
    Calculate Stochastic Oscillator.
    
    Args:
        data: DataFrame with 'High', 'Low', 'Close' columns
        k_window: %K window
        d_window: %D window (smoothing of %K)
    
    Returns:
        Series with %K and %D values
    """
    # Calculate %K
    lowest_low = data['Low'].rolling(window=k_window).min()
    highest_high = data['High'].rolling(window=k_window).max()
    
    data['%K'] = 100 * (data['Close'] - lowest_low) / (highest_high - lowest_low)
    
    # Calculate %D (smoothed %K)
    data['%D'] = data['%K'].rolling(window=d_window).mean()
    
    return data['%K'], data['%D']

# Calculate Stochastic
data['%K'], data['%D'] = calculate_stochastic(data, 14, 3)
```

---

### Trading Strategy

**超买区域** (%K > 80):
```
- 可能价格过高
- 等待卖出信号
- %K crosses below %D: Sell
```

**超卖区域** (%K < 20):
```
- 可能价格过低
- 等待买入信号
- %K crosses above %D: Buy
```

---

## 7. Relative Strength Index (RSI)

### 指标说明

**定义**: 量化价格变化及其速度的动量指标

**用途**: 
```
✓ 超买: RSI > 70
✓ 超卖: RSI < 30
```

---

### Python实现

```python
def calculate_rsi(data, window):
    """
    Calculate Relative Strength Index.
    
    Args:
        data: DataFrame with 'Close' column
        window: RSI window (e.g., 14)
    
    Returns:
        Series with RSI values
    """
    # Calculate price changes
    delta = data['Close'].diff()
    
    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Calculate average gain and loss
    avg_gain = wilders_smoothing(gain, window)
    avg_loss = wilders_smoothing(loss, window)
    
    # Calculate RS
    rs = avg_gain / avg_loss
    
    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

# Calculate RSI
data['RSI_14'] = calculate_rsi(data, 14)
```

---

### Trading Strategy

**超买信号** (RSI > 70):
```
- 价格可能回调
- 等待卖出机会
- RSI crosses below 70: Sell
```

**超卖信号** (RSI < 30):
```
- 价格可能反弹
- 等待买入机会
- RSI crosses above 30: Buy
```

---

## 8. Moving Average Convergence Divergence (MACD)

### 指标说明

**定义**: 使用两个指数移动平均线的趋势分析

**组件**:
```
MACD Line: EMA(12) - EMA(26)
Signal Line: EMA(MACD, 9)
Histogram: MACD - Signal
```

**用途**: 基于收敛/发散的趋势分析

---

### Python实现

```python
def calculate_macd(data, fast, slow, signal):
    """
    Calculate MACD.
    
    Args:
        data: DataFrame with 'Close' column
        fast: Fast EMA period (e.g., 12)
        slow: Slow EMA period (e.g., 26)
        signal: Signal line period (e.g., 9)
    
    Returns:
        Series with MACD, Signal, Histogram
    """
    # Calculate EMAs
    ema_fast = data['Close'].ewm(span=fast, adjust=False).mean()
    ema_slow = data['Close'].ewm(span=slow, adjust=False).mean()
    
    # Calculate MACD Line
    macd_line = ema_fast - ema_slow
    
    # Calculate Signal Line
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    
    # Calculate Histogram
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram

# Calculate MACD (using 5/15 for consistency)
data['MACD'], data['Signal'], data['Histogram'] = calculate_macd(data, 5, 15, 9)
```

---

### Trading Strategy

**买入信号**:
```
✓ MACD crosses above Signal (Golden Cross)
✓ Histogram positive and rising
✓ MACD line trending upward
```

**卖出信号**:
```
✓ MACD crosses below Signal (Death Cross)
✓ Histogram negative and falling
✓ MACD line trending downward
```

---

## 9. Bollinger Bands

### 指标说明

**定义**: 捕捉股票波动性，识别超买/超卖

**组件**:
```
Middle Band: SMA(20)
Upper Band: SMA(20) + 2*STD(20)
Lower Band: SMA(20) - 2*STD(20)
```

**用途**: 
```
✓ 价格触及Upper Band: 超买
✓ 价格触及Lower Band: 超卖
```

---

### Python实现

```python
def calculate_bollinger_bands(data, window, num_std):
    """
    Calculate Bollinger Bands.
    
    Args:
        data: DataFrame with 'Close' column
        window: SMA window (e.g., 20)
        num_std: Number of standard deviations (e.g., 2)
    
    Returns:
        Series with Middle, Upper, Lower bands
    """
    # Calculate Middle Band (SMA)
    middle_band = data['Close'].rolling(window=window).mean()
    
    # Calculate Standard Deviation
    std = data['Close'].rolling(window=window).std()
    
    # Calculate Upper and Lower Bands
    upper_band = middle_band + (num_std * std)
    lower_band = middle_band - (num_std * std)
    
    return middle_band, upper_band, lower_band

# Calculate Bollinger Bands
data['BB_Middle'], data['BB_Upper'], data['BB_Lower'] = calculate_bollinger_bands(data, 20, 2)

# Calculate Band Width
data['BB_Width'] = data['BB_Upper'] - data['BB_Lower']

# Calculate Band Position
data['BB_Position'] = (data['Close'] - data['BB_Lower']) / (data['BB_Upper'] - data['BB_Lower'])
```

---

### Trading Strategy

**超买信号** (价格触及Upper Band):
```
- 价格可能回调
- 等待卖出机会
- 价格回归Middle Band
```

**超卖信号** (价格触及Lower Band):
```
- 价格可能反弹
- 等待买入机会
- 价格回归Middle Band
```

**波动性信号**:
```
- Band Width扩大: 波动性增加
- Band Width收窄: 波动性减少
- Squeeze: 可能突破信号
```

---

## 10. Rate of Change (ROC)

### 指标说明

**定义**: 相对固定周期前价格动量的动量指标

**用途**: 衡量价格变化速度

---

### Python实现

```python
def calculate_roc(data, window):
    """
    Calculate Rate of Change.
    
    Args:
        data: DataFrame with 'Close' column
        window: ROC window
    
    Returns:
        Series with ROC values
    """
    # Calculate ROC
    roc = 100 * (data['Close'] - data['Close'].shift(window)) / data['Close'].shift(window)
    
    return roc

# Calculate ROC
data['ROC_10'] = calculate_roc(data, 10)
```

---

### Trading Strategy

**正ROC**:
```
- 价格上涨动量
- ROC上升: 加速上涨
- ROC下降: 减速上涨
```

**负ROC**:
```
- 价格下跌动量
- ROC下降: 加速下跌
- ROC上升: 减速下跌
```

---

## 完整指标组合实现

### Comprehensive Technical Indicators

```python
import pandas as pd
import numpy as np

def add_all_technical_indicators(data):
    """
    Add comprehensive set of technical indicators.
    
    Args:
        data: DataFrame with OHLCV columns
    
    Returns:
        DataFrame with all indicators added
    """
    # Trend Indicators
    data['SMA_5'] = calculate_sma(data, 5)
    data['SMA_15'] = calculate_sma(data, 15)
    data['SMA_ratio'] = data['SMA_15'] / data['SMA_5']
    
    # Volatility Indicators
    data['ATR_5'] = calculate_atr(data, 5)
    data['ATR_15'] = calculate_atr(data, 15)
    data['BB_Middle'], data['BB_Upper'], data['BB_Lower'] = calculate_bollinger_bands(data, 20, 2)
    
    # Momentum Indicators
    data['RSI_14'] = calculate_rsi(data, 14)
    data['%K'], data['%D'] = calculate_stochastic(data, 14, 3)
    data['ROC_10'] = calculate_roc(data, 10)
    
    # Trend Strength Indicators
    data['ADX_14'] = calculate_adx(data, 14)
    
    # Trend Analysis Indicators
    data['MACD'], data['Signal'], data['Histogram'] = calculate_macd(data, 12, 26, 9)
    
    # Volume Indicators
    data['SMA_Volume_5'] = calculate_sma_volume(data, 5)
    data['SMA_Volume_15'] = calculate_sma_volume(data, 15)
    
    return data

# Usage
data = pd.read_csv('stock_data.csv')
data_with_indicators = add_all_technical_indicators(data)
```

---

## csi10实战应用

### 多指数系统集成

```python
# csi10 case: Apply indicators to multi-index system

def analyze_multi_index(hs300_data, zz500_data):
    """
    Apply technical indicators to multi-index system.
    
    Args:
        hs300_data: 沪深300 data
        zz500_data: 中证500 data
    
    Returns:
        Combined indicators with composite index
    """
    # Calculate indicators for each index
    hs300_indicators = add_all_technical_indicators(hs300_data)
    zz500_indicators = add_all_technical_indicators(zz500_data)
    
    # Calculate composite indicators (60:40 weight)
    composite = {
        'SMA_composite': 0.6 * hs300_indicators['SMA_15'] + 0.4 * zz500_indicators['SMA_15'],
        'RSI_composite': 0.6 * hs300_indicators['RSI_14'] + 0.4 * zz500_indicators['RSI_14'],
        'ATR_composite': 0.6 * hs300_indicators['ATR_15'] + 0.4 * zz500_indicators['ATR_15'],
        'ADX_composite': 0.6 * hs300_indicators['ADX_14'] + 0.4 * zz500_indicators['ADX_14']
    }
    
    return composite
```

---

## Machine Learning集成

### Feature Engineering

```python
# Prepare features for ML model

def prepare_features_for_ml(data):
    """
    Prepare technical indicators as ML features.
    
    Returns:
        Feature matrix for ML model
    """
    features = data[[
        'SMA_5', 'SMA_15', 'SMA_ratio',
        'ATR_5', 'ATR_15',
        'RSI_14', '%K', '%D',
        'ADX_14',
        'MACD', 'Signal', 'Histogram',
        'BB_Position', 'BB_Width',
        'ROC_10',
        'SMA_Volume_5', 'SMA_Volume_15'
    ]]
    
    # Add target variable (e.g., next day return)
    data['Target'] = data['Close'].pct_change().shift(-1)
    
    return features, data['Target']
```

---

## 指标自定义

### 参数调整

```python
# Customize indicators for different strategies

INDICATOR_PARAMS = {
    'short_term': {
        'sma_fast': 5,
        'sma_slow': 15,
        'rsi_window': 14,
        'atr_window': 5
    },
    'medium_term': {
        'sma_fast': 10,
        'sma_slow': 30,
        'rsi_window': 21,
        'atr_window': 14
    },
    'long_term': {
        'sma_fast': 20,
        'sma_slow': 60,
        'rsi_window': 28,
        'atr_window': 21
    }
}

def apply_strategy_params(data, strategy='short_term'):
    """
    Apply strategy-specific parameters.
    """
    params = INDICATOR_PARAMS[strategy]
    
    data['SMA_fast'] = calculate_sma(data, params['sma_fast'])
    data['SMA_slow'] = calculate_sma(data, params['sma_slow'])
    data['RSI'] = calculate_rsi(data, params['rsi_window'])
    data['ATR'] = calculate_atr(data, params['atr_window'])
    
    return data
```

---

## Pattern-Key

`stock.quantitative.indicators` - 股票量化技术指标完整指南

---

**来源**: Towards Data Science - Technical Indicators in Python
**更新时间**: 2026-04-23 15:20
**适用项目**: csi10 + BrainSystem + Quantitative Analysis