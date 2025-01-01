
def to_entity(data: dict):
    data["id"]= str(data.get("_id"))
    data.pop("_id", None)
    return data

def to_list_entity(list_data: list[dict]):
    return [to_entity(data) for data in list_data]