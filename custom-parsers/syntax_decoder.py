import tokenizer
import re


class ParserPipeline:
    def __init__(self, scope_lookup):
        self.scope_lookup = scope_lookup
        self.hints = []
        self.needle_box = None

    # def probe():

    def get_hints(self, input_str):
        needle_box = tokenizer.variable_lookup(input_str)
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
        # if res is None:
        #     raise Exception(f"Cannot find the variable")
        return res


def treesplitter_processor(split_tree):
    output = []
    print(split_tree)

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


def assemble_token_result(split_tree, raw):
    # treefields = list(map(lambda x: x["field"], token_trees))
    # f = treefields
    buffer = []
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
            # print("THIS IS BRANCH", branch_key, val)
            # lots of copy !!!
            copied_raw[branch_key] = val

            # buffer.append(copied_raw)
        buffer.append(copied_raw)

    return buffer


def generate_token(k, raw):
    try:
        v = raw[k]
        # fmt = str(v)
        # pol = ppl.get_hints(fmt)

        # replaced = ppl.pipeline(fmt)
        # if replaced is None:
        #     # request new pipeline
        #     return -1

        # raw[k] = replaced
        kkb = tokenizer.tokenize_array(v, ["$[", "]"])
        if len(kkb) > 0:
            token_tree = {}

            token_tree["field"] = k
            token_tree["matches"] = kkb
            token_tree["raw_string"] = raw[k]

            # token_trees.append(token_tree)

            return token_tree

    except Exception as e:
        print("Encountered error", e)


class PossibleNonLocalError(ValueError):
    def __init__(self, key, message="Cannot find variable"):
        self.key = key
        self.message = message
        super().__init__(self.message)


# convert dict with <msg,param,bind> to
def multiCommandParser(
    raw, keywords=["msg", "param", "bind"], pmc_bind=None
):
    # accumulateKeyword(key, raw[key])

    token_trees = []

    for key in keywords:
        token_tree = generate_token(key, raw)

        if token_tree is None:
            continue
        elif token_tree == -1:
            raise PossibleNonLocalError(key)

        token_trees.append(token_tree)

    print("RARA", raw, token_trees)
    split_tree = treesplitter_processor(token_trees)
    return assemble_token_result(split_tree, raw)


sample = {
    "msg": "%prne app ",
    "param": "10 $[1,2,3,4,5,6]",
    "prne": "a",
    "bind": "shift",
}

multVars = {
    "msg": "%prne app $prne",
    "param": "10 $[1,4]",
    # "prne": "a",
    "bind": "shift $[2,3]",
}


# assembled = multiCommandParser(sample)
# assembledVar = multiCommandParser(multVars)

# print("assmb", assembledVar)

# ParserPipeline({"var": 1}).get_hints("ahahah %var %do %bean")
# .pipeline(
#     "ahahah %var %do %bean"
# )
# tokenizer.tokenize_array()
