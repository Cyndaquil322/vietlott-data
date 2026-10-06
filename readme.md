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
| 2026-03-21 | [1, 6, 40, 43, 47, 53, 3]   | [53, 40, 6, 43, 47, 8]  |
| 2021-12-09 | [3, 14, 33, 40, 41, 50, 17] | [50, 14, 41, 13, 3, 40] |



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
|   result |   count |    % |
|---------:|--------:|-----:|
|        2 |       1 | 4.76 |
|        5 |       1 | 4.76 |
|        7 |       1 | 4.76 |
|        8 |       1 | 4.76 |
|       11 |       1 | 4.76 |
|       14 |       1 | 4.76 |
|       17 |       1 | 4.76 |
|       22 |       1 | 4.76 |
|       23 |       1 | 4.76 |
|       24 |       1 | 4.76 |
|       25 |       1 | 4.76 |
|       28 |       1 | 4.76 |
|       31 |       1 | 4.76 |
|       32 |       1 | 4.76 |
|       43 |       1 | 4.76 |
|       47 |       1 | 4.76 |
|       50 |       1 | 4.76 |
|       51 |       1 | 4.76 |
|       53 |       1 | 4.76 |
|       54 |       2 | 9.52 |

#### Last 60 Days
|   result |   count |    % | -   |   result |   count |    % | -   | result   | count   | %    |
|---------:|--------:|-----:|:----|---------:|--------:|-----:|:----|:---------|:--------|:-----|
|        1 |       2 | 1.79 |     |       24 |       3 | 2.68 |     | 45       | 4       | 3.57 |
|        2 |       4 | 3.57 |     |       25 |       3 | 2.68 |     | 46       | 2       | 1.79 |
|        3 |       2 | 1.79 |     |       26 |       1 | 0.89 |     | 47       | 4       | 3.57 |
|        5 |       5 | 4.46 |     |       27 |       2 | 1.79 |     | 48       | 1       | 0.89 |
|        7 |       3 | 2.68 |     |       28 |       1 | 0.89 |     | 49       | 1       | 0.89 |
|        8 |       4 | 3.57 |     |       29 |       4 | 3.57 |     | 50       | 3       | 2.68 |
|        9 |       4 | 3.57 |     |       30 |       2 | 1.79 |     | 51       | 2       | 1.79 |
|       10 |       2 | 1.79 |     |       31 |       4 | 3.57 |     | 53       | 1       | 0.89 |
|       11 |       4 | 3.57 |     |       32 |       1 | 0.89 |     | 54       | 2       | 1.79 |
|       13 |       1 | 0.89 |     |       33 |       2 | 1.79 |     | 55       | 1       | 0.89 |
|       14 |       2 | 1.79 |     |       34 |       1 | 0.89 |     |          |         |      |
|       15 |       2 | 1.79 |     |       36 |       1 | 0.89 |     |          |         |      |
|       16 |       2 | 1.79 |     |       37 |       1 | 0.89 |     |          |         |      |
|       17 |       2 | 1.79 |     |       38 |       3 | 2.68 |     |          |         |      |
|       18 |       3 | 2.68 |     |       39 |       2 | 1.79 |     |          |         |      |
|       19 |       2 | 1.79 |     |       40 |       2 | 1.79 |     |          |         |      |
|       20 |       2 | 1.79 |     |       41 |       2 | 1.79 |     |          |         |      |
|       21 |       3 | 2.68 |     |       42 |       2 | 1.79 |     |          |         |      |
|       22 |       1 | 0.89 |     |       43 |       1 | 0.89 |     |          |         |      |
|       23 |       1 | 0.89 |     |       44 |       2 | 1.79 |     |          |         |      |

#### Last 90 Days
|   result |   count |    % | -   |   result |   count |    % | -   | result   | count   | %    |
|---------:|--------:|-----:|:----|---------:|--------:|-----:|:----|:---------|:--------|:-----|
|        1 |       4 | 1.97 |     |       23 |       3 | 1.48 |     | 43       | 2       | 0.99 |
|        2 |       6 | 2.96 |     |       24 |       6 | 2.96 |     | 44       | 4       | 1.97 |
|        3 |       3 | 1.48 |     |       25 |       3 | 1.48 |     | 45       | 8       | 3.94 |
|        5 |       6 | 2.96 |     |       26 |       1 | 0.49 |     | 46       | 2       | 0.99 |
|        7 |       4 | 1.97 |     |       27 |       4 | 1.97 |     | 47       | 5       | 2.46 |
|        8 |       6 | 2.96 |     |       28 |       2 | 0.99 |     | 48       | 5       | 2.46 |
|        9 |       7 | 3.45 |     |       29 |       4 | 1.97 |     | 49       | 4       | 1.97 |
|       10 |       4 | 1.97 |     |       30 |       3 | 1.48 |     | 50       | 4       | 1.97 |
|       11 |       6 | 2.96 |     |       31 |       5 | 2.46 |     | 51       | 5       | 2.46 |
|       12 |       1 | 0.49 |     |       32 |       2 | 0.99 |     | 53       | 2       | 0.99 |
|       13 |       2 | 0.99 |     |       33 |       6 | 2.96 |     | 54       | 4       | 1.97 |
|       14 |       6 | 2.96 |     |       34 |       1 | 0.49 |     | 55       | 5       | 2.46 |
|       15 |       2 | 0.99 |     |       35 |       2 | 0.99 |     |          |         |      |
|       16 |       4 | 1.97 |     |       36 |       2 | 0.99 |     |          |         |      |
|       17 |       4 | 1.97 |     |       37 |       2 | 0.99 |     |          |         |      |
|       18 |       4 | 1.97 |     |       38 |       4 | 1.97 |     |          |         |      |
|       19 |       3 | 1.48 |     |       39 |       5 | 2.46 |     |          |         |      |
|       20 |       4 | 1.97 |     |       40 |       5 | 2.46 |     |          |         |      |
|       21 |       4 | 1.97 |     |       41 |       5 | 2.46 |     |          |         |      |
|       22 |       4 | 1.97 |     |       42 |       4 | 1.97 |     |          |         |      |



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

