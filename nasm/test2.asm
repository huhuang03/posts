start:
	mov ax, 0
	jmp _hlt

_hlt:
	hlt
	jmp _hlt
