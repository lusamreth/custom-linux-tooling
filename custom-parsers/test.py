import re
import syntax_decoder
import dunst
import tomli as toml

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


def apply_reg_escape(txt):
    res = ""
    for char in txt:
        res += f"\\{char}"
    return res


testmsg = "$[1,2,3] $[3,4,5] [sjdaskd,asdkasdask,]"
res = re.finditer("\$\[(.+?)\]", testmsg)
for r in res:
    print("SS", r.group(), r.groups())
    print("SS", r.group())
    print("SS", r.group())
    for group in r.groups():
        items = group.split(",")
        print(group)
        print(items)
    print(r.start(), r.end(), r.string)

print(res)
print(apply_reg_escape("$["))


def fn(matches):
    print(matches)


new = re.subn("\$\[(.+?)\]", fn, testmsg)
print(new)


write_buffer = []

sample = {
    "msg": "%prne app ",
    "param": "10 $[1,2,3,4,5,6]",
    "prne": "a",
    "bind": "shift",
}

assembled = syntax_decoder.multiCommandParser(sample, "cmo")


class StructDecoder:
    def __init__(self):
        self.token_buffer = []

    def dispatch(self, dispatch, raw):
        hpc = {
            "msg": raw["msg"],
            "struct": {"cmd": dispatch, "param": raw["param"]},
        }
        key = raw.get("bind")

        if key:
            hpc["bind"] = key

        self.token_buffer.append(hpc)

    def tokens(self):
        return self.token_buffer


def hasDict(values):
    f = list(filter(lambda v: isinstance(v, dict), values))
    print(f)
    return len(f) > 0


def process_toml_cfg(config_section):
    std = StructDecoder()
    for dispatch_cmd in config_section:
        val = config_section[dispatch_cmd]
        if not isinstance(val, dict):
            continue

        # def dispatch_cmd():

        def dispatcher(inner_val, dispatch_cfg_key):
            cmds = syntax_decoder.multiCommandParser(
                inner_val, dispatch_cfg_key
            )

            if len(cmds) > 0:
                for cmd in cmds:
                    std.dispatch(dispatch_cfg_key, cmd)
            else:
                std.dispatch(dispatch_cfg_key, inner_val)

        # returnHasDict(val.values(), [])
        if hasDict(val.values()) > 0:
            # accumulateKeyword(val)

            for dispatch_cfg_key in val.keys():

                inner_val = val[dispatch_cfg_key]
                dispatcher(inner_val, dispatch_cfg_key)
        else:

            dispatcher(val, dispatch_cmd)
    return std.tokens()


test_sect = {
    "dispatch": {"param": 1, "msg": "xd", "bind": "s"},
    "bruh": {"param": 1, "msg": "xd", "bind": "s"},
}


# with open("hypr_ins.toml", "rb") as f:
#     tml = toml.load(f)

#     for supported_key in CURRENT_SUPPORTED_KEYS:
#         Field = tml.get(supported_key)
#         if Field:
#             res = process_toml_cfg(Field)
#     # else:
#     #     dispatch(*dispatch_arg(dispatch_cmd, val))

#     # dispatch(f.msg,f.)

#     print(tml)
for hpc in process_toml_cfg(test_sect):
    k = keybind_gen(hpc)
    write_buffer.append(f"{k}\n")

with open("hmc_test.conf", "w+") as f:
    print("writing cfg to file", write_buffer)
    f.writelines(write_buffer)

# for r in res :
# re.findall
