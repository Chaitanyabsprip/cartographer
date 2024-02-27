local M = {}
local finders = require 'telescope.finders'
local pickers = require 'telescope.pickers'
local previewers = require 'telescope.previewers'
local sorters = require 'telescope.sorters'
local utils = require 'semantic_search.utils'

local config = {
    directory = '',
    embeddings_path = '',
    host = 'http://127.0.0.1:30001',
}

local function getpid()
    local command = 'curl'
    local args = { config.host .. '/info' }
    local resp = utils.execute(command, args)
    local json = vim.fn.json_decode(resp:result()[1])
    return json and json.pid or nil
end

function M.setup(opts)
    print 'ha'
    config = vim.tbl_deep_extend('force', config, opts) or config
    local command = 'cartographer'
    -- TODO(chaitanya): remove trailing slash if added to install_path
    local args = { '-D' }
    local job = utils.exec_async(command, args, nil, { ['PYTHONPATH'] = opts.install_path })
    config.job = job
    local group = vim.api.nvim_create_augroup('semantic_search', { clear = true })
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
    vim.api.nvim_create_user_command('ObsidianIndexAllFiles', M.index_files, { nargs = 0 })
    vim.api.nvim_create_user_command('ObsidianSemanticSearch', M.telescope_search, { nargs = 0 })
end

function M.index_files(filepath)
    if type(filepath) ~= 'string' then filepath = nil end
    local command = 'curl'
    local endpoint = filepath and '/index?filepath' .. filepath or '/index'
    local args = { config.host .. endpoint }
    utils.exec_async(
        command,
        args,
        vim.schedule_wrap(
            function() vim.notify('Indexing files completed', vim.log.levels.INFO) end
        )
    )
end

function M.search(query)
    query = vim.fn.substitute(query, [[\s\+]], '%20', 'g')
    local command = 'curl'
    local args = { config.host .. '/search?query=' .. query }
    local job = utils.execute(command, args)
    local json = job:result()
    return vim.fn.json_decode(json)
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
                        display = entry.display_filename,
                        path = entry.filename,
                        ordinal = entry.filename,
                    }
                end,
            },
            sorter = sorters.get_generic_fuzzy_sorter(),
            previewer = previewers.vim_buffer_vimgrep.new {},
        })
        :find()
end

return M
