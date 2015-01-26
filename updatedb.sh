yes yes | python ~/kutime_web/manage.py flush
python ~/kutime_web/load_data.py
/etc/init.d/nginx restart
