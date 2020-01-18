"""
TODO plans

design as plugins that can be "registered"
each plugin should perform a task, must have a help description
plugins planned
  1. view projects
  2. view/create/delete buckets
     support parameters like zone and region
  3. view permissions
  4. change permissions?
  5. transfer between buckets
Needs topics for each category and one for help

add command group for service accounts.
Register it in init

keys https://stackoverflow.com/questions/44291205/iam-service-account-key-vs-google-credentials-file/

"""

from click import Context

from . import gcloud


cmd = "gcloud bucket iam -n akhilesh-test-1"
cmd = "gcloud bucket iam -n akhilesh-test-1 add -r roles/storage.objectViewer -m user:akhileshhalageri@gmail.com"
ctx = Context(gcloud, info_name=gcloud.name, obj={})
gcloud.parse_args(ctx, cmd.split()[1:])
gcloud.invoke(ctx)

