#!/usr/bin/env python

""" 
Christopher Bradshaw												27/12/13
token.py

Contains functions to deal with tokens. 
"""
import pickle
import requests

global client_id, client_secret, token_file

token_file = "token"
client_file = "client"

# Prompts the user to go to a page, enter their login, copy a code from the url...
# Messy. Needs to be re written but much much later...
def login():
	# Get the code
	f = open(client_file, 'r')
	client_id = f.readline().split(' ')[0]
	client_secret = f.readline().split(' ')[0]

	payload ={'response_type': 'code', 'client_id': client_id}
	lpage = "https://www.box.com/api/oauth2/authorize"
	r = requests.get(lpage, params=payload)
	print r.url
	
	# Enter the code and get the access key!
	code = raw_input("Please enter the code you got:")	
	payload2 = {"client_id": client_id, "grant_type": "authorization_code", "client_secret": client_secret, "code": code}
	r = requests.post("https://www.box.com/api/oauth2/token", data=payload2)
	with open(token_file, "wb") as f:
		pickle.dump(r.json(), f)
	return(r.json())

# Given a token, pings box and asks for it to be renewed
# Should be valid for another 14 days
# saves it to the token file as a pickle
def refresh_token(access_token):
	f = open(client_file, 'r')
	client_id = f.readline().split(' ')[0]
	client_secret = f.readline().split(' ')[0]
	payload = {"client_id": client_id, "client_secret":client_secret, "grant_type":"refresh_token", "refresh_token":access_token["refresh_token"]}
	r = requests.post("https://www.box.com/api/oauth2/token", data=payload)

	with open(token_file, "wb") as f:
		pickle.dump(r.json(), f)
	return(r.json())

# Grabs old token from the token file
def read_old_token():
	with open(token_file, "rb") as f:
		access_token = pickle.load(f)
	f.close()
	return(access_token)
