import os
import sys
import time
from datetime import datetime
import json
import statistics
from config import BENCHMARK_ITERATIONS, BENCHMARK_RESULTS_DIR
from FCmath import function_call_playground

# Test cases for math functions
test_cases = [
    {
        "name": "basic_arithmetic",
        "prompt": "What is 5 plus 3?",
        "expected_function": "add",
        "expected_args": {"a": 5, "b": 3}
    },
    {
        "name": "subtraction",
        "prompt": "Calculate 10 minus 4",
        "expected_function": "subtract",
        "expected_args": {"a": 10, "b": 4}
    },
    {
        "name": "multiplication",
        "prompt": "Multiply 6 by 7",
        "expected_function": "multiply",
        "expected_args": {"a": 6, "b": 7}
    },
    {
        "name": "division",
        "prompt": "Divide 15 by 3",
        "expected_function": "divide",
        "expected_args": {"a": 15, "b": 3}
    },
    {
        "name": "derivative",
        "prompt": "Find the derivative of x^2",
        "expected_function": "derivative",
        "expected_args": {"expression": "x^2", "variable": "x"}
    },
    {
        "name": "integration",
        "prompt": "Integrate 2x with respect to x",
        "expected_function": "integrate",
        "expected_args": {"expression": "2x", "variable": "x"}
    },
    {
        "name": "equation_solving",
        "prompt": "Solve the equation x + 5 = 10",
        "expected_function": "solve_equation",
        "expected_args": {"equation": "x + 5 = 10", "variable": "x"}
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
    results_file = os.path.join(BENCHMARK_RESULTS_DIR, f"math_benchmark_{timestamp}.json")
    
    with open(results_file, "w") as f:
        json.dump(results, f, indent=4)
    
    print(f"Math benchmark results saved to: {results_file}")
    return results

if __name__ == "__main__":
    run_benchmark() 