-- Options are automatically loaded before lazy.nvim startup
-- Default options that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/options.lua
-- Add any additional options here

vim.opt.relativenumber = false

-- Use ty instead of pyright with the lang.python extra
vim.g.lazyvim_python_lsp = "ty"

-- Don't format on save; format manually with <leader>cf
vim.g.autoformat = false
