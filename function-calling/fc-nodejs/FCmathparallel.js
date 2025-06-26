import { OpenAI } from "openai";
import { config } from "dotenv";
import { BASE_URL, OPENAI_API_KEY, MODEL_NAME } from "./config.js";
import * as mathjs from "mathjs";

config();

const openai = new OpenAI({
    apiKey: OPENAI_API_KEY,
    baseURL: BASE_URL,
});

// Define all your math functions
const add = (a, b) => {
    console.log("addition function called");
    return Number(a) + Number(b);
};

const subtract = (a, b) => {
    console.log("subtraction function called");
    return Number(a) - Number(b);
};

const multiply = (a, b) => {
    console.log("multiplication function called");
    return Number(a) * Number(b);
};

const divide = (a, b) => {
    console.log("division function called");
    return Number(b) === 0 ? "Error" : Number(a) / Number(b);
};

const sqrt = (a) => {
    console.log("square root function called");
    return mathjs.sqrt(Number(a));
};

const derivative = (func, x) => {
    console.log("derivative function called");
    try {
        const expr = mathjs.parse(func);
        const symbol = mathjs.parse('x');
        const derivative = mathjs.derivative(expr, symbol);
        return derivative.evaluate({x: Number(x)}).toString();
    } catch (error) {
        return error.toString();
    }
};

const integrate = (func, x) => {
    console.log("integration function called");
    try {
        const expr = mathjs.parse(func);
        // Handle basic integration cases
        if (expr.type === 'SymbolNode' && expr.name === 'x') {
            return (Number(x) * Number(x) / 2).toString();
        } else if (expr.type === 'OperatorNode' && expr.op === '^') {
            if (expr.args[0].name === 'x') {
                const power = expr.args[1].value;
                return (Math.pow(Number(x), power + 1) / (power + 1)).toString();
            }
        }
        return "Integration not supported for this function";
    } catch (error) {
        return error.toString();
    }
};

// Tool name to function mapping
const available_functions = {
    "add": add,
    "subtract": subtract,
    "multiply": multiply,
    "divide": divide,
    "sqrt": sqrt,
    "derivative": derivative,
    "integrate": integrate,
};

// Simulate parallel function calling
export const function_call_playground_parallel = async (prompt) => {
    try {
        const messages = [
            {
                role: "system",
                content: (
                    "You are a math assistant. Given a question, always respond with a JSON array " +
                    "of function calls (not explanations). Each function call should have a 'name' " +
                    "and an 'arguments' field. Example:\n" +
                    "[{\"name\": \"add\", \"arguments\": {\"a\": 2, \"b\": 3}}," +
                    " {\"name\": \"multiply\", \"arguments\": {\"a\": 4, \"b\": 5}}]"
                )
            },
            { role: "user", content: prompt }
        ];

        const response = await openai.chat.completions.create({
            model: MODEL_NAME,
            messages: messages,
            temperature: 0.01,
            stream: false,
            top_p: 0.95
        });

        const tool_call_json = response.choices[0].message.content.trim();

        // Try parsing JSON from model output
        let tool_calls;
        try {
            tool_calls = JSON.parse(tool_call_json);
        } catch (error) {
            return { isValid: false, error: `Invalid JSON output: ${tool_call_json}` };
        }

        // Parallel execution using Promise.all
        const results = {};

        const call_function = async (tc) => {
            const name = tc.name;
            const args = tc.arguments;
            if (name in available_functions) {
                return [name, await available_functions[name](...Object.values(args))];
            } else {
                return [name, `Unknown function '${name}'`];
            }
        };

        // Execute all functions in parallel
        const promises = tool_calls.map(call_function);
        const function_results = await Promise.all(promises);

        // Build results object
        for (const [fname, result] of function_results) {
            results[fname] = result;
        }

        return {
            isValid: true,
            results: results
        };

    } catch (error) {
        return {
            isValid: false,
            error: `Error in function_call_playground: ${error.message}`
        };
    }
};

// Test the function
if (import.meta.url === `file://${process.argv[1]}`) {
    try {
        const prompt = "What is 10 + 10, then times the result by 10?";
        const start_time = Date.now();
        const result = await function_call_playground_parallel(prompt);
        const end_time = Date.now();
        console.log("Result:", result);
        console.log(`Execution time: ${(end_time - start_time) / 1000} seconds`);
    } catch (error) {
        console.error("Error in main execution:", error);
    }
} 