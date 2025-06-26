import fs from 'fs';
import { OpenAI } from 'openai';
import { config } from './config.js';

const openai = new OpenAI({
    apiKey: config.OPENAI_API_KEY,
    baseURL: config.BASE_URL
});

// Load tools definition
const toolsDefinition = JSON.parse(fs.readFileSync('tools.json', 'utf8'));

// Function to format prompt with parameters
function formatPrompt(template, parameters) {
    let prompt = template;
    for (const [key, value] of Object.entries(parameters)) {
        prompt = prompt.replace(`{${key}}`, value);
    }
    return prompt;
}

// Function to validate parameters against tool definition
function validateParameters(toolId, parameters) {
    const tool = toolsDefinition.tools.find(t => t.id === toolId);
    if (!tool) {
        throw new Error(`Tool ${toolId} not found`);
    }

    // Check if all required parameters are present
    for (const [paramName, paramDef] of Object.entries(tool.parameters)) {
        if (!(paramName in parameters)) {
            throw new Error(`Missing required parameter: ${paramName}`);
        }

        // Check enum values if specified
        if (paramDef.enum && !paramDef.enum.includes(parameters[paramName])) {
            throw new Error(`Invalid value for parameter ${paramName}. Must be one of: ${paramDef.enum.join(', ')}`);
        }
    }

    return true;
}

// Main function calling function
export async function callFunction(toolId, parameters) {
    try {
        // Validate parameters
        validateParameters(toolId, parameters);

        // Get tool definition
        const tool = toolsDefinition.tools.find(t => t.id === toolId);
        
        // Format the prompt
        const prompt = formatPrompt(tool.prompt_template, parameters);

        // Call the model
        const response = await openai.chat.completions.create({
            model: config.MODEL_NAME,
            messages: [
                {
                    role: "system",
                    content: `You are a helpful assistant that provides accurate and concise responses. 
                             For the following request, provide only the direct answer without any additional explanation or context.`
                },
                {
                    role: "user",
                    content: prompt
                }
            ],
            temperature: 0.7,
            max_tokens: 150
        });

        return {
            tool_id: toolId,
            input: parameters,
            prompt: prompt,
            output: response.choices[0].message.content.trim(),
            timestamp: new Date().toISOString()
        };
    } catch (error) {
        console.error(`Error calling function ${toolId}:`, error);
        throw error;
    }
}

// Function to get all available tools
export function getAvailableTools() {
    return toolsDefinition.tools.map(tool => ({
        id: tool.id,
        name: tool.name,
        description: tool.description,
        parameters: tool.parameters,
        example: tool.example
    }));
}

// Function to get a specific tool by ID
export function getToolById(toolId) {
    return toolsDefinition.tools.find(tool => tool.id === toolId);
} 