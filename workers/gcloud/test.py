from click import Context

from . import cmd_grp

cmd = "gcloud bucket -l haha create -n hoho"
args = cmd.split()


ctx = Context(cmd_grp, info_name="gcloud")
cmd_name, cmd, args = cmd_grp.resolve_command(ctx, args[1:])
print(cmd.name, args)


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
