from pathlib import Path

import dlite
from otelib import OTEClient

thisdir = Path(__file__).resolve().parent
dlite.storage_path.append(thisdir)


# client = OTEClient('python')  # for testing
client = OTEClient("http://localhost:8080")  # replace with correct url

dataresource = client.create_dataresource(
    downloadUrl="https://github.com/EMMC-ASBL/oteapi-services/blob/example-for-testing/examples/example1/data.xlsx?raw=true",
    mediaType="application/vnd.dlite-xlsx",
    configuration={
        "excel_config": {
            "worksheet": "PhysicalParameters",
            "header_row": "1",
            "row_from": "2",
            "row_to": "4",
        },
        "metadata": "http://onto-ns.com/meta/0.1/PhysicalProperties",
        "storage_path": "https://github.com/EMMC-ASBL/oteapi-services/blob/example-for-testing/examples/example1/datamodel.json?raw=true",
        "label": "Physical_properties",
    },
)

generator = client.create_function(
    functionType="application/vnd.dlite-generate",
    configuration={
        "driver": "json",
        "location": "/app/examples/example1/output.json",  # this stores in the volumes (modify as required)
        "options": "mode=w",
        "label": "Physical_properties",
    },
)

pipeline = dataresource >> generator

pipeline.get()
