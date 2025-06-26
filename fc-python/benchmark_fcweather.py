import time
import statistics
import json
from datetime import datetime
from FCweather import function_call_playground_coords, function_call_playground, latitude, longtitude

# Test cases with different cities
test_cases = [
    {"city": "Zurich, Switzerland", "name": "Zurich"},
    {"city": "New York, USA", "name": "New York"},
    {"city": "London, UK", "name": "London"},
    {"city": "Tokyo, Japan", "name": "Tokyo"},
    {"city": "Sydney, Australia", "name": "Sydney"},
    # Invalid city to test error handling
    {"city": "NonExistentCity123", "name": "Invalid City"}
]

# Number of iterations for each test case
iterations = 5

# Results storage
results = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "test_cases": [],
    "summary": {}
}

# Run benchmarks
for test_case in test_cases:
    print(f"Running benchmark for {test_case['name']}...")
    
    execution_times = []
    success_count = 0
    
    for i in range(iterations):
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
                
                print(f"  Iteration {i+1}/{iterations}: {execution_time:.2f} seconds")
            else:
                print(f"  Iteration {i+1}/{iterations} failed: Could not get coordinates")
                
        except Exception as e:
            print(f"  Iteration {i+1}/{iterations} failed: {str(e)}")
    
    # Calculate statistics for this test case
    if execution_times:
        test_result = {
            "name": test_case["name"],
            "success_rate": success_count / iterations * 100,
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
with open(f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
    json.dump(results, f, indent=4)

# Print summary
print("\n=== BENCHMARK SUMMARY ===")
print(f"Timestamp: {results['timestamp']}")
print("\nTest Case Results:")
for test in results["test_cases"]:
    print(f"\n{test['name']}:")
    print(f"  Success Rate: {test['success_rate']:.1f}%")
    if test['avg_time'] is not None:
        print(f"  Average Time: {test['avg_time']:.2f} seconds")
        print(f"  Min Time: {test['min_time']:.2f} seconds")
        print(f"  Max Time: {test['max_time']:.2f} seconds")
        print(f"  Median Time: {test['median_time']:.2f} seconds")
        print(f"  Std Dev: {test['std_dev']:.2f} seconds")
    else:
        print("  All iterations failed")

if results["summary"]:
    print("\nOverall Summary:")
    print(f"  Average Time: {results['summary']['overall_avg_time']:.2f} seconds")
    print(f"  Min Time: {results['summary']['overall_min_time']:.2f} seconds")
    print(f"  Max Time: {results['summary']['overall_max_time']:.2f} seconds")
    print(f"  Median Time: {results['summary']['overall_median_time']:.2f} seconds")
    print(f"  Std Dev: {results['summary']['overall_std_dev']:.2f} seconds") 