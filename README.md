# Function Calling Benchmark

This project contains a comprehensive benchmark suite for testing function calling capabilities across different modules including math operations, string manipulation, data handling, validation, weather information, and more.

# <font color=red>ONLY FOR PYTHON DIRECTORY: fc-python folder</font>

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Setup Instructions

1. Clone the repository and navigate to the project directory:
   ```bash
   cd fc-python
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Before running the benchmarks, you need to configure the following in `config.py`:

1. API Configuration:
   - `OPENAI_API_KEY`: Your Silicon Flow API key
   - `MODEL_NAME`: The model you want to benchmark (e.g., "THUDM/glm-4-9b-chat")
   - `BASE_URL`: The API endpoint (default: "https://api.siliconflow.cn/v1")

2. Benchmark Configuration:
   - `BENCHMARK_ITERATIONS`: Number of iterations for each test case
   - `BENCHMARK_RESULTS_DIR`: Directory for storing benchmark results (default: "benchmark_results")

**Note:** Do not modify the `BASE_URL` and `BENCHMARK_RESULTS_DIR` values.

## Running the Benchmarks

You can run the benchmarks in two ways:

1. Run all benchmarks:
   ```bash
   python run_all_benchmarks.py
   ```

2. Run individual module benchmarks:
   ```bash
   python benchmark_fcmath.py      # Math operations
   python benchmark_fcstring.py    # String operations
   python benchmark_fcdata.py      # Data handling
   python benchmark_fcvalidation.py # Validation
   python benchmark_fcweather.py   # Weather information
   python benchmark_fcdefinition.py # Definition handling
   ```

## Benchmark Results

Results will be saved in the `benchmark_results` directory. Each benchmark run generates detailed performance metrics and logs.

## Project Structure

- `FC*.py`: Core function modules
- `benchmark_*.py`: Individual benchmark scripts
- `run_all_benchmarks.py`: Script to run all benchmarks
- `config.py`: Configuration settings
- `requirements.txt`: Project dependencies

## Troubleshooting

If you encounter any issues:

1. Ensure all dependencies are correctly installed
2. Verify your API key is valid and has sufficient permissions
3. Check that the model name is correctly specified
4. Ensure you have proper internet connectivity for API calls

## Support

For any issues or questions, please open an issue in the repository.
