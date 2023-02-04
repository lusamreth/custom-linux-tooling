import subprocess


class Dunstify:
    def __init__(self, title="", body=""):
        self.cmd = ["dunstify"]
        self.title = title
        self.body = body

    def icon(self, name):
        self.cmd.extend(["--icon", name])
        return self

    def timeout(self, tval):
        self.cmd.extend(["-t", f"{tval}"])
        return self

    def hint(self, h_type, h_name, h_val):

        self.cmd.extend(["-h", f"{h_type}:{h_name}:{h_val}"])
        return self

    def progress_bar(self, val):
        self.hint("int", "value", str(val))
        return self

    def get_command(self):
        self.cmd.append(self.title)
        self.cmd.append(self.body)
        return self.cmd

    def run(self):
        subprocess.run(self.get_command())


def notifymsg(title, body="", t=None):
    D = Dunstify(
        title,
        body,
    )
    if t:
        D.timeout(t)
    D.run()


def create_notification_cmd(dispatch, title, body="", t=None):
    D = Dunstify(
        title,
        body,
    )
    if t:
        D.timeout(t)
    cmd = f"{dispatch} && "
    for c in D.get_command():
        cmd += c + " "
    return cmd


# create_notification_cmd("echo hi", "babbaba", "vruh")
