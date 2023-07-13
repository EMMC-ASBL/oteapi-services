from pathlib import Path
from otelib import OTEClient
import dlite


thisdir = Path(__file__).resolve().parent
dlite.storage_path.append(thisdir)


# client = OTEClient('python')  # for testing
client = OTEClient("http://localhost:8080")  # replace with correct url
url = f"data.xlsx"

dataresource = client.create_dataresource(
    downloadUrl=Path("/app/examples/example1/data.xlsx").as_uri(),
    mediaType="application/vnd.dlite-xlsx",
    configuration={
        "excel_config": {
            "worksheet": "PhysicalParameters",
            "header_row": "1",
            "row_from": "2",
            "row_to": "4",
        },
        "metadata": "http://onto-ns.com/meta/0.1/PhysicalProperties",
        "storage_path": Path("/app/examples/example1/datamodel.json").as_uri(),
        "label": "Physical_properties",
    },
)

generator = client.create_function(
    functionType="application/vnd.dlite-generate",
    configuration={
        "driver": "json",
        "location": "/app/examples/example1/output.json",
        "options": "mode=w",
        "label": "Physical_properties",
    },
)

pipeline = dataresource >> generator

pipeline.get()
