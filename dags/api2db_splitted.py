import datetime as dt

from airflow import DAG
from airflow.operators.python import PythonOperator
from dotenv import load_dotenv

from mongodb.data2mongo import insert_ohlcvs
from upbit.request import fetch_minute_ohlcvs
from utils.timeutils import ETZ

load_dotenv("/tmp/.env")

########################### Set Configs ###########################
SCHEDULE_INTERVAL = "0 * * * *"  # every hour
MINUTE_INTERVAL = 60
GET_CNT = 1

fetch_base_template_dict = {
    "minute_interval": MINUTE_INTERVAL,
    "get_cnt": GET_CNT,
    "start_time": "{{ ts_nodash }}",
}
tickers = ["USDT-BTC", "USDT-ETH"]
req_time_intervals = [float(i + 1) for i in range(len(tickers))]

fetch_template_dicts = {}
for ticker, req_time_interval in zip(tickers, req_time_intervals):
    fetch_base_template_dict.update(
        coin_ticker=ticker, req_time_interval=req_time_interval
    )
    fetch_template_dicts[ticker] = fetch_base_template_dict.copy()
################################################################

dag = DAG(
    dag_id="api2db_splitted",
    description="Get ohlcv data using upbit API",
    start_date=dt.datetime(2022, 6, 1, 0, 0, tzinfo=ETZ),
    end_date=dt.datetime(2022, 7, 22, 0, 0, tzinfo=ETZ),
    schedule_interval=SCHEDULE_INTERVAL,
)

fetch_usdt_btc = PythonOperator(
    task_id="fetch_usdt_btc",
    python_callable=fetch_minute_ohlcvs,
    templates_dict=fetch_template_dicts["USDT-BTC"],
    dag=dag,
)

fetch_usdt_eth = PythonOperator(
    task_id="fetch_usdt_eth",
    python_callable=fetch_minute_ohlcvs,
    templates_dict=fetch_template_dicts["USDT-ETH"],
    dag=dag,
)

insert_jsons = PythonOperator(
    task_id="insert_jsons",
    python_callable=insert_ohlcvs,
    dag=dag,
    templates_dict={"start_time": "{{ ts_nodash }}"},
)

fetch_usdt_btc >> insert_jsons
fetch_usdt_eth >> insert_jsons
