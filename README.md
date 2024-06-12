# Preparing Environment

```
$ python3.9 -m venv myenv OR
$ virtualenv myenv
$ source myenv/bin/activate
$ pip install -r requirements.txt
$ python create_news_item.py -s biotech
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
$ openai api fine_tunes.results -i ft-K7Hrh4sNyTAl6aaxypowMK0L > result.csv
```

# Business Model

Once we reach say 10k users per market, options:

1. Go to public company eg Tallink and offer to be paid % if the volume of the company increases
2. Trade yourself - once you are able to move the market can front run (legal as it's public)
3. Lead generator - ask brokers to pay you 100 EUR / customer (Admiral markets told they are paying 200 eur / customer)
4. Subscription for premium features / signals - hard (seekingalpha)
5. Advertising (not preferred) - https://www.zerohedge.com/
