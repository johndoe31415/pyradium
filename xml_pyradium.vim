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
:amenu 500.10 &pyradium.&Slide.&Main\title :call PyradiumTemplateHelperCommand("slide_title")<Enter>
:amenu 500.20 &pyradium.&Slide.&Table\ of\ contents :call PyradiumTemplateHelperCommand("slide_toc")<Enter>
:amenu 500.30 &pyradium.&Slide.&Sectiontitle :call PyradiumTemplateHelperCommand("slide_sectiontitle")<Enter>
:amenu 500.40 &pyradium.&Slide.&Left/right :call PyradiumTemplateHelperCommand("slide_leftright")<Enter>
:amenu 500.50 &pyradium.&Slide.&Quote :call PyradiumTemplateHelperCommand("slide_quote")<Enter>
:amenu 500.60 &pyradium.&Slide.&Final :call PyradiumTemplateHelperCommand("slide_final")<Enter>
:amenu 500.70 &pyradium.&Slide.&Acronyms :call PyradiumTemplateHelperCommand("slide_acronyms")<Enter>
:amenu 500.80 &pyradium.&Slide.F&eedback :call PyradiumTemplateHelperCommand("slide_feedback")<Enter>
:amenu 500.90 &pyradium.&Textblock.&Code :call PyradiumTemplateHelperCommand("textblock_code")<Enter>
:amenu 500.100 &pyradium.&Textblock.&Terminal :call PyradiumTemplateHelperCommand("textblock_term")<Enter>
:amenu 500.110 &pyradium.&Image.&Still\ image :call PyradiumTemplateHelperCommand("image_img")<Enter>
:amenu 500.120 &pyradium.&Image.&Animation :call PyradiumTemplateHelperCommand("image_anim")<Enter>
:amenu 500.130 &pyradium.&Image.&Plot :call PyradiumTemplateHelperCommand("image_plot")<Enter>
:amenu 500.140 &pyradium.&Image.&Graphviz :call PyradiumTemplateHelperCommand("image_graphviz")<Enter>
:amenu 500.150 &pyradium.&Other.&CircuitJS :call PyradiumTemplateHelperCommand("other_circuitjs")<Enter>

" Add specific keybindings
vmap <C-S-b> :s/\%V.*\%V./<b>&<\/b><Enter>:noh<Enter>
vmap <C-S-i> :s/\%V.*\%V./<i>&<\/i><Enter>:noh<Enter>
vmap <C-S-a> :s/\%V.*\%V./<a href="">&<\/a><Enter>:noh<Enter>
vmap <C-S-q> :s/\%V.*\%V./<s:enq>&<\/s:enq><Enter>:noh<Enter>
vmap <C-S-l> :s/\%V.*\%V./<s:tex>&<\/s:tex><Enter>:noh<Enter>
vmap <C-S-t> :s/\%V.*\%V./<s:tt>&<\/s:tt><Enter>:noh<Enter>
vmap <C-S-p> :s/\(\s*\)\(.*\)$/\1<li>\2<\/li>/g<Enter>:noh<Enter>
imap <C-S-a> <s:ar>-)</s:ar>
vmap <F6> :s/\%V.*\%V./<s:ac>&<\/s:ac><Enter>:noh<Enter>
vmap <F7> :s/\%V.*\%V./<s:nlb>&<\/s:nlb><Enter>:noh<Enter>
vmap <F8> :s/\%V.*\%V./<s:nsc>&<\/s:nsc><Enter>:noh<Enter>
