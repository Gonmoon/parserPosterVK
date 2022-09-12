import json
import os
import requests
import vk_api
import asyncio
from time import sleep


# -----Настройки-----
vk_session = vk_api.VkApi('', '')
token = ""
# -----Кол-во постов-----
count_post = 51

# -----Парсинг и репост-----
async def Posts(group_name:str, owner_id_my_group:str) -> None:
	#-----Авторизация-----
	vk_session.auth()

	# -----Получение постов-----
	url = f"https://api.vk.com/method/wall.get?domain={group_name}&count={count_post}&access_token={token}&v=5.81"
	src = requests.get(url).json()

	# -----Извлечение постов-----
	src = src["response"]["items"]

	# -----Переварачиваем------
	posts = src[::-1]

	fresh_posts_id = []
	for fresh_post_id in posts:
		fresh_post_id = fresh_post_id["id"]
		fresh_posts_id.append(fresh_post_id)
     
	# -----Иноформация из постов-----
	for post in posts:
		# -----Id поста-----
		post_id = post["id"]

		# -----Id владельца-----
		owner_id = post["from_id"]

		# -----Проверка на созданые посты-----
		if os.path.exists(f"exist_posts_{group_name}.txt"):
			with open(f"exist_posts_{group_name}.txt", "r") as data_file:
				data = data_file.read().splitlines()
				for old_id in data:
					if int(old_id) == int(post_id):
						post = ""
		
		# -----Текст-----
		if "text" in post:
			text = post["text"]

		# -----Проверка вложений-----
		try:
			if post["attachments"][0]["type"] != "photo" or post["attachments"][0]["type"] != "video":
				text = None
		except:
			pass

		if "attachments" in post:
			post = post["attachments"]
			try:
				photo_quality_url = post[0]["photo"]["sizes"][-1]["url"]
			except:
				pass

		# -----Кол-во видео/фото-----
		attachments = None
		if len(post) == 1:
			# -----Фото-----
			if post[0]["type"] == "photo":
				photo_post_id = post[0]["photo"]["id"]
				# -----Вложения-----
				attachments = f"photo{owner_id}_{photo_post_id}"
			# -----Видео-----	
			elif post[0]["type"] == "video":
				video_post_id = post[0]["video"]["id"]
				video_owner_id = post[0]["video"]["owner_id"]
				# -----Вложения-----
				attachments = f"video{video_owner_id}_{video_post_id}"
			else:
				print(f"Post №{post_id} group {group_name} error")
		else:
			attachments = []
			for post_item_photo in post:
				# -----Фото-----
				if post_item_photo["type"] == "photo":
					photo_post_id = post_item_photo["photo"]["id"]
					attachments.append(f"photo{owner_id}_{photo_post_id}")

				# -----Видео-----
				elif post_item_photo["type"] == "video":
					video_post_id = post_item_photo["video"]["id"]
					video_owner_id = post_item_photo["video"]["owner_id"]
					# -----Вложения-----
					attachments.append(f"video{video_owner_id}_{video_post_id}")
				else:
					print(f"Post №{post_id} group {group_name} error")

			# -----Перевод вложений в str----- 
			attachments = ",".join(attachments)
		
		try:
			# -----Данные для репоста-----
			params = {
				"attachments": attachments,
				"message": text,
				"owner_id": owner_id_my_group,
				"from_group": "1"
				}
			# -----Репост-----
			sleep(2)
			# vk_session.get_api().wall.post(**params)
		except:
			print(f"Post №{post_id} already created or cannot be published")

	# -----Сохранения id постов-----
	if os.path.exists(f"exist_posts_{group_name}.txt"):
		with open(f"exist_posts_{group_name}.txt", "r+") as file:
			data = file.read().split("\n")
			if fresh_posts_id != data:
				# -----Разность-----
				new_ads = list(set(fresh_posts_id) - set(data))
				for item in new_ads:
					# -----Сохранение-----
					file.write(str(item) + "\n")
	else:
		with open(f"exist_posts_{group_name}.txt", "w") as file:
			for item in fresh_posts_id:
				file.write(str(item) + "\n")

async def main():
	await Posts("", "")
	await Posts("", "")
	await Posts("", "")

# -----Запуск-----
while True:
	asyncio.run(main())
	sleep(150)
