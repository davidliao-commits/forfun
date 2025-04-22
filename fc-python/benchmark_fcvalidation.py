import os
import sys
import time
from datetime import datetime
import json
import statistics
from config import BENCHMARK_ITERATIONS, BENCHMARK_RESULTS_DIR
from FCvalidation import function_call_playground

# Test cases for validation functions
test_cases = [
    {
        "name": "email_validation",
        "prompt": "Is test@example.com a valid email address?",
        "expected_function": "validate_email",
        "expected_args": {"email": "test@example.com"}
    },
    {
        "name": "phone_validation",
        "prompt": "Is +1-555-123-4567 a valid phone number?",
        "expected_function": "validate_phone",
        "expected_args": {"phone": "+1-555-123-4567"}
    },
    {
        "name": "url_validation",
        "prompt": "Is https://www.example.com a valid URL?",
        "expected_function": "validate_url",
        "expected_args": {"url": "https://www.example.com"}
    },
    {
        "name": "password_validation",
        "prompt": "Is 'Password123!' a strong password?",
        "expected_function": "validate_password",
        "expected_args": {"password": "Password123!"}
    },
    {
        "name": "date_validation",
        "prompt": "Is 2024-02-29 a valid date?",
        "expected_function": "validate_date",
        "expected_args": {"date": "2024-02-29"}
    },
    {
        "name": "ip_validation",
        "prompt": "Is 192.168.1.1 a valid IP address?",
        "expected_function": "validate_ip",
        "expected_args": {"ip": "192.168.1.1"}
    },
    {
        "name": "credit_card_validation",
        "prompt": "Is 4532015112830366 a valid credit card number?",
        "expected_function": "validate_credit_card",
        "expected_args": {"card_number": "4532015112830366"}
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
    results_file = os.path.join(BENCHMARK_RESULTS_DIR, f"validation_benchmark_{timestamp}.json")
    
    with open(results_file, "w") as f:
        json.dump(results, f, indent=4)
    
    print(f"Validation benchmark results saved to: {results_file}")
    return results

if __name__ == "__main__":
    run_benchmark() 