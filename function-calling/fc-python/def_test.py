import requests

url = "https://urban-dictionary7.p.rapidapi.com/v0/define"

querystring = {"term":"yeet"}

headers = {
	"x-rapidapi-key": "a9f051cf53msh70504d662074c20p10960fjsn413232e29f01",
	"x-rapidapi-host": "urban-dictionary7.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())