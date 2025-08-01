import os
import argparse
import sys
import yaml
import jinja2
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--oidc-admin-username",required=True)
parser.add_argument("--oidc-admin-email",required=False)
parser.add_argument("--tenancy",required=True)
args = parser.parse_args()

base_dir = os.path.dirname(__file__)

tenancy_dir = os.path.join(base_dir, "../tenancies")
users_dir = os.path.join(base_dir,"../users/users")
groups_dir = os.path.join(base_dir,"../users/memberships")
tenancies = [t for t in os.listdir(tenancy_dir) if os.path.isdir(os.path.join(tenancy_dir, t))]

if not (args.tenancy in tenancies):
    print("Tenancy does not exist: "+args.tenancy)
    sys.exit(1)

user_filename = args.oidc_admin_username+".yaml"
user_filepath = os.path.join(users_dir, user_filename)
membership_filepath = os.path.join(groups_dir, user_filename)

if user_filename in os.listdir(users_dir):
    with open(user_filepath) as stream:
        user_stream = yaml.safe_load(stream)
    
    if args.oidc_admin_email != None and user_stream["spec"]["forProvider"]["email"] != args.oidc_admin_email:
        print("User already exists with a different email address")
        sys.exit(1)

    with open(membership_filepath) as stream:
        try:
            membership_stream = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    if args.tenancy in map(lambda x: x["name"], membership_stream["spec"]["forProvider"]["groupIdsRefs"]):
        print("Already a member of that tenancy")
        os.exit(1)
    else:
        membership_stream["spec"]["forProvider"]["groupIdsRefs"].append(
            {
                "name": args.tenancy,
                "resolve": "Always"
            }
        )
        with open(membership_filepath, mode="w", encoding="utf-8") as file:
            yaml.dump(membership_stream, file)
        print("Added "+args.oidc_admin_username+" as member of "+args.tenancy)
        sys.exit(0)
    
else:
    if args.oidc_admin_email == None:
        print("--oidc-admin-email is required for new users")
        sys.exit(1)
    
    email_search_result = subprocess.run(['grep', '-rl', args.oidc_admin_email, users_dir], stdout=subprocess.PIPE, text=True)
    files_with_email = email_search_result.stdout.strip().split('\n') if email_search_result.stdout else []
    if len(files_with_email) > 0:
        print("Another user already exists with that email")
        sys.exit(1)

    jinja_vars = dict(
        tenancy=args.tenancy,
        oidc_admin_username=args.oidc_admin_username,
        oidc_admin_email=args.oidc_admin_email
    )
    environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(base_dir, "templates", "user")))

    with open(os.path.join(users_dir,user_filename), mode="w", encoding="utf-8") as outputFile:
        outputFile.write(environment.get_template("user.yaml.j2").render(jinja_vars))

    with open(os.path.join(groups_dir,user_filename), mode="w", encoding="utf-8") as outputFile:
        outputFile.write(environment.get_template("membership.yaml.j2").render(jinja_vars))

    with open(os.path.join(base_dir,"../users/kustomization.yaml"),'a') as resourcesFile:
        resourcesFile.write("  - ./users/"+user_filename+"\n")
        resourcesFile.write("  - ./memberships/"+user_filename+"\n")

    print("Created user "+user_filename)
