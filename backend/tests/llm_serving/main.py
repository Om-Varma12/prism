import requests
		
url = "https://api.catalyst.zoho.in/quickml/v1/project/46143000000022001/glm/chat"
headers = {
	"Content-Type": "application/json",
	"Authorization": "Bearer 1000.dbd956a056a337230b25ed4b607a1b7e.d72a63df78975be26364663858cdccfa", 
	"CATALYST-ORG": "60074849663"
}
data = {
	"model": "crm-di-glm47b_30b_it",
	"messages": [
		{
			"role": "system",
			"content": "You are a helpful assistant. Listen to what the user says and always respond."
		},
		{
			"role": "user",
			"content": "what is the capital of india?"
		}
	],
	"max_tokens": 500,
	"temperature": 0.2,
	"stream": False
}

print(data)
response = requests.post(url, json=data, headers=headers)
print(response.json())