import json


json_str = '[{\"class\":\"Recurring Pattern 1\",\"mode\":\"bbox\",\"data\":[[435,157],[584,285]]},{\"class\":\"Recurring Pattern 1\",\"mode\":\"bbox\",\"data\":[[193,87],[261,140]]}]'

json_dict = json.loads(json_str)

print (json_dict)