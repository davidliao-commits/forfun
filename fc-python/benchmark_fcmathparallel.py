import time
from FCmathparallel import function_call_playground, client
import statistics

def run_benchmark(prompt, num_runs=3):
    """Run a single benchmark test with multiple iterations."""
    times = []
    results = []
    
    for _ in range(num_runs):
        start_time = time.time()
        try:
            result = function_call_playground(prompt, client)
            end_time = time.time()
            execution_time = end_time - start_time
            times.append(execution_time)
            results.append(result)
        except Exception as e:
            print(f"Error running benchmark for prompt: {prompt}")
            print(f"Error: {str(e)}")
            return None, None
    
    return times, results

def main():
    # Define test cases
    test_cases = [
        {
            "name": "Simple Addition",
            "prompt": "What is 2 + 3?"
        },
        {
            "name": "Multiple Operations",
            "prompt": "What is 2 + 3 and then multiply the result by 4?"
        },
        {
            "name": "Complex Math",
            "prompt": "What is the derivative of x^2 + 3x + 2 at x = 2?"
        },
        {
            "name": "Multiple Functions",
            "prompt": "Calculate sqrt(16) and then add 5 to the result"
        },
        {
            "name": "Integration",
            "prompt": "What is the integral of x^2 + 2x + 1 at x = 3?"
        }
    ]

    print("Starting Benchmark Tests...")
    print("-" * 50)

    benchmark_results = []

    for test in test_cases:
        print(f"\nRunning test: {test['name']}")
        print(f"Prompt: {test['prompt']}")
        
        times, results = run_benchmark(test['prompt'])
        
        if times and results:
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            
            benchmark_results.append({
                "name": test['name'],
                "avg_time": avg_time,
                "min_time": min_time,
                "max_time": max_time,
                "success": True
            })
            
            print(f"Average execution time: {avg_time:.3f} seconds")
            print(f"Min execution time: {min_time:.3f} seconds")
            print(f"Max execution time: {max_time:.3f} seconds")
            print(f"Results: {results[0]}")  # Show first result as example
        else:
            benchmark_results.append({
                "name": test['name'],
                "success": False
            })
            print("Test failed")

    # Print summary
    print("\n" + "=" * 50)
    print("Benchmark Summary")
    print("=" * 50)
    
    successful_tests = [r for r in benchmark_results if r['success']]
    if successful_tests:
        avg_times = [r['avg_time'] for r in successful_tests]
        print(f"\nTotal tests: {len(benchmark_results)}")
        print(f"Successful tests: {len(successful_tests)}")
        print(f"Failed tests: {len(benchmark_results) - len(successful_tests)}")
        print(f"\nAverage execution time across all successful tests: {statistics.mean(avg_times):.3f} seconds")
        print(f"Fastest test: {min(successful_tests, key=lambda x: x['avg_time'])['name']}")
        print(f"Slowest test: {max(successful_tests, key=lambda x: x['avg_time'])['name']}")
    else:
        print("No successful tests to summarize")

if __name__ == "__main__":
    main() 