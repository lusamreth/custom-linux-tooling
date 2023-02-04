from math import e
import json
from test_subj import pina


def pretty_print(result):
    print(json.dumps(result, sort_keys=True, indent=4))


def get_items(test_dict, lvl):

    # querying for lowest level
    if lvl == 0:
        yield from (
            (key, val)
            for key, val in test_dict.items()
            if not isinstance(val, dict)
        )
    else:

        # recur for inner dictionaries
        yield from (
            (key1, val1)
            for val in test_dict.values()
            if isinstance(val, dict)
            for key1, val1 in get_items(val, lvl - 1)
        )


# e = get_items(pina, 2)
# print(dict(e))
def recursive_items(dictionary):
    for key, value in dictionary.items():
        if type(value) is dict:
            yield (key, value)
            yield from recursive_items(value)
        else:
            yield (key, value)


a = {"a": {1: {1: 2, 3: 4}, 2: {5: 6}}, "b": 100}


dict_ptr = {
    "root_keys": {},
    "prev": [],
    "upholding_root": [],
    "upholding_key": "",
    "persist_key": {},
    "pk": "",
}

result = {}

for key, value in recursive_items(pina):
    stop_code = False
    if isinstance(value, dict):
        prev_keys = dict_ptr["prev"]
        # dict_ptr["prev"] = prev_keys
        if prev_keys.count(key) > 0:
            # we found the inner nested value

            root_key = dict_ptr["prev_key"]

            # this block of code allow the inner dict to know its parent
            main_val = result.get(root_key)
            mwwl = result.get(dict_ptr["upholding_key"])
            if mwwl is not None:
                if len(list(mwwl.get("children").keys())) > 0:
                    result[root_key] = 1
                    print(
                        "!THIS IS CHILDREN of",
                        key,
                        root_key,
                        dict_ptr["persist_key"]
                        # mwwl,
                        # mwwl["children"].get(root_key),
                    )
                    inner_child = result[dict_ptr["upholding_key"]][
                        "children"
                    ]

                    # if (
                    #     inner_child.get("node") is not None
                    #     and len(inner_child["node"]) > 0
                    # ):
                    #     result[dict_ptr["upholding_key"]][
                    #         "children"
                    #     ]["node"].append(key)
                    # else:
                    persisted = dict_ptr["persist_key"]
                    prev_key = dict_ptr["pk"]
                    print(
                        "PERSIS KEY",
                        dict_ptr["persist_key"],
                        key,
                        value,
                        dict_ptr["pk"],
                    )
                    kkb = dict_ptr["persist_key"].get(key)
                    print("BRACK")
                    if persisted.get(prev_key) is not None:
                        if (
                            persisted[prev_key]["keys"].count(key)
                            > 0
                        ):
                            print("the key is included !")
                            pass
                    # persist only append the first dictionary found in nested
                    if kkb is not None:
                        kkb["count"] += 1
                        dict_ptr["persist_key"][key] = kkb
                        count = kkb["count"]
                        dict_ptr["persist_key"][
                            f"{key}{count}"
                        ] = list(value.keys())
                        print("BRACK")
                    else:
                        dict_ptr["persist_key"][key] = {
                            "count": 0,
                            "keys": list(value.keys()),
                            "prev": prev_key,
                        }
                        ding = dict_ptr["persist_key"].get(prev_key)
                        if ding:
                            if ding["count"] > 0:
                                c = ding["count"]
                                print(
                                    "PRUM",
                                    dict_ptr["persist_key"].get(
                                        f"{prev_key}{c}"
                                    ),
                                )

                    dict_ptr["pk"] = root_key

                    # if (
                    #     dict_ptr["persist_key"][root_key].count(key)
                    #     == 0
                    # ):
                    #     dict_ptr["persist_key"][key] = {
                    #         "keys": list(value.keys())
                    #     }
                    #     result[dict_ptr["upholding_key"]][
                    #         "children"
                    #     ][root_key] = {
                    #         "keys": mwwl["children"].get(root_key),
                    #         "node": {
                    #             key: list(value.keys()),
                    #             "parente": root_key,
                    #         },
                    #     }
                    # else:

                    #     # result[dict_ptr["upholding_key"]][
                    #     #     "children"][root_key]
                    #     # persisted[dict_ptr["pk"]].remove(key)
                    #     # persisted
                    #     print("BRUH")

                    stop_code = True
                    # dict_ptr["upholding_root"].remove(key)

                else:
                    if main_val is None:
                        print("HOLDING", dict_ptr["upholding_key"])
                        result[root_key] = {
                            "keys": prev_keys,
                            "children": {},
                            "main": dict_ptr["upholding_key"],
                        }
                    else:
                        print("MAINN WALLL", main_val, key)
            else:

                print("MAINN WALLL", main_val, key)
                print(dict_ptr["upholding_key"])
                result[root_key] = {
                    "keys": prev_keys,
                    "children": {},
                    "main": dict_ptr["upholding_key"],
                }
            # "lookup":1,else:
            # if main_val.get("children") is None:

            #     result[root_key] = {
            #         "keys": prev_keys,
            #         "children": {},
            #         "main": dict_ptr["upholding_key"],
            #     }
            #     result[root_key]["children"] = {
            #         key: prev_keys,
            #     }
        else:
            # this is when we know we left a block of scope
            if dict_ptr["upholding_root"].count(key) > 0:
                print(
                    "THIS IS CHILDREN of =",
                    dict_ptr["upholding_key"],
                )
                # result["upholding_key"]

                dict_ptr["upholding_root"].remove(key)
                result[dict_ptr["upholding_key"]]["children"][
                    key
                ] = value.keys()
            # else ,:
        # print("UPL", result[dict_ptr["upholding_key"]])

        holding_key = dict_ptr["upholding_key"]
        holding_root = dict_ptr["upholding_root"]

        if holding_key != "" and len(holding_root) > 0:
            if stop_code:
                print("STOP")
                result[holding_key]["children"][key] = {
                    "keys": list(value.keys()),
                    "parent": dict_ptr["prev_key"],
                }

            else:
                result[holding_key]["children"][key] = list(
                    value.keys()
                )

        founder = dict_ptr["root_keys"].get(key)
        if key == "bra":
            print(
                "FOUND BRAcla",
                key,
                dict_ptr,
            )
            # pretty_print(dict_ptr)
        # if founder is not None:
        #     print("CONSOL", founder.count(key))
        dict_ptr["prev"] = list(value.keys())
        dict_ptr["root_keys"][key] = value.keys()

        if len(dict_ptr["upholding_root"]) == 0:
            dict_ptr["upholding_root"] = list(value.keys())
            dict_ptr["upholding_key"] = key

        dict_ptr["prev_key"] = key
        # print("ROOT:", key, dict_ptr)
        continue

    if dict_ptr["upholding_root"].count(key) > 0:
        print("THIS IS CHILDREN OF", dict_ptr["upholding_key"])
        result["root"] = dict_ptr["upholding_key"]
        dict_ptr["upholding_root"].remove(key)

    # print(key, value, dict_ptr["upholding_root"])
# print("REUSLTj", result["app"])
print(dict_ptr["persist_key"])
