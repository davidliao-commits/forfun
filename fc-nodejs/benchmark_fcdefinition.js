import {function_call_playground_definition} from "./FCdefinition.js";
import {BENCHMARK_ITERATIONS, BENCHMARK_RESULTS_DIR} from "./config.js";
import path from 'path';
import fs from 'fs';

const prompt = [
    "what is the definition of 'hello'?",
    "what is the definition of 'world'?",
    "what is the definition of 'catastrophe'?",
    "what is the definition of 'exectution'?",
]

const iterations = BENCHMARK_ITERATIONS;

const run_benchmark = async()=>{
    console.log("Running benchmark for FCdefinition...");
    const results = [];
    for(const p of prompt){
        for (let i=0; i<iterations; i++){
            console.log("Prompt:", p);
            const start = Date.now();
            const result = await function_call_playground_definition(p);
            const end = Date.now();
            const timeTaken = (end-start)/1000;
            results.push({
                prompt:p,
                timeTaken:timeTaken,
                result:result
            })
        }
    }
    return results;
}

const success_rate = (results)=>{
    const success_count = results.filter(r=>r.result.isValid).length;
    return (success_count/results.length)*100;
}

const min_time = (results)=>{
    return Math.min(...results.map(r=>r.timeTaken));
}

const max_time = (results)=>{
    return Math.max(...results.map(r=>r.timeTaken));
}

const avg_time = (results)=>{
    return results.reduce((sum,r)=>sum+r.timeTaken,0)/results.length;
}

const median_time = (results)=>{
    const sorted = results.map(r=>r.timeTaken).sort((a,b)=>a-b);
    const mid = Math.floor(sorted.length/2);
    return sorted[mid];
}

const std_dev = (results)=>{
    const avg = avg_time(results);
    const variance = results.reduce((sum,r)=>sum+(r.timeTaken-avg)**2,0)/results.length;
    return Math.sqrt(variance);
}

const save_results = (results)=>{
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `fcdefinition_benchmark_${timestamp}.json`;
    
    // Create the directory if it doesn't exist
    if (!fs.existsSync(BENCHMARK_RESULTS_DIR)) {
        fs.mkdirSync(BENCHMARK_RESULTS_DIR, { recursive: true });
    }
    
    const filepath = path.join(BENCHMARK_RESULTS_DIR, filename);
    fs.writeFileSync(filepath, JSON.stringify(results, null, 2));
    console.log(`Results saved to: ${filepath}`);
}

export const main_definition = async()=>{
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
    save_results(results);
}

main_definition();
