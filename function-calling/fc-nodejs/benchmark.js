import fs from 'fs';
import path from 'path';
import { callFunction, getAvailableTools } from './function_caller.js';

// Create benchmark results directory if it doesn't exist
const BENCHMARK_RESULTS_DIR = 'benchmark_results';
if (!fs.existsSync(BENCHMARK_RESULTS_DIR)) {
    fs.mkdirSync(BENCHMARK_RESULTS_DIR);
}

// Function to generate test cases for a tool
function generateTestCases(tool) {
    const testCases = [];
    
    // Use the example as one test case
    testCases.push({
        test_name: `${tool.id}_example`,
        parameters: tool.example
    });

    // Generate additional test cases based on tool type
    switch (tool.id) {
        case 'math_calculation':
            testCases.push(
                { test_name: 'math_sqrt_169', parameters: { operation: 'square root', input: '169' } },
                { test_name: 'math_percent_50', parameters: { operation: 'percentage', input: '50' } }
            );
            break;
        case 'weather_info':
            testCases.push(
                { test_name: 'weather_london', parameters: { location: 'London' } },
                { test_name: 'weather_paris', parameters: { location: 'Paris' } }
            );
            break;
        case 'string_operation':
            testCases.push(
                { test_name: 'string_reverse_world', parameters: { operation: 'reverse', input: 'world' } },
                { test_name: 'string_count_vowels', parameters: { operation: 'count vowels', input: 'beautiful' } }
            );
            break;
        case 'data_lookup':
            testCases.push(
                { test_name: 'data_population_tokyo', parameters: { data_type: 'population', subject: 'Tokyo' } },
                { test_name: 'data_gdp_usa', parameters: { data_type: 'GDP', subject: 'United States' } }
            );
            break;
        case 'validation_check':
            testCases.push(
                { test_name: 'validation_prime_17', parameters: { validation_type: 'prime number', input: '17' } },
                { test_name: 'validation_email', parameters: { validation_type: 'email address', input: 'test@example.com' } }
            );
            break;
        case 'definition_lookup':
            testCases.push(
                { test_name: 'definition_algorithm', parameters: { term: 'algorithm' } },
                { test_name: 'definition_api', parameters: { term: 'API' } }
            );
            break;
    }

    return testCases;
}

// Main benchmark function
async function runBenchmark() {
    const tools = getAvailableTools();
    const results = {
        timestamp: new Date().toISOString(),
        tools: []
    };

    for (const tool of tools) {
        console.log(`Benchmarking tool: ${tool.name}`);
        const toolResults = {
            tool_id: tool.id,
            tool_name: tool.name,
            results: []
        };

        const testCases = generateTestCases(tool);
        
        for (const testCase of testCases) {
            try {
                console.log(`Running test: ${testCase.test_name}`);
                const result = await callFunction(tool.id, testCase.parameters);
                toolResults.results.push({
                    test_name: testCase.test_name,
                    parameters: testCase.parameters,
                    output: result.output,
                    execution_time: result.execution_time
                });
            } catch (error) {
                console.error(`Error in test ${testCase.test_name}:`, error);
                toolResults.results.push({
                    test_name: testCase.test_name,
                    parameters: testCase.parameters,
                    error: error.message
                });
            }
        }

        results.tools.push(toolResults);
    }

    // Save results
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = path.join(BENCHMARK_RESULTS_DIR, `benchmark_results_${timestamp}.json`);
    fs.writeFileSync(filename, JSON.stringify(results, null, 2));
    
    console.log(`Benchmark completed. Results saved to ${filename}`);
    return results;
}

// Run the benchmark if this file is executed directly
if (process.argv[1] === import.meta.url) {
    runBenchmark().catch(console.error);
}

export { runBenchmark }; 