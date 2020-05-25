import json	#standard
import subprocess #standard. Using "capture_output" arg which requires >=3.7
import os
import requests #not standard

with open("tavish.cfg") as c:
	global parser_path
	parser_path = c.read().strip("\n")

#https://gist.github.com/bcahue/4eae86ae1d10364bb66d
steamid64ident = 76561197960265728 #I Don't know what this does but it is important to conversions
def usteamid_to_commid(usteamid):
	if not usteamid == "BOT":
		for ch in ['[', ']']:
			if ch in usteamid:
				usteamid = usteamid.replace(ch, '')
	 
		usteamid_split = usteamid.split(':')
		commid = int(usteamid_split[2]) + steamid64ident
		return str(commid)
	else:
		return "BOT"

def spawns(p):
	i = 0
	if p["team"] != "other" or p["team"] != "spectator":
		for c, s in p['classes'].items():
			if c != "0":
				i = i + s
	return i

#Icewind confirms that the demos.tf API does not include users who are on team spectate/other ("other" is a catchall for issues. What issues, I don't know.)
#The problem is that while STV demos start recording on match start, POV demos typically start recording on connect (PREC responsibly follows STV's footsteps, though)
#Therefore, the user count includes users who played on "teams" during SOAP.
#We need an appropriate way to determine if someone is "playing" in just the pregame or the entire game
#POV demos count all spawns (including SOAP) but only count real-game deaths.

def parse(f, method="A", sul=6, l=True):
	if method == "A":
		if os.path.splitext(f)[1] != ".dem":	#TODO LATER: READ BINARY AND CHECK IF THIS HAS HL2DEMO HEADER
			raise ValueError("That file is not a demo")
		if os.path.getsize(f) < 9000000: #9MB
			print("Warning! This demo is very short. Information may not be enough to provide accurate results.")
		p_out = subprocess.run([parser_path, f], capture_output=True)
		j = json.loads(p_out.stdout)
		users64 = {}
		all_victims = set()
		for d in j["deaths"]:
			if d['killer'] != d['victim']:
				all_victims.add(d['victim'])
		for d in all_victims:
			d = str(d)
			u64 = usteamid_to_commid(j["users"][d]["steamId"])
			if u64 == "BOT" or spawns(j["users"][d]) < sul:
				continue
			users64[j["users"][d]["name"]] = u64	#take the SteamID3s from the local demo file, turn to a Steam64. I use the victim list from deaths because thats who actually plays the game as opposed to people connected ? If i understand the demo json right. I don't know much about it.
			lambda: print("Adding", j["users"][d]["steamId"], u64, j["users"][d]["name"]) if l else Non
		print(users64) if l else None
		rs = "?" #Request String
		for id_ in set(users64.values()):	#there is a possibility of duplicate values if someone changes their username midgame
			rs = rs + "&players[]=" + id_
		print(rs) if l else None
		r = requests.get('https://api.demos.tf/demos/?'+rs)
		try:
			lambda: print("OK Response.", r.json()[0]) if l else None
			return r.json()[0]["id"]
		except IndexError:
			print("Can't find good result, upping spawn-upper-limit {} and trying again.".format(sul))
			parse(f, sul=sul+1, l=False)
			#return -1 #r.json() is empty. absolutely no returns?
	elif method == "B":
		print("poo")
#f = input("Enter the name of the file >")
#print(parse(f))
