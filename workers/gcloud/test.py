from click import Context

from . import cmd_grp

cmd = "gcloud bucket -l haha create -n akhilesh-test-1"
args = cmd.split()

ctx = Context(cmd_grp, info_name=cmd_grp.name)
cmd_grp.parse_args(ctx, args[1:])
print(cmd_grp.invoke(ctx))


# print(ctx.get_help())
# print()
# print("-" * 70)
# print(bucket_ctx.get_help())
# print()
# print("-" * 70)
# print(create_ctx.get_help())
# print()
# print("-" * 70)
# print(create_ctx.invoke(create_cmd, name="akhilesh-test-click"))
