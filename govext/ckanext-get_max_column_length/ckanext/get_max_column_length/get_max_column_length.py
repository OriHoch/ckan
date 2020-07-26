import ckan.controllers.home as home
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import ckan.lib.base as base
import pylons.config as config
from webob import Request
import json
CACHE_PARAMETERS = ['__cache', '__no_cache__']


class GetMaxColumnLengthController(home.HomeController):

    def get_max_column_length(self):

        url = self._py_object.session._environ['CKAN_CURRENT_URL'].split("/")
        id = url[2]
        eng = create_engine(config.get('ckan.datastore.write_url'))
        con = eng.connect()
        try:
            cl = {}
            sql = "SELECT column_name FROM information_schema.columns WHERE table_name =" + "'" + id + "'"
            rows = con.execute(text(sql)).fetchall()
            for row in rows:
                sql = 'SELECT max(length("' + row[0] + '"::text)) FROM public."' + id + '"'
                count = con.execute(text(sql)).fetchone()._row[0]
                cl[row[0]] = str(count)
            cl = json.dumps(cl)
            return cl
        except:
            print ("No such resource")

        con.close()
        return base.render('admin/get_column_max_length.html', cache_force=True)



