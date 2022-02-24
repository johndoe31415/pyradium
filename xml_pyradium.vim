" Vim filetype plugin
" Language:			pyradium
" Maintainer:		Johannes Bauer <joe@johannes-bauer.com>
" URL:				https://github.com/johndoe31415/pyradium
" Last Change:		2022 Feb 14
"
" ~/.vim/after/ftplugin/xml_pyradium.vim

" Only affect XML files if the pyradium namespace is found
if !search("https://github.com/johndoe31415/pyradium", "n", 10)
	finish
endif

function PyradiumTemplateHelperCommand(cmd)
	:let output=system("pyradium template-helper " . a:cmd)
	set paste
	exec "normal i" . l:output
	set nopaste
endfunction

" Add a menu
:amenu 500.10 &pyradium.&Code :call PyradiumTemplateHelperCommand("code")<Enter>
:amenu 500.20 &pyradium.&Terminal :call PyradiumTemplateHelperCommand("term")<Enter>
:amenu 500.30 &pyradium.&Sectiontitle :call PyradiumTemplateHelperCommand("sectiontitle")<Enter>
:amenu 500.40 &pyradium.&Quote :call PyradiumTemplateHelperCommand("quote")<Enter>
:amenu 500.50 &pyradium.&Image :call PyradiumTemplateHelperCommand("img")<Enter>
:amenu 500.60 &pyradium.&Animation :call PyradiumTemplateHelperCommand("anim")<Enter>

" Add specific keybindings
vmap <C-S-b> :s/\%V.*\%V./<b>&<\/b><Enter>:noh<Enter>
vmap <C-S-i> :s/\%V.*\%V./<i>&<\/i><Enter>:noh<Enter>
vmap <C-S-a> :s/\%V.*\%V./<a href="">&<\/a><Enter>:noh<Enter>
vmap <C-S-q> :s/\%V.*\%V./<s:enq>&<\/s:enq><Enter>:noh<Enter>
vmap <C-S-l> :s/\%V.*\%V./<s:tex>&<\/s:tex><Enter>:noh<Enter>
vmap <C-S-t> :s/\%V.*\%V./<s:tt>&<\/s:tt><Enter>:noh<Enter>
imap <C-S-a> <s:ar>-)</s:ar>
vmap <F6> :s/\%V.*\%V./<s:ac>&<\/s:ac><Enter>:noh<Enter>
vmap <F7> :s/\%V.*\%V./<s:nlb>&<\/s:nlb><Enter>:noh<Enter>
vmap <F8> :s/\%V.*\%V./<s:nsc>&<\/s:nsc><Enter>:noh<Enter>
