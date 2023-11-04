local utils = {}
local Job = require 'plenary.job'

function utils.execute(command, args)
    local job = Job:new { command = command, args = args }
    job:sync(10000)
    return job
end

function utils.exec_async(command, args, on_exit)
    local job = Job:new { command = command, args = args, on_exit = on_exit }
    job:start()
    return job
end

return utils
