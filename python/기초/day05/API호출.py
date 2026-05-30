import requests

# 무료 공개 API (키 없이 사용 가능)
url = "https://jsonplaceholder.typicode.com/posts/1"

response = requests.get(url)
data = response.json()

print("=== API 응답 ===")
print(f"제목: {data['title']}")
print(f"내용: {data['body']}")
print(f"유저ID: {data['userId']}")