	section .text
	global a
	global start
	extern b

a:
	mov ax, 0
	ret

start:
	call b
