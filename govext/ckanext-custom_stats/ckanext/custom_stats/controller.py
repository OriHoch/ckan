import ckan.plugins as p
from ckan.lib.base import BaseController
import ckan.logic as logic
import ckan.model as model
import ckan.lib.base as base
from ckan.common import _, c
import stats as stats_lib
import logging
import sys
import xlwt as xlrd
import ckan.lib.helpers as h

log = logging.getLogger(__name__)

try:
    from pylons import config
    log.info("import pylons config succeeded")
except ImportError as ex:
    config = None
    log.info("ImportError - from pylons import config: " + ex.message)

reload(sys)
sys.setdefaultencoding('utf8')


path = config.get('excel_files_directory')

def export_tags_to_excel(c, stats):
    try:

        book = xlrd.Workbook(encoding="utf-8")
        sheet1 = book.add_sheet('sheet1')

        top_tags = stats.top_tags()

        sheet1.write(0, 0, _('Tag Name'))
        sheet1.write(0, 1, _('Number of Datasets'))
        for i, e in enumerate(top_tags):
            sheet1.write(i + 1, 0, top_tags[i][0].name)
            sheet1.write(i + 1, 1, top_tags[i][1])

        name = config.get('top_tags_file_name')
        full_path = path + name
        c.path_to_tags_file = name

        book.save(full_path)
    except Exception as ex:
        log.info("export_tags_to_excel - Error: " + ex.message)
        return None


def export_largest_groups_to_excel(c, stats):
    try:

        book = xlrd.Workbook(encoding="utf-8")
        sheet1 = book.add_sheet('sheet1')

        largest_groups = stats.largest_groups()

        sheet1.write(0, 0, _('Group'))
        sheet1.write(0, 1, _('Number of Datasets'))
        for i, e in enumerate(largest_groups):
            sheet1.write(i + 1, 0, largest_groups[i][0].title)
            sheet1.write(i + 1, 1, largest_groups[i][1])

        name = config.get('largest_groups_file_name')
        full_path = path + name
        c.path_to_largest_groups_file = name
        book.save(full_path)
    except Exception as ex:
        log.info("export_largest_groups_to_excel - Error: " + ex.message)
        return None


def export_datasets_most_edited_to_excel(c, stats):
    try:
        book = xlrd.Workbook(encoding="utf-8")
        sheet1 = book.add_sheet('sheet1')

        most_edited_packages = stats.most_edited_packages()

        sheet1.write(0, 0, _('Dataset'))
        sheet1.write(0, 1, _('Number of edits'))
        for i, e in enumerate(most_edited_packages):
            sheet1.write(i + 1, 0, most_edited_packages[i][0].title)
            sheet1.write(i + 1, 1, most_edited_packages[i][1])

        name = config.get('datasets_most_edited_file')
        full_path = path + name
        c.path_to_datasets_most_edited_file = name
        book.save(full_path)
    except Exception as ex:
        log.info("export_datasets_most_edited_to_excel - Error: " + ex.message)
        return None


def export_top_users_to_excel(c, stats):
    try:
        book = xlrd.Workbook(encoding="utf-8")
        sheet1 = book.add_sheet('sheet1')

        top_users = stats.top_package_creators()

        sheet1.write(0, 0, _('User'))
        sheet1.write(0, 1, _('Number of Datasets'))
        for i, e in enumerate(top_users):
            sheet1.write(i + 1, 0, top_users[i][0].display_name)
            sheet1.write(i + 1, 1, top_users[i][1])

        name = config.get('top_users_file')
        full_path = path + name
        c.path_to_top_users_file = name
        book.save(full_path)
    except Exception as ex:
        log.info("export_top_users_to_excel - Error: " + ex.message)
        return None


def export_modified_resources_to_excel(c, stats):
    try:
        url_max_length = 255
        book = xlrd.Workbook(encoding="utf-8")
        sheet1 = book.add_sheet('sheet1')

        modified_resources = stats.modified_resources()

        sheet1.write(0, 0, _('Group'))
        sheet1.write(0, 1, _('Dataset'))
        sheet1.write(0, 2, _('Resource'))
        sheet1.write(0, 3, _('Last Modified'))
        sheet1.write(0, 4, _('Created'))
        sheet1.write(0, 5, _('URL'))

        date_format = xlrd.XFStyle()
        date_format.num_format_str = 'dd/mm/yyyy'

        for i, e in enumerate(modified_resources):
            sheet1.write(i+1, 0, modified_resources[i][0])
            sheet1.write(i+1, 1, modified_resources[i][1])
            sheet1.write(i + 1, 2, modified_resources[i][2])
            sheet1.write(i + 1, 3, modified_resources[i][3], date_format)
            sheet1.write(i + 1, 4, modified_resources[i][4], date_format)
            if 'http' in modified_resources[i][7] and len(str(modified_resources[i][7])) < url_max_length:
                sheet1.write(i + 1, 5, xlrd.Formula('HYPERLINK("%s")' % (modified_resources[i][7])))
            else:
                sheet1.write(i + 1, 5, modified_resources[i][7])

        name = config.get('modified_resources_file')
        full_path = path + name
        c.path_to_modified_resources_file = name
        book.save(full_path)
    except Exception as ex:
        log.info("export_modified_resources_to_excel Error: " + ex.message)
        return None

def export_org_resources_to_excel(c, stats):
    try:
        book = xlrd.Workbook(encoding="utf-8")
        sheet1 = book.add_sheet('sheet1')

        org_resources = stats.org_resources()

        sheet1.write(0, 0, _('Organization'))
        sheet1.write(0, 1, _('CSV'))
        sheet1.write(0, 2, _('DOC'))
        sheet1.write(0, 3, _('DOCX'))
        sheet1.write(0, 4, _('GeoJSON'))
        sheet1.write(0, 5, _('HTML'))
        sheet1.write(0, 6, _('JPEG'))
        sheet1.write(0, 7, _('JSON'))
        sheet1.write(0, 8, _('PDF'))
        sheet1.write(0, 9, _('PNG'))
        sheet1.write(0, 10, _('PPT'))
        sheet1.write(0, 11, _('PPTX'))
        sheet1.write(0, 12, _('RSS'))
        sheet1.write(0, 13, _('TXT'))
        sheet1.write(0, 14, _('XLS'))
        sheet1.write(0, 15, _('XLSX'))
        sheet1.write(0, 16, _('XML'))
        sheet1.write(0, 17, _('ZIP'))
        for i, e in enumerate(org_resources):
            sheet1.write(i + 1, 0, org_resources[i][0])
            sheet1.write(i + 1, 1, org_resources[i][1])
            sheet1.write(i + 1, 2, org_resources[i][2])
            sheet1.write(i + 1, 3, org_resources[i][3])
            sheet1.write(i + 1, 4, org_resources[i][4])
            sheet1.write(i + 1, 5, org_resources[i][5])
            sheet1.write(i + 1, 6, org_resources[i][6])
            sheet1.write(i + 1, 7, org_resources[i][7])
            sheet1.write(i + 1, 8, org_resources[i][8])
            sheet1.write(i + 1, 9, org_resources[i][9])
            sheet1.write(i + 1, 10, org_resources[i][10])
            sheet1.write(i + 1, 11, org_resources[i][11])
            sheet1.write(i + 1, 12, org_resources[i][12])
            sheet1.write(i + 1, 13, org_resources[i][13])
            sheet1.write(i + 1, 14, org_resources[i][14])
            sheet1.write(i + 1, 15, org_resources[i][15])
            sheet1.write(i + 1, 16, org_resources[i][16])
            sheet1.write(i + 1, 17, org_resources[i][17])
        name = config.get('org_resources_file')
        full_path = path + name
        c.path_to_org_resources_file = name
        book.save(full_path)
    except Exception as ex:
        log.info("export_org_resources_to_excel - Error: " + ex.message)
        return None

def export_datapush_tasks_to_excel(c, stats):
    pass

class StatsController(BaseController):

    def index(self):
        c = p.toolkit.c
        try:
            context = {'model': model, 'user': c.user,
                       'auth_user_obj': c.userobj}
            logic.check_access('sysadmin', context)
        except logic.NotAuthorized:
            base.abort(403, _('Not authorized to see this page'))

        stats = stats_lib.Stats()
        rev_stats = stats_lib.RevisionStats()
        c.top_rated_packages = stats.top_rated_packages()

        c.most_edited_packages = stats.most_edited_packages()
        export_datasets_most_edited_to_excel(c, stats)

        c.largest_groups = stats.largest_groups()
        export_largest_groups_to_excel(c, stats)

        c.top_tags = stats.top_tags()
        export_tags_to_excel(c, stats)

        c.top_package_creators = stats.top_package_creators()
        export_top_users_to_excel(c, stats)

        c.new_packages_by_week = rev_stats.get_by_week('new_packages')
        c.deleted_packages_by_week = rev_stats.get_by_week('deleted_packages')
        c.num_packages_by_week = rev_stats.get_num_packages_by_week()
        c.package_revisions_by_week = rev_stats.get_by_week('package_revisions')

        c.modified_resources = stats.modified_resources()
        export_modified_resources_to_excel(c, stats)

        c.org_resources = stats.org_resources()
        export_org_resources_to_excel(c, stats)

        c.datapusher_tasks = stats.datapusher_tasks()
        export_datapush_tasks_to_excel(c, stats)

        c.raw_packages_by_week = []
        for week_date, num_packages, cumulative_num_packages in c.num_packages_by_week:
            c.raw_packages_by_week.append({'date': h.date_str_to_datetime(week_date), 'total_packages': cumulative_num_packages})

        c.all_package_revisions = []
        c.raw_all_package_revisions = []
        for week_date, revs, num_revisions, cumulative_num_revisions in c.package_revisions_by_week:
            c.all_package_revisions.append('[new Date(%s), %s]' % (week_date.replace('-', ','), num_revisions))
            c.raw_all_package_revisions.append({'date': h.date_str_to_datetime(week_date), 'total_revisions': num_revisions})

        c.new_datasets = []
        c.raw_new_datasets = []
        for week_date, pkgs, num_packages, cumulative_num_packages in c.new_packages_by_week:
            c.new_datasets.append('[new Date(%s), %s]' % (week_date.replace('-', ','), num_packages))
            c.raw_new_datasets.append({'date': h.date_str_to_datetime(week_date), 'new_packages': num_packages})

        return p.toolkit.render('ckanext/stats/index.html')





