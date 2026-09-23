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
| Power 655 |          1397 | 2017-08-01   | 2026-09-12 |            1397 | 00001      | 01397       |
| Power 645 |          1365 | 2017-10-25   | 2026-09-13 |            1365 | 00198      | 01562       |
| Power 535 |           398 | 2025-06-29   | 2026-09-14 |             795 | 00001      | 00885       |
| Keno      |           960 | 2022-12-04   | 2026-09-14 |          134902 | #0110271   | #0295720    |
| 3D        |          1130 | 2019-04-22   | 2026-09-09 |            1130 | 00001      | 01130       |
| 3D Pro    |           777 | 2021-09-14   | 2026-09-10 |             777 | 00001      | 00777       |
| Bingo18   |           233 | 2024-12-03   | 2026-09-14 |           36631 | 0083123    | 0186495     |

## 🔮 Prediction Models

> ⚠️ **Disclaimer**: These are experimental models for educational purposes only. Lottery outcomes are random and cannot be predicted reliably.

### 🎲 Random Strategy Backtest

- **Strategy**: Random number selection
- **Tickets per day**: 20
- **Daily cost**: 200,000 VND
- **Results with 5+ matches**:

| date       | result                      | predicted               |
|:-----------|:----------------------------|:------------------------|
| 2019-04-16 | [16, 29, 32, 33, 52, 53, 5] | [10, 5, 32, 16, 33, 29] |



## 📈 Power 6/55 Analysis

### 📅 Recent Results (Last 10 draws)
| date       |    id | result                      |   page | process_time               |
|:-----------|------:|:----------------------------|-------:|:---------------------------|
| 2026-09-12 | 01397 | [7, 24, 31, 43, 47, 54, 22] |      0 | 2026-09-12T21:45:41.616280 |
| 2026-09-10 | 01396 | [2, 5, 28, 32, 51, 53, 50]  |      0 | 2026-09-10 22:54:59.462202 |
| 2026-09-08 | 01395 | [8, 11, 14, 23, 25, 54, 17] |      0 | 2026-09-08 19:23:35.331150 |
| 2026-09-05 | 01394 | [9, 11, 24, 31, 33, 47, 21] |      0 | 2026-09-05 19:16:24.699593 |
| 2026-09-03 | 01393 | [8, 9, 16, 42, 46, 47, 11]  |      0 | 2026-09-04 20:43:06.111602 |
| 2026-09-01 | 01392 | [1, 17, 41, 44, 49, 55, 45] |      0 | 2026-09-04 20:43:06.111602 |
| 2026-08-29 | 01391 | [5, 10, 15, 29, 34, 45, 24] |      0 | 2026-09-04 20:43:06.120236 |
| 2026-08-27 | 01390 | [1, 3, 11, 21, 26, 44, 10]  |      0 | 2026-09-04 20:43:06.120236 |
| 2026-08-25 | 01389 | [5, 7, 13, 18, 31, 40, 14]  |      0 | 2026-09-04 20:43:06.120236 |
| 2026-08-22 | 01388 | [9, 18, 19, 21, 25, 36, 8]  |      0 | 2026-09-04 20:43:06.120236 |

### 🎲 Number Frequency (All Time)
|   result |   count |    % | -   |   result |   count |    % | -   | result   | count   | %    |
|---------:|--------:|-----:|:----|---------:|--------:|-----:|:----|:---------|:--------|:-----|
|        1 |     188 | 1.92 |     |       21 |     175 | 1.79 |     | 41       | 206     | 2.11 |
|        2 |     162 | 1.66 |     |       22 |     207 | 2.12 |     | 42       | 181     | 1.85 |
|        3 |     189 | 1.93 |     |       23 |     188 | 1.92 |     | 43       | 199     | 2.04 |
|        4 |     144 | 1.47 |     |       24 |     179 | 1.83 |     | 44       | 182     | 1.86 |
|        5 |     183 | 1.87 |     |       25 |     160 | 1.64 |     | 45       | 181     | 1.85 |
|        6 |     143 | 1.46 |     |       26 |     166 | 1.7  |     | 46       | 182     | 1.86 |
|        7 |     158 | 1.62 |     |       27 |     162 | 1.66 |     | 47       | 179     | 1.83 |
|        8 |     196 | 2    |     |       28 |     159 | 1.63 |     | 48       | 190     | 1.94 |
|        9 |     195 | 1.99 |     |       29 |     191 | 1.95 |     | 49       | 174     | 1.78 |
|       10 |     166 | 1.7  |     |       30 |     162 | 1.66 |     | 50       | 178     | 1.82 |
|       11 |     183 | 1.87 |     |       31 |     188 | 1.92 |     | 51       | 198     | 2.02 |
|       12 |     180 | 1.84 |     |       32 |     187 | 1.91 |     | 52       | 177     | 1.81 |
|       13 |     173 | 1.77 |     |       33 |     180 | 1.84 |     | 53       | 188     | 1.92 |
|       14 |     179 | 1.83 |     |       34 |     196 | 2    |     | 54       | 169     | 1.73 |
|       15 |     166 | 1.7  |     |       35 |     170 | 1.74 |     | 55       | 179     | 1.83 |
|       16 |     175 | 1.79 |     |       36 |     167 | 1.71 |     |          |         |      |
|       17 |     161 | 1.65 |     |       37 |     158 | 1.62 |     |          |         |      |
|       18 |     178 | 1.82 |     |       38 |     172 | 1.76 |     |          |         |      |
|       19 |     174 | 1.78 |     |       39 |     172 | 1.76 |     |          |         |      |
|       20 |     189 | 1.93 |     |       40 |     194 | 1.98 |     |          |         |      |

### 📊 Frequency Analysis by Period

#### Last 30 Days
|   result |   count |    % | -   |   result |   count |    % | -   | result   | count   | %    |
|---------:|--------:|-----:|:----|---------:|--------:|-----:|:----|:---------|:--------|:-----|
|        1 |       2 | 3.17 |     |       26 |       1 | 1.59 |     | 55       | 1       | 1.59 |
|        2 |       1 | 1.59 |     |       28 |       1 | 1.59 |     |          |         |      |
|        3 |       1 | 1.59 |     |       29 |       1 | 1.59 |     |          |         |      |
|        5 |       3 | 4.76 |     |       31 |       3 | 4.76 |     |          |         |      |
|        7 |       2 | 3.17 |     |       32 |       1 | 1.59 |     |          |         |      |
|        8 |       2 | 3.17 |     |       33 |       1 | 1.59 |     |          |         |      |
|        9 |       2 | 3.17 |     |       34 |       1 | 1.59 |     |          |         |      |
|       10 |       2 | 3.17 |     |       40 |       1 | 1.59 |     |          |         |      |
|       11 |       4 | 6.35 |     |       41 |       1 | 1.59 |     |          |         |      |
|       13 |       1 | 1.59 |     |       42 |       1 | 1.59 |     |          |         |      |
|       14 |       2 | 3.17 |     |       43 |       1 | 1.59 |     |          |         |      |
|       15 |       1 | 1.59 |     |       44 |       2 | 3.17 |     |          |         |      |
|       16 |       1 | 1.59 |     |       45 |       2 | 3.17 |     |          |         |      |
|       17 |       2 | 3.17 |     |       46 |       1 | 1.59 |     |          |         |      |
|       18 |       1 | 1.59 |     |       47 |       3 | 4.76 |     |          |         |      |
|       21 |       2 | 3.17 |     |       49 |       1 | 1.59 |     |          |         |      |
|       22 |       1 | 1.59 |     |       50 |       1 | 1.59 |     |          |         |      |
|       23 |       1 | 1.59 |     |       51 |       1 | 1.59 |     |          |         |      |
|       24 |       3 | 4.76 |     |       53 |       1 | 1.59 |     |          |         |      |
|       25 |       1 | 1.59 |     |       54 |       2 | 3.17 |     |          |         |      |

#### Last 60 Days
|   result |   count |    % | -   |   result |   count |    % | -   | result   | count   | %    |
|---------:|--------:|-----:|:----|---------:|--------:|-----:|:----|:---------|:--------|:-----|
|        1 |       3 | 1.95 |     |       23 |       3 | 1.95 |     | 43       | 2       | 1.3  |
|        2 |       5 | 3.25 |     |       24 |       4 | 2.6  |     | 44       | 4       | 2.6  |
|        3 |       2 | 1.3  |     |       25 |       3 | 1.95 |     | 45       | 4       | 2.6  |
|        5 |       6 | 3.9  |     |       26 |       1 | 0.65 |     | 46       | 2       | 1.3  |
|        7 |       4 | 2.6  |     |       27 |       4 | 2.6  |     | 47       | 5       | 3.25 |
|        8 |       4 | 2.6  |     |       28 |       2 | 1.3  |     | 48       | 3       | 1.95 |
|        9 |       5 | 3.25 |     |       29 |       4 | 2.6  |     | 49       | 3       | 1.95 |
|       10 |       2 | 1.3  |     |       30 |       2 | 1.3  |     | 50       | 4       | 2.6  |
|       11 |       5 | 3.25 |     |       31 |       5 | 3.25 |     | 51       | 4       | 2.6  |
|       12 |       1 | 0.65 |     |       32 |       1 | 0.65 |     | 53       | 1       | 0.65 |
|       13 |       1 | 0.65 |     |       33 |       3 | 1.95 |     | 54       | 3       | 1.95 |
|       14 |       5 | 3.25 |     |       34 |       1 | 0.65 |     | 55       | 3       | 1.95 |
|       15 |       2 | 1.3  |     |       35 |       1 | 0.65 |     |          |         |      |
|       16 |       3 | 1.95 |     |       36 |       1 | 0.65 |     |          |         |      |
|       17 |       2 | 1.3  |     |       37 |       2 | 1.3  |     |          |         |      |
|       18 |       4 | 2.6  |     |       38 |       3 | 1.95 |     |          |         |      |
|       19 |       2 | 1.3  |     |       39 |       4 | 2.6  |     |          |         |      |
|       20 |       2 | 1.3  |     |       40 |       3 | 1.95 |     |          |         |      |
|       21 |       3 | 1.95 |     |       41 |       3 | 1.95 |     |          |         |      |
|       22 |       2 | 1.3  |     |       42 |       3 | 1.95 |     |          |         |      |

#### Last 90 Days
|   result |   count |    % | -   |   result |   count |    % | -   | result   | count   | %    |
|---------:|--------:|-----:|:----|---------:|--------:|-----:|:----|:---------|:--------|:-----|
|        1 |       5 | 2.04 |     |       21 |       5 | 2.04 |     | 41       | 7       | 2.86 |
|        2 |       6 | 2.45 |     |       22 |       5 | 2.04 |     | 42       | 5       | 2.04 |
|        3 |       4 | 1.63 |     |       23 |       6 | 2.45 |     | 43       | 4       | 1.63 |
|        4 |       1 | 0.41 |     |       24 |       6 | 2.45 |     | 44       | 6       | 2.45 |
|        5 |       8 | 3.27 |     |       25 |       4 | 1.63 |     | 45       | 8       | 3.27 |
|        6 |       1 | 0.41 |     |       26 |       1 | 0.41 |     | 46       | 2       | 0.82 |
|        7 |       5 | 2.04 |     |       27 |       4 | 1.63 |     | 47       | 6       | 2.45 |
|        8 |       8 | 3.27 |     |       28 |       4 | 1.63 |     | 48       | 5       | 2.04 |
|        9 |       7 | 2.86 |     |       29 |       4 | 1.63 |     | 49       | 5       | 2.04 |
|       10 |       4 | 1.63 |     |       30 |       3 | 1.22 |     | 50       | 4       | 1.63 |
|       11 |       7 | 2.86 |     |       31 |       6 | 2.45 |     | 51       | 5       | 2.04 |
|       12 |       1 | 0.41 |     |       32 |       3 | 1.22 |     | 52       | 1       | 0.41 |
|       13 |       4 | 1.63 |     |       33 |       7 | 2.86 |     | 53       | 2       | 0.82 |
|       14 |       6 | 2.45 |     |       34 |       2 | 0.82 |     | 54       | 5       | 2.04 |
|       15 |       4 | 1.63 |     |       35 |       3 | 1.22 |     | 55       | 6       | 2.45 |
|       16 |       5 | 2.04 |     |       36 |       2 | 0.82 |     |          |         |      |
|       17 |       4 | 1.63 |     |       37 |       2 | 0.82 |     |          |         |      |
|       18 |       6 | 2.45 |     |       38 |       4 | 1.63 |     |          |         |      |
|       19 |       3 | 1.22 |     |       39 |       5 | 2.04 |     |          |         |      |
|       20 |       4 | 1.63 |     |       40 |       5 | 2.04 |     |          |         |      |



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

