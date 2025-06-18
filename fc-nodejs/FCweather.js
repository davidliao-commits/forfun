import { OpenAI } from "openai";
import { config } from "dotenv";
import {BASE_URL, OPENAI_API_KEY, MODEL_NAME, OPENWEATHERMAP_API_KEY} from "./config.js";

config();
let longtitude = 0;
let latitude = 0;
// console.log("Environment variables:");
// console.log("OPENAI_API_KEY:", process.env.OPENAI_API_KEY);
// console.log("MODEL_NAME:", process.env.MODEL_NAME);
// console.log("BASE_URL:", "https://api.siliconflow.cn/v1");

const openai = new OpenAI({
    apiKey: OPENAI_API_KEY,
    baseURL: BASE_URL,
});

const getCoordinates = async(city)=>{
    console.log("get coordinates started for city:",city);
    const apiKey = OPENWEATHERMAP_API_KEY;
    const base_url = "https://api.openweathermap.org/geo/1.0/direct";
    const params = {
        q: city,
        appid: apiKey
    };
    const response = await fetch(`${base_url}?${new URLSearchParams(params)}`);
    if(response.status === 200){
        const data = await response.json();
        if(data.length > 0){
            const {name, lat, lon} = data[0];
            console.log("coordinates fetched for city:",name, lat, lon);
            return {name, lat, lon};
        }
    }
    console.error("failed to fetch coordinates with status code:", response.status);
    return null;
}

const getWeather = async(latitude, longtitude) => {
    console.log("get weather started for coordinates:",latitude, longtitude);
    const apiKey = OPENWEATHERMAP_API_KEY;
    const url = "https://api.openweathermap.org/data/2.5/weather";
    const params = new URLSearchParams({
        lat: latitude,
        lon: longtitude,
        appid: apiKey,
    });

    const response = await fetch(`${url}?${params}`);
    if(response.status === 200){
        const data = await response.json();
        const weather = data.weather[0].description;
        return `the weather at ${latitude} and ${longtitude} is ${weather}`;
    } else {
        return `failed to fetch weather at coordinates ${latitude} and ${longtitude}`;
    }
}

const tools = [{
    type: "function",
    function: {
        name: "getWeather",
        description: "get the weather for a specific latitude and longtitude",
        parameters: {
            type: "object",
            properties: {
                latitude: {
                    type: "number",
                    description: "the latitude of the location",
                },
                longtitude: {
                    type: "number",
                    description: "the longtitude of the location",
                }
            },
            required: [
                "latitude",
                "longtitude",
            ],
        },
    }
},
{
    type:"function",
    function:{
        name:"getCoordinates",
        description:"get the coordinates for a specific city",
        parameters:{
            type:"object",
            properties:{
                city:{
                    type:"string",
                    description:"the name of the city to get coordinates for",
                }
            },
            required:[
                "city",
            ]
        }
    },
}
]
export const function_call_playground_coordinates = async(prompt)=>{
    console.log("function call playground for coordinates starting...");
    const messages=[
        {
            role:"system",
            content:prompt,
        }
    ];
    const response = await openai.chat.completions.create({
        model:MODEL_NAME,
        messages:messages,
        temperature:0.01,
        stream:false,
        top_p:0.95,
        tools:tools,
    })

    const func1_name = response.choices[0].message.tool_calls[0].function.name;
    const func1_args = JSON.parse(response.choices[0].message.tool_calls[0].function.arguments);
    const func1_out = await getCoordinates(func1_args.city);

    if(func1_out && func1_out.lat && func1_out.lon){
        console.log("coordinates fetched for city", func1_out.lat, func1_out.lon);
        latitude = func1_out.lat;
        longtitude = func1_out.lon;
        return {latitude: func1_out.lat, longitude: func1_out.lon};
    } else {
        console.error("failed to fetch coordinates for city:", func1_args.city);
        return null;
    }
}

export const function_call_playground_weather = async(prompt) => {
    console.log("function call playground for weather starting...");
    const messages = [
        {
            role: "system",
            content: prompt,
        },
    ];

    const response = await openai.chat.completions.create({
        model: MODEL_NAME,
        messages: messages,
        temperature: 0.01,
        stream: false,
        top_p: 0.95,
        tools: tools,
    })
    if (!response.choices[0].message.tool_calls){
        console.error("no tool calls found in the response");
        return null;
    }
    const func1_name = response.choices[0].message.tool_calls[0].function.name;
    const func1_args = JSON.parse(response.choices[0].message.tool_calls[0].function.arguments);
    const func1_out = await getWeather(latitude, longtitude);

    messages.push(response.choices[0].message);
    messages.push({
        role: "tool",
        content: `${func1_out}`,
        tool_call_id: response.choices[0].message.tool_calls[0].id,
    })

    const response2 = await openai.chat.completions.create({
        model: MODEL_NAME,
        messages: messages,
        temperature: 0.01,
        stream: false,
        top_p: 0.95,
        tools: tools,
    })

    return response2.choices[0].message.content;
}

const prompt1 = "what are the coordinates of beijing, china?";

// Execute the function
const start_time = Date.now();

// First get coordinates
function_call_playground_coordinates(prompt1)
    .then(coords => {
        if (!coords) {
            throw new Error("Failed to get coordinates");
        }
        console.log("Got coordinates:", coords);
        // Create prompt2 here after we have the coordinates
        const prompt2 = `What is the weather like at latitude ${coords.latitude} and longitude ${coords.longitude}?`;
        return function_call_playground_weather(prompt2);
    })
    .then(result => {
        const end_time = Date.now();
        console.log(`Time taken for function call playground: ${(end_time - start_time) / 1000} seconds`);
        console.log(result);
    })
    .catch(error => {
        console.error("Error:", error);
    });
