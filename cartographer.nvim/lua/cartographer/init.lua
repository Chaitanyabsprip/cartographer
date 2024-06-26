---@diagnostic disable: no-unknown
local M = {}
local finders = require 'telescope.finders'
local pickers = require 'telescope.pickers'
local previewers = require 'telescope.previewers'
local sorters = require 'telescope.sorters'
local utils = require 'cartographer.utils'
local curl = require 'plenary.curl'

local config = {
    directory = '',
    embeddings_path = '',
    host = 'http://127.0.0.1',
}

local function install_path()
    for _, path in ipairs(vim.api.nvim_list_runtime_paths()) do
        if path:match '/cartographer$' then return path end
    end
    return ''
end

local function get_cache_dir()
    local osname = vim.loop.os_uname().sysname
    local dir
    if osname == 'Linux' then
        dir = os.getenv 'XDG_CACHE_HOME'
        dir = dir or os.getenv 'HOME' .. '/.cache'
    elseif osname == 'Darwin' then
        dir = os.getenv 'XDG_CACHE_HOME'
        dir = dir or os.getenv 'HOME' .. '/Library/Caches'
    elseif osname == 'Windows' then
        dir = os.getenv 'LOCALAPPDATA'
    end
    return dir .. '/cartographer'
end

local function getport()
    if config.port ~= nil then return config.port end
    local file = io.open(get_cache_dir() .. '/.port', 'r')
    if file == nil then return nil end
    local port = file:read()
    file:close()
    config.port = port
    return port
end

local function uri(endpoint) return config.host .. ':' .. getport() .. endpoint end

local function getpid()
    local resp = curl.get(uri '/info')
    local json = vim.fn.json_decode(resp.body)
    return json and json.pid or nil
end

local function launch_app(opts)
    local app_path = install_path()
    local command = app_path .. '/bin/cartographer'
    local args = { '-d' }
    local env = {
        ['HOME'] = os.getenv 'HOME',
        ['PATH'] = opts.python_path,
        ['PYTHONPATH'] = app_path,
        ['XDG_CACHE_HOME'] = os.getenv 'XDG_CACHE_HOME',
        ['XDG_CONFIG_HOME'] = os.getenv 'XDG_CONFIG_HOME',
    }
    local job = utils.exec_async(command, args, nil, env)
    config.job = job
end

function M.setup(opts)
    config = vim.tbl_deep_extend('force', config, opts) or config
    launch_app(config)
    local group = vim.api.nvim_create_augroup('cartographer', { clear = true })
    vim.api.nvim_create_autocmd('VimLeavePre', {
        group = group,
        callback = function()
            local uv = vim.loop
            local pid = getpid()
            if pid then uv.kill(pid, uv.constants.SIGTERM) end
            job:shutdown()
        end,
    })
    vim.api.nvim_create_autocmd('BufWrite', {
        group = group,
        pattern = '*.md',
        callback = function(event) M.index_files(event.match) end,
    })
    vim.api.nvim_create_user_command('CartographerIndex', M.index_files, { nargs = 0 })
    vim.api.nvim_create_user_command('CartographerSearch', M.telescope_search, { nargs = 0 })
end

function M.index_files(filepath)
    if type(filepath) ~= 'string' then filepath = nil end
    local endpoint = filepath and '/index?filepath' .. filepath or '/index'
    curl.get(uri(endpoint))
end

function M.search(query)
    query = vim.fn.substitute(query, [[\s\+]], '%20', 'g')
    local resp = curl.get(uri('/search?query=' .. query .. '&limit=30'))
    return vim.fn.json_decode(resp.body)
end

function M.telescope_search()
    local prompt = 'Search Files: '
    local query = vim.fn.input { prompt = prompt, cancelreturn = nil }
    if query == nil then return end
    pickers
        .new({}, {
            prompt_title = prompt,
            finder = finders.new_table {
                results = M.search(query),
                entry_maker = function(entry)
                    return {
                        value = entry,
                        display = entry.filepath,
                        path = entry.filepath,
                        ordinal = entry.score,
                    }
                end,
            },
            sorter = sorters.get_generic_fuzzy_sorter(),
            previewer = previewers.vim_buffer_vimgrep.new {},
        })
        :find()
end

return M
