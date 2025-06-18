import { config } from "dotenv";
import { BASE_URL, OPENAI_API_KEY, MODEL_NAME} from "./config.js";
import { OpenAI } from "openai";
config();

const openai = new OpenAI({
    apiKey: OPENAI_API_KEY, 
    baseURL: BASE_URL,
});

const count_words = async(text)=>{
    if (typeof text !== 'string') {
        text = String(text);
    }
    return text.split(/\s+/).length;
}

const find_substring = async(text, substring)=>{
    const positions = [];
    let startIndex=0;
    while(true){
        const index = text.indexOf(substring, startIndex);
        if(index===-1){
            break;
        }
        positions.push(index);
        startIndex=index+substring.length;
    }
    return positions;
}

const extract_emails = async(text)=>{
    const pattern = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
    return text.match(pattern);

}

const word_frequency = async(text)=>{
    if (typeof text !== 'string') {
        text = String(text);
    }
    const words = text.split(/\s+/);
    const frequency = {};
    for(const word of words){
        if(word.length>0){
            frequency[word]=(frequency[word]||0)+1
        }
    }
    return frequency;
}

const text_statistics = async(text)=>{
    if (typeof text !== 'string') {
        text = String(text);
    }
    const words = text.split(/\s+/);
    const sentences = text.split(/[.!?]+/).filter(sentence => sentence.trim().length > 0);
    const word_count = words.length;
    const sentence_count = sentences.length;
    
    const sum = (arr) => arr.reduce((a, b) => a + b, 0);
    
    const average_word_length = word_count > 0 ? sum(words.map(word => word.length)) / word_count : 0;
    const average_sentence_length = sentence_count > 0 ? sum(sentences.map(sentence => sentence.length)) / sentence_count : 0;
    
    return {
        word_count,
        sentence_count,
        average_word_length,
        average_sentence_length,
    }
}

const format_text = async(text, max_length) => {
    if (typeof text !== 'string') {
        text = String(text);
    }
    const words = text.split(/\s+/);
    const lines = [];
    let current_line = "";
    let current_length = 0;
    
    for(const word of words){
        if(current_line.length + word.length + 1 <= max_length){
            current_line += (current_line ? " " : "") + word;
            current_length = current_line.length;
        }
        else{
            if(current_line) {
                lines.push(current_line);
            }
            current_line = word;
            current_length = word.length;
        }
    }
    if(current_line){
        lines.push(current_line);
    }
    return lines.join("\n");
}

const executeFunctionCall = async(func_name, args) => {
    switch(func_name){
        case "count_words":
            return await count_words(args.text);
        case "find_substring":
            return await find_substring(args.text, args.substring);
        case "extract_emails":
            return await extract_emails(args.text);
        case "word_frequency":
            return await word_frequency(args.text);
        case "text_statistics":
            return await text_statistics(args.text);
        case "format_text":
            return await format_text(args.text, args.max_length);
        default:
            console.error(`Unknown function name: ${func_name}`);
            return null;
    }
}

const tools = [{
    type: "function",
    name:"count_words",
    description:"count the number of words in a given text",
    parameters:{
        type:"object",
        properties:{
            text:{
                type:"string",
                description:"the given text to count the words for"
            }
        },
        required:["text"]
    }
},
{
    type:"function",
    name:"find_substring",
    description:"find the positions of a substring in a given text",
    parameters:{
        type:"object",
        properties:{
            text:{
                type:"string",
                description:"the given text to find the substring in"
            },
            substring:{
                type:"string",
                description:"the substring to find in the given text"
            }
        },
        required:["text", "substring"]
    }
},
{
    type:"function",
    name:"extract_emails",
    description:"extract all the email addresses from a given text",
    parameters:{
        type:"object",
        properties:{
            text:{
                type:"string",
                description:"the given text to extract the emails from"
            }
        },
        required:["text"]
    }
},
{
    type:"function",
    name: "word_frequency",
    description:"calculate the frequency of each word in a given text",
    parameters:{
        type:"object",
        properties:{
            text:{
                type:"string",
                description:"the given text to calculate the word frequency for"
            }
        },
        required: ["text"]
    }
},
{
    type:"function",
    name:"text_statistics",
    description:"calculate some statistics about a given text",
    parameters:{
        type:"object",
        properties:{
            text:{
                type:"string",
                description:"the given text to calculate the statistics for"
            }
        },
        required:["text"]
    }
},
{
    type:"function",
    name:"format_text",
    description:"format a given text to a given max length",
    parameters:{
        type:"object",
        properties:{
            text:{
                type:"string",
                description:"the given text to format"
            },
            max_length:{
                type:"number",
                description:"the max length to format the text to"
            }
        },
        required:["text", "max_length"]
    }
}]



export const function_call_playground_string = async(prompt)=>{
   console.log("function call playground for string starting...");
   const messages = [
    {
        role:"system",
        content: "You are a string assistant. You can count the number of words, find given substrings, extract emails, calculate word frequency, calculate text statistics, and format text based on given max length, all for a given text. When prompted with one of these tasks, respond with a JSON object containing the type and value. For example: {\"type\": \"count_words\", \"value\": \"Hello, world!\"}. For find_substring, use format: {\"type\": \"find_substring\", \"value\": \"Hello, world!\", \"substring\": \"world\"}. For word frequency, use format: {\"type\": \"word_frequency\", \"value\": \"Hello, world!\"}. For text statistics, use format: {\"type\": \"text_statistics\", \"value\": \"Hello, world!\"}. For format_text, use format: {\"type\": \"format_text\", \"value\": \"Hello, world!\", \"max_length\": 10}"
    },
    {
        role:"user",
        content:prompt
    }
   ]

   try{
    const response = await openai.chat.completions.create({
        model:MODEL_NAME,
        messages:messages,
        temperature: 0.01,
        stream: false,
        top_p: 0.95,
        response_format: { type: "json_object" }
    })
    
    const responseContent = JSON.parse(response.choices[0].message.content);
    console.log("API Response:", responseContent);

    let validationResult;
    switch(responseContent.type){
        case "count_words":
            validationResult = await count_words(responseContent.value);
            break;
        case "find_substring":
            validationResult = await find_substring(responseContent.value, responseContent.substring);
            break;
        case "extract_emails":
            validationResult = await extract_emails(responseContent.value);
            break;
        case "word_frequency":
            validationResult = await word_frequency(responseContent.value);
            break;
        case "text_statistics":
            validationResult = await text_statistics(responseContent.value);
            break;
        case "format_text":
            validationResult = await format_text(responseContent.value, responseContent.max_length);
            break;
        default:
            throw new Error(`Unknown validation type: ${responseContent.type}`);
    }

    return JSON.stringify({
        type:responseContent.type,
        value:responseContent.value,
        isValid:validationResult
    })
   }
   catch(error){
    console.error("API Error:", {
        status:error.status,
        message:error.message,
        type: error.type,
        headers: error.headers,
        response: error.response?.data
    })
   }
}

const prompt = [
    "count the number of words in the text 'Hello, world!'",
    "find the positions of the substring 'world' in the text 'Hello, world!'",
    "extract all the email addresses from the text 'Hello, world! my email is john.doe@example.com and jane.smith@example.com'",
    "calculate the frequency of each word in the text 'Hello, world! my email is john.doe@example.com and jane.smith@example.com'",
    "calculate the statistics of the text 'Hello, world! my email is john.doe@example.com and jane.smith@example.com'",
    "format the text 'Hello, world! my email is john.doe@example.com and jane.smith@example.com' to a max length of 10",
]

for(const p of prompt){
    console.log("Prompt:", p);
    const start= Date.now();
    const result = await function_call_playground_string(p);
    const end=Date.now();
    console.log("Result:", result);
    console.log(`Time taken: ${end-start/1000}seconds`);
    console.log("--------------------------------");
}