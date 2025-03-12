from . import user_management_bp
from flask import redirect, url_for, render_template, flash, request
from flask_login import login_required
import string, random
from ...extensions import db
from ...models.users import User, Role, Module, UserModule
from ...forms import AddRoleForm, AddModuleForm
from ...decorators import is_admin


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


@user_management_bp.route('/user/<int:user_id>', methods=['GET', 'POST'])
def user_detail(user_id):
    user = User.query.get_or_404(user_id)

    def show_available_user_modules(user_id):
        # Get the user from the database
        user = User.query.get_or_404(user_id)

        # Get all modules that the user is currently assigned to
        assigned_modules = [user_module.module.id for user_module in user.user_modules]

        # Get all modules from the database
        all_modules = Module.query.all()

        # Filter out modules already assigned to the user
        available_modules = [module for module in all_modules if module.id not in assigned_modules]

        return available_modules

    all_modules = show_available_user_modules(user_id=user_id)

    if request.method == 'POST':
        module_id = request.form['module_id']
        module = Module.query.get_or_404(module_id)

        # Add module to the user
        user_module = UserModule(user_id=user.id, module_id=module.id)
        db.session.add(user_module)
        db.session.commit()

        flash(f'Modul {module.name} byl přidán uživateli.', 'success')
        return redirect(url_for('user_management.user_detail', user_id=user.id))

    return render_template('user_detail.html', user=user, all_modules=all_modules)


@user_management_bp.route('/user/<int:user_id>/remove_module/<int:module_id>', methods=['POST'])
def user_remove_module(user_id, module_id):
    user = User.query.get_or_404(user_id)
    module = Module.query.get_or_404(module_id)

    # Find the association and remove it
    user_module = UserModule.query.filter_by(user_id=user.id, module_id=module.id).first()
    if user_module:
        db.session.delete(user_module)
        db.session.commit()

    flash(f'Modul {module.name} byl odebrán uživateli.', 'success')
    return redirect(url_for('user_management.user_detail', user_id=user.id))


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


@user_management_bp.route("/modules", methods=["POST", "GET"])
def modules():
    modules = Module.query.all()
    form = AddModuleForm()
    if form.validate_on_submit():
        new_module = Module(name=form.name.data)
        db.session.add(new_module)
        db.session.commit()
        flash("Role byla vytvořena úspěšně", "success")
        return redirect(url_for("user_management.modules"))
    return render_template("modules_management.html", modules=modules, form=form)
