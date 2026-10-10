Integrating APIs is a core skill for AI agent development, as it allows your agent to fetch data and interact with the digital world. In Python, the standard library for this is requests for synchronous operations, and httpx or aiohttp for asynchronous (fast, non-blocking) operations.
Below are three structured tutorials and code examples ranging from basic REST API fetching to advanced authenticated and asynchronous integrations.
------------------------------
## 1. The Basics: Fetching Data from a Public API (REST GET)
This tutorial shows how to safely request data from a public endpoint, parse JSON, and handle common HTTP error codes.

	import requests
	def get_crypto_price(coin_id="bitcoin"):
		"""Fetches real-time price information for a given cryptocurrency."""
		url = f"https://coingecko.com"
		params = {
			"ids": coin_id,
			"vs_currencies": "usd"
		}
    
    try:
        # 1. Send the GET request
        response = requests.get(url, params=params, timeout=10)
        
        # 2. Raise an exception if the server returned an HTTP error code (4xx or 5xx)
        response.raise_for_status()
        
        # 3. Parse JSON data into a Python dictionary
        data = response.json()
        
        price = data.get(coin_id, {}).get("usd")
        return f"The current price of {coin_id.capitalize()} is ${price:,} USD."
        
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except requests.exceptions.RequestException as err:
        return f"An error occurred: {err}"
	# Example Executionif __name__ == "__main__":
    print(get_crypto_price("bitcoin"))

------------------------------
## 2. Authenticated POST Request (Sending Data with API Keys)
Most production APIs require an API Key or Bearer Token passed inside the headers, and payload data sent inside the request body (JSON).

	import osimport requestsfrom dotenv import load_dotenv

	load_dotenv()  # Loads variables from a .env file into environment variables
	def create_github_issue(repo_owner: str, repo_name: str, title: str, body: str):
		"""Creates a GitHub issue using a Personal Access Token (PAT)."""
		url = f"https://github.com{repo_owner}/{repo_name}/issues"
    
    # Retrieve the token safely from environment variables
    api_token = os.getenv("GITHUB_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    payload = {
        "title": title,
        "body": body,
        "labels": ["bug", "agent-reported"]
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    
    if response.status_code == 201:
        issue_data = response.json()
        return f"Issue created successfully! URL: {issue_data.get('html_url')}"
    else:
        return f"Failed to create issue: {response.status_code} - {response.text}"

	# Example Setup (Make sure GITHUB_TOKEN is in your environment)
	print(create_github_issue("your-username", "your-repo", "Fix Agent Loop", "The agent is stuck in an infinite loop."))

------------------------------
## 3. Asynchronous API Calls (For High-Performance AI Agents)
AI agents often need to pull information from multiple sources simultaneously. Using asyncio and httpx allows you to trigger multiple API requests concurrently without waiting for them sequentially.

	import asyncioimport httpximport time
	async def fetch_pokemon_ability(client: httpx.AsyncClient, pokemon_name: str) -> str:
		"""Asynchronously fetches a Pokémon's primary ability."""
		url = f"https://pokeapi.co{pokemon_name.lower()}"
		try:
			response = await client.get(url, timeout=5.0)
			if response.status_code == 200:
				data = response.json()
				ability = data["abilities"][0]["ability"]["name"]
				return f"{pokemon_name.capitalize()}: {ability}"
			return f"{pokemon_name.capitalize()}: Failed to fetch"
		except Exception as e:
			return f"{pokemon_name.capitalize()}: Error {str(e)}"
	async def main():
		pokemon_list = ["ditto", "pikachu", "charizard", "bulbasaur", "squirtle"]
    
    # Use a single client session for pooling connections efficiently
    async with httpx.AsyncClient() as client:
        # Create a list of concurrent tasks
        tasks = [fetch_pokemon_ability(client, poke) for poke in pokemon_list]
        
        # Run all tasks simultaneously
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        print("\n".join(results))
        print(f"\nFetched {len(pokemon_list)} APIs concurrently in {end_time - start_time:.2f} seconds.")
	if __name__ == "__main__":
		# Run the async loop
		asyncio.run(main())

------------------------------
## Best Practices for API Integrations in AI Agents

* Always Set a Timeout: Never call requests.get() without timeout=. If the API hangs, your whole agent hangs forever.
* Use .json() carefully: Check response.headers.get('Content-Type') or wrap it in a try/except block. A crashing API often returns plain HTML error pages instead of JSON, which will crash your app.
* Environment Variables: Never hardcode secrets. Always use os.environ or the python-dotenv package.
* Backoff and Retries: For production-grade tools, use libraries like tenacity to automatically retry failed requests if the API returns a rate limit (HTTP 429) or temporary server error (HTTP 503).

Are you looking to integrate a specific API (like OpenAI, Stripe, Notion, or Slack) into your workspace, or would you like to see how to wrap one of these custom API functions as a callable Tool that an AI Agent can autonomously run? Let me know your target platform!


