import json
import subprocess
import os
import time

def test_metadata_filters(metadata_filters, how):
    if os.path.exists("output.json"):
        os.remove("output.json")
    if how == "config":
        with open("config.json") as handle:
            config = json.load(handle)
        config["metadata_filters"] = metadata_filters
        config_name = str(time.time()) + ".json"
        with open(config_name, "w") as handle:
            json.dump(config, handle)
        command = ["plantcv-workflow.py", "--config", config_name]
        print("Testing metadata filters", metadata_filters, "with config file", config_name)
    elif how == "cli":
        match_values = []
        for field, values in metadata_filters.items():
            if isinstance(values, list):
                for value in values:
                    match_values.append(f"{field}:{value}")
            else:
                match_values.append(f"{field}:{values}")
        arguments = {
            "workflow":"vis_image_workflow.py",
            "match":",".join(match_values),
            "dir":"input_dir",
            "json":"output.json",
            "meta":"camera,id"
        }
        command = ["plantcv-workflow.py"]
        for key, value in arguments.items():
            command.append("--" + key)
            command.append(value)
        print("Testing metadata filters", metadata_filters, "with command:", " ".join(command))
    subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with open("output.json") as handle:
        output = json.load(handle)
    print("Metadata values used")
    for entity in output["entities"]:
        entity_metadata_values = {}
        for field in metadata_filters:
            entity_metadata_values[field] = entity["metadata"][field]["value"]
        print(entity_metadata_values)
    for meta_field, filter in metadata_filters.items():
        if isinstance(filter, list):
            for entity in output["entities"]:
                assert entity["metadata"][meta_field]["value"] in filter
        else:
            for entity in output["entities"]:
                assert entity["metadata"][meta_field]["value"] == filter

test_metadata_filters({"camera":"cam1","id":"p1"},"cli")
test_metadata_filters({"camera":"cam1","id":"p1"},"config")
test_metadata_filters({"camera":"cam2","id":["p2","p3"]},"cli")
test_metadata_filters({"camera":"cam2","id":["p2","p3"]},"config")
test_metadata_filters({"camera":["cam1","cam2"],"id":["p4"]},"cli")
test_metadata_filters({"camera":["cam1","cam2"],"id":["p4"]},"config")
test_metadata_filters({"camera":["cam1","cam2","cam3","cam4"],"id":"p3"},"cli")
test_metadata_filters({"camera":["cam1","cam2","cam3","cam4"],"id":"p3"},"config")
test_metadata_filters({"camera":["cam1","cam2","cam3","cam4"],"id":["p3","p4"]},"cli")
test_metadata_filters({"camera":["cam1","cam2","cam3","cam4"],"id":["p3","p4"]},"config")
test_metadata_filters({"camera":["cam1","cam2","cam3","cam4"],"id":["p1","p2","p3","p4"]},"cli")
test_metadata_filters({"camera":["cam1","cam2","cam3","cam4"],"id":["p1","p2","p3","p4"]},"config")
