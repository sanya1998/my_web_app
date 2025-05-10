from app.common.dependencies.auth.admin import AdminUserDep
from app.common.dependencies.auth.admin_moderator import AdminOrModeratorUserDep, get_admin_or_moderator_by_request
from app.common.dependencies.auth.base import CurrentUserDep
from app.common.dependencies.auth.manager import ManagerUserDep
from app.common.dependencies.auth.manager_user import ManagerOrUserDep
from app.common.dependencies.auth.moderator import ModeratorUserDep
