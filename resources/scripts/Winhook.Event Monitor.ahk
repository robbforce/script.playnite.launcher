#Requires AutoHotkey v2.0
#include WinHook.ahk

OnExit(ObjBindMethod(WinHook.Event, "UnHookAll"))

start := false
MyGui := Gui("+AlwaysOnTop", "WinHook Monitor")
MyGui.Add("Tab3", "w1020" " h480 x5 y5 vTabs +0x8 +Theme", ["Shell", "Events"])
MyGui["Tabs"].UseTab(1)
	Btn3 := MyGui.Add("Button", "", "Start")
	Btn4 := MyGui.Add("Button", "x+10", "Stop")
	MyGui.Add("Text",  "x+10 yp+4", "WinHook.Shells")
	Btn3.OnEvent("Click", (*)=>WinHook.Shell.Add(AllShell))
	Btn4.OnEvent("Click", (*)=>WinHook.Shell.UnHookAll())
	LV2 := MyGui.Add("ListView", "xs+10 yp+25 r25 w1000", ["Win_Hwnd","Win_Title","Win_Class","Win_Exe","Win_Event"])
MyGui["Tabs"].UseTab(2)
Btn1 := MyGui.Add("Button", "", "Start")
	Btn2 := MyGui.Add("Button", "x+10", "Stop")
	Btn1.OnEvent("Click", (*)=>WinHook.Event.Add(0x0000, 0xFFFF, AllEvent))
	Btn2.OnEvent("Click", (*)=>WinHook.Event.UnHookAll())
	MyGui.Add("Text", "x+10 yp+4", "WinHook.Events")
	LV1 := MyGui.Add("ListView", "xs+10 yp+25 r25 w1000", ["hWinEventHook","Event","hWnd","idObject","idChild","dwEventThread","dwmsEventTime","wClass","wTitle"])
MyGui.Show()

AllShell(Win_Hwnd, Win_Title, Win_Class, Win_Exe, Win_Event) {
	n := LV2.add(, Win_Hwnd, Win_Title, Win_Class, Win_Exe, Win_Event)
	LV2.Modify(n, "Vis")
	Loop 5
		LV2.ModifyCol(A_Index, "AutoHdr") 
}

AllEvent(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime) {
	try wTitle := WinGetTitle("ahk_id " Hwnd)
	try wClass := WinGetClass("ahk_id " Hwnd)
	n := LV1.add(, hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime, wClass, wTitle)
	LV1.Modify(n, "Vis")
	Loop 8
		LV1.ModifyCol(A_Index, "AutoHdr") 
}
