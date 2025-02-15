	section .text
	global b
	extern a
b:
	call a
	ret
