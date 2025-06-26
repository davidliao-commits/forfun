import {main_math} from "./benchmark_fcmath.js";
import {main_string} from "./benchmark_fcstring.js";
import {main_validation} from "./benchmark_fcvalidation.js";
import {main_definition} from "./benchmark_fcdefinition.js";
import {main_data} from "./benchmark_fcdata.js";
import {main_weather} from "./benchmark_fcweather.js";
import {BENCHMARK_ITERATIONS, BENCHMARK_RESULTS_DIR} from "./config.js";

const main_all = async()=>{
    console.log("Starting benchmark for all functions: iteration count:", BENCHMARK_ITERATIONS, "results directory:", BENCHMARK_RESULTS_DIR);
    await main_math();
    await main_string();
    await main_validation();
    await main_definition();
    await main_data();
    await main_weather();
    console.log("Benchmark completed successfully");
}

main_all();

