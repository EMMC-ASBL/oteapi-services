from pathlib import Path
from otelib import OTEClient
import dlite


thisdir = Path(__file__).resolve().parent
dlite.storage_path.append(thisdir)


client = OTEClient('python')  # for testing
#client = OTEClient('http://localhost:8080')  # replace with correct url
datafile = thisdir / 'data.xlsx'

dataresource = client.create_dataresource(
     downloadUrl=datafile.as_uri(),
     mediaType="application/vnd.dlite-xlsx",
     configuration={
         'excel_config':{
             'worksheet':'PhysicalParameters',
             "header_row": "1",
             "row_from": "2",
             "row_to":"4"
         },
         "metadata": "http://onto-ns.com/meta/0.1/PhysicalProperties" ,
         "storage_path": "file://"+"/datamodel.json" ,
         "label": "Physical_properties",
     }
)

generator = client.create_function(
    functionType="application/vnd.dlite-generate",
    configuration={
        "driver": "json",
        "location": f"{thisdir}/output.json",
        "options": "mode=w",
        "label": "Physical_properties",
    },
)

pipeline = dataresource >> generator

pipeline.get()
