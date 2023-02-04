from re import A
import tomli as toml

LUMO = {
    "volume": {
        "prne": 100,
        "param": "1 %prne $[fucking itch %prne,2 ] %sukaka",
        "keybind": 1,
        "cmd": 10,
        "xmddd": {
            "hahah": "babab %prne",
            "hahah2": {
                "bruhak": 1000,
                "BAP": {
                    "BRU": 10,
                    "param": "1 %prne $[fucking itch %prne,2 ] %sukaka",
                    "keybind": 1,
                    "cmd": 10,
                },
            },
        }
        # "prne": 000,
    }
}


def unpeel_layer(layers):
    def internal_call(ll):
        print("TRAGE", ll)
        if isinstance(ll, dict):
            for lk in ll.keys():
                internal_call(ll[lk])

    for k in layers.keys():
        layer = layers[k]
        print(isinstance(layer, dict))

        internal_call(layer)


with open("hypr_ins.toml", "rb") as f:
    tml = toml.load(f)

    # else:

    # dispatch(f.msg,f.)

    print(tml)

# unpeel_layer(LUMO)
