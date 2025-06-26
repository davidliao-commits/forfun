# Function Calling Projects

This directory contains both Node.js and Python implementations of function calling projects.

## Directory Structure

```
function-calling/
├── fc-nodejs/          # Node.js implementation
│   ├── FCmath.js       # Math function calling
│   ├── FCstring.js     # String manipulation functions
│   ├── FCvalidation.js # Data validation functions
│   ├── FCweather.js    # Weather API functions
│   ├── FCdefinition.js # Definition lookup functions
│   ├── config.js       # Configuration file
│   ├── package.json    # Node.js dependencies
│   └── benchmark_*.js  # Benchmark scripts
│
└── fc-python/          # Python implementation
    ├── FCmath.py       # Math function calling
    ├── FCstring.py     # String manipulation functions
    ├── FCvalidation.py # Data validation functions
    ├── FCweather.py    # Weather API functions
    ├── FCdefinition.py # Definition lookup functions
    ├── config.py       # Configuration file
    ├── requirements.txt # Python dependencies
    └── benchmark_*.py  # Benchmark scripts
```

## Getting Started

### Node.js Setup
```bash
cd fc-nodejs
npm install
```

### Python Setup
```bash
cd fc-python
pip install -r requirements.txt
```

## Running Benchmarks

### Node.js Benchmarks
```bash
cd fc-nodejs
node benchmark_fcmath.js
node benchmark_fcstring.js
node benchmark_fcvalidation.js
node benchmark_fcweather.js
node benchmark_fcdefinition.js
```

### Python Benchmarks
```bash
cd fc-python
python benchmark_fcmath.py
python benchmark_fcstring.py
python benchmark_fcvalidation.py
python benchmark_fcweather.py
python benchmark_fcdefinition.py
```

## Configuration

Both implementations use similar configuration files:
- `config.js` (Node.js) / `config.py` (Python)
- Contains API keys, model names, and benchmark settings
- Update these files with your own API credentials

## Features

Both implementations provide:
- Math operations (add, subtract, multiply, divide, sqrt, derivative, integral)
- String manipulation (word count, substring search, email extraction, etc.)
- Data validation (email, phone, password, JSON schema, etc.)
- Weather API integration
- Definition lookup
- Comprehensive benchmarking 