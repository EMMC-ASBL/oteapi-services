from otelib import OTEClient
import dlite

dlite.storage_path.append()
client = OTEClient('http://localhost:8080') #replace with correct url
url= "file://"+"/data.xlsx"

dataresource=client.create_dataresource(
     downloadUrl=url,
     mediaType="application/vnd.dlite-xlsx",
     configuration={
         'worksheet':'PhysicalParameters',  
            "header_row": "1",
            "row_from": "2",
            "row_to":"4",
        # 'excel_config':{
        #     'worksheet':'Sheet1',  
        #     "header_row": "1",
        #     "row_from": "2",
        #     "row_to":"7"
        # },
        "metadata": "http://onto-ns.com/meta/0.1/PhysicalProperties" ,
        "storage_path": "file://"+"/datamodel.json" ,
        "label": "Physical_properties",
    }
)