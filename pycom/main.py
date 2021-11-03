
Input1 = Pin('P2', mode = Pin.IN, pull=Pin.PULL_UP)
Input2 = Pin('P3', mode = Pin.IN, pull=Pin.PULL_UP)
Input3 = Pin('P4', mode = Pin.IN, pull=Pin.PULL_UP)
Input4 = Pin('P6', mode = Pin.IN, pull=Pin.PULL_UP)
Input5 = Pin('P8', mode = Pin.IN, pull=Pin.PULL_UP)
Input6 = Pin('P9', mode = Pin.IN, pull=Pin.PULL_UP)
Input7 = Pin('P10', mode = Pin.IN, pull=Pin.PULL_UP)

Output1 = Pin('P19', mode = Pin.OUT)
Output1.value(1)
Output2 = Pin('P20', mode = Pin.OUT)
Output2.value(1)
Output3 = Pin('P21', mode = Pin.OUT)
Output3.value(1)
Output4 = Pin('P22', mode = Pin.OUT)
Output4.value(1)

keypushed = ""

#keymapping of the keyboard matrix
Matrix = [["TimeOutHome","Periode-","RestartTimer","Periode+","TimeOutAway"],
          ["FoulHome-","FoulHome+","Nothing","FoulAway-","FoulAway+"],
          ["ScoreHome-","ScoreHome+","StartStop","ScoreAway-","ScoreAway+"]]

client = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
try:
    client.connect(('10.3.141.1', 8080))
    client.send(b'Nothing')
except usocket.error:
    print("error code ontvangen")
    client.close()
    machine.reset()
print("Verbinding gemaakt")

while True:
    #test all buttons
    Output1.value(0)  #first signal below
    if Input1.value()==0:
        keypushed = "TimeOutHome"
    if Input2.value()==0:
        keypushed = "Periode-"
    if Input3.value()==0:
        keypushed = "RestartTimer"
    if Input4.value()==0:
        keypushed = "Periode+"
    if Input5.value()==0:
        keypushed = "TimeOutAway"
    Output1.value(1)  #first signal below

    Output2.value(0)  #first signal below
    if Input1.value()==0:
        keypushed = "FoulHome-"
    if Input2.value()==0:
        keypushed = "FoulHome+"
    if Input3.value()==0:
        keypushed = "Nothing"
    if Input4.value()==0:
        keypushed = "FoulAway-"
    if Input5.value()==0:
        keypushed = "FoulAway+"
    Output2.value(1)  #first signal below

    Output3.value(0)  #first signal below
    if Input1.value()==0:
        keypushed = "ScoreHome-"
    if Input2.value()==0:
        keypushed = "ScoreHome+"
    if Input3.value()==0:
        keypushed = "StartStop"
    if Input4.value()==0:
        keypushed = "ScoreAway-"
    if Input5.value()==0:
        keypushed = "ScoreAway+"
    Output3.value(1)  #first signal below

    if keypushed:
        print("Ingedrukte toets", keypushed)
        client.send(keypushed.encode())
        keypushed = ""
        time.sleep(0.3)

client.close()
