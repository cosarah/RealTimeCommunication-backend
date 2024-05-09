mkdir db
chmod 664 db/db.sqlite3

# 设置数据库文件的路径
DB_FILE="db.sqlite3"

# 检查文件是否存在
if [ -f "$DB_FILE" ]; then
    echo "数据库文件已存在：$DB_FILE"
else
    # 使用 SQLite 命令创建空的数据库文件
    sqlite3 "$DB_FILE" '.databases'
    
    echo "数据库文件已创建：$DB_FILE"
fi


coverage run --source DjangoHW,user,friend,message,conversation,utils -m pytest --junit-xml=xunit-reports/xunit-result.xml
ret=$?
coverage xml -o coverage-reports/coverage.xml
coverage report
exit $ret