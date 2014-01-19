#!/usr/bin/env python

""" 
Christopher Bradshaw												27/12/13
token.py

Contains functions to deal with tokens. 
"""
import pickle
import requests

global token_file, client_file

# Token is stored and read from this token file - it is a pickled file
token_file = "token"
# Client id and client secret are stored and read from this client file.
# This is just so that I do not expose them on github...
client_file = "client"

# Reads the client_id and client_secret from the client_file
# returns them in a list: [client_id, client_secret]
def get_client_info():
	f = open(client_file, 'r')
	client = [f.readline().split(' ')[0]] # client id
	client.append(f.readline().split(' ')[0]) # client secret
	f.close()
	return(client)
	

# Prompts the user to allow box_sync to access their box account
# They need to copy a code from the url. 
# Messy. Should grab this code automatically somehow.
# Needs to be re written but much much later...
def login():
	client = get_client_info()

	payload ={'response_type': 'code', 'client_id': client[0]}
	lpage = "https://www.box.com/api/oauth2/authorize"
	r = requests.get(lpage, params=payload)
	print r.url
	print "Please follow the instructions, and once done copy the 'code=XXXXX' in the url"
	
	# Enter the code and get the access key!
	code = raw_input("Please enter the code you got:")	
	payload2 = {"client_id": client[0], "grant_type": "authorization_code", "client_secret": client[1], "code": code}
	r = requests.post("https://www.box.com/api/oauth2/token", data=payload2)
	with open(token_file, "wb") as f:
		pickle.dump(r.json(), f)
	return(r.json())

# Renews the access_token
# Writes the new token to the token_file and returns the new token
def refresh_token(access_token):
	client = get_client_info()

	payload = {"client_id": client[0], "client_secret":client[1], "grant_type":"refresh_token", "refresh_token":access_token["refresh_token"]}
	r = requests.post("https://www.box.com/api/oauth2/token", data=payload)

	with open(token_file, "wb") as f:
		pickle.dump(r.json(), f)
	f.close()
	return(r.json())

# Reads old token from token_file and returns it
def read_old_token():
	with open(token_file, "rb") as f:
		access_token = pickle.load(f)
	f.close()
	return(access_token)
