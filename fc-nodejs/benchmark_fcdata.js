import { function_call_playground_data } from "./FCdata.js";
import {BENCHMARK_ITERATIONS, BENCHMARK_RESULTS_DIR} from "./config.js";
import path from 'path';
import fs from 'fs';

const prompts = [
    "Convert this CSV data to JSON: name,age,city\nJohn,30,New York\nJane,25,Los Angeles",
    "Convert this JSON to CSV: [{\"name\":\"John\",\"age\":30,\"city\":\"New York\"},{\"name\":\"Jane\",\"age\":25,\"city\":\"Los Angeles\"}]",
    "Filter this data to show only people over 25: [{\"name\":\"John\",\"age\":30},{\"name\":\"Jane\",\"age\":25},{\"name\":\"Bob\",\"age\":35}]",
    "Sort this data by age in descending order: [{\"name\":\"John\",\"age\":30},{\"name\":\"Jane\",\"age\":25},{\"name\":\"Bob\",\"age\":35}]",
    "Calculate the average age from this data: [{\"name\":\"John\",\"age\":30},{\"name\":\"Jane\",\"age\":25},{\"name\":\"Bob\",\"age\":35}]"
];


const run_benchmark = async()=>{
    const results = [];
    for (const p of prompts){
        for (let i =0;i<BENCHMARK_ITERATIONS;i++){
            const start = Date.now();
            const result = await function_call_playground_data(p);
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
    const filename = `fcdata_benchmark_${timestamp}.json`;
    
    // Create the directory if it doesn't exist
    if (!fs.existsSync(BENCHMARK_RESULTS_DIR)) {
        fs.mkdirSync(BENCHMARK_RESULTS_DIR, { recursive: true });
    }
    
    const filepath = path.join(BENCHMARK_RESULTS_DIR, filename);
    fs.writeFileSync(filepath, JSON.stringify(results, null, 2));
    console.log(`Results saved to: ${filepath}`);
}

export const main_data = async()=>{
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

main_data();