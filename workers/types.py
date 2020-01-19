from json import dumps
from json import loads

from requests import post
from requests import codes
from click import Group
from click import Context
from click.exceptions import MissingParameter

from . import config
from . import amqp_cnxn
from .slack import Response as SlackResponse


class Worker:
    def __init__(self, cmd_grp: Group):
        self._grp = cmd_grp

    def invoke_cmd(self, cmd: str) -> str:
        try:
            ctx = Context(self._grp, info_name=self._grp.name, obj={})
            self._grp.parse_args(ctx, cmd.split()[1:])
            return self._grp.invoke(ctx)
        except MissingParameter as err:
            return f":warning: Something went wrong.\n```{err.format_message()}```"
        except Exception as err:
            return f":warning: Something went wrong. Please refer `help`.\n```{err}```"

    def callback(self, ch, method, properties, body):
        event = loads(body)["event"]
        # print(dumps(event, indent=2))
        msg = self.invoke_cmd(event["user_cmd"])
        response = SlackResponse(event)
        assert response.send(msg).status_code == codes.ok  # pylint: disable=no-member

    def start(self, routing_key: str):
        channel = amqp_cnxn.channel()
        channel.exchange_declare(exchange=config.EXCHANGE_NAME, exchange_type="topic")

        queue_name = channel.queue_declare("", exclusive=True).method.queue
        channel.queue_bind(
            exchange=config.EXCHANGE_NAME, queue=queue_name, routing_key=routing_key
        )
        channel.basic_consume(
            queue=queue_name, on_message_callback=self.callback, auto_ack=True
        )

        print(" [*] Waiting for work. To exit press CTRL+C")
        channel.start_consuming()
