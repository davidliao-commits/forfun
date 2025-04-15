import time
import json
import statistics
from datetime import datetime
import sys
import os

# Import the function_call_playground directly since we're in the same directory
from FCstring import function_call_playground

# Create benchmark_results directory if it doesn't exist
results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "benchmark_results")
os.makedirs(results_dir, exist_ok=True)

test_cases = {
    "Count the words in this text: Hello world, this is a test message.": {
        "expected_output": "The text contains 8 words."
    },
    "Find all occurrences of 'the' in this text: The quick brown fox jumps over the lazy dog.": {
        "expected_output": "The word 'the' appears 2 times in the text."
    },
    "Extract email addresses from this text: Contact us at test@example.com or support@company.com": {
        "expected_output": "Found 2 email addresses: test@example.com, support@company.com"
    },
    "Calculate word frequency in this text: The cat and the dog and the cat and the mouse": {
        "expected_output": "Word frequencies: the (4), cat (2), and (2), dog (1), mouse (1)"
    },
    "Get text statistics for this text: This is a test. It has multiple sentences! How many words?": {
        "expected_output": "Text statistics: 10 words, 3 sentences, average word length 3.5, average sentence length 3.33"
    },
    "Format this text to 40 characters per line: This is a long text that needs to be formatted to fit within a specific line length while maintaining readability.": {
        "expected_output": "Text formatted to 40 characters per line with proper line breaks."
    }
}

iterations = 5

results = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "test_cases": [],
    "summary": {}
}

for test_case in test_cases:
    print(f"Running benchmark for {test_case}...")
    
    execution_times = []
    success_count = 0
    
    for i in range(iterations):
        try:
            start_time = time.time()
            response = function_call_playground(test_case)
            end_time = time.time()
            
            execution_time = end_time - start_time
            execution_times.append(execution_time)
            success_count += 1
            
            print(f"Iteration {i+1}/{iterations}: {execution_time:.2f} seconds")
        except Exception as e:
            print(f"Iteration {i+1}/{iterations} failed: {str(e)}")
    
    # Calculate statistics for this test case
    if execution_times:
        test_result = {
            "name": test_case,
            "success_rate": success_count / iterations * 100,
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

# Save results to file in the benchmark_results directory
results_file = os.path.join(results_dir, f"benchmark_results_string_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
with open(results_file, "w") as f:
    json.dump(results, f, indent=4)

print(f"\nResults saved to: {results_file}")

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
        print(f"  Standard Deviation: {test['std_dev']:.2f} seconds")
    else:
        print("  All iterations failed")

if results["summary"]:
    print("\nOverall Summary:")
    print(f"  Overall Average Time: {results['summary']['overall_avg_time']:.2f} seconds")
    print(f"  Overall Min Time: {results['summary']['overall_min_time']:.2f} seconds")
    print(f"  Overall Max Time: {results['summary']['overall_max_time']:.2f} seconds")
    print(f"  Overall Median Time: {results['summary']['overall_median_time']:.2f} seconds")
    print(f"  Overall Standard Deviation: {results['summary']['overall_std_dev']:.2f} seconds") 