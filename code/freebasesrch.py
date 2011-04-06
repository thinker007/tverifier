import freebase
import pprint
import sys

query = {
            "id": '/en/les_paul',
            "/type/reflect/any_master": [{
              "id" : None,
            }]
        }
results=freebase.mqlread(query)
pprint.PrettyPrinter(indent=4).pprint(results)
images=dict()
for thing in results["/type/reflect/any_master"]:
	print thing

