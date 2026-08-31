# VHS Tape for Somnia DreamDEX Agent Demo
Output "assets/somnia_agent_demo.gif"
Output "assets/somnia_agent_demo.mp4"

Set FontSize 14
Set Width 1200
Set Height 700
Set Padding 20
Set Theme "TokyoNight"
Set TypingSpeed 25ms

Type "python3 -m pytest -v"
Enter
Sleep 3s

Type "python3 scripts/record_demo_walkthrough.py"
Enter
Sleep 4s

Sleep 2s
