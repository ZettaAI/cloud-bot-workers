from json import loads
from typing import Tuple

from click import Group
from requests import codes

from .slack import Response as SlackResponse


class Worker:
    def __init__(self, cmd_grp: Group):
        self._grp = cmd_grp

    def _invoke_cmd(self, cmd: str, user_id: str) -> Tuple[bool, str]:
        from click import Context
        from click.exceptions import MissingParameter

        ctx = Context(self._grp, info_name=self._grp.name, obj={})
        ctx.obj["long_job"] = False
        ctx.obj["broadcast"] = False
        ctx.obj["user_id"] = user_id
        try:
            self._grp.parse_args(ctx, cmd.split()[1:])
            msg = self._grp.invoke(ctx)
        except MissingParameter as err:
            msg = f":warning: Something went wrong.\n```{err.format_message()}```"
            ctx.obj["broadcast"] = False
        except Exception as err:
            err = repr(err).split("\n")
            if len(err) > 5:
                err_start = "\n".join(err[:2])
                err_end = "\n".join(err[-2:])
                err = f"{err_start}\n.\n.\n.\n{err_end}"
            else:
                err = "\n".join(err)
            msg = f":warning: Something went wrong. Please refer help.\n```{err}```"
            ctx.obj["broadcast"] = False
        return (msg, ctx.obj["long_job"], ctx.obj["broadcast"])

    def callback(self, ch, method, properties, body):
        event = loads(body)["event"]
        msg, long_job, broadcast = self._invoke_cmd(event["user_cmd"], event["user"])
        SlackResponse(event).send(msg, long_job, broadcast)

    def start(self, routing_key: str, callback: callable):
        from . import config
        from . import amqp_connection

        print(f"initializing worker for {routing_key}")
        channel = amqp_connection.channel()
        channel.exchange_declare(exchange=config.EXCHANGE_NAME, exchange_type="topic")

        queue_name = channel.queue_declare("", exclusive=True).method.queue
        channel.queue_bind(
            exchange=config.EXCHANGE_NAME, queue=queue_name, routing_key=routing_key
        )
        channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True
        )

        print(" [*] Waiting for work. To exit press CTRL+C")
        channel.start_consuming()


class HelpWorker(Worker):
    def __init__(self, cmd_grps: dict):
        self._cmd_grps = cmd_grps

    def callback(self, ch, method, properties, body):
        """Entrypoint for the `help` worker."""
        from .utils import get_help_msg

        event = loads(body)["event"]
        try:
            msg = get_help_msg(event["user_cmd"], self._cmd_grps)
        except Exception as err:
            msg = ":warning: Something went wrong. Check help to see "
            msg += f"if your command is properly formatted.\n```{repr(err)}```"
        SlackResponse(event).send(msg)
