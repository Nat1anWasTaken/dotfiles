return {
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        -- Use the binaries already on PATH instead of installing them with Mason
        ty = { mason = false },
        ruff = { mason = false },
      },
    },
  },
}
