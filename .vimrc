set nocompatible

set autoread

set mouse +=a

filetype on

set encoding=utf-8
set termencoding=utf-8
set fileencodings=utf-8,cp1251,koi8-r

set novisualbell
set t_vb=

colorscheme delek
"colorscheme ingretu

syntax on
set t_Co=256
set number
set tabpagemax=100

set tabstop=4      " tab width is 4 spaces
set shiftwidth=4   " indent also with 4 spaces
set expandtab      " expand tabs to spaces

if filereadable(".vim.custom")
    so .vim.custom
endif

augroup vimrc                                                                                                                                                                        
  " Automatically delete trailing DOS-returns and whitespace on file open and                                                                                                        
  " write.                                                                                                                                                                           
  autocmd BufRead,BufWritePre,FileWritePre * silent! %s/[\r \t]\+$//                                                                                                                 
augroup END
