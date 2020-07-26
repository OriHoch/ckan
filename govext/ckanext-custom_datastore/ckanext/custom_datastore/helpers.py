# encoding: utf-8

import json
import logging

import paste.deploy.converters as converters
import sqlparse

from ckan.plugins.toolkit import get_action, ObjectNotFound, NotAuthorized

log = logging.getLogger(__name__)


def is_single_statement(sql):
    '''Returns True if received SQL string contains at most one statement'''
    return len(sqlparse.split(sql)) <= 1


def is_valid_field_name(name):
    '''
    Check that field name is valid:
    * can't start or end with whitespace characters
    * can't start with underscore
    * can't contain double quote (")
    * can't be empty
    '''
    return (name and name == name.strip() and
            not name.startswith('_') and
            '"' not in name)


def is_valid_table_name(name):
    if '%' in name:
        return False
    return is_valid_field_name(name)


def get_list(input, strip_values=True):
    '''Transforms a string or list to a list'''
    if input is None:
        return
    if input == '':
        return []

    converters_list = converters.aslist(input, ',', True)
    if strip_values:
        return [_strip(x) for x in converters_list]
    else:
        return converters_list


def validate_int(i, non_negative=False):
    try:
        i = int(i)
    except ValueError:
        return False
    return i >= 0 or not non_negative


def _strip(input):
    if isinstance(input, basestring) and len(input) and input[0] == input[-1]:
        return input.strip().strip('"')
    return input


def should_fts_index_field_type(field_type):
    return field_type.lower() in ['tsvector', 'text', 'number']


def get_table_names_from_sql(context, sql):
    '''Parses the output of EXPLAIN (FORMAT JSON) looking for table names

    It performs an EXPLAIN query against the provided SQL, and parses
    the output recusively looking for "Relation Name".

    Note that this requires Postgres 9.x.

    :param context: a CKAN context dict. It must contain a 'connection' key
        with the current DB connection.
    :type context: dict
    :param sql: the SQL statement to parse for table names
    :type sql: string

    :rtype: list of strings
    '''
    log.info("get_table_names_from_sql - start - HELPERS OLD")

    def _get_table_names_from_plan(plan):

        log.info("_get_table_names_from_plan start")
        table_names = []
        try:
            if plan.get('Relation Name'):
                table_names.append(plan['Relation Name'])

            if 'Plans' in plan:
                for child_plan in plan['Plans']:
                    table_name = _get_table_names_from_plan(child_plan)
                    if table_name:
                        table_names.extend(table_name)
        except Exception, e:
            log.error('_get_table_names_from_plan - ', e.message)
        return table_names

    log.info("<SQL>")
    log.info(sql)
    log.info("</SQL>")

    result = context['connection'].execute(
        'EXPLAIN (FORMAT JSON) {0}'.format(sql.encode('utf-8'))).fetchone()

    log.info("<RESULT>")
    log.info(result)
    log.info("</RESULT>")

    table_names = []

    try:

        log.info("<result['QUERY PLAN']>")
        log.info(result['QUERY PLAN'])
        log.info("</result['QUERY PLAN']>")

        log.info("<query_plan parsing START>")

        if isinstance(result['QUERY PLAN'], list):
            log.info("LIST query plan")
            result_query_plan = json.dumps(result['QUERY PLAN'])
        #    result_query_plan_unicode = ''.join(map(str, result['QUERY PLAN']))
        #    log.info("is result query plan str? ")
        #    log.info(isinstance(result_query_plan_unicode, str))
        #    log.info('unicode list query plan')
        #    log.info(result_query_plan_unicode)
        #    result_query_plan_decoded = result_query_plan_unicode.replace("u'", "'")
        #    log.info('list query plan')
        #    result_query_plan = result_query_plan_decoded.replace("False", "'False'")
        #    log.info("the result_query_planis: ")
        #    log.info(result_query_plan)
        else:
            log.info('STR query plan')
            log.info("is result query plan str? ")
            log.info(isinstance(result['QUERY PLAN'], str))
            result_query_plan = result['QUERY PLAN']
            log.info("the result_query_plan is: ")
            log.info(result_query_plan)

        log.info("*********** <query_plan> ************")
        try:
            query_plan = json.loads(result_query_plan)
            log.info(query_plan)
        except Exception, e:
            log.error(e.message)
            raise
        log.info("</query_plan>")

        log.info("<plan>")
        plan = query_plan[0]['Plan']
        log.info("<query_plan[0]['Plan']>")
        log.info(plan)
        log.info("</query_plan[0]['Plan']>")
        log.info("</plan>")
        log.info("</query_plan parsing FINISH>")

        log.info("<table_names.extend>")
        table_names.extend(_get_table_names_from_plan(plan))
        log.info(table_names)
        log.info("</table_names.extend>")

    except ValueError:
        log.error('Could not parse query plan')

    return table_names


def datastore_dictionary(resource_id):
    """
    Return the data dictionary info for a resource
    """
    try:
        return [
            f for f in get_action('datastore_search')(
                None, {
                    u'resource_id': resource_id,
                    u'limit': 0,
                    u'include_total': False})['fields']
            if not f['id'].startswith(u'_')]
    except (ObjectNotFound, NotAuthorized):
        return []
