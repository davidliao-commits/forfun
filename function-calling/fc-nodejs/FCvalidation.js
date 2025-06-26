import { OpenAI } from "openai";
import { config } from "dotenv";
import { BASE_URL, OPENAI_API_KEY, MODEL_NAME } from "./config.js";
config();


const openai = new OpenAI({
    apiKey: OPENAI_API_KEY,
    baseURL: BASE_URL,
});

const validate_email = async(email) =>{
    const pattern= /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    console.log("email validation function called");
    return pattern.test(email);
}

const validate_phone = async(phone) => {
    console.log("phone validation function called");
    const pattern = /^\d{10}$/;
    return pattern.test(phone);
}

const validate_password = async(password) =>{
    console.log("password validation function called");
    const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return pattern.test(password);
}


const validate_json_schema = async (data, schema) => {
    console.log("json schema validation function called");
    console.log("Data:", data);
    console.log("Schema:", schema);
    
    // Validate data against a JSON schema
    const errors = [];
    
    const validate_type = (value, expected_type) => {
        if (expected_type === "string") {
            return typeof value === "string";
        } else if (expected_type === "number") {
            return typeof value === "number";
        } else if (expected_type === "boolean") {
            return typeof value === "boolean";
        } else if (expected_type === "array") {
            return Array.isArray(value);
        } else if (expected_type === "object") {
            return typeof value === "object" && value !== null && !Array.isArray(value);
        }
        return false;
    };
    
    const check_required = (data, required) => {
        return required.filter(field => !(field in data));
    };
    
    const validate_field = (value, field_schema, field_name) => {
        const field_errors = [];
        
        // Check type
        if (field_schema && field_schema.type) {
            if (!validate_type(value, field_schema.type)) {
                field_errors.push(`${field_name} should be of type ${field_schema.type}`);
            }
        }
        
        // Check required
        if (field_schema && field_schema.required === true && (value === null || value === undefined)) {
            field_errors.push(`${field_name} is required`);
        }
        
        // Check minimum/maximum for numbers
        if (field_schema && field_schema.type === "number") {
            if (field_schema.minimum !== undefined && value < field_schema.minimum) {
                field_errors.push(`${field_name} must be at least ${field_schema.minimum}`);
            }
            if (field_schema.maximum !== undefined && value > field_schema.maximum) {
                field_errors.push(`${field_name} must be at most ${field_schema.maximum}`);
            }
        }
        
        // Check minLength/maxLength for strings
        if (field_schema && field_schema.type === "string") {
            if (field_schema.minLength !== undefined && value.length < field_schema.minLength) {
                field_errors.push(`${field_name} must be at least ${field_schema.minLength} characters`);
            }
            if (field_schema.maxLength !== undefined && value.length > field_schema.maxLength) {
                field_errors.push(`${field_name} must be at most ${field_schema.maxLength} characters`);
            }
        }
        
        return field_errors;
    };
    
    // Ensure schema is an object
    if (!schema || typeof schema !== 'object') {
        return {
            is_valid: false,
            errors: ["Invalid schema: schema must be an object"],
            message: "Validation failed"
        };
    }
    
    // Check required fields
    if (schema.required && Array.isArray(schema.required)) {
        const missing = check_required(data, schema.required);
        if (missing.length > 0) {
            errors.push(...missing.map(field => `Missing required field: ${field}`));
        }
    }
    
    // Validate each field
    const properties = schema.properties || {};
    for (const [field_name, field_schema] of Object.entries(properties)) {
        if (field_name in data) {
            errors.push(...validate_field(data[field_name], field_schema, field_name));
        }
    }
    
    return {
        is_valid: errors.length === 0,
        errors: errors,
        message: errors.length === 0 ? "Valid data" : "Validation failed"
    };
};

const validate_date_format = async(date, format) => {
    console.log("date format validation function called");
    console.log("Date:", date);
    console.log("Format:", format);
    
    // If no format is provided, use a default format
    if (!format) {
        format = "YYYY-MM-DD";
    }
    
    // Convert format to regex pattern
    const formatToRegex = (format) => {
        return format
            .replace(/YYYY/g, '\\d{4}')
            .replace(/MM/g, '(0[1-9]|1[0-2])')
            .replace(/DD/g, '(0[1-9]|[12]\\d|3[01])')
            .replace(/HH/g, '([01]\\d|2[0-3])')
            .replace(/mm/g, '([0-5]\\d)')
            .replace(/ss/g, '([0-5]\\d)');
    };
    
    const pattern = new RegExp(`^${formatToRegex(format)}$`);
    return pattern.test(date);
};

const validate_ip_address = async(ip) => {
    console.log("ip address validation function called");
    const ipv4_pattern = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    const ipv6_pattern = /^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$/;
    return ipv4_pattern.test(ip) || ipv6_pattern.test(ip);
}
const executeFunctionCall = async(func_name, args) =>{
    switch(func_name){
        case "validate_email":
            return validate_email(args.email);
        case "validate_phone":
            return validate_phone(args.phone);
        case "validate_password":
            return validate_password(args.password);
        case "validate_json_schema":
            return validate_json_schema(JSON.parse(args.data), JSON.parse(args.schema));
        case "validate_date_format":
            return validate_date_format(args.date, args.format);
        case "validate_ip_address":
            return validate_ip_address(args.ip);
        default:
            throw new Error(`Unknown function:${func_name}`);
    }
}
const tools = [{
    type:"function",
    name:"validate_email",
    description:"validate an email address",
    parameters:{
        type:"object",
        properties:{
            email:{
                type:"string",
                description:"the email address needed to validate",
            }
        },
        required:["email"],
        additionalProperties:false,
    }
},
{
    type:"function",
    name:"validate_phone",
    description:"validate a phone number",
    parameters:{
        type:"object",
        properties:{
            phone:{
                type:"string",
                description:"the phone number needed to validate"
            }
        },
        required:["phone"],
        additionalProperties:false,
    }
},
{
    type:"function",
    name:"validate_password",
    description:"validate a password",
    parameters:{
        type:"object",
        properties:{
            password:{
                type:"string",
                description:"the password needed to validate"
            }
        },
        required:["password"],
        additionalProperties:false,
    }
},
{
    type:"function",
    name:"validate_json_schema",
    description:"validate a given json data against a given json schema",
    parameters:{
        type:"object",
        properties:{
            data:{
                type:"string",
                description:"the json data needed to validate"
            },
            schema:{
                type:"string",
                description:"the json schema needed to validate"
            }
        },
        required:["data", "schema"],
        additionalProperties:false,
    }
},
{
    type:"function",
    name:"validate_date_format",
    description:"validate a given date against a given date format",
    parameters:{
        type:"object",
        properties:{
            date:{
                type:"string",
                description:"the date needed to validate"
            },
            format:{
                type:"string",
                description:"the date format used to validate the given date"
            }
        },
        required:["date","format"],
    }
},
{
    type:"function",
    name:"validate_ip_address",
    description:"validate an ip address",
    parameters:{
        type:"object",
        properties:{
            ip:{
                type:"string",
                description:"the ip address needed to validate"
            }
        },
        required:["ip"],
        additionalProperties:false,
    }
}]

export const function_call_playground_validation = async(prompt) => {
    const messages = [{
        "role": "system",
        "content": "You are a validation assistant. You can validate emails, phone numbers, passwords, JSON schemas, date formats, and IP addresses. When asked to validate something, respond with a JSON object containing the validation type and the value to validate. For example: {\"type\": \"email\", \"value\": \"test@example.com\"}. For JSON schema validation, use format: {\"type\": \"json_schema\", \"data\": {...}, \"schema\": {...}}. For phone numbers, use type: \"phone\". For date format validation, use format: {\"type\": \"date_format\", \"date\": \"2023-12-31\", \"format\": \"YYYY-MM-DD\"}"
    }, {
        "role": "user",
        "content": prompt
    }];

    try {
        const response = await openai.chat.completions.create({
            model: MODEL_NAME,
            messages: messages,
            temperature: 0.01,
            stream: false,
            top_p: 0.95,
            response_format: { type: "json_object" }
        });

        const responseContent = JSON.parse(response.choices[0].message.content);
        console.log("API Response:", responseContent);

        let validationResult;
        switch(responseContent.type) {
            case "email":
                validationResult = await validate_email(responseContent.value);
                break;
            case "phone":
            case "phone_number":
                validationResult = await validate_phone(responseContent.value);
                break;
            case "password":
                validationResult = await validate_password(responseContent.value);
                break;
            case "json_schema":
                const data = typeof responseContent.data === 'string' ? JSON.parse(responseContent.data) : responseContent.data;
                const schema = typeof responseContent.schema === 'string' ? JSON.parse(responseContent.schema) : responseContent.schema;
                validationResult = await validate_json_schema(data, schema);
                break;
            case "date_format":
                validationResult = await validate_date_format(
                    responseContent.date || responseContent.value,
                    responseContent.format
                );
                break;
            case "ip_address":
                validationResult = await validate_ip_address(responseContent.value);
                break;
            default:
                throw new Error(`Unknown validation type: ${responseContent.type}`);
        }

        return JSON.stringify({
            type: responseContent.type,
            value: responseContent.value || responseContent.data || responseContent.date,
            isValid: validationResult
        });
    } catch (error) {
        console.error("API Error:", {
            status: error.status,
            message: error.message,
            type: error.type,
            headers: error.headers,
            response: error.response?.data
        });
        throw error;
    }
}

const prompt= [
    "Validate this email address: user@example.com",
    "Validate this phone number: +1-555-123-4567",
    "Validate this password: Password123!",
    "Validate this data against the schema: {'name': 'John', 'age': 30} with schema {'type': 'object', 'properties': {'name': {'type': 'string'}, 'age': {'type': 'number', 'minimum': 0, 'maximum': 120}}, 'required': ['name', 'age']}",
    "Validate this date format: 2023-12-31",
    "Validate this IP address: 192.168.1.1"
]
let total_time=0;
for (const p of prompt){
    const start=Date.now();
    const result=await function_call_playground_validation(p);
    const end=Date.now();
    total_time+=(end-start);
    console.log(`Prompt: ${p}`);
    console.log(`Result: ${result}`);
    console.log(`Time taken: ${(end-start)/1000} seconds`);
    console.log("--------------------------------");
}
console.log(`Total time taken: ${total_time/1000} seconds`);