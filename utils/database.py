import MySQLdb
from flask import g, current_app

def get_db():
    if 'db' not in g:
        g.db = MySQLdb.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            db=current_app.config['MYSQL_DB'],
            cursorclass=MySQLdb.cursors.DictCursor
        )
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)
    # app.cli.add_command(init_db_command) # Descomentar para añadir comando CLI

# Código para comando CLI 'init-db' (opcional, requiere 'click')
# import click
# from flask.cli import with_appcontext

# def init_db_contents():
#     db = get_db()
#     cursor = db.cursor()
#     with current_app.open_resource('schema.sql') as f:
#         sql_script = f.read().decode('utf8')
#         # Esto es una simplificación. Ejecutar scripts SQL complejos con múltiples
#         # comandos y cambios de delimitador puede ser problemático aquí.
#         # Se recomienda ejecutar schema.sql usando el cliente mysql directamente.
#         try:
#             # Intentar ejecutar todo el script. Puede fallar con delimitadores.
#             # for result in cursor.execute(sql_script, multi=True): pass # Necesita un conector que lo soporte bien
#             print("Para inicializar la BD, ejecuta schema.sql manualmente con un cliente MySQL.")
#             print("Ejemplo: mysql -u tu_usuario -p tu_base_de_datos < schema.sql")
#         except Exception as e:
#             print(f"Error al intentar ejecutar schema.sql: {e}")
#             print("Por favor, ejecuta schema.sql manualmente.")
#     db.commit()

# @click.command('init-db')
# @with_appcontext
# def init_db_command():
#     # init_db_contents()
#     click.echo('Comando init-db llamado. Revisa las instrucciones para ejecutar schema.sql manualmente.')
