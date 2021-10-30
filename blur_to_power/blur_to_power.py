import json

def blur_to_power(blur: int) -> float:
    with open("./blur_to_power/blur5.json") as f:
        btp = json.load(f)

    blur = min(max([int(i) for i in btp]), blur)
    return btp[str(blur)]