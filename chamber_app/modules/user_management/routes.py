from . import user_management_bp
from flask import redirect, url_for, render_template, flash
import string, random
from ...extensions import db
from ...models.users import User, Role
from ...forms import AddRoleForm


@user_management_bp.route('<int:user_id>/generate_password')
def generate_password(user_id):
    all_characters = list(string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation)
    password = ''.join(random.sample(all_characters, 8))
    user = User.query.filter_by(id=user_id).first()
    user.set_password(password)
    print(password)
    db.session.commit()
    return redirect(url_for("auth.management"))


@user_management_bp.route('/users')
def users():
    users = User.query.all()
    return render_template('users_management.html', users=users)


@user_management_bp.route('/roles')
def roles():
    form = AddRoleForm()
    roles = Role.query.all()
    return render_template('roles_management.html', form=form, roles=roles)


@user_management_bp.route('/role/add', methods=["POST"])
def add_role():
    form = AddRoleForm()
    if form.validate_on_submit():
        new_role = Role(name=form.name.data)
        db.session.add(new_role)
        db.session.commit()
        flash("Role byla vytvořena úspěšně", "success")
        return redirect(url_for("user_management.roles"))
