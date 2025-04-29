# Grover Quantum Search & Web Information Retrieval System

## Overview

This project implements a quantum-enhanced information retrieval system that combines Grover's quantum search algorithm with classical web content aggregation. It demonstrates how quantum algorithms can provide a theoretical advantage in search operations while integrating with practical web data collection.

The system features a complete graphical user interface allowing users to:

- Crawl web content based on keywords
- Build a local unstructured database
- Compare classical and quantum search performance
- Visualize quantum circuits and measurement results

## Key Features

- **Quantum Search Implementation**: Full simulation of Grover's algorithm using Qiskit
- **Multi-Source Web Crawler**: Aggregate content from multiple search engines
- **Classical vs. Quantum Comparison**: Visual performance analysis and metrics
- **Interactive Quantum Visualization**: Circuit diagrams and measurement distributions
- **Elegant PyQt5 Interface**: User-friendly design with light/dark theme support

## Project Structure

```
├── grover/                     # Grover's algorithm implementation
│   ├── grover_core.py          # Core quantum search logic
│   └── oracle.py               # Oracle gate implementation
├── web_crawler/                # Web content aggregation
│   ├── aggregator.py           # Content deduplication and processing
│   ├── baidu.py                # Baidu search engine crawler
│   ├── sogou.py                # Sogou search engine crawler
│   ├── crawler.py              # Base crawler functionality
│   └── multi_crawler.py        # Multi-source orchestration
├── gui/                        # PyQt5 GUI implementation
│   └── main_window.py          # Main application window
├── classical_search.py         # Classical search implementation
├── database.py                 # Local database management
├── main.py                     # Application entry point
├── requirements.txt            # Dependencies
├── quantum_computing_report.md # Detailed project report
└── README.md                   # This file
```

## Theoretical Foundation

Grover's algorithm provides a quadratic speedup for searching unstructured databases:

- Classical search: O(N) queries required
- Quantum search: O(√N) queries required

This advantage becomes increasingly significant as the database size grows:

| Database Size   | Classical        | Quantum        | Speedup |
| --------------- | ---------------- | -------------- | ------- |
| 100 items       | ~50 queries      | ~10 queries    | 5x      |
| 10,000 items    | ~5,000 queries   | ~100 queries   | 50x     |
| 1,000,000 items | ~500,000 queries | ~1,000 queries | 500x    |

## Installation & Setup

### Prerequisites

- Python 3.8+
- Pip package manager

### Installation Steps

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/grover-quantum-search.git
   cd grover-quantum-search
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python main.py
   ```

## Usage Guide

### Web Content Crawling

1. Enter a keyword in the "Keyword" field
2. Click "Crawl Web Content"
3. View results in the database tab

### Performing Searches

1. Enter a target string in the "Target" field
2. Select either "Classical Search" or "Grover Quantum Search"
3. Click "Search"
4. View results in the results panel

### Quantum Visualization

1. Perform a quantum search
2. Click "Quantum Search Details"
3. Explore the quantum circuit and measurement results

### Algorithm Comparison

1. Click "Algorithm Efficiency Comparison"
2. View the performance metrics and theoretical complexity charts

## Technology Stack

- **Quantum Computing**: Qiskit (IBM's quantum computing framework)
- **Data Visualization**: Matplotlib, Qiskit visualization tools
- **Web Crawling**: Requests, BeautifulSoup4
- **GUI Framework**: PyQt5
- **Data Management**: JSON-based local database

## Educational Value

This project serves as an educational tool for understanding:

- Quantum computing fundamentals
- Grover's search algorithm implementation
- Practical applications of quantum algorithms
- Integration of quantum and classical systems
- Web content aggregation and search techniques

## Future Directions

1. **Real Quantum Hardware Integration**: Adapt simulation for IBM Q hardware
2. **Advanced Oracle Implementations**: Support for complex search criteria
3. **Quantum Machine Learning**: Integrate quantum classification algorithms
4. **Distributed Database Support**: Scale to larger, distributed data sources
5. **Additional Quantum Algorithms**: Implement Shor's, QFT, and others

## References

1. Nielsen, M. A., & Chuang, I. L. (2010). Quantum Computation and Quantum Information.
2. Grover, L. K. (1996). A fast quantum mechanical algorithm for database search.
3. IBM Qiskit Documentation: https://qiskit.org/documentation/

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

_This project was developed as a final assignment for the Quantum Computing course, demonstrating the practical application of quantum search algorithms in information retrieval systems._
