from test_subj import pina
import json


def pretty_print(result):
    print(json.dumps(result, sort_keys=True, indent=4))


def recursive_items(dictionary):
    for key, value in dictionary.items():
        if type(value) is dict:
            yield (key, value)
            yield from recursive_items(value)
        else:
            yield (key, value)


dict_ptr = {
    "root_keys": {},
    "prev": [],
    "upholding_root": [],
    "upholding_key": "",
    "persist_key": {},
    "pk": "",
}


prev_scope = {}


def hasChildren(scope):
    return scope.get("children") is not None


class ScopeAnalyzer:
    def __init__(self):
        self.result = {}
        self.prev_scope = {}
        self.parent_tree_list = []

    def build_scope_maker(self, values):
        transformer = self.make_transformer(values)

        def make_scope(
            root, parent_keys, offset=None, value=None, level=0
        ):
            scope = {
                "root": root,
                "children": transformer(parent_keys),
                "level": level,
            }
            if offset:
                scope["offset"] = offset
            if value:
                scope["value"] = value

            return scope

        return make_scope

    def make_transformer(self, parent_values):
        def transform_each(enum_val):
            i, k = enum_val
            return {
                "root": k,
                "parent": self.parent_tree_list.copy(),
                "offset": i,
                "value": parent_values[k],
            }

        def transformer(v):
            return list(map(transform_each, enumerate(v)))

        return transformer

    # parent tree helper
    def reset_parent_tree(self, curr_parent_root):
        if len(self.parent_tree_list) > 0:
            self.parent_tree_list.clear()

        self.parent_tree_list.append(curr_parent_root)

    def append_new_parent_to_tree(self, scope, curr_parent_root):
        corrected_level = scope["level"]
        if corrected_level == 0:
            self.parent_tree_list = [self.parent_tree_list[0]]
        self.parent_tree_list.append(curr_parent_root)

    def determine_parent_tree_list(self, scope, curr_parent_root):

        if scope.get("root") is None:
            self.reset_parent_tree(curr_parent_root)
        else:
            self.append_new_parent_to_tree(scope, curr_parent_root)

    def analyze_scope(self, raw_dict, scope={}):
        encapsulated_scope = self.result

        for k in raw_dict.keys():
            v = raw_dict[k]
            make_scope = self.build_scope_maker(v)

            if isinstance(v, dict):
                input_scope = scope
                # print("END", ks[-1])

                self.determine_parent_tree_list(
                    scope, curr_parent_root=k
                )
                isLevelZeroRoot = scope.get("root") is None

                if isLevelZeroRoot:

                    input_scope = make_scope(
                        root=k, parent_keys=v.keys()
                    )
                    self.prev_scope = input_scope

                else:
                    # this code is for probing the parent root key
                    # that has ->
                    # nested dictionary with its(child) inside
                    def find_sub_parent():
                        count = None
                        for i, child in enumerate(
                            input_scope["children"]
                        ):
                            if child["root"] == k:
                                count = i
                        return count

                    # corrected_level = scope["level"]
                    # print(
                    #     "COCO",
                    #     k,
                    #     self.parent_tree_list,
                    #     corrected_level,
                    #     self.parent_tree_list[corrected_level - 1 :],
                    # )

                    has_children = find_sub_parent()
                    # we replace the sub_parent(children that contain nested
                    # dictionary) with its own tree of children
                    if has_children:
                        sub_parent = input_scope["children"].pop(
                            has_children
                        )
                        inner_scope = make_scope(
                            root=k,
                            offset=sub_parent["offset"],
                            level=input_scope["level"] + 1,
                            parent_keys=v.keys(),
                        )
                        input_scope["children"].append(inner_scope)
                        input_scope = inner_scope

                self.analyze_scope(v, input_scope)

            if len(list(scope.keys())) == 0 and isinstance(v, dict):
                encapsulated_scope[k] = self.prev_scope

        return encapsulated_scope


def analyze_scope(raw_dict):
    return ScopeAnalyzer().analyze_scope(raw_dict)


# analyze_scope = ScopeAnalyzer().analyze_scope
# analyze_scope(pina)


# ["children"]


class ScopePointer:
    def __init__(self):
        self.curr_ptr = ""
        self.prev_ptr = ""
        self.layers = {}
        self.max_layer = 0
        self.layer_prefix = "L_"

    def layer_key(self, num):
        return f"{self.layer_prefix}{num}"

    def push_to_layer(self, layer_num, payload):
        if self.max_layer < layer_num:
            self.max_layer
        prev_layer = self.fetch_from_layer(layer_num)
        key = self.layer_key(layer_num)

        each_key_layer = {
            "key_value": payload,
            "parent": self.prev_ptr,
        }
        if prev_layer is None:
            self.layers[key] = []

        self.layers[key].append(each_key_layer)

    def exist_in_layer(self, layer, needle):
        targeted_layer = self.fetch_from_layer(layer)
        if targeted_layer is None:
            return None

        def finder(layer_data):
            return layer_data["key_value"] == needle

        print("LL", self.fetch_from_layer(layer))
        llv = list(filter(finder, targeted_layer))
        if len(llv) > 0:
            return llv

    def fetch_from_layer(self, layer_num):
        return self.layers.get(self.layer_key(layer_num))

    def point_to_curr(self, current):
        self.prev_ptr = self.curr_ptr
        self.curr_ptr = current

    # def detect_layer_switch(curr_level):

    # if self.prev > self.curr_ptr :
    # pass
    # if self.prev


# def transform_layer(scope_root,ptr,transformer):
#   ptr.get()
# transformer()

search_index = "x"


def get_only(children, key):
    def mapper(child):
        root = child.get(key)
        if root is None:
            raise Exception("Invalid children type !!")
        return root

    return list(map(mapper, children))


Utility_VAR = ["setting", "volume", "gaming"]
VALID_UTILITY_TEST = {
    "setting": {"prun": 10, "ee": {"ss": 1}},
    "volume": {"param": "1", "BOBO": 1},
    "gaming": 100,
}


# result2 = analyze_scope(VALID_UTILITY_TEST)
# pretty_print(result)
# probing(result2, Utility_VAR)


# def convert_to_layers(all_scopes):
#     layer_result = {}
#     for scope_key in all_scopes.keys():
#         scope = all_scopes[scope_key]
#         ptr = ScopePointer()

#         def internal_call(scope):
#             children = scope.get("children")
#             if children:
#                 level = scope["level"]
#                 root = scope["root"]

#                 ptr.point_to_curr([scope["root"]])
#                 ptr.push_to_layer(level, scope["root"])

#                 if level > 0:
#                     # scope_ptr["prev_ptr"] =
#                     # ptr.point_to_prev
#                     print(f"IN LEVEL {level} in scope {root}")

#                 global current_level
#                 current_level = scope["level"]
#                 # for child in children:
#                 #     internal_call(child)
#                 print("EDX", scope["root"], scope)
#             else:
#                 # layer_result[]
#                 ptr.point_to_curr(scope["parent"])
#                 lv = scope.get("level") or 1
#                 ptr.push_to_layer(lv, scope["root"])

#         internal_call(scope)

#         layer_result[scope_key] = ptr.layers
#     return layer_result
