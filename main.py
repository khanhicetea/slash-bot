import os
import hug
from falcon import HTTP_BAD_REQUEST, HTTP_OK
from bot.slash import *


SLASH_TOKEN = os.environ.get('SLASH_TOKEN')


@hug.post('/slash', input_format=hug.input_format.urlencoded)
def webhook_slash_bot(token: hug.types.text, team_id: hug.types.text, team_domain: hug.types.text,
	channel_id: hug.types.text, channel_name: hug.types.text, user_id: hug.types.text,
	user_name: hug.types.text, command: hug.types.text,
	text: hug.types.text, response_url: hug.types.text, response):
	
	if token != SLASH_TOKEN:
		response.status = HTTP_BAD_REQUEST
		return {"error": "Wrong slash token !"}

	func_name = 'slash_{}'.format(command[1:])
	func = globals()[func_name]

	text, response_type = func(user_name, text)

	return {"text": text, "response_type": response_type}
