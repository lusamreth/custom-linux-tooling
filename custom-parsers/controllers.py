import pulsectl
import click
import math
import subprocess
import dunst

PULSE_CLIENT = "LINUX_PC"


def adjustOverFlow(target):
    if target > 1:
        return 1
    elif target < 0:
        return 0


def getVol():
    with pulsectl.Pulse(PULSE_CLIENT) as pulse:
        default = pulse.server_info().default_sink_name
        default_sink = pulse.get_sink_by_name(default)
        vol = pulse.volume_get_all_chans(default_sink)
        return vol, default_sink


def incFn(vol):
    # return 1 / (math.exp(-vol) + 1)
    return vol / 100


def incVol(vol, surpass=False):
    with pulsectl.Pulse(PULSE_CLIENT) as pulse:
        currentVol, default_sink = getVol()
        target = currentVol + incFn(vol)
        if target > 1:
            target = 1

        if not surpass and (target >= 1):
            raise ValueError()
        else:
            pulse.volume_set_all_chans(default_sink, target)

        return target


def decVol(vol):
    with pulsectl.Pulse(PULSE_CLIENT) as pulse:
        currentVol, default_sink = getVol()
        target = currentVol - incFn(vol)
        if target < 0:
            target = 0
        print("TARGET", target, currentVol)
        pulse.volume_set_all_chans(obj=default_sink, vol=(target))
        return target


def toggleMute():
    with pulsectl.Pulse(PULSE_CLIENT) as pulse:

        default = pulse.server_info().default_sink_name
        default_sink = pulse.get_sink_by_name(default)
        muteState = default_sink.mute == 0
        pulse.mute(default_sink, muteState)
        print("DEF", default_sink.mute)
        return muteState


# @click.command
# @click.argument('')
# print(getVol())


def dunst_notify_vol(vol):
    icon = "audio-volume-"
    if vol == 0:
        icon = f"{icon}muted"
    elif vol <= 30:
        icon = f"{icon}low"
    elif vol <= 60:
        icon = f"{icon}medium"
    else:
        icon = f"{icon}high"

    dunst.Dunstify(f"Volume : {vol}").icon(icon).hint(
        h_type="string",
        h_name="x-canonical-private-synchronous",
        h_val="audio",
    ).progress_bar(vol).timeout(1200).run()


def dunst_forward_norm(un_norm):
    return dunst_notify_vol(math.floor(un_norm * 100))


@click.group()
def cli():
    pass


@cli.group()
def audio():
    pass


@audio.command()
def getvol():
    dunst_forward_norm(getVol()[0])


@audio.command()
@click.argument("volume")
def incvol(volume):
    res = None
    try:
        res = incVol(int(volume))
        click.echo(f"Volume increased by {res * 100} %")
    except ValueError as e:
        print("MAXIMUM VOLUME", e)
        dunst.notifymsg(
            "Hearing LOSS",
            "Please turn down the volume to protect hearing !!",
            1500,
        )
        res = 1

    dunst_forward_norm(res)


@audio.command()
@click.argument("volume")
def decvol(volume):
    res = decVol(int(volume))
    click.echo(f"Volume decreased by {res * 100} %")
    dunst_forward_norm(res)


@audio.command()
def mute():
    # res = decVol(100)
    # click.echo(f"Volume decreased by {res * 100} %")
    state = toggleMute()
    dunst_forward_norm(0 if state else getVol()[0])


class BrightnessCtl:
    def __init__(self):
        self.cmds = ["brightnessctl"]

    def set(self, v):
        self.cmds.extend(["set", str(v)])
        return self

    def restore(self):
        self.cmds.extend(["restore"])
        return self

    def get(self):
        self.cmds.extend(["g"])
        return self

    def run(self):
        print(self.cmds)
        output = subprocess.check_output(self.cmds)
        return output


@cli.group()
def backlight():
    pass


def brightnessHandler(val):
    light_icon = (
        lambda light_icon: f"display-brightness-{light_icon}-symbolic"
    )
    D = dunst.Dunstify(title="Brightness")
    if val == 0:
        D.icon(light_icon("off"))
    elif val <= 30:
        D.icon(light_icon("low"))
    elif val <= 70:
        D.icon(light_icon("medium"))
    else:
        D.icon(light_icon("high"))

    D.hint(
        "string", "x-canonical-private-synchronous", "brightness"
    ).progress_bar(val).timeout(1600).run()


def setBrightness(val, sign):
    BrightnessCtl().set(f"{val}%{sign}").run()
    output = BrightnessCtl().get().run()
    num = int(output.decode().strip())

    brightnessHandler((num / 255) * 100)


@backlight.command()
@click.argument("increased_by")
def inc(increased_by):
    setBrightness(increased_by, "+")
    # BrightnessCtl().set(f"{increased_by}%+").run()


@backlight.command()
@click.argument("decreased_by")
def dec(decreased_by):
    setBrightness(decreased_by, "-")


@backlight.command()
@click.argument("decreased_by")
def restore(decreased_by):
    BrightnessCtl().set(f"{decreased_by}%-").run()


if __name__ == "__main__":
    cli()

# pulse.get_sink_by_name()
