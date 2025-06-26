import os
import sys
import time
from datetime import datetime
import json
import statistics
from config import BENCHMARK_ITERATIONS, BENCHMARK_RESULTS_DIR
from FCdata import function_call_playground

# Test cases for data processing functions
test_cases = [
    {
        "name": "csv_to_json",
        "prompt": "Convert this CSV data to JSON: name,age,city\nJohn,30,New York\nJane,25,Los Angeles",
        "expected_function": "csv_to_json",
        "expected_args": {"csv_data": "name,age,city\nJohn,30,New York\nJane,25,Los Angeles"}
    },
    {
        "name": "json_to_csv",
        "prompt": "Convert this JSON to CSV: [{\"name\":\"John\",\"age\":30,\"city\":\"New York\"},{\"name\":\"Jane\",\"age\":25,\"city\":\"Los Angeles\"}]",
        "expected_function": "json_to_csv",
        "expected_args": {"json_data": "[{\"name\":\"John\",\"age\":30,\"city\":\"New York\"},{\"name\":\"Jane\",\"age\":25,\"city\":\"Los Angeles\"}]"}
    },
    {
        "name": "filter_data",
        "prompt": "Filter this data to show only people over 25: [{\"name\":\"John\",\"age\":30},{\"name\":\"Jane\",\"age\":25},{\"name\":\"Bob\",\"age\":35}]",
        "expected_function": "filter_data",
        "expected_args": {
            "data": "[{\"name\":\"John\",\"age\":30},{\"name\":\"Jane\",\"age\":25},{\"name\":\"Bob\",\"age\":35}]",
            "condition": "age > 25"
        }
    },
    {
        "name": "sort_data",
        "prompt": "Sort this data by age in descending order: [{\"name\":\"John\",\"age\":30},{\"name\":\"Jane\",\"age\":25},{\"name\":\"Bob\",\"age\":35}]",
        "expected_function": "sort_data",
        "expected_args": {
            "data": "[{\"name\":\"John\",\"age\":30},{\"name\":\"Jane\",\"age\":25},{\"name\":\"Bob\",\"age\":35}]",
            "key": "age",
            "reverse": True
        }
    },
    {
        "name": "aggregate_data",
        "prompt": "Calculate the average age from this data: [{\"name\":\"John\",\"age\":30},{\"name\":\"Jane\",\"age\":25},{\"name\":\"Bob\",\"age\":35}]",
        "expected_function": "aggregate_data",
        "expected_args": {
            "data": "[{\"name\":\"John\",\"age\":30},{\"name\":\"Jane\",\"age\":25},{\"name\":\"Bob\",\"age\":35}]",
            "operation": "average",
            "field": "age"
        }
    }
]

def run_benchmark():
    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "test_cases": []
    }
    
    for test_case in test_cases:
        case_results = {
            "name": test_case["name"],
            "prompt": test_case["prompt"],
            "iterations": []
        }
        
        for i in range(BENCHMARK_ITERATIONS):
            try:
                start_time = time.time()
                response = function_call_playground(test_case["prompt"])
                end_time = time.time()
                
                execution_time = end_time - start_time
                
                iteration_result = {
                    "iteration": i + 1,
                    "execution_time": execution_time,
                    "response": response,
                    "success": True
                }
                
            except Exception as e:
                iteration_result = {
                    "iteration": i + 1,
                    "execution_time": None,
                    "error": str(e),
                    "success": False
                }
            
            case_results["iterations"].append(iteration_result)
        
        # Calculate statistics for this test case
        successful_times = [r["execution_time"] for r in case_results["iterations"] if r["success"]]
        
        if successful_times:
            case_results["summary"] = {
                "avg_time": statistics.mean(successful_times),
                "min_time": min(successful_times),
                "max_time": max(successful_times),
                "median_time": statistics.median(successful_times),
                "std_dev": statistics.stdev(successful_times) if len(successful_times) > 1 else 0,
                "success_rate": len(successful_times) / BENCHMARK_ITERATIONS
            }
        else:
            case_results["summary"] = {
                "success_rate": 0
            }
        
        results["test_cases"].append(case_results)
    
    # Calculate overall statistics
    all_times = []
    for case in results["test_cases"]:
        if "summary" in case and "avg_time" in case["summary"]:
            all_times.append(case["summary"]["avg_time"])
    
    if all_times:
        results["summary"] = {
            "overall_avg_time": statistics.mean(all_times),
            "overall_min_time": min(all_times),
            "overall_max_time": max(all_times),
            "overall_median_time": statistics.median(all_times),
            "overall_std_dev": statistics.stdev(all_times) if len(all_times) > 1 else 0
        }
    
    # Save results
    os.makedirs(BENCHMARK_RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(BENCHMARK_RESULTS_DIR, f"data_benchmark_{timestamp}.json")
    
    with open(results_file, "w") as f:
        json.dump(results, f, indent=4)
    
    print(f"Data processing benchmark results saved to: {results_file}")
    return results

if __name__ == "__main__":
    run_benchmark() 