import {function_call_playground_math} from "./FCmath.js";
import {BENCHMARK_ITERATIONS, BENCHMARK_RESULTS_DIR} from "./config.js";
import path from 'path';
import fs from 'fs';

const prompt = [
    "what is the square root of 16?",
    "what is the derivative of x^2 with respect to x?",
    "what is 10 plus 10?",
    "what is the integral of x with respect to x?",
    "solve x+3=6 for x"
]

const iteration_count = BENCHMARK_ITERATIONS;

const run_benchmark = async()=>{
    const results = [];
    for (let i =0; i<iteration_count;i++){
        for (const p of prompt){
            console.log(`Running iteration ${i+1} of ${iteration_count} with prompt: ${p}`);
            const start_time = Date.now();
            const result = await function_call_playground_math(p);
            console.log('Debug - Raw result:', JSON.stringify(result, null, 2));
            const end_time = Date.now();
            const time_taken = (end_time-start_time)/1000;
            results.push({
                prompt: p,
                time_taken: time_taken,
                result: result
            });
        }
    }
    return results;
}

const success_rate = (results)=>{
    const success_count = results.filter(r=>r.result.isValid).length;
    return (success_count/results.length)*100;
}

const min_time = (results)=>{
    const valid_times = results.filter(r=>r.result.isValid).map(r=>r.time_taken);
    return valid_times.length > 0 ? Math.min(...valid_times) : 0;
}

const max_time = (results)=>{
    const valid_times = results.filter(r=>r.result.isValid).map(r=>r.time_taken);
    return valid_times.length > 0 ? Math.max(...valid_times) : 0;
}

const avg_time = (results)=>{
    const valid_times = results.filter(r=>r.result.isValid).map(r=>r.time_taken);
    return valid_times.length > 0 ? valid_times.reduce((sum,t)=>sum+t,0)/valid_times.length : 0;
}

const median_time = (results)=>{
    const valid_times = results.filter(r=>r.result.isValid).map(r=>r.time_taken).sort((a,b)=>a-b);
    if (valid_times.length === 0) return 0;
    const mid = Math.floor(valid_times.length/2);
    return valid_times[mid];
}

const std_dev = (results)=>{
    const valid_times = results.filter(r=>r.result.isValid).map(r=>r.time_taken);
    if (valid_times.length === 0) return 0;
    const avg = avg_time(results);
    const variance = valid_times.reduce((sum,t)=>sum+(t-avg)**2,0)/valid_times.length;
    return Math.sqrt(variance);
}

const save_results = (results)=>{
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `fcmath_benchmark_${timestamp}.json`;
    
    // Create the directory if it doesn't exist
    if (!fs.existsSync(BENCHMARK_RESULTS_DIR)) {
        fs.mkdirSync(BENCHMARK_RESULTS_DIR, { recursive: true });
    }
    
    const filepath = path.join(BENCHMARK_RESULTS_DIR, filename);
    fs.writeFileSync(filepath, JSON.stringify(results, null, 2));
    console.log(`Results saved to: ${filepath}`);
}

export const main_math = async()=>{
    const results = await run_benchmark();
    const successRate = success_rate(results);
    const minTime = min_time(results);
    const maxTime = max_time(results);
    const avgTime = avg_time(results);
    const medianTime = median_time(results);
    const stdDev = std_dev(results);
    
    console.log(`Benchmark Results:`);
    console.log(`Success Rate: ${successRate.toFixed(2)}%`);
    console.log(`Min Time: ${minTime.toFixed(2)}s`);
    console.log(`Max Time: ${maxTime.toFixed(2)}s`);
    console.log(`Avg Time: ${avgTime.toFixed(2)}s`);
    console.log(`Median Time: ${medianTime.toFixed(2)}s`);
    console.log(`Std Dev: ${stdDev.toFixed(2)}s`);
    
    // Add detailed error reporting
    const failedResults = results.filter(r => !r.result.isValid);
    if (failedResults.length > 0) {
        console.log('\nFailed Operations:');
        failedResults.forEach(r => {
            console.log(`- Prompt: "${r.prompt}"`);
            console.log(`  Error: ${r.result.error}`);
        });
    }
    
    save_results(results);
}

main_math();



