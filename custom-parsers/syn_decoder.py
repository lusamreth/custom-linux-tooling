import tokenizer
import re


class ParserPipeline:
    def __init__(self, scope_lookup):
        self.scope_lookup = scope_lookup
        self.hints = []
        self.needle_box = None

    def switch_context(self, new_scope):
        self.scope_lookup = new_scope

    def get_hints(self, input_str):
        needle_box = tokenizer.variable_lookup(str(input_str))
        # print("NEEd", needle_box.keys())
        self.needle_box = needle_box
        self.hints.extend(list(needle_box.keys()))
        self.input_str = input_str
        return self

    def apply(self):
        self.pipeline(self.input_str)

    def pipeline(self, input_str):
        if len(self.hints) == 0:
            self.get_hints(input_str)
        res = tokenizer.sub_needle_box(
            self.needle_box, self.scope_lookup, input_str
        )
        return res


def treesplitter_processor(split_tree):
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
            pattern = match["pattern"]

            def repl(val, stt=raw_str):
                stt = stt or raw_str
                return re.sub(re.escape(pattern), val, stt)

            filling_value(field, value, repl)

    return output


def assemble_token_result(split_tree, token_trees, raw):
    # treefields = list(map(lambda x: x["field"], token_trees))
    # f = treefields
    buffer = []
    print("TK TREE", token_trees)
    # must enforce parity check
    parity = None
    for branch in split_tree:
        branch_len = len(branch.keys())
        if parity is None:
            parity = branch_len
        else:
            if branch_len != parity:

                raise Exception(
                    "Encountered Parity problem! All array must be equal length !"
                )

        copied_raw = raw.copy()
        for branch_key in branch.keys():
            val = branch[branch_key]
            # lots of copy !!!
            copied_raw[branch_key] = val

            # buffer.append(copied_raw)
        buffer.append(copied_raw)

    return buffer


# convert dict with <msg,param,bind> to
def multiCommandParser(raw, pmc_bind=None):
    keywords = ["msg", "param", "bind"]
    # accumulateKeyword(key, raw[key])
    lookup_dict = raw
    if pmc_bind:
        lookup_dict = pmc_bind

    ppl = ParserPipeline(lookup_dict)
    token_trees = []
    for key in keywords:
        try:
            fmt = str(raw[key])
            pol = ppl.get_hints(fmt)
            bo = ppl.pipeline(fmt)

            raw[key] = bo

            kkb = tokenizer.tokenize_array(raw[key], ["$[", "]"])

            if len(kkb) > 0:
                token_tree = {}

                token_tree["field"] = key
                token_tree["matches"] = kkb
                token_tree["raw_string"] = raw[key]
                token_trees.append(token_tree)

                print("RAW", raw[key], pol.hints, bo, kkb)

        except Exception as e:
            print("EE", e, raw)

            continue

    split_tree = treesplitter_processor(token_trees)
    return assemble_token_result(split_tree, token_trees, raw)


# convert dict with <msg,param,bind> to
def multiCommandParserTest(raw, pmc_test):
    keywords = ["msg", "param", "bind"]
    # accumulateKeyword(key, raw[key])

    ppl = ParserPipeline(raw)
    token_trees = []
    for key in keywords:
        try:
            fmt = str(raw[key])
            pol = ppl.get_hints(fmt)
            bo = ppl.pipeline(fmt)

            raw[key] = bo

            kkb = tokenizer.tokenize_array(raw[key], ["$[", "]"])

            if len(kkb) > 0:
                token_tree = {}

                token_tree["field"] = key
                token_tree["matches"] = kkb
                token_tree["raw_string"] = raw[key]
                token_trees.append(token_tree)

                print("RAW", raw[key], pol.hints, bo, kkb)

        except Exception as e:
            print("EE", e, raw)

            continue

    split_tree = treesplitter_processor(token_trees)
    return assemble_token_result(split_tree, token_trees, raw)


sample = {
    "msg": "%prne app ",
    "param": "10 $[1,2,3,4,5,6]",
    "prne": "a",
    "bind": "shift",
}

multVars = {
    "msg": "%prne app",
    "param": "10 $[1,4]",
    "prne": "a",
    "bind": "shift $[2,3]",
}

assembled = multiCommandParser(sample)
assembledVar = multiCommandParser(multVars)

print("assmb", assembledVar)

# ParserPipeline({"var": 1}).get_hints("ahahah %var %do %bean")
# .pipeline(
#     "ahahah %var %do %bean"
# )
# tokenizer.tokenize_array()
