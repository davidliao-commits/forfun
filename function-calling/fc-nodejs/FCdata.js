import { OpenAI } from "openai";
import { config } from "dotenv";
import { BASE_URL, OPENAI_API_KEY, MODEL_NAME } from "./config.js";
import csv from "csv-parser";
import fs from "fs";

config();

const openai = new OpenAI({
    apiKey: OPENAI_API_KEY,
    baseURL: BASE_URL,
});

// Data processing functions
const csvToJson = async (csvData) => {
    console.log("Converting CSV to JSON...");
    try {
        const lines = csvData.trim().split('\n');
        const headers = lines[0].split(',').map(h => h.trim());
        const data = [];
        
        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',').map(v => v.trim());
            const row = {};
            headers.forEach((header, index) => {
                row[header] = values[index];
            });
            data.push(row);
        }
        
        return JSON.stringify(data, null, 2);
    } catch (error) {
        console.error("Error converting CSV to JSON:", error.message);
        return `Error converting CSV to JSON: ${error.message}`;
    }
};

const jsonToCsv = async (jsonData) => {
    console.log("Converting JSON to CSV...");
    try {
        const data = JSON.parse(jsonData);
        
        if (!data || data.length === 0) {
            throw new Error("Empty JSON data");
        }
        
        const headers = Object.keys(data[0]);
        let csv = headers.join(',') + '\n';
        
        data.forEach(row => {
            const values = headers.map(header => row[header] || '');
            csv += values.join(',') + '\n';
        });
        
        return csv;
    } catch (error) {
        console.error("Error converting JSON to CSV:", error.message);
        return `Error converting JSON to CSV: ${error.message}`;
    }
};

const filterData = async (data, condition) => {
    console.log("Filtering data with condition:", condition);
    try {
        const items = JSON.parse(data);
        const filterFunc = new Function('x', `return ${condition}`);
        const filteredItems = items.filter(filterFunc);
        return JSON.stringify(filteredItems, null, 2);
    } catch (error) {
        console.error("Error filtering data:", error.message);
        return `Error filtering data: ${error.message}`;
    }
};

const sortData = async (data, key, reverse = false) => {
    console.log(`Sorting data by ${key} in ${reverse ? 'descending' : 'ascending'} order...`);
    try {
        const items = JSON.parse(data);
        const sortedItems = items.sort((a, b) => {
            if (reverse) {
                return a[key] < b[key] ? 1 : -1;
            } else {
                return a[key] > b[key] ? 1 : -1;
            }
        });
        return JSON.stringify(sortedItems, null, 2);
    } catch (error) {
        console.error("Error sorting data:", error.message);
        return `Error sorting data: ${error.message}`;
    }
};

const aggregateData = async (data, operation, field) => {
    console.log(`Performing ${operation} on field ${field}...`);
    try {
        const items = JSON.parse(data);
        const values = items.map(item => parseFloat(item[field]));
        
        let result;
        switch (operation.toLowerCase()) {
            case "average":
                result = values.reduce((sum, val) => sum + val, 0) / values.length;
                break;
            case "sum":
                result = values.reduce((sum, val) => sum + val, 0);
                break;
            case "min":
                result = Math.min(...values);
                break;
            case "max":
                result = Math.max(...values);
                break;
            default:
                throw new Error(`Unsupported operation '${operation}'`);
        }
        
        return JSON.stringify({ operation, field, result }, null, 2);
    } catch (error) {
        console.error("Error aggregating data:", error.message);
        return `Error aggregating data: ${error.message}`;
    }
};

// Define the tools available to the model
const tools = [
    {
        type: "function",
        function: {
            name: "csv_to_json",
            description: "Convert CSV data to JSON format",
            parameters: {
                type: "object",
                properties: {
                    csv_data: {
                        type: "string",
                        description: "The CSV data to convert"
                    }
                },
                required: ["csv_data"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "json_to_csv",
            description: "Convert JSON data to CSV format",
            parameters: {
                type: "object",
                properties: {
                    json_data: {
                        type: "string",
                        description: "The JSON data to convert"
                    }
                },
                required: ["json_data"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "filter_data",
            description: "Filter data based on a condition",
            parameters: {
                type: "object",
                properties: {
                    data: {
                        type: "string",
                        description: "The JSON data to filter"
                    },
                    condition: {
                        type: "string",
                        description: "The condition to filter by (e.g., 'x.age > 25')"
                    }
                },
                required: ["data", "condition"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "sort_data",
            description: "Sort data by a specified key",
            parameters: {
                type: "object",
                properties: {
                    data: {
                        type: "string",
                        description: "The JSON data to sort"
                    },
                    key: {
                        type: "string",
                        description: "The key to sort by"
                    },
                    reverse: {
                        type: "boolean",
                        description: "Whether to sort in descending order",
                        default: false
                    }
                },
                required: ["data", "key"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "aggregate_data",
            description: "Perform aggregation operations on data",
            parameters: {
                type: "object",
                properties: {
                    data: {
                        type: "string",
                        description: "The JSON data to aggregate"
                    },
                    operation: {
                        type: "string",
                        description: "The operation to perform (average, sum, min, max)",
                        enum: ["average", "sum", "min", "max"]
                    },
                    field: {
                        type: "string",
                        description: "The field to aggregate"
                    }
                },
                required: ["data", "operation", "field"]
            }
        }
    }
];

export const function_call_playground_data = async (prompt) => {
    console.log("Starting function call playground...");
    try {
        const messages = [
            {
                role: "system",
                content: prompt
            }
        ];

        const response = await openai.chat.completions.create({
            model: MODEL_NAME,
            messages: messages,
            tools: tools,
            tool_choice: "auto"
        });

        const message = response.choices[0].message;
        
        if (!message.tool_calls) {
            console.log("No function call was made in response to the prompt.");
            return message.content;
        }

        const results = [];
        for (const toolCall of message.tool_calls) {
            const functionName = toolCall.function.name;
            const functionArgs = JSON.parse(toolCall.function.arguments);
            
            let result;
            switch (functionName) {
                case "csv_to_json":
                    result = await csvToJson(functionArgs.csv_data);
                    break;
                case "json_to_csv":
                    result = await jsonToCsv(functionArgs.json_data);
                    break;
                case "filter_data":
                    result = await filterData(functionArgs.data, functionArgs.condition);
                    break;
                case "sort_data":
                    result = await sortData(
                        functionArgs.data,
                        functionArgs.key,
                        functionArgs.reverse || false
                    );
                    break;
                case "aggregate_data":
                    result = await aggregateData(
                        functionArgs.data,
                        functionArgs.operation,
                        functionArgs.field
                    );
                    break;
                default:
                    result = `Unknown function: ${functionName}`;
            }
            
            results.push(result);
        }

        return results.join('\n');
    } catch (error) {
        console.error("Error in function call playground:", error.message);
        return `Error in function call playground: ${error.message}`;
    }
};

// Test the functionality
if (import.meta.url === `file://${process.argv[1]}`) {
    const testPrompts = [
        "Convert this CSV data to JSON: name,age,city\nJohn,30,New York\nJane,25,Los Angeles",
        "Convert this JSON to CSV: [{\"name\":\"John\",\"age\":30,\"city\":\"New York\"},{\"name\":\"Jane\",\"age\":25,\"city\":\"Los Angeles\"}]",
        "Filter this data to show only people over 25: [{\"name\":\"John\",\"age\":30},{\"name\":\"Jane\",\"age\":25},{\"name\":\"Bob\",\"age\":35}]",
        "Sort this data by age in descending order: [{\"name\":\"John\",\"age\":30},{\"name\":\"Jane\",\"age\":25},{\"name\":\"Bob\",\"age\":35}]",
        "Calculate the average age from this data: [{\"name\":\"John\",\"age\":30},{\"name\":\"Jane\",\"age\":25},{\"name\":\"Bob\",\"age\":35}]"
    ];

    const start_time = Date.now();

    (async () => {
        try {
            for (const prompt of testPrompts) {
                console.log(`\nProcessing prompt: ${prompt}`);
                const response = await function_call_playground_data(prompt);
                console.log("Response:", response);
            }
            const end_time = Date.now();
            console.log(`\nTotal time taken: ${(end_time - start_time) / 1000} seconds`);
        } catch (error) {
            console.error("Error in test execution:", error);
        }
    })();
}

// export {
//     csvToJson,
//     jsonToCsv,
//     filterData,
//     sortData,
//     aggregateData,
//     function_call_playground_data
// };