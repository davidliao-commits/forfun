# FC-NodeJS

Function calling examples in Node.js

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure API Keys:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and replace the placeholder values with your actual API keys:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `URBAN_DICTIONARY_API_KEY`: Your Urban Dictionary API key
     - `OPENWEATHERMAP_API_KEY`: Your OpenWeatherMap API key

3. Run the application:
```bash
npm start
```

## Benchmark Results

Benchmark results are stored in the `benchmark_results/` directory. This directory is tracked in git to maintain a history of performance measurements.

## Available Scripts

- `npm start`: Run the main application
- `node benchmark_fc_all.js`: Run all benchmarks
- `node benchmark_fcdefinition.js`: Run FC definition benchmarks
- `node benchmark_fcdata.js`: Run FC data benchmarks
- `node benchmark_fcvalidation.js`: Run FC validation benchmarks
- `node benchmark_fcmath.js`: Run FC math benchmarks
- `node benchmark_fcweather.js`: Run FC weather benchmarks
- `node benchmark_fcstring.js`: Run FC string benchmarks 