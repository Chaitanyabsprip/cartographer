local utils = {}
local Job = require 'plenary.job'

function utils.execute(command, args)
    local job = Job:new { command = command, args = args }
    job:sync(10000)
    return job
end

function utils.exec_async(command, args, on_exit, env)
    local job = Job:new { command = command, args = args, on_exit = on_exit, env = env }
    job:start()
    return job
end

return utils
