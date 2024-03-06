local utils = {}
---@class Job
---@field command string Command to run
---@field args? string[] List of arguments to pass
---@field cwd? string Working directory for job
---@field env? table<string, string>|string[] Environment looking like: { ['VAR'] = 'VALUE' } or { 'VAR=VALUE' }
---@field interactive? boolean
---@field detached? boolean Spawn the child in a detached state making it a process group leader
---@field skip_validation? boolean Skip validating the arguments
---@field enable_handlers? boolean If set to false, disables all callbacks associated with output (default: true)
---@field enabled_recording? boolean
---@field on_start? fun()
---@field on_stdout? fun(error: string, data: string, self?: Job)
---@field on_stderr? fun(error: string, data: string, self?: Job)
---@field on_exit? fun(self: Job, code: number, signal: number)
---@field maximum_results? number Stop processing results after this number
---@field writer? Job|table|string Job that writes to stdin of this job.

local Job = require 'plenary.job'

function utils.execute(command, args, on_exit, env)
    ---@type Job
    local job = Job:new {
        command = command,
        args = args,
        on_exit = on_exit,
        env = env,
        -- on_stderr = function(error, data)
        --     vim.print(error)
        --     vim.print(data)
        -- end,
        -- on_stdout = function(error, data)
        --     vim.print(error)
        --     vim.print(data)
        -- end,
    }
    job:sync(10000)
    return job
end

function utils.exec_async(command, args, on_exit, env)
    ---@class Job
    local job = Job:new {
        command = command,
        args = args,
        on_exit = on_exit,
        env = env,
        -- on_stderr = function(error, data)
        --     vim.print(error)
        --     vim.print(data)
        -- end,
        -- on_stdout = function(error, data)
        --     vim.print(error)
        --     vim.print(data)
        -- end,
    }
    job:start()
    return job
end

return utils
