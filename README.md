# Preparing Environment

```
$ python3.9 -m venv myenv
$ source myenv/bin/activate
$ pip install -r requirements.txt
$ python3 news_reader.py
$ python3 create_news_ticker_bq.py
```
# Open AI Fine Tuning using Open AI CLI

```
$ echo "export OPENAI_API_KEY='my_key'" >> ~/.bashrc
$ source ~/.bashrc
```
```
$ echo $OPENAI_API_KEY
$ openai tools fine_tunes.prepare_data -f data/news.jsonl -q
$ openai api fine_tunes.create -t "data/news_prepared_train.jsonl" -v "data/news_prepared_valid.jsonl" --compute_classification_metrics --classification_positive_class " long" -m ada
$ openai api fine_tunes.results -i ft-ft-K7Hrh4sNyTAl6aaxypowMK0L > result.csv
```

