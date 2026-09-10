# 🎰 Vietlott Data

[![GitHub Actions](https://github.com/vietvudanh/vietlott-data/workflows/crawl/badge.svg)](https://github.com/vietvudanh/vietlott-data/actions)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Data Updated](https://img.shields.io/badge/data-daily%20updated-brightgreen.svg)](https://github.com/vietvudanh/vietlott-data/commits/main)

> 📊 **Automated Vietnamese Lottery Data Collection & Analysis**
> 
> This project automatically crawls and analyzes Vietnamese lottery data from [vietlott.vn](https://vietlott.vn/), providing comprehensive statistics and insights for all major lottery products.

## 🎯 Supported Lottery Products

| Product | Link | Description |
|---------|------|-------------|
| **Power 6/55** | [🔗 Results](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/655) | Choose 6 numbers from 1-55 |
| **Power 6/45** | [🔗 Results](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/645) | Choose 6 numbers from 1-45 |
| **Power 5/35** | [🔗 Results](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/535) | Choose 5 numbers from 1-35 |
| **Keno** | [🔗 Results](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-keno) | Fast-pace number game |
| **Max 3D** | [🔗 Results](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/max-3d) | 3-digit lottery game |
| **Max 3D Pro** | [🔗 Results](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/max-3dpro) | Enhanced 3D lottery |
| **Bingo18** | [🔗 Results](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-bingo18) | 3 numbers from 0-9 game |


## 📋 Table of Contents

- [🎯 Supported Lottery Products](#-supported-lottery-products)
- [📊 Data Statistics](#-data-statistics)
- [🔮 Prediction Models](#-prediction-models)
- [📈 Power 6/55 Analysis](#-power-655-analysis)
  - [📅 Recent Results](#-recent-results)
  - [🎲 Number Frequency (All Time)](#-number-frequency-all-time)
  - [📊 Frequency Analysis by Period](#-frequency-analysis-by-period)
- [📈 Power 5/35 Analysis](#-power-535-analysis)
  - [📅 Recent Results](#-recent-results-1)
  - [🎲 Number Frequency (All Time)](#-number-frequency-all-time-1)
  - [📊 Frequency Analysis by Period](#-frequency-analysis-by-period-1)
- [⚙️ How It Works](#️-how-it-works)
- [🚀 Installation & Usage](#-installation--usage)
- [📄 License](#-license)


## 📊 Data Statistics

| Product   |   Total Draws | Start Date   | End Date   |   Total Records | First ID   | Latest ID   |
|:----------|--------------:|:-------------|:-----------|----------------:|:-----------|:------------|
| Power 655 |          1395 | 2017-08-01   | 2026-09-08 |            1395 | 00001      | 01395       |
| Power 645 |          1363 | 2017-10-25   | 2026-09-09 |            1363 | 00198      | 01560       |
| Power 535 |           157 | 2025-06-29   | 2026-09-10 |             312 | 00001      | 00877       |
| Keno      |           956 | 2022-12-04   | 2025-07-18 |          134692 | #0110271   | #0245327    |
| 3D        |          1125 | 2019-04-22   | 2026-08-28 |            1125 | 00001      | 01125       |
| 3D Pro    |           771 | 2021-09-14   | 2026-08-27 |             771 | 00001      | 00771       |
| Bingo18   |           228 | 2024-12-03   | 2025-07-18 |           36004 | 0083123    | 0119174     |

## 🔮 Prediction Models

> ⚠️ **Disclaimer**: These are experimental models for educational purposes only. Lottery outcomes are random and cannot be predicted reliably.

### 🎲 Random Strategy Backtest

- **Strategy**: Random number selection
- **Tickets per day**: 20
- **Daily cost**: 200,000 VND
- **Results with 5+ matches**:

| date       | result                       | predicted                |
|:-----------|:-----------------------------|:-------------------------|
| 2025-03-25 | [14, 23, 29, 30, 35, 40, 17] | [40, 23, 30, 19, 17, 14] |



## 📈 Power 6/55 Analysis

### 📅 Recent Results (Last 10 draws)
| date       |    id | result                      |   page | process_time               |
|:-----------|------:|:----------------------------|-------:|:---------------------------|
| 2026-09-08 | 01395 | [8, 11, 14, 23, 25, 54, 17] |      0 | 2026-09-08T19:23:35.331150 |
| 2026-09-05 | 01394 | [9, 11, 24, 31, 33, 47, 21] |      0 | 2026-09-05T19:16:24.699593 |
| 2026-09-03 | 01393 | [8, 9, 16, 42, 46, 47, 11]  |      0 | 2026-09-04T20:43:06.111602 |
| 2026-09-01 | 01392 | [1, 17, 41, 44, 49, 55, 45] |      0 | 2026-09-04T20:43:06.111602 |
| 2026-08-29 | 01391 | [5, 10, 15, 29, 34, 45, 24] |      0 | 2026-09-04T20:43:06.120236 |
| 2026-08-27 | 01390 | [1, 3, 11, 21, 26, 44, 10]  |      0 | 2026-09-04T20:43:06.120236 |
| 2026-08-25 | 01389 | [5, 7, 13, 18, 31, 40, 14]  |      0 | 2026-09-04T20:43:06.120236 |
| 2026-08-22 | 01388 | [9, 18, 19, 21, 25, 36, 8]  |      0 | 2026-09-04T20:43:06.120236 |
| 2026-08-20 | 01387 | [2, 8, 29, 38, 39, 51, 47]  |      0 | 2026-09-04T20:43:06.120236 |
| 2026-08-18 | 01386 | [3, 15, 18, 38, 41, 48, 30] |      0 | 2026-09-04T20:43:06.120236 |

### 🎲 Number Frequency (All Time)
|   result |   count |    % | -   |   result |   count |    % | -   | result   | count   | %    |
|---------:|--------:|-----:|:----|---------:|--------:|-----:|:----|:---------|:--------|:-----|
|        1 |     188 | 1.93 |     |       21 |     175 | 1.79 |     | 41       | 206     | 2.11 |
|        2 |     161 | 1.65 |     |       22 |     206 | 2.11 |     | 42       | 181     | 1.85 |
|        3 |     189 | 1.94 |     |       23 |     188 | 1.93 |     | 43       | 198     | 2.03 |
|        4 |     144 | 1.47 |     |       24 |     178 | 1.82 |     | 44       | 182     | 1.86 |
|        5 |     182 | 1.86 |     |       25 |     160 | 1.64 |     | 45       | 181     | 1.85 |
|        6 |     143 | 1.46 |     |       26 |     166 | 1.7  |     | 46       | 182     | 1.86 |
|        7 |     157 | 1.61 |     |       27 |     162 | 1.66 |     | 47       | 178     | 1.82 |
|        8 |     196 | 2.01 |     |       28 |     158 | 1.62 |     | 48       | 190     | 1.95 |
|        9 |     195 | 2    |     |       29 |     191 | 1.96 |     | 49       | 174     | 1.78 |
|       10 |     166 | 1.7  |     |       30 |     162 | 1.66 |     | 50       | 177     | 1.81 |
|       11 |     183 | 1.87 |     |       31 |     187 | 1.92 |     | 51       | 197     | 2.02 |
|       12 |     180 | 1.84 |     |       32 |     186 | 1.9  |     | 52       | 177     | 1.81 |
|       13 |     173 | 1.77 |     |       33 |     180 | 1.84 |     | 53       | 187     | 1.92 |
|       14 |     179 | 1.83 |     |       34 |     196 | 2.01 |     | 54       | 168     | 1.72 |
|       15 |     166 | 1.7  |     |       35 |     170 | 1.74 |     | 55       | 179     | 1.83 |
|       16 |     175 | 1.79 |     |       36 |     167 | 1.71 |     |          |         |      |
|       17 |     161 | 1.65 |     |       37 |     158 | 1.62 |     |          |         |      |
|       18 |     178 | 1.82 |     |       38 |     172 | 1.76 |     |          |         |      |
|       19 |     174 | 1.78 |     |       39 |     172 | 1.76 |     |          |         |      |
|       20 |     189 | 1.94 |     |       40 |     194 | 1.99 |     |          |         |      |

### 📊 Frequency Analysis by Period

#### Last 30 Days
|   result |   count |   % | -   |   result |   count |   % | -   | result   | count   | %   |
|---------:|--------:|----:|:----|---------:|--------:|----:|:----|:---------|:--------|:----|
|        1 |       2 | 2.2 |     |       25 |       3 | 3.3 |     | 50       | 2       | 2.2 |
|        2 |       3 | 3.3 |     |       26 |       1 | 1.1 |     | 51       | 1       | 1.1 |
|        3 |       2 | 2.2 |     |       27 |       2 | 2.2 |     | 54       | 1       | 1.1 |
|        5 |       3 | 3.3 |     |       29 |       3 | 3.3 |     | 55       | 1       | 1.1 |
|        7 |       2 | 2.2 |     |       30 |       2 | 2.2 |     |          |         |     |
|        8 |       4 | 4.4 |     |       31 |       3 | 3.3 |     |          |         |     |
|        9 |       4 | 4.4 |     |       33 |       1 | 1.1 |     |          |         |     |
|       10 |       2 | 2.2 |     |       34 |       1 | 1.1 |     |          |         |     |
|       11 |       4 | 4.4 |     |       36 |       1 | 1.1 |     |          |         |     |
|       13 |       1 | 1.1 |     |       38 |       2 | 2.2 |     |          |         |     |
|       14 |       2 | 2.2 |     |       39 |       2 | 2.2 |     |          |         |     |
|       15 |       2 | 2.2 |     |       40 |       1 | 1.1 |     |          |         |     |
|       16 |       2 | 2.2 |     |       41 |       2 | 2.2 |     |          |         |     |
|       17 |       2 | 2.2 |     |       42 |       2 | 2.2 |     |          |         |     |
|       18 |       3 | 3.3 |     |       44 |       2 | 2.2 |     |          |         |     |
|       19 |       2 | 2.2 |     |       45 |       3 | 3.3 |     |          |         |     |
|       20 |       2 | 2.2 |     |       46 |       2 | 2.2 |     |          |         |     |
|       21 |       3 | 3.3 |     |       47 |       3 | 3.3 |     |          |         |     |
|       23 |       1 | 1.1 |     |       48 |       1 | 1.1 |     |          |         |     |
|       24 |       2 | 2.2 |     |       49 |       1 | 1.1 |     |          |         |     |

#### Last 60 Days
|   result |   count |    % | -   |   result |   count |    % | -   | result   | count   | %    |
|---------:|--------:|-----:|:----|---------:|--------:|-----:|:----|:---------|:--------|:-----|
|        1 |       4 | 2.29 |     |       23 |       3 | 1.71 |     | 43       | 1       | 0.57 |
|        2 |       4 | 2.29 |     |       24 |       5 | 2.86 |     | 44       | 4       | 2.29 |
|        3 |       3 | 1.71 |     |       25 |       3 | 1.71 |     | 45       | 7       | 4.0  |
|        5 |       5 | 2.86 |     |       26 |       1 | 0.57 |     | 46       | 2       | 1.14 |
|        7 |       3 | 1.71 |     |       27 |       4 | 2.29 |     | 47       | 4       | 2.29 |
|        8 |       6 | 3.43 |     |       28 |       1 | 0.57 |     | 48       | 5       | 2.86 |
|        9 |       5 | 2.86 |     |       29 |       4 | 2.29 |     | 49       | 3       | 1.71 |
|       10 |       3 | 1.71 |     |       30 |       3 | 1.71 |     | 50       | 3       | 1.71 |
|       11 |       6 | 3.43 |     |       31 |       4 | 2.29 |     | 51       | 4       | 2.29 |
|       12 |       1 | 0.57 |     |       32 |       1 | 0.57 |     | 53       | 1       | 0.57 |
|       13 |       2 | 1.14 |     |       33 |       5 | 2.86 |     | 54       | 3       | 1.71 |
|       14 |       5 | 2.86 |     |       34 |       1 | 0.57 |     | 55       | 5       | 2.86 |
|       15 |       2 | 1.14 |     |       35 |       2 | 1.14 |     |          |         |      |
|       16 |       4 | 2.29 |     |       36 |       2 | 1.14 |     |          |         |      |
|       17 |       2 | 1.14 |     |       37 |       2 | 1.14 |     |          |         |      |
|       18 |       4 | 2.29 |     |       38 |       4 | 2.29 |     |          |         |      |
|       19 |       3 | 1.71 |     |       39 |       5 | 2.86 |     |          |         |      |
|       20 |       3 | 1.71 |     |       40 |       4 | 2.29 |     |          |         |      |
|       21 |       4 | 2.29 |     |       41 |       4 | 2.29 |     |          |         |      |
|       22 |       3 | 1.71 |     |       42 |       3 | 1.71 |     |          |         |      |

#### Last 90 Days
|   result |   count |    % | -   |   result |   count |    % | -   | result   | count   | %    |
|---------:|--------:|-----:|:----|---------:|--------:|-----:|:----|:---------|:--------|:-----|
|        1 |       7 | 2.63 |     |       21 |       5 | 1.88 |     | 41       | 7       | 2.63 |
|        2 |       7 | 2.63 |     |       22 |       4 | 1.5  |     | 42       | 6       | 2.26 |
|        3 |       4 | 1.5  |     |       23 |       7 | 2.63 |     | 43       | 3       | 1.13 |
|        4 |       3 | 1.13 |     |       24 |       5 | 1.88 |     | 44       | 6       | 2.26 |
|        5 |       9 | 3.38 |     |       25 |       4 | 1.5  |     | 45       | 8       | 3.01 |
|        6 |       1 | 0.38 |     |       26 |       2 | 0.75 |     | 46       | 5       | 1.88 |
|        7 |       5 | 1.88 |     |       27 |       4 | 1.5  |     | 47       | 6       | 2.26 |
|        8 |       9 | 3.38 |     |       28 |       4 | 1.5  |     | 48       | 5       | 1.88 |
|        9 |       7 | 2.63 |     |       29 |       4 | 1.5  |     | 49       | 6       | 2.26 |
|       10 |       4 | 1.5  |     |       30 |       4 | 1.5  |     | 50       | 3       | 1.13 |
|       11 |       7 | 2.63 |     |       31 |       6 | 2.26 |     | 51       | 4       | 1.5  |
|       12 |       1 | 0.38 |     |       32 |       2 | 0.75 |     | 52       | 2       | 0.75 |
|       13 |       5 | 1.88 |     |       33 |       8 | 3.01 |     | 53       | 2       | 0.75 |
|       14 |       8 | 3.01 |     |       34 |       2 | 0.75 |     | 54       | 4       | 1.5  |
|       15 |       4 | 1.5  |     |       35 |       3 | 1.13 |     | 55       | 6       | 2.26 |
|       16 |       6 | 2.26 |     |       36 |       4 | 1.5  |     |          |         |      |
|       17 |       4 | 1.5  |     |       37 |       2 | 0.75 |     |          |         |      |
|       18 |       6 | 2.26 |     |       38 |       5 | 1.88 |     |          |         |      |
|       19 |       4 | 1.5  |     |       39 |       5 | 1.88 |     |          |         |      |
|       20 |       5 | 1.88 |     |       40 |       7 | 2.63 |     |          |         |      |



## ⚙️ How It Works

### 🤖 Automated Data Collection

This project runs completely automatically using **GitHub Actions** - no server required!

- **⏰ Schedule**: Runs daily via [GitHub Actions workflow](.github/workflows/crawl.yaml)
- **🔄 Process**: Fetches latest results → Processes data → Commits to repository
- **📊 Analysis**: Generates statistics and updates README automatically

### 🕵️ Data Crawling Method

The data collection works by:
1. **🔍 Network Analysis**: Inspecting browser-server communication
2. **🐍 Python Replication**: Recreating the data fetch logic in Python
3. **📋 Structured Storage**: Saving results in JSONL format for easy analysis
4. **🔄 Continuous Updates**: Daily automated runs ensure fresh data

> **Note**: This is purely for educational and research purposes. No gambling advice is provided.


## 🚀 Installation & Usage

### 📦 Install via pip

```bash
pip install -i https://test.pypi.org/simple/ vietlott-data==0.1.3
```

### 💻 Command Line Interface

#### 🔍 Crawl Data

```bash
vietlott-crawl [OPTIONS] PRODUCT

# Options:
#   --run-date TEXT       Specific date to crawl
#   --index_from INTEGER  Starting page index
#   --index_to INTEGER    Ending page index
#   --help               Show help message
```

#### 🔧 Backfill Missing Data

```bash
vietlott-missing [OPTIONS] PRODUCT

# Options:
#   --limit INTEGER  Number of pages to process
#   --help          Show help message
```

### 🛠️ Development Setup

```bash
# Clone the repository
git clone https://github.com/vietvudanh/vietlott-data.git
cd vietlott-data

# Install dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <strong>⭐ If you find this project useful, please consider giving it a star!</strong>
</div>

