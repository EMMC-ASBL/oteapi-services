from otelib import OTEClient
client = OTEClient('http://localhost:8080') #replace with correct url
url= "https://file-examples.com/wp-content/storage/2017/02/file_example_XLSX_10.xlsx"

dataresource=client.create_dataresource(
     downloadUrl=url,
     mediaType="application/vnd.dlite-xlsx",
     configuration={
         'worksheet':'Sheet1',  
            "header_row": "1",
            "row_from": "2",
            "row_to":"7",
        # 'excel_config':{
        #     'worksheet':'Sheet1',  
        #     "header_row": "1",
        #     "row_from": "2",
        #     "row_to":"7"
        # },
        "metadata": "http://onto-ns.com/meta/ontotrans/demo/0.1/elementprop" ,
        "storage_path": "file://"+"/dome_demo/models/PROV_element_properties.json" ,
        "label": "dome_chem_properties",
    }
)