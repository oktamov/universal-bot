import requests

url = "https://background-removal.p.rapidapi.com/remove"

headers = {
    'content-type': "application/x-www-form-urlencoded",
    'x-rapidapi-host': "background-removal.p.rapidapi.com",
    'x-rapidapi-key': "6f01dc13e8msh46da8b6a8249169p1b5857jsn3dfb408ca3e5"
}


async def remove_background(img_url):
    payload = f"image_url={img_url}"
    response = requests.request("POST", url, data=payload, headers=headers)
    return response.json()['response']['image_url']
