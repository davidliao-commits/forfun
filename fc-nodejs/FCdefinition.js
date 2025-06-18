import {OpenAI} from "openai"
import {config} from "dotenv"
import {BASE_URL, OPENAI_API_KEY, MODEL_NAME, URBAN_DICTIONARY_API_KEY} from "./config.js"

config();

const openai = new OpenAI({
    apiKey: OPENAI_API_KEY,
    baseURL: BASE_URL
})

const getDefinition = async(word) => {
    try {

        const response = await fetch(`https://urban-dictionary7.p.rapidapi.com/v0/define?term=${encodeURIComponent(word)}`, {
            method: 'GET',
            headers: {
                'x-rapidapi-key': URBAN_DICTIONARY_API_KEY,
                'x-rapidapi-host': 'urban-dictionary7.p.rapidapi.com'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (data.list && data.list.length > 0) {
            console.log("data.list", data.list);
            return `The definition of "${word}" is: ${data.list[0].definition}`;
        } else {
            return `No definition found for "${word}"`;
        }
    } catch (error) {
        console.error("Error fetching definition:", error);
        return `Failed to fetch definition for "${word}": ${error.message}`;
    }
}

const tools = [{
    type: "function",
    function: {
        name: "getDefinition",
        description: "Get the definition of a word from Urban Dictionary",
        parameters: {
            type: "object",
            properties: {
                word: {
                    type: "string",
                    description: "The word to get the definition for"
                }
            },
            required: ["word"],
            additionalProperties: false
        }
    }
}];

export const function_call_playground_definition = async (prompt) => {
    const messages = [
        {
            role: "system",
            content: prompt
        }
    ];

    try {
        const response = await openai.chat.completions.create({
            model: MODEL_NAME,
            messages: messages,
            temperature: 0.01,
            stream: false,
            top_p: 0.95,
            tools: tools
        });

        const func1_name = response.choices[0].message.tool_calls[0].function.name;
        const func1_args = JSON.parse(response.choices[0].message.tool_calls[0].function.arguments);
        const func1_out = await getDefinition(func1_args.word);
        
        messages.push(response.choices[0].message);
        messages.push({
            role: "tool",
            content: func1_out,
            tool_call_id: response.choices[0].message.tool_calls[0].id
        });

        const response2 = await openai.chat.completions.create({
            model: MODEL_NAME,
            messages: messages,
            temperature: 0.01,
            stream: false
        });

        return response2.choices[0].message.content;
    } catch (error) {
        console.error("Error in function_call_playground:", error);
        if (error.response) {
            console.error("API Response:", error.response.data);
        }
        throw error;
    }
};

const prompt = "What is the definition of the word 'sabbatical'?";

const start_time = Date.now();
try {
    const result = await function_call_playground_definition(prompt);
    const end_time = Date.now();
    console.log(`Time taken for function call playground: ${(end_time-start_time)/1000} seconds`);
    console.log(result);
} catch (error) {
    console.error("Error running the program:", error);
}