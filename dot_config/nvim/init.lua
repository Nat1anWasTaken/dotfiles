-- Minimal Neovim setup with lazy.nvim and hop.nvim.
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable",
    lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)
vim.opt.ignorecase = true
vim.opt.smartcase = true
vim.opt.number = true

require("lazy").setup({
  {
    "smoka7/hop.nvim",
    version = "*",
    config = function()
      local hop = require("hop")

      hop.setup()

      local function hop_char2_case_insensitive(opts)
        local previous_smartcase = vim.o.smartcase
        local previous_ignorecase = vim.o.ignorecase
        vim.o.ignorecase = true
        vim.o.smartcase = false

        local ok, err = pcall(hop.hint_char2, vim.tbl_extend("force", {
          current_line_only = true,
          case_insensitive = true,
        }, opts or {}))

        vim.o.ignorecase = previous_ignorecase
        vim.o.smartcase = previous_smartcase
        if not ok then
          error(err)
        end
      end

      vim.keymap.set({ "n", "x", "o" }, "f", function()
        hop_char2_case_insensitive()
      end, { remap = true, desc = "Hop: 2-char jump (bidirectional, case-insensitive)" })
      vim.keymap.set({ "n", "x", "o" }, "t", function()
        hop_char2_case_insensitive()
      end, { remap = true, desc = "Hop: 2-char jump (bidirectional, case-insensitive)" })
      vim.keymap.set({ "n", "x", "o" }, "F", "<cmd>HopLineStart<CR>", {
        desc = "Hop: line-start jump (bidirectional)",
      })
      vim.keymap.set({ "n", "x", "o" }, "T", "<cmd>HopLine<CR>", {
        desc = "Hop: line jump (bidirectional)",
      })
    end,
  },
})
