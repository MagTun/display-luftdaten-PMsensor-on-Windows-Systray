; https://www.autohotkey.com/boards/viewtopic.php?f=76&t=60978

Loop % A_Args[1]
{
	ToolTip % --A_Args[1]
	; TrayTip, PM watch,  % --A_Args[1]

	Sleep 1000
}
ToolTip
