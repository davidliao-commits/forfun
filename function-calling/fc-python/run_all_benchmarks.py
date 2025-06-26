import os
import sys
import time
from datetime import datetime
import json
import statistics
from config import BENCHMARK_ITERATIONS, BENCHMARK_RESULTS_DIR, OPENAI_API_KEY, BASE_URL, MODEL_NAME

# Import all benchmark modules
from benchmark_fcdefinition import test_cases as definition_test_cases
from benchmark_fcmath import run_benchmark as run_math_benchmark
from benchmark_fcvalidation import run_benchmark as run_validation_benchmark
from benchmark_fcdata import run_benchmark as run_data_benchmark
from benchmark_fcstring import test_cases as string_test_cases
from benchmark_fcweather import test_cases as weather_test_cases

# Import function_call_playground from each module
from FCdefinition import function_call_playground as definition_playground
from FCstring import function_call_playground as string_playground
from FCweather import function_call_playground as weather_playground, function_call_playground_coords, latitude, longtitude
from FCmathparallel import function_call_playground as math_parallel_playground

def run_definition_benchmark():
    """Run benchmark for definition functions"""
    import time
    import json
    import statistics
    from datetime import datetime
    import os
    
    # Create benchmark_results directory if it doesn't exist
    os.makedirs(BENCHMARK_RESULTS_DIR, exist_ok=True)
    
    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "test_cases": [],
        "summary": {}
    }
    
    for test_case in definition_test_cases:
        print(f"Running benchmark for {test_case}...")
        
        execution_times = []
        success_count = 0
        
        for i in range(BENCHMARK_ITERATIONS):
            try:
                start_time = time.time()
                response = definition_playground(test_case)
                end_time = time.time()
                
                execution_time = end_time - start_time
                execution_times.append(execution_time)
                success_count += 1
                
                print(f"Iteration {i+1}/{BENCHMARK_ITERATIONS}: {execution_time:.2f} seconds")
            except Exception as e:
                print(f"Iteration {i+1}/{BENCHMARK_ITERATIONS} failed: {str(e)}")
        
        # Calculate statistics for this test case
        if execution_times:
            test_result = {
                "name": test_case,
                "success_rate": success_count / BENCHMARK_ITERATIONS * 100,
                "max_time": max(execution_times),
                "min_time": min(execution_times),
                "avg_time": statistics.mean(execution_times),
                "median_time": statistics.median(execution_times),
                "std_dev": statistics.stdev(execution_times) if len(execution_times) > 1 else 0
            }
        else:
            test_result = {
                "name": test_case,
                "success_rate": 0,
                "max_time": None,
                "min_time": None,
                "avg_time": None,
                "median_time": None,
                "std_dev": None
            }
        
        results["test_cases"].append(test_result)
    
    # Calculate overall summary
    all_times = [t["avg_time"] for t in results["test_cases"] if t["avg_time"] is not None]
    
    if all_times:
        results["summary"] = {
            "overall_avg_time": statistics.mean(all_times),
            "overall_min_time": min(all_times),
            "overall_max_time": max(all_times),
            "overall_median_time": statistics.median(all_times),
            "overall_std_dev": statistics.stdev(all_times) if len(all_times) > 1 else 0
        }
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(BENCHMARK_RESULTS_DIR, f"definition_benchmark_{timestamp}.json")
    
    with open(results_file, "w") as f:
        json.dump(results, f, indent=4)
    
    print(f"\nDefinition benchmark results saved to: {results_file}")
    return results

def run_string_benchmark():
    """Run benchmark for string functions"""
    import time
    import json
    import statistics
    from datetime import datetime
    import os
    
    # Create benchmark_results directory if it doesn't exist
    os.makedirs(BENCHMARK_RESULTS_DIR, exist_ok=True)
    
    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "test_cases": [],
        "summary": {}
    }
    
    for test_case in string_test_cases:
        print(f"Running benchmark for {test_case}...")
        
        execution_times = []
        success_count = 0
        
        for i in range(BENCHMARK_ITERATIONS):
            try:
                start_time = time.time()
                response = string_playground(test_case)
                end_time = time.time()
                
                execution_time = end_time - start_time
                execution_times.append(execution_time)
                success_count += 1
                
                print(f"Iteration {i+1}/{BENCHMARK_ITERATIONS}: {execution_time:.2f} seconds")
            except Exception as e:
                print(f"Iteration {i+1}/{BENCHMARK_ITERATIONS} failed: {str(e)}")
        
        # Calculate statistics for this test case
        if execution_times:
            test_result = {
                "name": test_case,
                "success_rate": success_count / BENCHMARK_ITERATIONS * 100,
                "max_time": max(execution_times),
                "min_time": min(execution_times),
                "avg_time": statistics.mean(execution_times),
                "median_time": statistics.median(execution_times),
                "std_dev": statistics.stdev(execution_times) if len(execution_times) > 1 else 0
            }
        else:
            test_result = {
                "name": test_case,
                "success_rate": 0,
                "max_time": None,
                "min_time": None,
                "avg_time": None,
                "median_time": None,
                "std_dev": None
            }
        
        results["test_cases"].append(test_result)
    
    # Calculate overall summary
    all_times = [t["avg_time"] for t in results["test_cases"] if t["avg_time"] is not None]
    
    if all_times:
        results["summary"] = {
            "overall_avg_time": statistics.mean(all_times),
            "overall_min_time": min(all_times),
            "overall_max_time": max(all_times),
            "overall_median_time": statistics.median(all_times),
            "overall_std_dev": statistics.stdev(all_times) if len(all_times) > 1 else 0
        }
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(BENCHMARK_RESULTS_DIR, f"string_benchmark_{timestamp}.json")
    
    with open(results_file, "w") as f:
        json.dump(results, f, indent=4)
    
    print(f"\nString benchmark results saved to: {results_file}")
    return results

def run_weather_benchmark():
    """Run benchmark for weather functions"""
    import time
    import json
    import statistics
    from datetime import datetime
    import os
    from FCweather import function_call_playground_coords, function_call_playground, latitude, longtitude
    
    # Create benchmark_results directory if it doesn't exist
    os.makedirs(BENCHMARK_RESULTS_DIR, exist_ok=True)
    
    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "test_cases": [],
        "summary": {}
    }
    
    for test_case in weather_test_cases:
        print(f"Running benchmark for {test_case['name']}...")
        
        execution_times = []
        success_count = 0
        
        for i in range(BENCHMARK_ITERATIONS):
            try:
                start_time = time.time()
                
                # Step 1: Get coordinates
                coord_prompt = f"what are the coordinates of {test_case['city']}?"
                coord_response = function_call_playground_coords(coord_prompt)
                
                # Step 2: Get weather if coordinates were obtained
                if "Coordinates obtained:" in coord_response:
                    weather_prompt = f"What is the weather like in coordinates {latitude}, {longtitude} today?"
                    weather_response = function_call_playground(weather_prompt)
                    end_time = time.time()
                    
                    execution_time = end_time - start_time
                    execution_times.append(execution_time)
                    success_count += 1
                    
                    print(f"Iteration {i+1}/{BENCHMARK_ITERATIONS}: {execution_time:.2f} seconds")
                else:
                    print(f"Iteration {i+1}/{BENCHMARK_ITERATIONS} failed: Could not get coordinates")
                    
            except Exception as e:
                print(f"Iteration {i+1}/{BENCHMARK_ITERATIONS} failed: {str(e)}")
        
        # Calculate statistics for this test case
        if execution_times:
            test_result = {
                "name": test_case["name"],
                "success_rate": success_count / BENCHMARK_ITERATIONS * 100,
                "min_time": min(execution_times),
                "max_time": max(execution_times),
                "avg_time": statistics.mean(execution_times),
                "median_time": statistics.median(execution_times),
                "std_dev": statistics.stdev(execution_times) if len(execution_times) > 1 else 0
            }
        else:
            test_result = {
                "name": test_case["name"],
                "success_rate": 0,
                "min_time": None,
                "max_time": None,
                "avg_time": None,
                "median_time": None,
                "std_dev": None
            }
        
        results["test_cases"].append(test_result)
    
    # Calculate overall summary
    all_times = [t["avg_time"] for t in results["test_cases"] if t["avg_time"] is not None]
    if all_times:
        results["summary"] = {
            "overall_avg_time": statistics.mean(all_times),
            "overall_min_time": min(all_times),
            "overall_max_time": max(all_times),
            "overall_median_time": statistics.median(all_times),
            "overall_std_dev": statistics.stdev(all_times) if len(all_times) > 1 else 0
        }
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(BENCHMARK_RESULTS_DIR, f"weather_benchmark_{timestamp}.json")
    
    with open(results_file, "w") as f:
        json.dump(results, f, indent=4)
    
    print(f"\nWeather benchmark results saved to: {results_file}")
    return results

def run_all_benchmarks():
    # Create results directory if it doesn't exist
    os.makedirs(BENCHMARK_RESULTS_DIR, exist_ok=True)
    
    # Dictionary to store all benchmark results
    all_results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "benchmarks": {}
    }
    
    # Run each benchmark
    benchmarks = {
        "definition": run_definition_benchmark,
        "math": run_math_benchmark,
        "validation": run_validation_benchmark,
        "data": run_data_benchmark,
        "string": run_string_benchmark,
        "weather": run_weather_benchmark
    }
    
    for name, benchmark_func in benchmarks.items():
        print(f"\nRunning {name} benchmark...")
        try:
            results = benchmark_func()
            all_results["benchmarks"][name] = results
        except Exception as e:
            print(f"Error running {name} benchmark: {str(e)}")
            all_results["benchmarks"][name] = {"error": str(e)}
    
    # Save combined results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(BENCHMARK_RESULTS_DIR, f"all_benchmarks_{timestamp}.json")
    
    with open(results_file, "w") as f:
        json.dump(all_results, f, indent=4)
    
    print(f"\nAll benchmark results saved to: {results_file}")
    
    # Print summary
    print("\n=== OVERALL BENCHMARK SUMMARY ===")
    print(f"Timestamp: {all_results['timestamp']}")
    
    for name, results in all_results["benchmarks"].items():
        print(f"\n{name.upper()} BENCHMARK:")
        if "error" in results:
            print(f"  Error: {results['error']}")
        else:
            if "summary" in results:
                summary = results["summary"]
                print(f"  Overall Average Time: {summary.get('overall_avg_time', 'N/A'):.2f} seconds")
                print(f"  Overall Min Time: {summary.get('overall_min_time', 'N/A'):.2f} seconds")
                print(f"  Overall Max Time: {summary.get('overall_max_time', 'N/A'):.2f} seconds")
                print(f"  Overall Median Time: {summary.get('overall_median_time', 'N/A'):.2f} seconds")
                print(f"  Overall Standard Deviation: {summary.get('overall_std_dev', 'N/A'):.2f} seconds")

if __name__ == "__main__":
    run_all_benchmarks() 