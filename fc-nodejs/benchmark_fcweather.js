import {function_call_playground_coordinates, function_call_playground_weather} from "./FCweather.js";
import {BENCHMARK_ITERATIONS, BENCHMARK_RESULTS_DIR} from "./config.js";
import path from 'path';
import fs from 'fs';

const prompt_coordinates = [
    "what are the coordinates of beijing, china?",
    "what are the coordinates of tokyo, japan?",
    "what are the coordinates of london, uk?",
    "what are the coordinates of paris, france?",
    "what are the coordinates of berlin, germany?",
]

const iterations = BENCHMARK_ITERATIONS;

const run_benchmark = async()=>{
    console.log("running benchmark for FCweather...");
    const results_coordinates = [];
    const results_weather = [];
    for (const p of prompt_coordinates){
        let coordinates = null;
        for (let i =0;i<iterations;i++){
            console.log("Prompt for coordinates:", p);
            const start = Date.now();
            const result = await function_call_playground_coordinates(p);
            const end = Date.now();
            const timeTaken = (end-start)/1000;
            results_coordinates.push({
                prompt:p,
                timeTaken:timeTaken,
                result:result
            });
            if (i === 0) { // Store coordinates from first iteration
                coordinates = result;
            }
        }
        
        if (coordinates) {
            const prompt2 = `What is the weather like at latitude ${coordinates.latitude} and longitude ${coordinates.longitude}?`;
            for (let i =0;i<iterations;i++){
                console.log("prompt for weather:", prompt2);
                const start = Date.now();
                const result = await function_call_playground_weather(prompt2);
                const end = Date.now();
                const timeTaken = (end-start)/1000;
                results_weather.push({
                    prompt:prompt2,
                    timeTaken:timeTaken,
                    result:result
                });
            }
        }
    }
    return {
        results_coordinates,
        results_weather
    }
}

const success_rate = (results)=>{
    const success_count = results.filter(r => {
        if (!r.result) return false;
        // For coordinates, check if we have both latitude and longitude
        if (r.result.latitude !== undefined && r.result.longitude !== undefined) return true;
        // For weather, check if we got a valid weather string response
        if (typeof r.result === 'string' && r.result.includes('weather')) return true;
        return false;
    }).length;
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
    const filename = `fcweather_benchmark_${timestamp}.json`;
    
    // Create the directory if it doesn't exist
    if (!fs.existsSync(BENCHMARK_RESULTS_DIR)) {
        fs.mkdirSync(BENCHMARK_RESULTS_DIR, { recursive: true });
    }
    
    const filepath = path.join(BENCHMARK_RESULTS_DIR, filename);
    fs.writeFileSync(filepath, JSON.stringify(results, null, 2));
    console.log(`Results saved to: ${filepath}`);
}

export const main_weather = async()=>{
    const results = await run_benchmark();
    const successRate = success_rate(results.results_coordinates);
    const minTime = min_time(results.results_coordinates);
    const maxTime = max_time(results.results_coordinates);
    const avgTime = avg_time(results.results_coordinates);
    const medianTime = median_time(results.results_coordinates);
    const stdDev = std_dev(results.results_coordinates);
    console.log(`Benchmark Results:`);
    console.log(`Success Rate: ${successRate.toFixed(2)}%`);
    console.log(`Min Time: ${minTime.toFixed(2)}s`);
    console.log(`Max Time: ${maxTime.toFixed(2)}s`);
    console.log(`Avg Time: ${avgTime.toFixed(2)}s`);
    console.log(`Median Time: ${medianTime.toFixed(2)}s`);
    console.log(`Std Dev: ${stdDev.toFixed(2)}s`);
    save_results(results.results_coordinates);
    save_results(results.results_weather);
}

main_weather();
