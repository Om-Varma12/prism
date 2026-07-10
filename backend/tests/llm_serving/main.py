import requests
		
url = "https://api.catalyst.zoho.in/quickml/v1/project/46143000000022001/glm/chat"
headers = {
	"Content-Type": "application/json",
	"Authorization": "Bearer 1000.ca6bb08e37adc22780c50e2313d4355b.0c84ada559c6139ff7d49da5a670d557", 
	"CATALYST-ORG": "60074849663"
}
data = {
	"model": "crm-di-glm47b_30b_it",
	"messages": [
		{
			"role": "system",
			"content": "You are a helpful assistant."
		},
		{
			"role": "user",
			"content": "What's the weather like in Paris today?"
		}
	],
	"max_tokens": 500,
	"temperature": 0.7,
	"stream": False,
	"chat_template_kwargs": {
		"enable_thinking": True
	},
	"tools": [
		{
			"type": "function",
			"function": {
				"name": "get_weather",
				"description": "Get current weather information for a specific location",
				"parameters": {
					"type": "object",
					"properties": {
						"location": {
							"type": "string",
							"description": "The city and country, e.g. Paris, France"
						},
						"unit": {
							"type": "string",
							"enum": [
								"celsius",
								"fahrenheit"
							],
							"description": "Temperature unit"
						}
					},
					"required": [
						"location"
					]
				}
			}
		}
	],
	"tool_choice": "auto"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())