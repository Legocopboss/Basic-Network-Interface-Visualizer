import subprocess
import threading
import time
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
import matplotlib.patches as mpatches

from datetime import datetime

signal_strengths = []
times = []
transmit_rates = []
receive_rates = []
text_output = []
wifi = ""
win_x = 16
win_y = 8
delay = 5

transmitBool = False

fig, axSignal = plt.subplots(figsize=(win_x, win_y), num="Network Interface Visualizer")
txtBox = fig.add_axes(rect=(0.85, 0.25, 0.14, 0.7), facecolor='skyblue')


def outputText(tim, signal, trans, recv):
    global transmitBool
    global txtBox
    if transmitBool:
        modifier = (7, 0.14)
    else:
        modifier = (10, 0.1)

    if len(text_output) == modifier[0]:  # 7 max for trans       10 max for signal
        text_output[0].remove()
        text_output.pop(0)

    if transmitBool:
        text_output.append(txtBox.text(0.01, 1, tim + "\n" + signal + "\n" + trans + "\n" + recv))
    else:
        text_output.append(txtBox.text(0.01, .98, tim + "\n" + signal + "\n\n"))

    for t in text_output:
        t.set_position((0.01, (t.get_position()[1] - modifier[1])))
        #print(t.get_position())


def getSignal():
    global wifi
    output = subprocess.check_output("netsh wlan show interface").decode().replace("  ", "").split("\r\n")
    time = datetime.now().__str__().split(" ")[1].split(".")[0]
    while "" in output:
        output.remove("")

    # print(output)
    receive = output[len(output) - 5]
    transmit = output[len(output) - 4]
    signal = output[len(output) - 3]
    wifi_name = output[len(output) - 2]

    if not signal.__contains__("Signal") or not wifi_name.__contains__("Profile") or not transmit.__contains__(
            "Transmit") or not receive.__contains__("Receive"):
        print("Something is wrong")
        return None

    print(signal)
    print(transmit)
    print(receive)
    print(time)

    outputText(time, signal, transmit, receive)

    signal_s = int(signal.split(" : ")[1].replace("% ", ""))
    transmit_r = float(transmit.split(" : ")[1])
    receive_r = float(receive.split(": ")[1])
    wifi = wifi_name.split(": ")[1].replace(" ", "")

    if len(signal_strengths) == 15:
        signal_strengths.pop(0)
        transmit_rates.pop(0)
        receive_rates.pop(0)
        times.pop(0)
    signal_strengths.append(signal_s)
    transmit_rates.append(transmit_r)
    receive_rates.append(receive_r)
    times.append(time)


print(wifi)

getSignal()

plot, = axSignal.plot(times, signal_strengths, color="blue")
axSignal.tick_params(axis='x', labelrotation=90)
axSignal.set_ylabel('Connection Percentage')
axTransRecv = axSignal.twinx()
fig.subplots_adjust(bottom=0.25, left=0.04, right=0.8, top=0.95)
plt.title("Network: " + wifi)
plt.xlabel('Time')

axTransRecv.set_ylabel('Transmit & Receive Rate (Mbps)')

transLine = mpatches.Patch(color='red', label="Transmit Rate")
recvLine = mpatches.Patch(color='orange', label="Receive Rate")

signalLine = mpatches.Patch(color='blue', label="Connection %")
axSignal.legend(handles=[signalLine])

axTransRecv.locator_params(axis='y', nbins=10)
axTransRecv.get_yaxis().set_visible(False)

plt.xticks(rotation=90)

txtBox.get_yaxis().set_visible(False)
txtBox.get_xaxis().set_visible(False)

# txtBox.text(0, 0.9, "text\ntext2\ntext3")


loopBool = True


def closeLooping(event):
    global loopBool
    print("close loop")
    loopBool = False


def looping(event):
    global delay
    global loopBool
    global transmitBool
    while loopBool:
        print("looping")
        getSignal()
        axSignal.plot(times, signal_strengths, color="blue")

        if transmitBool:
            axTransRecv.plot(times, receive_rates, color='orange', linestyle='--')
            axTransRecv.plot(times, transmit_rates, color="red", linestyle='--')
        else:
            None

        plt.draw()
        time.sleep(delay)
    print("exit loop")


def looping_pre(event):
    print("loop pre")
    thread = threading.Thread(target=looping, args=(event,))
    thread.daemon = True
    thread.start()


def addTransmitAndReceive(event):
    for t in text_output:
        t.remove()
    text_output.clear()

    global transmitBool
    transmitBool = not transmitBool
    if transmitBool:
        axTransRecv.set_visible(True)
        axSignal.legend(handles=[signalLine, transLine, recvLine])
    else:
        axTransRecv.set_visible(False)
        axSignal.legend(handles=[signalLine])


def updateSlider(val):
    global delay
    delay = sDelay.val


def resetSlider(event):
    sDelay.reset()


axStopButton = plt.axes([0.15, 0.05, 0.1, 0.06])
bClose = widgets.Button(axStopButton, "Stop", hovercolor="0.975", color="red")
bClose.on_clicked(closeLooping)
axStartButton = plt.axes([0.05, 0.05, 0.1, 0.06])
bStart = widgets.Button(axStartButton, "Start", hovercolor="0.975", color="lime")
bStart.on_clicked(looping_pre)

toggleTransAndRec = plt.axes([0.3, 0.05, 0.15, 0.06])
bTog = widgets.Button(toggleTransAndRec, "Transmit & Receive Rates\nToggle", hovercolor="0.975")
bTog.on_clicked(addTransmitAndReceive)

axDelaySlider = plt.axes([0.5, 0.09, 0.2, 0.03])
sDelay = widgets.Slider(axDelaySlider, 'Delay', 0.5, 15.0, 5.0, valstep=0.5)
sDelay.on_changed(updateSlider)

axResetSlider = plt.axes([0.5, 0.02, 0.1, 0.06])
bResetSlider = widgets.Button(axResetSlider, 'Reset Delay', hovercolor="0.975", color='skyblue')
bResetSlider.on_clicked(resetSlider)

plt.show()
