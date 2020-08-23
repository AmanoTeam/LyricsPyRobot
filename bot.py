from config import bot, sudos, loop, plgns
from amanobot.aio.loop import MessageLoop

for i in plgns:
    exec('from plugins.{0} import {0}'.format(i))

if __name__ == '__main__':
    loop.create_task(MessageLoop(bot, dict(chat=handle,
                      callback_query=callback,
                      inline_query=inline,
                      chosen_inline_result=chosen)).run_forever())
    loop.run_forever()
