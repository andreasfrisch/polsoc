#-*- coding: utf8 -*-
import urllib3
import json
import logging
from dateutil import parser

http = urllib3.PoolManager()
logging.basicConfig(filename="csv_creator.log", level=logging.DEBUG)

def handle_comments(post_identifier, options, comment_indent_level=1):
	done = False
	pageLimit = 50
	
	comments = [] #storing comments for sorting
	#url = "https://graph.facebook.com/{facebook_identifier}/comments?access_token={access_token}&limit={limit}&filter=toplevel&fields=from,message,comments.limit(0),like_count,created_time".format(
	#			facebook_identifier = post_identifier,
	#			access_token = options["access_token"],
	#			limit = pageLimit
	#)
	url = "https://graph.facebook.com/{facebook_identifier}/comments?access_token={access_token}&limit={limit}&filter=toplevel&fields=from,message,like_count,created_time".format(
				facebook_identifier = post_identifier,
				access_token = options["access_token"],
				limit = pageLimit
	)
	print("url: %s" % url)
	logging.debug("attempting to fetch url: %s" % url)
	#response, content = httplib2.Http(".cache", disable_ssl_certificate_validation=True).request(url)
	response = http.request('GET', url)
	logging.debug("fetched url, decoding..")
	post_page = json.loads(response.data.decode('utf-8'))
	logging.debug("..done decoding and loading url as JSON")
	#post_page = json.loads(content, "utf-8")
	while not done:
		if not "data" in post_page:
			done = True
			logging.debug("no 'data' in page")
			break
		if post_page["data"] == []:
			done = True
			logging.debug("empty 'data' in page")
			break
		for comment in post_page['data']:
			if "created_time" in comment:
				comments.append((comment['created_time'],comment))	
		if "paging" in post_page:
			if "next" in post_page["paging"]:
				url = post_page["paging"]["next"]
				#response, content = httplib2.Http(".cache", disable_ssl_certificate_validation=True).request(url)
				#post_page = json.loads(content, "utf-8")
				response = http.request('GET', url)
				post_page = json.loads(response.data.decode('utf-8'))
			else:
				done = True
				logging.debug("no 'next' in 'paging' in page. We are done")
				break
		else:
			done = True
			logging.debug("no 'paging' in page. We are done")
			break

	##sorting comments by timestamp
	#comments.sort(key=lambda tup: tup[0])

	return_text = ""
	for timestamp, comment_object in comments:
		nextlvl_comment_count, nextlvl_comment_string = handle_comments(comment_object['id'], options, comment_indent_level+1)
		comment_string = "-".join(["comment"] * comment_indent_level) + "," # fucking magic
		
		comment_string += "%s," % comment_object["from"]["name"]
		comment_string += "%s," % comment_object["from"]["id"]
		comment_datetime = parser.parse(comment_object["created_time"])
		comment_string += u"%s," % comment_datetime.time() # time (hour)
		comment_string += u"%s," % comment_datetime.date() # time (date)
		comment_string += "%s," % comment_object["like_count"]
		comment_string += "%s," % nextlvl_comment_count
		try:
			comment_string += "\"%s\"," % comment_object["message"] \
					.replace('"',"'") \
					.replace("\n"," ") \
					.replace("\r"," ")
		except:
			comment_string += ","
			print(">>> Error in comment")
			logging.warn("Error in comment: %s, ignoring!" % comment_object)
			#print post
			#print "<<<"
		return_text += '%s\n%s' % (comment_string, nextlvl_comment_string) #reverses comment order

	return len(comments), return_text

def get_likes(post_identifier, options):
	#h = httplib2.Http(".cache", disable_ssl_certificate_validation=True)
	url = "https://graph.facebook.com/" + post_identifier + "/likes" \
		+ "?access_token=" + options["access_token"] \
		+ "&summary=1"
	
	#response, content = h.request(url)
	#post_page = eval(
	#		content
	#		.replace("false", "False")
	#		.replace("true", "True")
	#	)
	response = http.request('GET', url)
	post_page = json.loads(response.data.decode('utf-8'))#.replace("false", "False").replace("true", "True"))
	if "summary" in post_page:
		return "%s" % post_page["summary"]["total_count"]
	else:
		return "n/a"

def handle_facebook_post(post, options):
	post_datetime = parser.parse(post["created_time"])
	#get comment amount and comment texts
	comment_amount, comment_string = handle_comments(post['id'], options)
	#remove comment text if undesired
	if not options["include_comments"]:
		comment_string = u""
	post_string = u""
	post_string += u"Facebook," # type
	post_string += u"%s," % post['from']['name']# name
	post_string += u"," # allow for id on comments
	post_string += u"%s," % post_datetime.time() # time (hour)
	post_string += u"%s," % post_datetime.date() # time (date)
	post_string += u"%s," % get_likes(post["id"], options) # likes
	post_string += u"%s," % comment_amount # comments
	try:
		if "message" in post:
			post_string += u"\"%s\"" % post["message"].replace('"',"'").replace("\n"," ") # text
			#print(post["message"])
		elif "story" in post:
			post_string += u"\"%s\"" % post["story"].replace('"',"'").replace("\n"," ") # text
	except:
		print(">>> Error in post")
	post_string += u"\n"
	post_string += comment_string
	return post_string


def handle_facebook_id(facebook_id, options):
	print("Handle Facebook Id: %s, with options: %s" % (facebook_id, options))
	logging.debug("Handle Facebook ID: %s, with options: %s" % (facebook_id, options))
	result_string = ""
	if facebook_id is not "":
		done = False
		pageLimit = 200
		url = "https://graph.facebook.com/%s/posts?access_token=%s&limit=%s" % (
				str(facebook_id),
				options["access_token"],
				str(pageLimit),
		)
		print("opening url: %s" % url)
		logging.debug("opening url: %s" % url)
		#response, content = httplib2.Http(
		#		".cache",
		#		disable_ssl_certificate_validation = True
		#).request(url, "GET")
		#post_page = json.loads(content, "utf-8")
		response = http.request('GET', url)
		content = response.data.decode('utf-8')
		#print("recieved content: %s" % content)
		#logging.debug("recieved content: %s" % content)
		post_page = json.loads(content)
		print("successfully loaded json content as python")
		logging.debug("successfully loaded json content as python")
		#	.replace("false", "False")
		#	.replace("true", "True")
		#)
		print("url content loaded correctly")
		while not done:
			print(">>> not done yet")
			if "data" in post_page:
				print(">>>>\t post has data")
				logging.debug("post has data")
				if post_page["data"] == []:
					print("ERROR >>>>\tERROR: data is empty <<< ERROR")
					done = True
					continue
				for post in post_page["data"]:
					post_created_time = parser.parse(post["created_time"]).date()
					#print(">> >> Date comparisons (post, from, to)", post_created_time, options["from_date"], options["to_date"])
					#logging.debug(">> >> Date comparisons (post, from, to)", post_created_time, options["from_date"], options["to_date"])
					if post_created_time < options["from_date"]:
						done = True
						continue
					if post_created_time > options["from_date"] \
							and post_created_time < options["to_date"]:
						#print(">>> >>>handling facebook post: ", post)
						#logging.debug(">>> >>>handling facebook post: ", post)
						result_string += handle_facebook_post(post, options)
				if "paging" in post_page:
					if "next" in post_page["paging"]:
						url = post_page["paging"]["next"]
						print('>>> next URL: ',url)
						logging.debug("next url: %s" % url)
						#response, content = httplib2.Http(
						#		".cache",
						#		disable_ssl_certificate_validation = True
						#).request(url, "GET")
						#post_page = json.loads(content, "utf-8")
						response = http.request('GET', url)
						post_page = json.loads(response.data.decode('utf-8'))
					else:
						done = True
						logging.debug("No 'next' in 'paging' in page. we are done!")
						break
				else:
					print("ERROR >>>>\tERROR: no paging <<< ERROR")
					logging.debug("No 'paging' in page. we are done!")
					done = True
					continue
			else:
				done = True
				continue
		print(">>> done!")
	#print("result string: ", result_string)
	return result_string
