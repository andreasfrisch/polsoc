# Polsoc CSV Creator
# - Andreas Frisch, March 2015
#
# Fetches single unhandled request, if any
# Generates CSV from request information and facebook
# Stores generated CSV to disk

import urllib.request
import json
from fb import handle_facebook_id
from datetime import datetime

#API_ROOT = "http://localhost:8000/api/"
API_ROOT = "http://polsoc.itu.dk/api/"
GET_NEXT = "getNextInQueue/"
MARK_COMPLETE = "markAsCompleted/"

def getNextInQueue():
    request = API_ROOT + GET_NEXT
    response = urllib.request.urlopen(request)
    obj = None
    if response.status == 200:
        try:
            obj = json.loads(response.readall().decode('utf-8'))
        except Exception as error:
            print("Error interpreting JSON response: %s" % error)
            return {}
    print('Got nextInQueue:\n>>status: %s\n>>object: %s' % (response.status, obj))
    return obj

def generateCsvFromRequest(request):
    facebook_id = request['facebook_id']
    date_format = "%Y-%m-%d"
    options = {
        'access_token': request['facebook_access_token'],
        'from_date': datetime.strptime(request['from_date'], date_format).date(),
        'to_date': datetime.strptime(request['to_date'], date_format).date(),
        'include_comments': request['include_comments']
    }
    print("opening output file")
    output_csv = open(request['filename'], 'w')
    print("printing to output file")
    try:
        output_csv.write(handle_facebook_id(facebook_id, options))
    except:
        output_csv.write("Something went wrong; probably access token time out")
    print("completed writing output file")
    output_csv.close()

def markRequestAsCompleted(request_id):
    request = API_ROOT + MARK_COMPLETE + str(request_id)
    response = urllib.request.urlopen(request)
    if response.status != 200:
        print("Error marking request as complete. Status: %s" % response.status)

if __name__ == "__main__":
    print("Getting next unfinished request")
    next_request = getNextInQueue()
    print("Generating CSV based on request: %s" % next_request)
    print(generateCsvFromRequest(next_request))
    print("CSV Complete. Marking as complete")
    markRequestAsCompleted(next_request['id'])
    print("..Done!")
