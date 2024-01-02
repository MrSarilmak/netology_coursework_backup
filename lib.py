import json


def json_save(data: dict | list, file_name: str) -> None:
    with open(file_name, "w") as file_io:
        json.dump(data, file_io, indent=2)
