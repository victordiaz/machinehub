from flask.helpers import url_for
from flask_classy import route, FlaskView
from flask.templating import render_template
from machinehub.server.app.controllers.auth_controller import requires_auth
from machinehub.server.app.models.machine_model import MachineModel
from werkzeug.exceptions import abort
from machinehub.server.app.models.explorer_model import Pagination


PER_PAGE = 20


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


class MachinehubController(FlaskView):
    decorators = [requires_auth]
    route_prefix = '/'
    route_base = '/'

    def __init__(self):
        self.machines_model = MachineModel()

    @route('/machines/<int:page>')
    def machines(self, page):
        links = []
        count = self.machines_model.count
        machines = self.machines_model.get_machines_for_page(page, PER_PAGE, count)
        for name, doc in machines:
            url = url_for('MachineController:machine', machine_name=name)
            links.append((url, name, doc.title or "", doc.description or ""))
        if not machines and page != 1:
            abort(404)
        pagination = Pagination(page, PER_PAGE, count)
        return render_template('explorer.html',
                               pagination=pagination,
                               links=links
                               )

    @route('/')
    def index(self):
        machines_info = []
        machines = self.machines_model.get_last_machines()
        for name, doc in machines:
            url = url_for('MachineController:machine', machine_name=name)
            image = doc.images[0] if doc.images else None
            machines_info.append((image, doc.title or "", doc.description or "", url))

        def chunks(l, n):
            """Yield successive n-sized chunks from l."""
            for i in xrange(0, len(l), n):
                yield l[i:i+n]
        splited_machines_info = list(chunks(machines_info, 4))

        return render_template('home.html',
                               splited_machines_info=splited_machines_info)
