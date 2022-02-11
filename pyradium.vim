" Testing: vi -c ':so pyradium.vim' pyradium.vim

" s: prefx doesn't work here for some reason? Why not?
function XXPyradiumTemplateHelperCommand(cmd)
	:let output=system("pyradium template-helper " . a:cmd)
	set paste
	exec "normal i" . l:output
	set nopaste
endfunction

:amenu 500.10 &pyradium.&Code :call XXPyradiumTemplateHelperCommand("code")<Enter>
:amenu 500.20 &pyradium.&Terminal :call XXPyradiumTemplateHelperCommand("term")<Enter>
:amenu 500.30 &pyradium.&Sectiontitle :call XXPyradiumTemplateHelperCommand("sectiontitle")<Enter>
:amenu 500.40 &pyradium.&Image :call XXPyradiumTemplateHelperCommand("img")<Enter>
:amenu 500.50 &pyradium.&Animation :call XXPyradiumTemplateHelperCommand("anim")<Enter>
:amenu 500.60 &pyradium.&Debug :call XXPyradiumTemplateHelperCommand("anim")<Enter>
