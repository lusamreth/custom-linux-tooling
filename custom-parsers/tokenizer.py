import re
import tomli as toml

# Program
"""
Program
; StatementList
; VariableNode(referencing , substitute)
; ArrayNode
Statement
;

"""

# necessary to produce variable lookup
def variable_lookup(cfg_line, var_id="%"):
    needle_boxes = {}
    all_references = re.finditer(f"\\{var_id}(\\w+)", cfg_line)
    for refs in all_references:
        needle = refs.group()
        indices = refs.span()
        needle_box = needle_boxes.get(needle)

        if needle_box is not None:
            needle_box.append(indices)
            needle_boxes[needle] = needle_box
        else:
            needle_boxes[needle] = [indices]

    return needle_boxes


# class NeedleError
# subsitute the variable
def sub_needle_box(needle_box, stb, cfg_line):
    result = cfg_line
    for k in needle_box.keys():

        sub_val = stb.get(k[1:])
        print("REFYY", needle_box, cfg_line, k, stb.get(k[1:]))
        if sub_val is None:
            return None

        new_value = re.sub(f"\\{k}", str(sub_val), result)

        result = new_value
    return result


# test code #
# sub_table = {"a": 10, "b": 20}
# cfg_line_test = "apple bee %a dine  %a %a %b %a"
# tb = variable_lookup(cfg_line_test)
# sub_needle_box(tb, sub_table, cfg_line_test)
# end test #


def apply_reg_escape(txt):
    return re.escape(txt)


def tokenize_array(text, list_identifier):
    text = str(text)
    start_str = apply_reg_escape(list_identifier[0])
    end_str = apply_reg_escape(list_identifier[1])

    matches = re.finditer(f"{start_str}(.+?){end_str}", text)
    result = []
    for matched in matches:
        res = {}
        for group in matched.groups():
            res["value"] = group.split(",")

        res["indices"] = (matched.start(), matched.end())
        res["pattern"] = matched.group()

        result.append(res)

    """
    # { value, indices, pattern }
    """
    return result


NativeKeywords = ["param", "msg", "bind"]


def buildKwAccumulator(native, initial):
    def accumulateKeyword(kw, value):
        if native.count(kw) > 0:
            return
        else:
            existed = initial.get(kw)
            if existed:
                raise Exception("Duplicated variable")
            initial[kw] = value

    return accumulateKeyword


def traveresDictTree(values, deep_callback, ascend_callback):

    if not isinstance(values, dict):
        return
    # print("VALA", values, values.keys())
    for k in values.keys():

        v = values[k]
        if not isinstance(v, dict):

            ascend_callback(k, v)

            continue
        deep_callback(k, v)
        traveresDictTree(v, deep_callback, ascend_callback)
        # print("valu", values)


pa = []
polo = {
    "aaa": {"ano": {"b": 1, "c": 1, "d": {"e": 1}, "bc": {"3": 1}}},
    "bean": {"apex": "%1"},
    "aha": 1,
}

pina = {
    "sss": 10,
    "utility": {
        "bruh": 1,
        "sss": 10,
        "lookup": {"param": 1, "msg": "bar"},
    },
    "app": {
        "setting": 1,
        "telegram": {
            "param": 1,
            "bind": 2,
            "bra": {"param": 1, "bind": 2},
        },
        "brave": {"param": 3, "bind": 4},
    },
    "pro": 1,
}

variable_scope_cache = {}
accm = {}

accumulateKeyword = buildKwAccumulator(NativeKeywords, accm)

print("APAPA", pa)
print("AAcca", accm)


# state_stepper = {"level": 0}


class TreePointer:
    def __init__(self):
        self.level = 0
        self.accumulate = {}
        self.buffer = []
        self.stop_code = ""

    def step(self, k, v):
        if k == self.stop_code:
            self.accumulate = {"root": k, "level": 0}
            self.buffer.append(self.accumulate)
        else:
            self.accumulate = {"root": k, "level": self.level}

    def enter_branch(self):
        print("AA-", self.accumulate)
        NotImplemented

    def set_stop_code(self, code):
        self.stop_code = code
        NotImplemented


Treept = TreePointer()


def inc_state_count(k, v):
    # expect V value is a dictionary
    # state_stepper.buf
    stepper_keys = list(v.keys())
    last_step = stepper_keys[-1]
    Treept.step(k, v)
    print(
        "from a1",
        k,
        last_step,
    )


def process_state_count(k, v):
    # state_stepper.appendBuffer(k, v)
    print(
        "from a2",
        k,
        v,
    )


traveresDictTree(pina, inc_state_count, process_state_count)

result = []
# print("buf", state_stepper.buffer)


def ascd(k, v):

    p = tokenize_array(v, ["$[", "]"])
    # hyprland_ctl.multiCommandParser(v, k)
    print("PE", p, variable_scope_cache)

    if accm.get(k) is None:
        print("KK", accm, k)
        accumulateKeyword(k, v)

    nb = variable_lookup(str(v))
    # if len(nb.keys()) > 0:

    #     sttr = sub_needle_box(nb, variable_scope_cache, v)
    #     print("substr", sttr, nb)
    # else:
    #     variable_scope_cache[k] = v

    print("ASCENDING", k, accm)
