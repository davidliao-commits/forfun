import { OpenAI } from "openai";
import { config } from "dotenv";
import { BASE_URL, OPENAI_API_KEY, MODEL_NAME } from "./config.js";
import * as mathjs from "mathjs";

config();

const openai = new OpenAI({
    apiKey: OPENAI_API_KEY,
    baseURL: BASE_URL,
});

// Mathematical operation functions
const add = (a, b) => {
    console.log("add function called with", a, b);
    return mathjs.add(Number(a), Number(b));
};

const sqrt = (a) => {
    console.log("sqrt function called with", a);
    return mathjs.sqrt(Number(a));
};

const subtract = (a,b) =>{
    console.log("subtract function called with", a, b);
    return mathjs.subtract(Number(a), Number(b));
}

const multiply = (a,b) =>{
    console.log("multiply function called with", a,b);
    return mathjs.multiply(Number(a), Number(b));
}

const divide = (a,b) =>{
    console.log("divide function called with", a, b);
    return mathjs.divide(Number(a), Number(b));
}

const derivative = (func, x) => {
    console.log("derivative function called with", func, x);
    try {
        // Parse the function string and create a symbol for the variable
        const expr = mathjs.parse(func);
        // Create a symbol node for the variable
        const symbol = mathjs.parse(x);
        const derivative = mathjs.derivative(expr, symbol);
        return derivative.toString();
    } catch (error) {
        console.error("Error in derivative calculation:", error);
        throw new Error(`Failed to calculate derivative: ${error.message}`);
    }
}

const integrate = (func, x) => {
    console.log("integrate function called with", func, x);
    try {
        // Parse the function string
        const expr = mathjs.parse(func);
        
        // Handle basic integration cases
        if (expr.type === 'SymbolNode' && expr.name === x) {
            // Integral of x is x^2/2
            return `(${x}^2)/2`;
        } else if (expr.type === 'OperatorNode' && expr.op === '^') {
            // Handle power rule: integral of x^n is x^(n+1)/(n+1)
            if (expr.args[0].name === x) {
                const power = expr.args[1].value;
                return `(${x}^${power + 1})/${power + 1}`;
            }
        } else if (expr.type === 'OperatorNode' && expr.op === '*') {
            // Handle constant multiplication
            if (expr.args[0].type === 'ConstantNode' && expr.args[1].name === x) {
                const constant = expr.args[0].value;
                return `${constant} * (${x}^2)/2`;
            }
        }
        
        throw new Error("Integration not supported for this function");
    } catch (error) {
        console.error("Error in integration calculation:", error);
        throw new Error(`Failed to calculate integral: ${error.message}`);
    }
}

const tools = [
    {
        type: "function",
        function: {
            name: "add",
            description: "Add two numbers together",
            parameters: {
                type: "object",
                properties: {
                    a: {
                        type: "number",
                        description: "First number"
                    },
                    b: {
                        type: "number",
                        description: "Second number"
                    }
                },
                required: ["a", "b"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "subtract",
            description: "subtract two given numbers",
            parameters: {
                type: "object",
                properties: {
                    a: {
                        type: "number",
                        description: "the number to subtract from"
                    },
                    b: {
                        type: "number",
                        description: "the number to subtract"
                    }
                },
                required: ["a", "b"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "multiply",
            description: "multiply two given numbers",
            parameters: {
                type: "object",
                properties: {
                    a: {
                        type: "number",
                        description: "the first number to multiply"
                    },
                    b: {
                        type: "number",
                        description: "the second number to multiply"
                    }
                },
                required: ["a", "b"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "divide",
            description: "divide two given numbers",
            parameters: {
                type: "object",
                properties: {
                    a: {
                        type: "number",
                        description: "the dividend"
                    },
                    b: {
                        type: "number",
                        description: "the divisor"
                    }
                },
                required: ["a", "b"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "sqrt",
            description: "calculate the square root of a given number",
            parameters: {
                type: "object",
                properties: {
                    a: {
                        type: "number",
                        description: "the number to calculate the square root for"
                    }
                },
                required: ["a"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "derivative",
            description: "calculate the derivative of a given function with respect to a given variable",
            parameters: {
                type: "object",
                properties: {
                    func: {
                        type: "string",
                        description: "the function to calculate the derivative for"
                    },
                    x: {
                        type: "string",
                        description: "the variable to differentiate expression with respect to"
                    }
                },
                required: ["func", "x"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "integrate",
            description: "calculate the integral of a given function with respect to a given variable",
            parameters: {
                type: "object",
                properties: {
                    func: {
                        type: "string",
                        description: "the function to integrate with"
                    },
                    x: {
                        type: "string",
                        description: "the variable to integrate with respect to"
                    }
                },
                required: ["func", "x"]
            }
        }
    }
];

// Create a Map for O(1) function lookup - this is the key optimization
const function_map = new Map([
    ["add", add],
    ["subtract", subtract],
    ["multiply", multiply],
    ["divide", divide],
    ["sqrt", sqrt],
    ["derivative", derivative],
    ["integrate", integrate]
]);

// Create a Map for O(1) tool lookup by name
const tool_map = new Map(tools.map(tool => [tool.function.name, tool.function]));

// Pre-compile regex for faster text parsing
const FUNCTION_CALL_REGEX = /(\w+)\(([^)]+)\)/;

export const function_call_playground_math = async (prompt) => {
    try {
        const response = await openai.chat.completions.create({
            model: MODEL_NAME,
            messages: [
                {
                    role: "system",
                    content: `You are a math assistant that solves problems using specific functions. You must use the function calling capability to solve problems and evaluate mathematical expressions.

For example, to solve x+3=5:
1. Recognize that to solve for x, we need to subtract 3 from both sides
2. Use the function calling capability to call subtract(5,3)

Available functions:
- add(a,b): Add two numbers
- subtract(a,b): Subtract b from a
- multiply(a,b): Multiply two numbers
- divide(a,b): Divide a by b
- sqrt(a): Calculate square root
- derivative(func,x): Calculate derivative
- integrate(func,x): Calculate integral

IMPORTANT: You must use the function calling capability. Do not write function calls as text.`
                },
                {
                    role: "user",
                    content: prompt,
                }
            ],
            tools: tools, // Keep original tools array for API
            tool_choice: "auto",
            temperature: 0.01,
            stream: false,
            top_p: 0.95
        });

        if (!response.choices || !response.choices[0] || !response.choices[0].message) {
            throw new Error("Invalid response format from API");
        }

        const toolCalls = response.choices[0].message.tool_calls;
        if (!toolCalls || toolCalls.length === 0) {
            // If no tool calls, try to parse the content as a function call
            const content = response.choices[0].message.content;
            try {
                // First try parsing as JSON
                const parsedContent = JSON.parse(content);
                if (parsedContent.name && parsedContent.arguments) {
                    const functionName = parsedContent.name;
                    const functionArgs = parsedContent.arguments;

                    // Use Map for O(1) lookup instead of object property access
                    const func = function_map.get(functionName);
                    if (!func) {
                        throw new Error(`Unknown function: ${functionName}`);
                    }

                    const result = await func(...Object.values(functionArgs));

                    return {
                        isValid: true,
                        results: [{
                            name: functionName,
                            arguments: functionArgs,
                            result: result
                        }]
                    };
                }
            } catch (parseError) {
                // If JSON parsing fails, try to parse plain text function call
                const functionCallMatch = content.match(FUNCTION_CALL_REGEX);
                if (functionCallMatch) {
                    const functionName = functionCallMatch[1];
                    const argsString = functionCallMatch[2];
                    const args = argsString.split(',').map(arg => arg.trim());

                    // Use Map for O(1) lookup
                    const func = function_map.get(functionName);
                    if (!func) {
                        throw new Error(`Unknown function: ${functionName}`);
                    }

                    const result = await func(...args);

                    return {
                        isValid: true,
                        results: [{
                            name: functionName,
                            arguments: args.reduce((acc, arg, i) => {
                                acc[`arg${i}`] = arg;
                                return acc;
                            }, {}),
                            result: result
                        }]
                    };
                }
            }
            throw new Error("No tool calls found in the response");
        }

        // Process tool calls with optimized lookup
        const results = [];
        for (const toolCall of toolCalls) {
            const functionName = toolCall.function.name;
            const functionArgs = JSON.parse(toolCall.function.arguments);

            // Use Map for O(1) lookup instead of object property access
            const func = function_map.get(functionName);
            if (!func) {
                throw new Error(`Unknown function: ${functionName}`);
            }

            const result = await func(...Object.values(functionArgs));

            results.push({
                name: functionName,
                arguments: functionArgs,
                result: result
            });
        }

        // Make a second request to format the results in natural language
        const formatResponse = await openai.chat.completions.create({
            model: MODEL_NAME,
            messages: [
                {
                    role: "system",
                    content: `You are a math assistant that explains solutions in natural language. Format the mathematical results in a clear, concise way.`
                },
                {
                    role: "user",
                    content: `Please explain the solution to this problem: ${prompt}\n\nResults: ${JSON.stringify(results)}`
                }
            ],
            temperature: 0.7,
            stream: false,
            top_p: 0.95
        });

        return {
            isValid: true,
            results: results,
            explanation: formatResponse.choices[0].message.content
        };

    } catch (error) {
        console.error("Error in function_call_playground:", error);
        return {
            isValid: false,
            error: error.message
        };
    }
};

// Test the function
const prompt = "what is 10 plus 10?";
console.log("prompt:", prompt);
const start_time = Date.now()
function_call_playground_math(prompt).then(result => {
    const end_time = Date.now();
    console.log(`Time taken for function call playground: ${(end_time-start_time)/1000} seconds`);
    console.log("result:", result);
    if (result.isValid) {
        console.log("\nExplanation:", result.explanation);
    }
}).catch(error => {
    console.error("Error:", error);
});

