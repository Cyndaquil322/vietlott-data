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
| Power 655 |          1396 | 2017-08-01   | 2026-09-10 |            1396 | 00001      | 01396       |
| Power 645 |          1363 | 2017-10-25   | 2026-09-09 |            1363 | 00198      | 01560       |
| Power 535 |           394 | 2025-06-29   | 2026-09-10 |             788 | 00001      | 00878       |
| Keno      |           958 | 2022-12-04   | 2026-09-10 |          134842 | #0110271   | #0295260    |
| 3D        |          1130 | 2019-04-22   | 2026-09-09 |            1130 | 00001      | 01130       |
| 3D Pro    |           777 | 2021-09-14   | 2026-09-10 |             777 | 00001      | 00777       |
| Bingo18   |           229 | 2024-12-03   | 2026-09-10 |           36016 | 0083123    | 0185880     |

## 🔮 Prediction Models

> ⚠️ **Disclaimer**: These are experimental models for educational purposes only. Lottery outcomes are random and cannot be predicted reliably.

### 🎲 Random Strategy Backtest

- **Strategy**: Random number selection
- **Tickets per day**: 20
- **Daily cost**: 200,000 VND
- **Results with 5+ matches**:

| date       | result                      | predicted                |
|:-----------|:----------------------------|:-------------------------|
| 2018-07-21 | [7, 31, 33, 37, 46, 52, 28] | [11, 52, 33, 46, 28, 31] |



## 📈 Power 6/55 Analysis

### 📅 Recent Results (Last 10 draws)
| date       |    id | result                      |   page | process_time               |
|:-----------|------:|:----------------------------|-------:|:---------------------------|
| 2026-09-10 | 01396 | [2, 5, 28, 32, 51, 53, 50]  |      0 | 2026-09-10 22:54:59.462202 |
| 2026-09-08 | 01395 | [8, 11, 14, 23, 25, 54, 17] |      0 | 2026-09-08 19:23:35.331150 |
| 2026-09-05 | 01394 | [9, 11, 24, 31, 33, 47, 21] |      0 | 2026-09-05 19:16:24.699593 |
| 2026-09-03 | 01393 | [8, 9, 16, 42, 46, 47, 11]  |      0 | 2026-09-04 20:43:06.111602 |
| 2026-09-01 | 01392 | [1, 17, 41, 44, 49, 55, 45] |      0 | 2026-09-04 20:43:06.111602 |
| 2026-08-29 | 01391 | [5, 10, 15, 29, 34, 45, 24] |      0 | 2026-09-04 20:43:06.120236 |
| 2026-08-27 | 01390 | [1, 3, 11, 21, 26, 44, 10]  |      0 | 2026-09-04 20:43:06.120236 |
| 2026-08-25 | 01389 | [5, 7, 13, 18, 31, 40, 14]  |      0 | 2026-09-04 20:43:06.120236 |
| 2026-08-22 | 01388 | [9, 18, 19, 21, 25, 36, 8]  |      0 | 2026-09-04 20:43:06.120236 |
| 2026-08-20 | 01387 | [2, 8, 29, 38, 39, 51, 47]  |      0 | 2026-09-04 20:43:06.120236 |

### 🎲 Number Frequency (All Time)
|   result |   count |    % | -   |   result |   count |    % | -   | result   | count   | %    |
|---------:|--------:|-----:|:----|---------:|--------:|-----:|:----|:---------|:--------|:-----|
|        1 |     188 | 1.92 |     |       21 |     175 | 1.79 |     | 41       | 206     | 2.11 |
|        2 |     162 | 1.66 |     |       22 |     206 | 2.11 |     | 42       | 181     | 1.85 |
|        3 |     189 | 1.93 |     |       23 |     188 | 1.92 |     | 43       | 198     | 2.03 |
|        4 |     144 | 1.47 |     |       24 |     178 | 1.82 |     | 44       | 182     | 1.86 |
|        5 |     183 | 1.87 |     |       25 |     160 | 1.64 |     | 45       | 181     | 1.85 |
|        6 |     143 | 1.46 |     |       26 |     166 | 1.7  |     | 46       | 182     | 1.86 |
|        7 |     157 | 1.61 |     |       27 |     162 | 1.66 |     | 47       | 178     | 1.82 |
|        8 |     196 | 2.01 |     |       28 |     159 | 1.63 |     | 48       | 190     | 1.94 |
|        9 |     195 | 2    |     |       29 |     191 | 1.95 |     | 49       | 174     | 1.78 |
|       10 |     166 | 1.7  |     |       30 |     162 | 1.66 |     | 50       | 178     | 1.82 |
|       11 |     183 | 1.87 |     |       31 |     187 | 1.91 |     | 51       | 198     | 2.03 |
|       12 |     180 | 1.84 |     |       32 |     187 | 1.91 |     | 52       | 177     | 1.81 |
|       13 |     173 | 1.77 |     |       33 |     180 | 1.84 |     | 53       | 188     | 1.92 |
|       14 |     179 | 1.83 |     |       34 |     196 | 2.01 |     | 54       | 168     | 1.72 |
|       15 |     166 | 1.7  |     |       35 |     170 | 1.74 |     | 55       | 179     | 1.83 |
|       16 |     175 | 1.79 |     |       36 |     167 | 1.71 |     |          |         |      |
|       17 |     161 | 1.65 |     |       37 |     158 | 1.62 |     |          |         |      |
|       18 |     178 | 1.82 |     |       38 |     172 | 1.76 |     |          |         |      |
|       19 |     174 | 1.78 |     |       39 |     172 | 1.76 |     |          |         |      |
|       20 |     189 | 1.93 |     |       40 |     194 | 1.99 |     |          |         |      |

### 📊 Frequency Analysis by Period

#### Last 30 Days
|   result |   count |    % | -   |   result |   count |    % | -   | result   | count   | %    |
|---------:|--------:|-----:|:----|---------:|--------:|-----:|:----|:---------|:--------|:-----|
|        1 |       2 | 2.04 |     |       25 |       3 | 3.06 |     | 48       | 1       | 1.02 |
|        2 |       4 | 4.08 |     |       26 |       1 | 1.02 |     | 49       | 1       | 1.02 |
|        3 |       2 | 2.04 |     |       27 |       2 | 2.04 |     | 50       | 3       | 3.06 |
|        5 |       4 | 4.08 |     |       28 |       1 | 1.02 |     | 51       | 2       | 2.04 |
|        7 |       2 | 2.04 |     |       29 |       3 | 3.06 |     | 53       | 1       | 1.02 |
|        8 |       4 | 4.08 |     |       30 |       2 | 2.04 |     | 54       | 1       | 1.02 |
|        9 |       4 | 4.08 |     |       31 |       3 | 3.06 |     | 55       | 1       | 1.02 |
|       10 |       2 | 2.04 |     |       32 |       1 | 1.02 |     |          |         |      |
|       11 |       4 | 4.08 |     |       33 |       1 | 1.02 |     |          |         |      |
|       13 |       1 | 1.02 |     |       34 |       1 | 1.02 |     |          |         |      |
|       14 |       2 | 2.04 |     |       36 |       1 | 1.02 |     |          |         |      |
|       15 |       2 | 2.04 |     |       38 |       2 | 2.04 |     |          |         |      |
|       16 |       2 | 2.04 |     |       39 |       2 | 2.04 |     |          |         |      |
|       17 |       2 | 2.04 |     |       40 |       1 | 1.02 |     |          |         |      |
|       18 |       3 | 3.06 |     |       41 |       2 | 2.04 |     |          |         |      |
|       19 |       2 | 2.04 |     |       42 |       2 | 2.04 |     |          |         |      |
|       20 |       2 | 2.04 |     |       44 |       2 | 2.04 |     |          |         |      |
|       21 |       3 | 3.06 |     |       45 |       3 | 3.06 |     |          |         |      |
|       23 |       1 | 1.02 |     |       46 |       2 | 2.04 |     |          |         |      |
|       24 |       2 | 2.04 |     |       47 |       3 | 3.06 |     |          |         |      |

#### Last 60 Days
|   result |   count |    % | -   |   result |   count |    % | -   | result   | count   | %    |
|---------:|--------:|-----:|:----|---------:|--------:|-----:|:----|:---------|:--------|:-----|
|        1 |       4 | 2.2  |     |       23 |       3 | 1.65 |     | 43       | 1       | 0.55 |
|        2 |       5 | 2.75 |     |       24 |       5 | 2.75 |     | 44       | 4       | 2.2  |
|        3 |       3 | 1.65 |     |       25 |       3 | 1.65 |     | 45       | 7       | 3.85 |
|        5 |       6 | 3.3  |     |       26 |       1 | 0.55 |     | 46       | 2       | 1.1  |
|        7 |       3 | 1.65 |     |       27 |       4 | 2.2  |     | 47       | 4       | 2.2  |
|        8 |       6 | 3.3  |     |       28 |       2 | 1.1  |     | 48       | 5       | 2.75 |
|        9 |       5 | 2.75 |     |       29 |       4 | 2.2  |     | 49       | 3       | 1.65 |
|       10 |       3 | 1.65 |     |       30 |       3 | 1.65 |     | 50       | 4       | 2.2  |
|       11 |       6 | 3.3  |     |       31 |       4 | 2.2  |     | 51       | 5       | 2.75 |
|       12 |       1 | 0.55 |     |       32 |       2 | 1.1  |     | 53       | 2       | 1.1  |
|       13 |       2 | 1.1  |     |       33 |       5 | 2.75 |     | 54       | 3       | 1.65 |
|       14 |       5 | 2.75 |     |       34 |       1 | 0.55 |     | 55       | 5       | 2.75 |
|       15 |       2 | 1.1  |     |       35 |       2 | 1.1  |     |          |         |      |
|       16 |       4 | 2.2  |     |       36 |       2 | 1.1  |     |          |         |      |
|       17 |       2 | 1.1  |     |       37 |       2 | 1.1  |     |          |         |      |
|       18 |       4 | 2.2  |     |       38 |       4 | 2.2  |     |          |         |      |
|       19 |       3 | 1.65 |     |       39 |       5 | 2.75 |     |          |         |      |
|       20 |       3 | 1.65 |     |       40 |       4 | 2.2  |     |          |         |      |
|       21 |       4 | 2.2  |     |       41 |       4 | 2.2  |     |          |         |      |
|       22 |       3 | 1.65 |     |       42 |       3 | 1.65 |     |          |         |      |

#### Last 90 Days
|   result |   count |    % | -   |   result |   count |    % | -   | result   | count   | %    |
|---------:|--------:|-----:|:----|---------:|--------:|-----:|:----|:---------|:--------|:-----|
|        1 |       7 | 2.56 |     |       21 |       5 | 1.83 |     | 41       | 7       | 2.56 |
|        2 |       8 | 2.93 |     |       22 |       4 | 1.47 |     | 42       | 6       | 2.2  |
|        3 |       4 | 1.47 |     |       23 |       7 | 2.56 |     | 43       | 3       | 1.1  |
|        4 |       3 | 1.1  |     |       24 |       5 | 1.83 |     | 44       | 6       | 2.2  |
|        5 |      10 | 3.66 |     |       25 |       4 | 1.47 |     | 45       | 8       | 2.93 |
|        6 |       1 | 0.37 |     |       26 |       2 | 0.73 |     | 46       | 5       | 1.83 |
|        7 |       5 | 1.83 |     |       27 |       4 | 1.47 |     | 47       | 6       | 2.2  |
|        8 |       9 | 3.3  |     |       28 |       5 | 1.83 |     | 48       | 5       | 1.83 |
|        9 |       7 | 2.56 |     |       29 |       4 | 1.47 |     | 49       | 6       | 2.2  |
|       10 |       4 | 1.47 |     |       30 |       4 | 1.47 |     | 50       | 4       | 1.47 |
|       11 |       7 | 2.56 |     |       31 |       6 | 2.2  |     | 51       | 5       | 1.83 |
|       12 |       1 | 0.37 |     |       32 |       3 | 1.1  |     | 52       | 2       | 0.73 |
|       13 |       5 | 1.83 |     |       33 |       8 | 2.93 |     | 53       | 3       | 1.1  |
|       14 |       8 | 2.93 |     |       34 |       2 | 0.73 |     | 54       | 4       | 1.47 |
|       15 |       4 | 1.47 |     |       35 |       3 | 1.1  |     | 55       | 6       | 2.2  |
|       16 |       6 | 2.2  |     |       36 |       4 | 1.47 |     |          |         |      |
|       17 |       4 | 1.47 |     |       37 |       2 | 0.73 |     |          |         |      |
|       18 |       6 | 2.2  |     |       38 |       5 | 1.83 |     |          |         |      |
|       19 |       4 | 1.47 |     |       39 |       5 | 1.83 |     |          |         |      |
|       20 |       5 | 1.83 |     |       40 |       7 | 2.56 |     |          |         |      |



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

