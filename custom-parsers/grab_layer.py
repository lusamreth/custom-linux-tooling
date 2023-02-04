from syn_decoder import ParserPipeline
from syntax_decoder import generate_token, multiCommandParser
from test2 import pretty_print
from tokenizer import tokenize_array, variable_lookup
import traversal

result = traversal.analyze_scope(
    {
        "a": {
            "b": 1,
            "e": 2,
            "ad": {"param": 100, "deza": {"p": {"bru": 1}}},
            "ac": "%b",
            "param": 1,
            "adx": {"param": 100, "dez": {"p": "$[1,2,3]"}},
            "x2": {"b": 1},
            "acx": 1,
        },
        "h": 1,
        "c": {"x": "1"},
        "dezo": {"p": 1},
    }
)


def layer_converter(scopes):
    for scope in scopes:
        traversal.pretty_print(scope)


# layer_converter.

Variable_RULE = {1: ["param", "bram"], 2: ["same"]}

for layer in Variable_RULE:
    rule = Variable_RULE[layer]

PARAM_PRIMITIVE = ["param", "keybind", "cmd"]

VALID_UTILITY_TEST = {
    "setting": {
        "bbb": {"ssjsjsj": "ss %sukaka"},
        "prun": "%sukaka",
        "prun31": {"param": 100, "cmd": 10, "keybind": 10},
        "ee": {"ss": 1},
        "prun1": {"param": 100, "cmd": 10, "keybind": "ass $[1,2]"},
        "prun2": "%sukaka",
    },
    "sukaka": 1000,
    # "saal": {
    #     "prne": 100,
    #     "param": "1 %prne $[fucking itch %prne,2 ] %sukaka",
    #     "keybind": 1,
    #     "cmd": 60,
    # },
    "volume": {
        "prne": 100,
        "param": "1 %prne $[fucking itch %prne,2 ] %sukaka",
        "keybind": 1,
        "cmd": 10,
        "xmddd": {
            "hahah": "babab %prne",
            "hahah4": {
                "bruhak": 1000,
                "hahah": "babab %prne",
                "BAP": {
                    "BRU": 10,
                    "param": "1 %prne $[fucking itch %prne,2 ] %sukaka",
                    "keybind": 1,
                    "cmd": 10,
                },
            },
            "hahah3": {
                "bruhak": 1000,
                "hahah": "babab %prne",
                "BAP": {
                    "BRU": 10,
                    "param": "1 %prne $[fucking itch %prne,2 ] %sukaka",
                    "keybind": 1,
                    "cmd": 10,
                },
            },
            "hahah2": {
                "bruhak": 1000,
                "hahah": "babab %prne",
                "BAP": {
                    "BRU": 10,
                    "param": "1 %prne $[fucking itch %prne,2 ] %sukaka",
                    "keybind": 1,
                    "cmd": 10,
                },
            },
        }
        # "prne": 000,
    },
    "gaming": 100,
}

SCREEN_RULE = {
    "REQ": PARAM_PRIMITIVE,
    "OPT": [],
    "LV": 1,
    "PARENT": "SETTINGS",
}

PARAM_PRIMITIVE = ["param", "keybind", "cmd"]
VOLUME_RULE = {
    "REQ": PARAM_PRIMITIVE,
    "OPT": [],
    "LV": 1,
    # "PARENT": "settings",
}


Groun = {"screen": SCREEN_RULE, "volume": VOLUME_RULE}


def checking_rule(scope, children, rules, ignore_level=-1):

    level = scope["level"]
    root = scope["root"]

    rule = rules.get(root)

    if rule:
        roots = list(map(lambda child: child["root"], children))
        for req_variable in rule["REQ"]:
            rule_level = rule.get("LV")
            if rule_level:
                if rule_level == ignore_level:
                    return
                if rule_level != level:
                    print(
                        f"This variables are not supported in level {level}"
                    )

            optionals = rule.get("OPT")
            if roots.count(req_variable) == 0:
                if optionals and optionals.count(req_variable) > 0:
                    continue
                err = f"This key {req_variable} is a requirement"
                raise Exception(err)


def check_variable(all_scopes, rules):
    for scope_key in all_scopes.keys():
        scope = all_scopes[scope_key]
        # ptr = ScopePointer()

        def internal_call(scope):
            children = scope.get("children")
            if children:
                # level = scope["level"]
                # root = scope["root"]
                checking_rule(scope, children, rules)
                for child in children:
                    internal_call(child)

        internal_call(scope)


def variable_consumer(all_scopes, original_dict):

    result = {}
    state = {}

    for scope_key in all_scopes.keys():
        scope = all_scopes[scope_key]
        # ptr = ScopePointer()
        print("SCOPA", scope_key)

        def internal_call(scope, interrupt={}):
            children = scope.get("children")
            variable_mark = {}

            # print(scope["level"], scope)
            if children:
                bundle_map = {}
                map_index = {}
                # ppl = ParserPipeline()

                def bundle(child, i):
                    k = str(child["root"])
                    v = child.get("value")
                    # the value is none here means that it contain
                    # dictionary(children)
                    if v is None:
                        # recurse until it found children
                        internal_call(
                            child,
                            interrupt={
                                "prev": interrupt,
                                "parent_key": k,
                            },
                        )
                        return

                    ppl = ParserPipeline(bundle_map)
                    # ppl.get_hints(v)
                    fin = ppl.pipeline(str(v))
                    global marked

                    if fin is None:
                        if variable_mark.get(k) is None:
                            variable_mark[k] = 1
                        bundle_map[k] = v
                    else:
                        bundle_map[k] = fin
                        if variable_mark.get(k) == 1:
                            variable_mark[k] = 0

                    map_index[k] = i

                for i, child in enumerate(children):
                    bundle(child, i)

                # print("VVl", variable_mark)
                prober = {"hints": None, "lookup_accumulator": {}}

                def traverse_lookup_variable(marker, lookup_scope):
                    st = bundle_map[marker]
                    child_idx = map_index[marker]
                    # children.find()
                    child_parent = children[child_idx]["parent"]

                    if prober.get("hints") is None:
                        ppl = ParserPipeline(lookup_scope)
                        ppl.get_hints(st)
                        prober["hints"] = ppl.hints

                    hints = prober["hints"]
                    # if probe:

                    for hint in hints:
                        probe = lookup_scope.get(hint[1:])
                        if probe:
                            prober["lookup_accumulator"][
                                hint[1:]
                            ] = probe
                            hints.remove(hint)

                            prober["hints"] = hints

                    if len(hints) != 0:
                        if len(child_parent) > 0:
                            nxt_key = child_parent.pop(0)
                            next = original_dict[nxt_key]
                            traverse_lookup_variable(
                                marker, lookup_scope=next
                            )
                        else:
                            not_found_vars = " ".join(
                                [str(elem) for elem in hints]
                            )
                            raise ValueError(
                                f"The variable {not_found_vars} in '{st}' is not precence in the scope"
                            )
                    else:
                        ppl = ParserPipeline(
                            prober["lookup_accumulator"]
                        )
                        llp = ppl.pipeline(str(st))
                        if llp is None:
                            raise Exception("Undefined Behavoirs")
                        variable_mark[marker] = llp

                # processing unmakred / not yet replaced variable
                for mk in variable_mark.keys():
                    marked = variable_mark[mk]
                    # ParserPipeline()
                    if marked == 1:
                        traverse_lookup_variable(
                            mk, lookup_scope=original_dict
                        )
                        bundle_map[mk] = variable_mark[mk]

                def parse_cmd(binder, interrupt):
                    mm = multiCommandParser(
                        bundle_map,
                        keywords=PARAM_PRIMITIVE,
                        pmc_bind=binder,
                    )
                    _contain_cmd_template = len(mm) != 0
                    if interrupt:
                        # print("S__+.", interrupt, bundle_map, scope)
                        prev_interrupt = interrupt["prev"]

                        if prev_interrupt:
                            pk = prev_interrupt["parent_key"]
                            ptr = {}
                            # pk = interrupt["parent_key"]

                            def nest_through(inner_interrupt):
                                prev = inner_interrupt.get("prev")
                                if prev:
                                    print(
                                        "__<A",
                                        inner_interrupt[
                                            "parent_key"
                                        ],
                                        prev["prev"],
                                    )
                                    if prev["prev"] == {}:
                                        return inner_interrupt[
                                            "parent_key"
                                        ]

                                    nest_through(prev)

                            llb = nest_through(prev_interrupt)
                            print("KAh", llb)
                            pkm = interrupt["parent_key"]
                            print(
                                "STA___>",
                                state,
                                prev_interrupt,
                                pkm,
                                bundle_map,
                            )
                            # state[pkm]["bruh"] = 100
                            state[interrupt["parent_key"]] = {
                                "parent": pk
                            }
                            if _contain_cmd_template:
                                state[interrupt["parent_key"]][
                                    "parsed"
                                ] = mm
                            else:
                                state[interrupt["parent_key"]][
                                    "parsed"
                                ] = bundle_map

                        else:
                            interrupt = {
                                **bundle_map,
                                "props": interrupt,
                                **state,
                                # "prime": state,
                            }

                            if not _contain_cmd_template:
                                return interrupt
                    return mm

                parsed = parse_cmd(bundle_map, interrupt)
                if result.get(scope_key) is None:
                    result[scope_key] = {}

                # if len(parsed) > 0 :
                #     result[scope_key][""]

                result[scope_key][scope["root"]] = parsed
                # print("MNMA", parse_cmd(bundle_map), bundle_map)

            else:
                print("NON LAYER", scope)

        internal_call(scope)
    return result


# ll = traversal.convert_to_layers(result)
# traversal.pretty_print(ll)

scopes = traversal.analyze_scope(VALID_UTILITY_TEST)
# check_variable(scopes, Groun)
rr = variable_consumer(scopes, VALID_UTILITY_TEST)

print("RESRES", rr)
pretty_print(rr)
# traversal.pretty_print(scopes)
# scopes = traversal.analyze_scope
