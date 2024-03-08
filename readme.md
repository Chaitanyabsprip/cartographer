# Cartographer

Cartographer is a powerful tool that leverages evolving Natural Language
Processing (NLP) models to search through your document-bases right from the
comfort of your text editor.

## Installation

### Dependencies

To use Cartographer, you need to have the following dependencies installed:

- Go programming language
- Sentence-transformers Python package

### Build from source

To build Cartographer from source, follow these steps:

```bash
  git clone https://github.com/Chaitanyabsprip/cartographer
  cd cartographer
  go build -o bin/cartographer
```

### Neovim Plugin

- Using [lazy.nvim](https://github.com/folke/lazy.nvim)

```lua
  {
    'Chaitanyabsprip/cartographer',
    build = 'go build -o bin/cartographer; cp cartographer.nvim/lua .',
    dependencies = { 'nvim-telescope/telescope.nvim' },
    opts = {
      --[[your configuration here]]
    }
  }
```

## Roadmap

Our future plans for Cartographer include:

- Enhancing search capabilities with advanced filtering options.
- Integrating with more text editors and IDEs.

## Contributing

We welcome contributions from the community! If you'd like to contribute to
Cartographer, please open a PR. In case the suggested change is big, we
recommend to open an issue first and discuss the changes.

## Authors

- [@Chaitanya Sharma](https://www.github.com/Chaitanyabsprip)
- [@Siddhant Gupta](https://www.github.com/gsiddhant159)

## License

[MIT](https://choosealicense.com/licenses/mit/)
