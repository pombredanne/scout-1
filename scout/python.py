import scout

class ScoutModule(scout.BasicScoutModule):

    name = "python"
    desc = "Search for the python modules."
    sql = 'SELECT package, module FROM modules LEFT JOIN packages ON modules.id_pkg=packages.id_pkg WHERE module LIKE ?'