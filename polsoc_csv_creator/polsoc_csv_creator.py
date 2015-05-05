# Polsoc CSV Creator
# - Andreas Frisch, March 2015
#
# Fetches single unhandled request, if any
# Generates CSV from request information and facebook
# Stores generated CSV to disk

import urllib3
import json
import logging
from fb import handle_facebook_id
from datetime import datetime

API_ROOT = "http://polsoc.itu.dk/api/"
GET_NEXT = "getNextInQueue/"
MARK_COMPLETE = "markAsCompleted/"

http = urllib3.PoolManager()

logging.basicConfig(filename="csv_creator.log", level=logging.DEBUG)

def getNextInQueue():
    request = API_ROOT + GET_NEXT
    response = http.request('GET', request)
    obj = None
    if response.status == 200:
        try:
            obj = json.loads(response.data.decode('utf-8'))
        except Exception as error:
            print("Error interpreting JSON response: %s" % error)
            logging.error("Error interpreting JSON response: %s" % error)
            return {}
    print('Got nextInQueue:\n>>status: %s\n>>object: %s' % (response.status, obj))
    logging.debug("Got next in queue; status: %s, object: %s" % (response.status, obj))
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
    logging.debug("opening output file")
    output_csv = open(request['filename'], 'w')
    print("printing to output file")
    logging.debug("printing to output file")
    output_csv.write(handle_facebook_id(facebook_id, options))
    print("completed writing output file")
    logging.debug("completed writing output file")
    output_csv.close()

def markRequestAsCompleted(request_id):
    request = API_ROOT + MARK_COMPLETE + str(request_id)
    response = http.request('GET', request)
    if response.status != 200:
        print("Error marking request as complete. Status: %s" % response.status)
        logging.error("Error marking request as complete. Status: %s" % response.status)

if __name__ == "__main__":
    print("Getting next unfinished request")
    logging.debug("Getting next unfinished request")
    next_request = getNextInQueue()
    print("Generating CSV based on request: %s" % next_request)
    logging.debug("Generating CSV based on request: %s" % next_request)
    generateCsvFromRequest(next_request)
    print("CSV Complete. Marking as complete")
    logging.debug("CSV Complete. Marking as complete")
    markRequestAsCompleted(next_request['id'])
    print("..Done!")
    logging.debug("..Done!")
