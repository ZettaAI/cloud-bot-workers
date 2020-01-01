from click import Context

from . import ctx
from . import cmd_grp


print(ctx.get_help())
print()
print("#" * 30)

create_ctx = Context(
    cmd_grp.get_command(None, "bucket"), parent=ctx, info_name="bucket"
)
print(create_ctx.get_help())

# create_ctx.invoke(create_cmd, bucket_name="akhilesh-test-click")
