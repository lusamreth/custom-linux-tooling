import controllers
import subprocess
import tomli as toml
import dunst
import re

cli = controllers.cli

GlobalHPC = []


def dispatch(msg, cmd_struct, key):
    hpc = {
        "msg": msg,
        "struct": {"cmd": cmd_struct[0], "param": cmd_struct[1]},
    }
    if key:
        hpc["bind"] = key

    GlobalHPC.append(hpc)


def dispatch_arg(dispatch, raw):
    p = raw["param"]
    msg = raw["msg"]
    bind = raw["bind"]

    print(bind)
    return [msg, dispatch, p]


def apply_reg_escape(txt):
    res = ""
    for char in txt:
        res += f"\\{char}"
    return res


class SubstitutionParser:
    def __init__(
        self, text, var_identifier, list_indentifier, key_arg
    ):
        self.txt = text
        self.key_arg = key_arg
        self.list_indentifier = list_indentifier
        self.var_identifier = var_identifier

    def sub_variables(self):
        p = self.txt
        # replacing internal text
        self.txt = p.replace(self.var_identifier, self.key_arg)
        # return p
        # self.txt = res

    def new_parse_array(self):
        p = self.txt

        start_str = apply_reg_escape(self.list_indentifier[0])
        end_str = apply_reg_escape(self.list_indentifier[1])

        matches = re.finditer(f"{start_str}(.+?){end_str}", p)
        result = []
        for matched in matches:
            res = {}
            for group in matched.groups():
                res["value"] = group.split(",")
            res["indices"] = (matched.start(), matched.end())
            res["pattern"] = matched.group()

            result.append(res)
        ###
        # { value, start, end }
        ###
        return result

    def parse_array(self):
        p = self.txt
        start_str = self.list_indentifier[0]
        end_str = self.list_indentifier[1]

        s = p.find(start_str)
        e = p.find(end_str)

        if s == -1:
            return

        if e == -1:
            raise Exception(
                "Bad substitution !! need closing bracket !"
            )

        ssl = p[s + len(start_str) : e]
        return ssl.split(","), s, e
        # print("SSL", ssl)


# finish the parity checker part!!!
def check_parity(split_tree):
    tree_len = len(split_tree)
    if tree_len > 1:
        # take first element and start comparing
        needle = len(split_tree[0]["value"])
        for k in split_tree:
            if len(k["value"]) < needle:
                raise Exception("Imparity found in the config")


def split_tree_processor(split_tree):
    output = []

    def filling_value(field, value, repl):
        if len(output) == 0:
            for i, field_val in enumerate(value):
                res = {}
                res[field] = repl(field_val)
                output.append(res)
        else:
            for i, field_val in enumerate(value):
                f = output[i].get(field)
                output[i][field] = repl(field_val, f)

    for i, tree in enumerate(split_tree):

        field = tree["field"]
        raw_str = tree["raw_string"]
        matches = tree["matches"]

        for match in matches:
            value = match["value"]
            # _ = match["indices"]
            pattern = match["pattern"]

            def repl(val, stt=raw_str):
                stt = stt or raw_str
                return re.sub(re.escape(pattern), val, stt)

            filling_value(field, value, repl)
        # filling in all the value and field
        # lamda raw_string,indices : substring()
    return output


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


# mcp (raw,key_arg) -> [{struct0,struct1,...,structn}]


CURRENT_SUPPORTED_KEYS = [
    "group",
    "layout",
    "app",
    "workspace",
    "utility",
]


def hasDict(values):
    f = list(filter(lambda v: isinstance(v, dict), values))
    print(f)
    return len(f) > 0


# b = returnHasDict(
#     polo.values(), lambda x: accumulateKeyword(list(x))
# )


def process_toml_cfg(config_section):
    # print("PROCESSING TOML CFG")
    for dispatch_cmd in config_section:
        val = config_section[dispatch_cmd]
        if not isinstance(val, dict):
            continue

        # def dispatch_cmd():

        def dispatcher(inner_val, dispatch_cfg_key):
            # cmds = multiCommandParser(inner_val, dispatch_cfg_key)
            cmds = []
            for cmd in cmds:
                dispatch(cmd[0], (dispatch_cmd, cmd[1]), cmd[2])

        # returnHasDict(val.values(), [])
        if hasDict(val.values()) > 0:
            # accumulateKeyword(val)

            for dispatch_cfg_key in val.keys():

                inner_val = val[dispatch_cfg_key]
                dispatcher(inner_val, dispatch_cfg_key)
        else:

            dispatcher(val, dispatch_cmd)


# - hpc_construct = [{"msg": "dwindle group activated!", "cmd": {}}]
# - need to add many more feature like dispatch function awareness
# - variable referencing , reliable multi-command generation from
# array($[...]) with full parity check !!
# - support controller agnostic command config
# - support multi-messaging state on one command
# - generate to different config file with the use of different
# resolvers (sway, hyprland, alacritty,...)

with open("hypr_ins.toml", "rb") as f:
    tml = toml.load(f)

    for supported_key in CURRENT_SUPPORTED_KEYS:
        Field = tml.get(supported_key)
        if Field:
            process_toml_cfg(Field)
    # else:
    #     dispatch(*dispatch_arg(dispatch_cmd, val))

    print("HP", GlobalHPC)
    for hp in GlobalHPC:
        print(hp["struct"])
    # dispatch(f.msg,f.)

    print(tml)


# generate python script
def keybind_gen(cfg):
    bind = cfg.get("bind")
    if bind is None:
        return

    msg = cfg["msg"]
    struct = cfg["struct"]
    dispatch = struct["cmd"]

    param = struct.get("param") or ""
    cmd = dunst.create_notification_cmd(
        f"exec,hyprctl dispatch {dispatch} {param}",
        f"'{msg}'",
        t=1400,
    )
    kb = f"bind={bind},{cmd}"
    return kb


def code_gen(cfg):
    hpc = "hyprctl"
    msg = cfg["msg"]

    struct = cfg["struct"]
    dispatch = struct["cmd"]

    param = struct.get("param") or ""
    dunst.notifymsg("Hyprland", msg, 1400)
    return f"{hpc} {dispatch} {param}"


# def open_application(cfg):
# return f"{cfg["app"]}"
write_buffer = []


sample = {
    "msg": "%prne app ",
    "param": "10 $[1,2,3,4,5,6]",
    "prne": "a",
    "bind": "shift",
}
