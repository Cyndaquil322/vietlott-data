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
| 2021-03-02 | [23, 29, 45, 46, 49, 51, 1] | [18, 1, 51, 46, 45, 49] |



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
|   result |   count |    % | -   | result   | count   | %    |
|---------:|--------:|-----:|:----|:---------|:--------|:-----|
|        1 |       1 | 2.04 |     | 32       | 1       | 2.04 |
|        2 |       1 | 2.04 |     | 33       | 1       | 2.04 |
|        5 |       2 | 4.08 |     | 34       | 1       | 2.04 |
|        7 |       1 | 2.04 |     | 41       | 1       | 2.04 |
|        8 |       2 | 4.08 |     | 42       | 1       | 2.04 |
|        9 |       2 | 4.08 |     | 43       | 1       | 2.04 |
|       10 |       1 | 2.04 |     | 44       | 1       | 2.04 |
|       11 |       3 | 6.12 |     | 45       | 2       | 4.08 |
|       14 |       1 | 2.04 |     | 46       | 1       | 2.04 |
|       15 |       1 | 2.04 |     | 47       | 3       | 6.12 |
|       16 |       1 | 2.04 |     | 49       | 1       | 2.04 |
|       17 |       2 | 4.08 |     | 50       | 1       | 2.04 |
|       21 |       1 | 2.04 |     | 51       | 1       | 2.04 |
|       22 |       1 | 2.04 |     | 53       | 1       | 2.04 |
|       23 |       1 | 2.04 |     | 54       | 2       | 4.08 |
|       24 |       3 | 6.12 |     | 55       | 1       | 2.04 |
|       25 |       1 | 2.04 |     |          |         |      |
|       28 |       1 | 2.04 |     |          |         |      |
|       29 |       1 | 2.04 |     |          |         |      |
|       31 |       2 | 4.08 |     |          |         |      |

#### Last 60 Days
|   result |   count |    % | -   |   result |   count |    % | -   | result   | count   | %    |
|---------:|--------:|-----:|:----|---------:|--------:|-----:|:----|:---------|:--------|:-----|
|        1 |       3 | 2.14 |     |       23 |       2 | 1.43 |     | 43       | 2       | 1.43 |
|        2 |       5 | 3.57 |     |       24 |       4 | 2.86 |     | 44       | 3       | 2.14 |
|        3 |       2 | 1.43 |     |       25 |       3 | 2.14 |     | 45       | 4       | 2.86 |
|        5 |       5 | 3.57 |     |       26 |       1 | 0.71 |     | 46       | 2       | 1.43 |
|        7 |       3 | 2.14 |     |       27 |       2 | 1.43 |     | 47       | 5       | 3.57 |
|        8 |       4 | 2.86 |     |       28 |       2 | 1.43 |     | 48       | 1       | 0.71 |
|        9 |       4 | 2.86 |     |       29 |       4 | 2.86 |     | 49       | 3       | 2.14 |
|       10 |       2 | 1.43 |     |       30 |       2 | 1.43 |     | 50       | 3       | 2.14 |
|       11 |       5 | 3.57 |     |       31 |       5 | 3.57 |     | 51       | 4       | 2.86 |
|       12 |       1 | 0.71 |     |       32 |       1 | 0.71 |     | 53       | 1       | 0.71 |
|       13 |       1 | 0.71 |     |       33 |       2 | 1.43 |     | 54       | 3       | 2.14 |
|       14 |       5 | 3.57 |     |       34 |       1 | 0.71 |     | 55       | 3       | 2.14 |
|       15 |       2 | 1.43 |     |       35 |       1 | 0.71 |     |          |         |      |
|       16 |       3 | 2.14 |     |       36 |       1 | 0.71 |     |          |         |      |
|       17 |       2 | 1.43 |     |       37 |       1 | 0.71 |     |          |         |      |
|       18 |       4 | 2.86 |     |       38 |       3 | 2.14 |     |          |         |      |
|       19 |       2 | 1.43 |     |       39 |       4 | 2.86 |     |          |         |      |
|       20 |       2 | 1.43 |     |       40 |       3 | 2.14 |     |          |         |      |
|       21 |       3 | 2.14 |     |       41 |       2 | 1.43 |     |          |         |      |
|       22 |       1 | 0.71 |     |       42 |       3 | 2.14 |     |          |         |      |

#### Last 90 Days
|   result |   count |    % | -   |   result |   count |    % | -   | result   | count   | %    |
|---------:|--------:|-----:|:----|---------:|--------:|-----:|:----|:---------|:--------|:-----|
|        1 |       4 | 1.73 |     |       21 |       4 | 1.73 |     | 41       | 7       | 3.03 |
|        2 |       6 | 2.6  |     |       22 |       5 | 2.16 |     | 42       | 5       | 2.16 |
|        3 |       3 | 1.3  |     |       23 |       4 | 1.73 |     | 43       | 4       | 1.73 |
|        4 |       1 | 0.43 |     |       24 |       6 | 2.6  |     | 44       | 6       | 2.6  |
|        5 |       8 | 3.46 |     |       25 |       4 | 1.73 |     | 45       | 8       | 3.46 |
|        6 |       1 | 0.43 |     |       26 |       1 | 0.43 |     | 46       | 2       | 0.87 |
|        7 |       4 | 1.73 |     |       27 |       4 | 1.73 |     | 47       | 6       | 2.6  |
|        8 |       7 | 3.03 |     |       28 |       3 | 1.3  |     | 48       | 5       | 2.16 |
|        9 |       7 | 3.03 |     |       29 |       4 | 1.73 |     | 49       | 5       | 2.16 |
|       10 |       4 | 1.73 |     |       30 |       3 | 1.3  |     | 50       | 4       | 1.73 |
|       11 |       7 | 3.03 |     |       31 |       6 | 2.6  |     | 51       | 5       | 2.16 |
|       12 |       1 | 0.43 |     |       32 |       3 | 1.3  |     | 53       | 2       | 0.87 |
|       13 |       4 | 1.73 |     |       33 |       7 | 3.03 |     | 54       | 4       | 1.73 |
|       14 |       6 | 2.6  |     |       34 |       2 | 0.87 |     | 55       | 5       | 2.16 |
|       15 |       3 | 1.3  |     |       35 |       2 | 0.87 |     |          |         |      |
|       16 |       4 | 1.73 |     |       36 |       2 | 0.87 |     |          |         |      |
|       17 |       4 | 1.73 |     |       37 |       2 | 0.87 |     |          |         |      |
|       18 |       6 | 2.6  |     |       38 |       4 | 1.73 |     |          |         |      |
|       19 |       3 | 1.3  |     |       39 |       5 | 2.16 |     |          |         |      |
|       20 |       4 | 1.73 |     |       40 |       5 | 2.16 |     |          |         |      |



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

