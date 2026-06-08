from src.tools.sql_tool import sql_query


def test_sql_rejects_non_select():
	result = sql_query.invoke({"sql": "DROP TABLE facts"})
	assert result[0].get("error")


def test_sql_rejects_unknown_table():
	result = sql_query.invoke({"sql": "SELECT * FROM users"})
	assert result[0].get("error")
